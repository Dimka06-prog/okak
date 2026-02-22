# 📋 Инструкция по сборке PREDATOR для Windows

## Что нужно сделать другу на Windows:

### 1. Установить Python
- Скачать Python с https://python.org (версия 3.9+)
- При установке обязательно поставить галочку "Add Python to PATH"

### 2. Скачать файлы проекта
Другу нужно скачать эти файлы:
```
PREDATOR_project.zip (создадим ниже)
```

### 3. Установить зависимости
Открыть командную строку (cmd) в папке проекта и выполнить:
```cmd
pip install -r requirements.txt
pip install pyinstaller
```

### 4. Собрать .exe файл
Выполнить в командной строке:
```cmd
pyinstaller --name=PREDATOR --windowed --onefile --clean --noconfirm --add-data="src/config;config" --add-data="data;data" --hidden-import=firebase_admin --hidden-import=google.cloud.firestore --hidden-import=google.auth --hidden-import=PyQt6.QtCore --hidden-import=PyQt6.QtWidgets --hidden-import=PyQt6.QtGui --exclude-module=tkinter --exclude-module=matplotlib --exclude-module=PIL app.py
```

### 5. Готовый файл
После сборки .exe файл будет здесь:
```
dist/PREDATOR.exe
```

## 🚀 Альтернативный вариант (проще):

Создать баш-скрипт для Windows:
```cmd
build_windows.bat
```

## 📦 Что нужно отправить другу:

1. Все файлы проекта (кроме build/, dist/, __pycache__/)
2. Эту инструкцию

## ⚡ Быстрый старт для друга:

1. Распаковать проект
2. Установить Python (если нет)
3. Запустить `build_windows.bat` (если создадим)
4. Готовый `PREDATOR.exe` в папке `dist`

## 🔧 Если что-то не работает:

- Убедиться что Python в PATH
- Установить Visual Studio Build Tools
- Проверить версию PyQt6: `pip show PyQt6`
