@echo off
echo 🚀 Сборка PREDATOR для Windows
echo =====================================

:: Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден! Установите Python с https://python.org
    pause
    exit /b 1
)
echo ✓ Python найден

:: Установка зависимостей
echo 📦 Установка зависимостей...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Ошибка установки зависимостей
    pause
    exit /b 1
)

pip install pyinstaller
if errorlevel 1 (
    echo ❌ Ошибка установки PyInstaller
    pause
    exit /b 1
)
echo ✓ Зависимости установлены

:: Очистка
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

:: Сборка
echo 🔨 Сборка .exe файла...
pyinstaller --name=PREDATOR --windowed --onefile --clean --noconfirm --add-data="src/config;config" --add-data="data;data" --hidden-import=firebase_admin --hidden-import=google.cloud.firestore --hidden-import=google.auth --hidden-import=PyQt6.QtCore --hidden-import=PyQt6.QtWidgets --hidden-import=PyQt6.QtGui --exclude-module=tkinter --exclude-module=matplotlib --exclude-module=PIL app.py

if errorlevel 1 (
    echo ❌ Ошибка сборки
    pause
    exit /b 1
)

echo ✓ Сборка завершена!

:: Проверка результата
if exist "dist\PREDATOR.exe" (
    echo 🎉 Готово! .exe файл находится здесь:
    echo 📂 dist\PREDATOR.exe
    echo.
    echo 📦 Создаю релизный пакет...
    if not exist release_windows mkdir release_windows
    copy "dist\PREDATOR.exe" "release_windows\PREDATOR.exe"
    copy "docs\ЗАПУСК.md" "release_windows\ЗАПУСК.md"
    copy "docs\EXE_ИНСТРУКЦИЯ.md" "release_windows\ИНСТРУКЦИЯ.md"
    copy "requirements.txt" "release_windows\"
    
    powershell -command "Compress-Archive -Path 'release_windows\*' -DestinationPath 'PREDATOR_Windows_Release.zip' -Force"
    
    echo ✓ Релизный пакет создан: PREDATOR_Windows_Release.zip
) else (
    echo ❌ .exe файл не найден!
    pause
    exit /b 1
)

echo.
echo 🎉 Все готово! Отправь другу файл PREDATOR_Windows_Release.zip
pause
