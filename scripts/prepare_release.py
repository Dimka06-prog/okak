#!/usr/bin/env python3
"""
Скрипт для подготовки релиза exe-файлов
"""
import os
import shutil
from pathlib import Path

def prepare_release():
    """Подготовить папку с exe-файлами и конфигурацией"""
    
    # Создаем папку для релиза
    release_dir = Path("release")
    release_dir.mkdir(exist_ok=True)
    
    # Копируем exe-файлы
    dist_dir = Path("dist")
    
    exe_files = [
        ("PredatIliSotrudnichat_v2", "v2 - Современная версия"),
        ("PredatIliSotrudnichat_v1_Original", "v1 - Оригинальная версия")
    ]
    
    print("🚀 Подготовка релиза...")
    
    for exe_name, description in exe_files:
        exe_path = dist_dir / exe_name
        if exe_path.exists():
            release_exe = release_dir / exe_name
            shutil.copy2(exe_path, release_exe)
            print(f"✅ Скопирован: {exe_name} ({description})")
            
            # Делаем исполняемым
            os.chmod(release_exe, 0o755)
        else:
            print(f"❌ Не найден: {exe_name}")
    
    # Копируем конфигурацию для v2
    src_config = Path("src/config/firebase_config.json.example")
    if src_config.exists():
        config_dir = release_dir / "src" / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        release_config = config_dir / "firebase_config.json.example"
        shutil.copy2(src_config, release_config)
        print(f"✅ Скопирован: firebase_config.json.example")
    
    # Копируем инструкции
    instructions = [
        "EXE_ИНСТРУКЦИЯ.md",
        "ЗАПУСК.md"
    ]
    
    for instruction in instructions:
        if Path(instruction).exists():
            shutil.copy2(instruction, release_dir / instruction)
            print(f"✅ Скопирована инструкция: {instruction}")
    
    print(f"\n🎉 Релиз подготовлен в папке: {release_dir.absolute()}")
    print("\n📋 Что делать дальше:")
    print("1. Отредактируйте firebase_config.json.example вашими данными")
    print("2. Переименуйте его в firebase_config.json")
    print("3. Запустите exe-файл")

if __name__ == "__main__":
    prepare_release()
