import asyncio
import socket
import time

async def test_proxy(proxy_string):
    """Тестировать прокси на работоспособность (без aiohttp)"""
    try:
        # Парсим прокси
        if proxy_string.startswith("socks5://"):
            parts = proxy_string.replace("socks5://", "").split("@")
            if len(parts) == 2:
                user_pass, host_port = parts
                user, password = user_pass.split(":")
                host, port = host_port.split(":")
            else:
                host_port = parts[0]
                host, port = host_port.split(":")
                user, password = None, None
        elif proxy_string.startswith("http://"):
            parts = proxy_string.replace("http://", "").split("@")
            if len(parts) == 2:
                user_pass, host_port = parts
                user, password = user_pass.split(":")
                host, port = host_port.split(":")
            else:
                host_port = parts[0]
                host, port = host_port.split(":")
                user, password = None, None
        else:
            return False, "Неизвестный формат прокси"
        
        # Проверяем через socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        try:
            sock.connect((host, int(port)))
            sock.close()
            return True, "Прокси доступен"
        except Exception as e:
            return False, f"Не отвечает: {str(e)[:30]}"
            
    except Exception as e:
        return False, f"Ошибка: {str(e)[:30]}"

async def test_proxy_with_ping(proxy_string):
    """Полная проверка прокси с пингом"""
    is_work, msg = await test_proxy(proxy_string)
    ping = 9999
    
    if is_work:
        try:
            if proxy_string.startswith("socks5://"):
                parts = proxy_string.replace("socks5://", "").split("@")
                if len(parts) == 2:
                    _, host_port = parts
                    host, port = host_port.split(":")
                else:
                    host_port = parts[0]
                    host, port = host_port.split(":")
            elif proxy_string.startswith("http://"):
                parts = proxy_string.replace("http://", "").split("@")
                if len(parts) == 2:
                    _, host_port = parts
                    host, port = host_port.split(":")
                else:
                    host_port = parts[0]
                    host, port = host_port.split(":")
            else:
                host, port = "unknown", 0
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            start_time = time.time()
            sock.connect((host, int(port)))
            ping = int((time.time() - start_time) * 1000)
            sock.close()
        except:
            ping = 9999
    
    if not is_work:
        status = "🔴 Прокси НЕ РАБОТАЕТ"
        recommendation = "🔴 Не подходит для рассылки"
        ping_display = "PING: ❌"
    elif ping <= 100:
        status = "🟢 Прокси рабочее"
        recommendation = "🟢 Отлично подходит для рассылки"
        ping_display = f"🔰 PING: {ping} мс"
    elif 100 < ping <= 500:
        status = "🟢 Прокси рабочее"
        recommendation = "🟠 Работает, но медленно"
        ping_display = f"🔰 PING: {ping} мс"
    else:
        status = "🟢 Прокси рабочее"
        recommendation = "🔴 Очень медленно"
        ping_display = f"🔰 PING: {ping} мс"
    
    return {
        "status": status,
        "recommendation": recommendation,
        "ping": ping_display,
        "is_work": is_work,
        "msg": msg
    }

def get_proxy_dict(proxy_string):
    """Получить словарь прокси для telethon"""
    if not proxy_string:
        return None
    
    try:
        if proxy_string.startswith("socks5://"):
            parts = proxy_string.replace("socks5://", "").split("@")
            if len(parts) == 2:
                user_pass, host_port = parts
                user, password = user_pass.split(":")
                host, port = host_port.split(":")
                return {
                    'proxy_type': 'socks5',
                    'addr': host,
                    'port': int(port),
                    'username': user,
                    'password': password
                }
            else:
                host_port = parts[0]
                host, port = host_port.split(":")
                return {
                    'proxy_type': 'socks5',
                    'addr': host,
                    'port': int(port)
                }
        elif proxy_string.startswith("http://"):
            parts = proxy_string.replace("http://", "").split("@")
            if len(parts) == 2:
                user_pass, host_port = parts
                user, password = user_pass.split(":")
                host, port = host_port.split(":")
                return {
                    'proxy_type': 'http',
                    'addr': host,
                    'port': int(port),
                    'username': user,
                    'password': password
                }
            else:
                host_port = parts[0]
                host, port = host_port.split(":")
                return {
                    'proxy_type': 'http',
                    'addr': host,
                    'port': int(port)
                }
    except:
        pass
    return None
