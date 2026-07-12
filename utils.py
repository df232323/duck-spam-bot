import os
import shutil
import re
from datetime import datetime

def format_time(seconds):
    """Форматировать время в минуты и секунды"""
    if seconds < 60:
        return f"{int(seconds)} сек"
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes} мин {secs} сек"

def format_progress_bar(progress, length=12):
    """Создать прогресс-бар"""
    filled = int(progress / 100 * length)
    bar = "█" * filled + "░" * (length - filled)
    return bar

def parse_proxy(proxy_string):
    """Парсинг прокси строки"""
    proxy_type = None
    if proxy_string.startswith("socks5://"):
        proxy_type = "socks5"
    elif proxy_string.startswith("http://"):
        proxy_type = "http"
    elif proxy_string.startswith("tg://proxy"):
        proxy_type = "tg"
    elif proxy_string.startswith("mtproto://"):
        proxy_type = "mtproto"
    else:
        return None, None
    
    return proxy_type, proxy_string

def extract_username(phone_or_username):
    """Извлечь username из строки"""
    if phone_or_username.startswith("+"):
        return phone_or_username
    elif phone_or_username.startswith("@"):
        return phone_or_username
    else:
        return phone_or_username

def clean_filename(filename):
    """Очистить имя файла от недопустимых символов"""
    return re.sub(r'[^\w\-_.]', '_', filename)

def get_file_size(file_path):
    """Получить размер файла в удобном формате"""
    size = os.path.getsize(file_path)
    for unit in ['Б', 'КБ', 'МБ', 'ГБ']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} ТБ"

def safe_delete_file(file_path):
    """Безопасно удалить файл"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except:
        pass
    return False

def safe_delete_dir(dir_path):
    """Безопасно удалить папку"""
    try:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
            return True
    except:
        pass
    return False

def get_current_time():
    """Получить текущее время в формате строки"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")