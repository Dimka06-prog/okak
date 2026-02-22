#!/usr/bin/env python3
"""
Скрипт для сборки .exe файла приложения для Windows
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

def build_windows_exe():
    """Сборка .exe файла для Windows"""
    print("\n🔨 Начинаю сборку .exe файла для Windows...")
    
    # Очистка предыдущих сборок
    if Path("build").exists():
        shutil.rmtree("build")
    if Path("dist").exists():
        shutil.rmtree("dist")
    
    # Параметры для PyInstaller (Windows)
    pyinstaller_args = [
        "pyinstaller",
        "--name=PREDATOR_Windows",
        "--windowed",  # Без консольного окна
        "--onefile",   # В один файл
        "--clean",     # Очистка кэша
        "--noconfirm", # Не спрашивать подтверждение
        "--add-data=src/config;config",  # Включить конфигурационные файлы (Windows синтаксис)
        "--add-data=data;data",          # Включить файлы данных (Windows синтаксис)
        "--hidden-import=firebase_admin",
        "--hidden-import=google.cloud.firestore",
        "--hidden-import=google.auth",
        "--hidden-import=PyQt6.QtCore",
        "--hidden-import=PyQt6.QtWidgets",
        "--hidden-import=PyQt6.QtGui",
        "--exclude-module=tkinter",
        "--exclude-module=matplotlib",
        "--exclude-module=PIL",
        "--icon=assets/icon.ico" if Path("assets/icon.ico").exists() else "",  # Иконка если есть
        "app.py"
    ]
    
    # Удаляем пустой аргумент иконки если ее нет
    pyinstaller_args = [arg for arg in pyinstaller_args if arg]
    
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

def create_windows_release():
    """Создание релизного пакета для Windows"""
    print("\n📦 Создаю релизный пакет для Windows...")
    
    release_dir = Path("release_windows")
    if release_dir.exists():
        shutil.rmtree(release_dir)
    
    release_dir.mkdir()
    
    # Копирование .exe файла
    exe_path = Path("dist/PREDATOR_Windows.exe")
    if exe_path.exists():
        shutil.copy2(exe_path, release_dir / "PREDATOR.exe")
        print("✓ .exe файл скопирован")
    else:
        print("⚠ .exe файл не найден!")
        return None
    
    # Копирование необходимых файлов
    files_to_copy = [
        ("README.md", "README.md"),
        ("docs/ЗАПУСК.md", "ЗАПУСК.md"),
        ("docs/EXE_ИНСТРУКЦИЯ.md", "ИНСТРУКЦИЯ.md"),
        ("requirements.txt", "requirements.txt")
    ]
    
    for src, dest in files_to_copy:
        src_path = Path(src)
        if src_path.exists():
            shutil.copy2(src_path, release_dir / dest)
            print(f"✓ Скопирован {src}")
    
    # Создание архива
    archive_name = "PREDATOR_Windows_v1.0_Release.zip"
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
    print("🚀 Скрипт сборки PREDATOR приложения для Windows")
    print("=" * 60)
    
    # Проверка зависимостей
    check_requirements()
    
    # Создание директорий
    create_directories()
    
    # Копирование конфигурационных файлов
    copy_config_files()
    
    # Сборка .exe для Windows
    if not build_windows_exe():
        print("❌ Сборка не удалась")
        return 1
    
    # Создание релизного пакета
    release_dir = create_windows_release()
    if not release_dir:
        print("❌ Не удалось создать релизный пакет")
        return 1
    
    # Очистка
    cleanup()
    
    print("\n🎉 Сборка для Windows завершена успешно!")
    print(f"📂 .exe файл: {Path('dist/PREDATOR_Windows.exe').absolute()}")
    print(f"📦 Релизный пакет: {release_dir.absolute()}")
    print(f"📦 Архив: {Path('PREDATOR_Windows_v1.0_Release.zip').absolute()}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
