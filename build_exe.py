#!/usr/bin/env python3
"""
Скрипт для сборки .exe файла приложения с помощью PyInstaller
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def check_requirements():
    """Проверка наличия необходимых зависимостей"""
    try:
        import PyInstaller
        print("✓ PyInstaller найден")
    except ImportError:
        print("✗ PyInstaller не установлен. Устанавливаю...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller установлен")

def create_directories():
    """Создание необходимых директорий"""
    dirs = ["build", "dist", "logs"]
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"✓ Директория '{dir_name}' готова")

def copy_config_files():
    """Копирование конфигурационных файлов"""
    config_files = [
        "src/config/firebase_config.json",
        "src/config/app_config.json"
    ]
    
    for config_file in config_files:
        if Path(config_file).exists():
            dest = Path(config_file).name
            shutil.copy2(config_file, dest)
            print(f"✓ Скопирован {config_file} -> {dest}")
        else:
            print(f"⚠ Файл {config_file} не найден")

def build_exe():
    """Сборка .exe файла"""
    print("\n🔨 Начинаю сборку .exe файла...")
    
    # Очистка предыдущих сборок
    if Path("build").exists():
        shutil.rmtree("build")
    if Path("dist").exists():
        shutil.rmtree("dist")
    
    # Определение ОС для правильного разделителя путей
    is_windows = os.name == 'nt'
    separator = ';' if is_windows else ':'
    
    # Параметры для PyInstaller
    pyinstaller_args = [
        "pyinstaller",
        "--name=GameApp",
        "--windowed",  # Без консольного окна
        "--onefile",   # В один файл
        "--clean",     # Очистка кэша
        "--noconfirm", # Не спрашивать подтверждение
        f"--add-data=src{separator}src",  # Включить всю папку src
        "--hidden-import=firebase_admin",
        "--hidden-import=google.cloud.firestore",
        "--hidden-import=google.auth",
        "--hidden-import=google.oauth2",
        "--hidden-import=google.auth.transport.requests",
        "--hidden-import=PyQt6.QtCore",
        "--hidden-import=PyQt6.QtWidgets",
        "--hidden-import=PyQt6.QtGui",
        "--hidden-import=asyncio",
        "--hidden-import=typing",
        "--hidden-import=datetime",
        "--hidden-import=json",
        "--hidden-import=logging",
        "--hidden-import=uuid",
        "--exclude-module=tkinter",
        "--exclude-module=matplotlib",
        "--exclude-module=PIL",
        "--exclude-module=numpy",
        "--exclude-module=scipy",
        "--exclude-module=pandas",
        "app.py"
    ]
    
    try:
        result = subprocess.run(pyinstaller_args, check=True, capture_output=True, text=True)
        print("✓ Сборка завершена успешно!")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"✗ Ошибка сборки: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False
    
    return True

def create_release_package():
    """Создание релизного пакета"""
    print("\n📦 Создаю релизный пакет...")
    
    release_dir = Path("release")
    if release_dir.exists():
        shutil.rmtree(release_dir)
    
    release_dir.mkdir()
    
    # Копирование .exe файла
    exe_name = "GameApp.exe" if os.name == 'nt' else "GameApp"
    exe_path = Path(f"dist/{exe_name}")
    if exe_path.exists():
        shutil.copy2(exe_path, release_dir / exe_name)
        print(f"✓ {exe_name} файл скопирован")
    
    # Создание инструкции для запуска
    instruction_content = """# 🎮 Игра "Дилемма заключенного" - Инструкция по запуску

## 🚀 Запуск приложения

### Для Windows:
1. Скачайте и распакуйте архив
2. Запустите файл `GameApp.exe`
3. Наслаждайтесь игрой!

### Для других ОС:
1. Убедитесь что установлен Python 3.8+
2. Установите зависимости: `pip install -r requirements.txt`
3. Запустите: `python app.py`

## 📋 Требования для Windows
- Windows 10 или новее
- Интернет-соединение для работы с Firebase

## 🎮 Как играть
1. Зарегистрируйтесь или войдите в систему
2. Создайте комнату или присоединитесь к существующей
3. Дождитесь второго игрока
4. Нажмите "Готов" когда будете готовы
5. Создатель комнаты запускает игру
6. Выбирайте "Сотрудничать" или "Предать" в каждом вопросе
7. Следите за статистикой в разделе "Статистика"

## 🏆 Система очков
- 🤝 Оба сотрудничают: (3, 3)
- 😔 Один предает, другой сотрудничает: (5, 0)
- ⚔️ Оба предают: (1, 1)

## 📊 Статистика
Просматривайте свою статистику и рейтинг других игроков в меню "Статистика".

## 🔧 Поддержка
При возникновении проблем, убедитесь что:
- Есть интернет-соединение
- Антивирус не блокирует .exe файл
- У вас есть права на запуск приложений

Приятной игры! 🎮
"""
    
    with open(release_dir / "README.md", "w", encoding="utf-8") as f:
        f.write(instruction_content)
    print("✓ Создана инструкция README.md")
    
    # Копирование requirements.txt если существует
    if Path("requirements.txt").exists():
        shutil.copy2("requirements.txt", release_dir / "requirements.txt")
        print("✓ Скопирован requirements.txt")
    
    # Создание архива
    archive_name = "GameApp_Release.zip"
    shutil.make_archive(archive_name.replace('.zip', ''), 'zip', release_dir)
    print(f"✓ Создан архив: {archive_name}")
    
    return release_dir

def cleanup():
    """Очистка временных файлов"""
    print("\n🧹 Очистка временных файлов...")
    
    # Удаление скопированных конфигурационных файлов
    temp_files = ["firebase_config.json", "app_config.json"]
    for file in temp_files:
        if Path(file).exists():
            Path(file).unlink()
            print(f"✓ Удален временный файл: {file}")

def main():
    """Главная функция"""
    print("🚀 Скрипт сборки GameApp приложения")
    print("=" * 50)
    
    # Проверка зависимостей
    check_requirements()
    
    # Создание директорий
    create_directories()
    
    # Сборка .exe
    if not build_exe():
        print("❌ Сборка не удалась")
        return 1
    
    # Создание релизного пакета
    release_dir = create_release_package()
    
    # Очистка
    cleanup()
    
    print("\n🎉 Сборка завершена успешно!")
    
    # Показываем пути к файлам
    exe_name = "GameApp.exe" if os.name == 'nt' else "GameApp"
    print(f"📂 .exe файл: {Path(f'dist/{exe_name}').absolute()}")
    print(f"📦 Релизный пакет: {release_dir.absolute()}")
    print(f"📦 Архив для распространения: {Path('GameApp_Release.zip').absolute()}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
