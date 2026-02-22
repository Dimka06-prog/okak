# PREDATOR - Структура проекта

## Описание
Чистая структура проекта после организации файлов

## Директории

### `/` (корень проекта)
- `app.py` - Главный файл приложения (новая версия)
- `build_exe.py` - Скрипт для сборки .exe файла
- `requirements.txt` - Зависимости Python
- `.gitignore` - Игнорируемые файлы Git

### `/src/` - Исходный код
- `business/` - Бизнес-логика
- `config/` - Конфигурационные файлы
- `data/` - Работа с данными
- `presentation/` - Пользовательский интерфейс
- `utils/` - Утилиты

### `/legacy/` - Устаревший код
- `main.py` - Старый главный файл
- `database.py` - SQLite база данных
- `firebase_database.py` - Firebase реализация
- `realtime_database.py` - Realtime база данных
- `realtime_game_window.py` - Окно игры реального времени
- `improved_database.py` - Улучшенная база данных
- `database_interface.py` - Интерфейс базы данных
- `run_old.py` - Запуск старой версии

### `/docs/` - Документация
- `README.md` - Основная документация
- `ЗАПУСК.md` - Инструкция по запуску
- `EXE_ИНСТРУКЦИЯ.md` - Инструкция для .exe
- `ПЕРЕДАЧА_ДРУГУ.md` - Инструкция по передаче

### `/scripts/` - Скрипты
- `build_app.py` - Старый скрипт сборки
- `prepare_release.py` - Подготовка релиза

### `/data/` - Данные
- `game_database.db` - База данных SQLite

## Использование

### Запуск приложения:
```bash
python app.py
```

### Сборка .exe файла:
```bash
python build_exe.py
```

### Запуск старой версии:
```bash
python legacy/main.py
```
