import os
import asyncio
import shutil
import logging
from telethon import TelegramClient
from telethon.errors import FloodWaitError, AuthKeyError, SessionPasswordNeededError
from telethon.tl.functions.contacts import GetContactIDsRequest
from config import SESSIONS_DIR, API_ID, API_HASH
import database as db

logger = logging.getLogger(__name__)

async def load_session_file(user_id, file_path):
    """Загрузить .session файл с подсчётом контактов"""
    try:
        session_name = os.path.basename(file_path).replace('.session', '')
        session_path = os.path.join(SESSIONS_DIR, f"{session_name}_{user_id}")
        
        shutil.copy2(file_path, f"{session_path}.session")
        
        client = TelegramClient(
            session_path,
            API_ID,
            API_HASH,
            timeout=10
        )
        
        try:
            await client.connect()
            me = await client.get_me()
            
            phone = me.phone if me and me.phone else "Неизвестно"
            username = me.username if me and me.username else "Неизвестно"
            first_name = me.first_name if me and me.first_name else "Неизвестно"
            last_name = me.last_name if me and me.last_name else ""
            
            # === ПОЛУЧАЕМ КОНТАКТЫ ===
            total_contacts = 0
            mutual_contacts = 0
            try:
                dialogs = await client.get_dialogs()
                total_contacts = len(dialogs)
                
                try:
                    contact_ids = await client(GetContactIDsRequest(hash=0))
                except Exception as e:
                    logger.warning(f"Не удалось получить список контактов: {e}")
                    contact_ids = []
                
                mutual_contacts = 0
                for dialog in dialogs:
                    if dialog.is_user and dialog.entity.id in contact_ids:
                        mutual_contacts += 1
            except Exception as e:
                logger.warning(f"Ошибка получения контактов: {e}")
            
            await client.disconnect()
            
            # Сохраняем с контактами
            db.add_session(
                user_id=user_id,
                session_name=f"{session_name}_{user_id}",
                phone=phone,
                username=username,
                first_name=first_name,
                last_name=last_name,
                total_contacts=total_contacts,
                mutual_contacts=mutual_contacts
            )
            
            db.increment_session_load(user_id)
            
            return {
                "status": "success",
                "phone": phone,
                "username": username,
                "total_contacts": total_contacts,
                "mutual_contacts": mutual_contacts
            }
            
        except AuthKeyError:
            return {"status": "error", "error": "Невалидная сессия"}
        except SessionPasswordNeededError:
            return {"status": "error", "error": "Требуется пароль 2FA"}
        except FloodWaitError as e:
            return {"status": "error", "error": f"Флуд: ждите {e.seconds} сек"}
        except Exception as e:
            return {"status": "error", "error": str(e)[:100]}
            
    except Exception as e:
        return {"status": "error", "error": f"Ошибка загрузки: {str(e)[:100]}"}

async def check_session(session_id, user_id, proxy_dict=None):
    """Проверить валидность сессии с повторными попытками получения диалогов"""
    sessions = db.get_sessions(user_id)
    session = next((s for s in sessions if s['id'] == session_id), None)
    
    if not session:
        return False, "Сессия не найдена"
    
    session_name = session['session_name']
    session_path = os.path.join(SESSIONS_DIR, session_name)
    
    if not os.path.exists(f"{session_path}.session"):
        db.update_session_valid(session_id, 0, "Файл сессии не найден")
        return False, "Файл сессии не найден"
    
    try:
        client = TelegramClient(
            session_path,
            API_ID,
            API_HASH,
            proxy=proxy_dict,
            timeout=10
        )
        
        await client.connect()
        
        me = await client.get_me()
        if not me:
            db.update_session_valid(session_id, 0, "Не удалось получить данные")
            await client.disconnect()
            return False, "Не удалось получить данные"
        
        # Повторные попытки получения диалогов (до 3 раз)
        dialogs = None
        for attempt in range(3):
            try:
                dialogs = await client.get_dialogs()
                if dialogs and len(dialogs) > 0:
                    break
                logger.info(f"Попытка {attempt+1}: диалогов {len(dialogs) if dialogs else 0}, ждём 1 сек...")
                await asyncio.sleep(1)
            except Exception as e:
                logger.warning(f"Ошибка получения диалогов (попытка {attempt+1}): {e}")
                await asyncio.sleep(1)
        
        if not dialogs:
            dialogs = []
        
        total_contacts = len(dialogs)
        
        try:
            contact_ids = await client(GetContactIDsRequest(hash=0))
        except Exception as e:
            logger.warning(f"Не удалось получить список контактов: {e}")
            contact_ids = []
        
        mutual_contacts = 0
        for dialog in dialogs:
            if dialog.is_user and dialog.entity.id in contact_ids:
                mutual_contacts += 1
        
        await client.disconnect()
        
        db.update_session_valid(session_id, 1, None)
        db.update_session_contacts(session_id, total_contacts, mutual_contacts)
        
        return True, f"Валидный. Контактов: {total_contacts}, Взаимных: {mutual_contacts}"
        
    except AuthKeyError:
        db.update_session_valid(session_id, 0, "Невалидная сессия")
        return False, "Невалидная сессия"
    except FloodWaitError as e:
        db.update_session_valid(session_id, 0, f"Флуд: ждите {e.seconds} сек")
        return False, f"Флуд: ждите {e.seconds} сек"
    except Exception as e:
        db.update_session_valid(session_id, 0, str(e)[:100])
        return False, str(e)[:100]