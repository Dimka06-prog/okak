#!/usr/bin/env python3
"""
Скрипт для создания правильного билда проекта для распространения
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

def create_proper_build():
    """Создать правильный билд с учетом всех зависимостей"""
    
    print("🔧 Создание правильного билда...")
    
    # Очищаем предыдущие сборки
    for cleanup_dir in ["build", "dist", "release"]:
        if Path(cleanup_dir).exists():
            shutil.rmtree(cleanup_dir)
            print(f"🧹 Очищена папка: {cleanup_dir}")
    
    # Создаем spec-файл с правильными настройками
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src', 'src'),
    ],
    hiddenimports=[
        'abc',
        'PyQt6.QtCore',
        'PyQt6.QtWidgets', 
        'PyQt6.QtGui',
        'firebase_admin',
        'firebase_admin.credentials',
        'firebase_admin.db',
        'google.cloud.firestore',
        'google.auth',
        'google.oauth2',
        'google.auth.transport.requests',
        'bcrypt',
        'cryptography',
        'cryptography.hazmat',
        'cryptography.hazmat.primitives',
        'cryptography.hazmat.primitives.hashes',
        'cryptography.hazmat.primitives.kdf',
        'cryptography.hazmat.backends',
        'cryptography.hazmat.backends.default_backend',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PredatIliSotrudnichat_v2_Fixed',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
    
    with open('app_fixed.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("📝 Создан spec-файл: app_fixed.spec")
    
    # Запускаем сборку
    print("🚀 Запуск сборки...")
    try:
        result = subprocess.run([
            sys.executable, '-m', 'PyInstaller', 
            '--clean', 
            'app_fixed.spec'
        ], check=True, capture_output=True, text=True)
        
        print("✅ Сборка завершена успешно!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка сборки: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False
    
    # Проверяем результат
    exe_path = Path("dist/PredatIliSotrudnichat_v2_Fixed")
    if exe_path.exists():
        print(f"✅ Exe-файл создан: {exe_path}")
        print(f"📊 Размер: {exe_path.stat().st_size / (1024*1024):.1f} MB")
        
        # Делаем исполняемым
        os.chmod(exe_path, 0o755)
        
        # Создаем папку для распространения
        release_dir = Path("release_fixed")
        release_dir.mkdir(exist_ok=True)
        
        # Копируем exe-файл
        release_exe = release_dir / "PredatIliSotrudnichat_v2_Fixed"
        shutil.copy2(exe_path, release_exe)
        
        # Копируем инструкции
        if Path("EXE_ИНСТРУКЦИЯ.md").exists():
            shutil.copy2("EXE_ИНСТРУКЦИЯ.md", release_dir)
        
        # Создаем структуру для конфигурации
        config_dir = release_dir / "src" / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Копируем пример конфигурации
        example_config = Path("src/config/firebase_config.json.example")
        if example_config.exists():
            shutil.copy2(example_config, config_dir / "firebase_config.json.example")
        
        # Создаем инструкцию для друга
        friend_instruction = f'''
# 📦 Инструкция для друга

## 🎮 Запуск игры

1. **Настройте Firebase**:
   - Откройте файл: `src/config/firebase_config.json.example`
   - Скопируйте его в `src/config/firebase_config.json`
   - Заполните вашими данными Firebase

2. **Запустите игру**:
   ```bash
   ./PredatIliSotrudnichat_v2_Fixed
   ```
   или просто дважды кликните по файлу

3. **Регистрация**:
   - Имя пользователя: 3-20 символов (буквы, цифры, _ и -)
   - Пароль: минимум 6 символов

## 🔐 Если нет данных Firebase

Попросите у отправителя файл `firebase_config.json` с настройками базы данных.

## 🎯 Что в игре

- Многопользовательская игра на основе дилеммы заключенного
- Современный интерфейс с анимациями
- Регистрация и вход в систему
- Создание игр с другими игроками

Приятной игры! 🎉
'''
        
        with open(release_dir / "README_ДРУГУ.md", 'w', encoding='utf-8') as f:
            f.write(friend_instruction)
        
        print(f"🎉 Готовый релиз в папке: {release_dir.absolute()}")
        print("\n📋 Что передавать другу:")
        print(f"📁 Папка: {release_dir.absolute()}")
        print("📄 Файлы:")
        for file in release_dir.rglob("*"):
            if file.is_file():
                print(f"  - {file.relative_to(release_dir)}")
        
        return True
    
    else:
        print("❌ Exe-файл не найден после сборки")
        return False

if __name__ == "__main__":
    success = create_proper_build()
    if success:
        print("\n🎉 Билд успешно создан для распространения!")
    else:
        print("\n❌ Ошибка создания билда")
        sys.exit(1)
