#!/usr/bin/env python3
"""
Кроссплатформенный скрипт сборки .exe файла приложения
"""

import os
import sys
import shutil
import subprocess
import platform
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

def build_crossplatform_exe():
    """Сборка .exe файла для текущей платформы"""
    system = platform.system()
    print(f"\n🔨 Начинаю сборку .exe файла для {system}...")
    
    # Очистка предыдущих сборок
    if Path("build").exists():
        shutil.rmtree("build")
    if Path("dist").exists():
        shutil.rmtree("dist")
    
    # Определение параметров для разных платформ
    is_windows = system == "Windows"
    is_macos = system == "Darwin"
    is_linux = system == "Linux"
    
    # Разделитель путей для add-data
    separator = ';' if is_windows else ':'
    
    # Базовые параметры PyInstaller
    pyinstaller_args = [
        "pyinstaller",
        "--name=PREDATOR",
        "--onefile",   # В один файл
        "--clean",     # Очистка кэша
        "--noconfirm", # Не спрашивать подтверждение
        f"--add-data=src/config{separator}config",  # Включить конфигурационные файлы
        f"--add-data=data{separator}data",          # Включить файлы данных
        "--hidden-import=firebase_admin",
        "--hidden-import=google.cloud.firestore",
        "--hidden-import=google.auth",
        "--hidden-import=PyQt6.QtCore",
        "--hidden-import=PyQt6.QtWidgets",
        "--hidden-import=PyQt6.QtGui",
        "--exclude-module=tkinter",
        "--exclude-module=matplotlib",
        "--exclude-module=PIL",
        "app.py"
    ]
    
    # Платформо-зависимые параметры
    if is_windows:
        pyinstaller_args.insert(pyinstaller_args.index("app.py"), "--windowed")
        pyinstaller_args.insert(pyinstaller_args.index("app.py"), "--icon=assets/icon.ico" if Path("assets/icon.ico").exists() else "")
    elif is_macos:
        pyinstaller_args.insert(pyinstaller_args.index("app.py"), "--windowed")
        pyinstaller_args.insert(pyinstaller_args.index("app.py"), "--icon=assets/icon.icns" if Path("assets/icon.icns").exists() else "")
    elif is_linux:
        pyinstaller_args.insert(pyinstaller_args.index("app.py"), "--windowed")
    
    # Удаляем пустые аргументы
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

def create_release_package():
    """Создание релизного пакета"""
    print("\n📦 Создаю релизный пакет...")
    
    system = platform.system()
    release_dir = Path(f"release_{system.lower()}")
    
    if release_dir.exists():
        shutil.rmtree(release_dir)
    
    release_dir.mkdir()
    
    # Определение имени исполняемого файла
    if system == "Windows":
        exe_name = "PREDATOR.exe"
    else:
        exe_name = "PREDATOR"
    
    # Копирование .exe файла
    exe_path = Path(f"dist/{exe_name}")
    if exe_path.exists():
        shutil.copy2(exe_path, release_dir / exe_name)
        print(f"✓ {exe_name} файл скопирован")
    else:
        print(f"⚠ {exe_name} файл не найден!")
        return None
    
    # Копирование необходимых файлов
    files_to_copy = [
        ("README.md", "README.md"),
        ("docs/ЗАПУСК.md", "ЗАПУСК.md"),
        ("docs/EXE_ИНСТРУКЦИЯ.md", "ИНСТРУКЦИЯ.md"),
        ("docs/WINDOWS_BUILD.md", "WINDOWS_BUILD.md"),
        ("requirements.txt", "requirements.txt")
    ]
    
    for src, dest in files_to_copy:
        src_path = Path(src)
        if src_path.exists():
            shutil.copy2(src_path, release_dir / dest)
            print(f"✓ Скопирован {src}")
    
    # Создание архива
    archive_name = f"PREDATOR_{system}_v1.0_Release.zip"
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
    system = platform.system()
    print(f"🚀 Скрипт сборки PREDATOR приложения для {system}")
    print("=" * 60)
    
    # Проверка зависимостей
    check_requirements()
    
    # Создание директорий
    create_directories()
    
    # Копирование конфигурационных файлов
    copy_config_files()
    
    # Сборка .exe
    if not build_crossplatform_exe():
        print("❌ Сборка не удалась")
        return 1
    
    # Создание релизного пакета
    release_dir = create_release_package()
    if not release_dir:
        print("❌ Не удалось создать релизный пакет")
        return 1
    
    # Очистка
    cleanup()
    
    # Определение имени файла
    exe_name = "PREDATOR.exe" if system == "Windows" else "PREDATOR"
    
    print(f"\n🎉 Сборка для {system} завершена успешно!")
    print(f"📂 Исполняемый файл: {Path(f'dist/{exe_name}').absolute()}")
    print(f"📦 Релизный пакет: {release_dir.absolute()}")
    print(f"📦 Архив: {Path(f'PREDATOR_{system}_v1.0_Release.zip').absolute()}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
