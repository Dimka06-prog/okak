"""
Скрипт для запуска старой версии приложения с исправленными путями
"""
import sys
import os
from pathlib import Path

# Добавляем текущую директорию в путь
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Импортируем и запускаем старое приложение
try:
    print("🚀 Запуск старой версии приложения...")
    
    # Импортируем QApplication
    from PyQt6.QtWidgets import QApplication
    from main import MainWindow
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
    
except Exception as e:
    print(f"❌ Ошибка запуска: {e}")
    print("\n💡 Рекомендуется использовать новую версию:")
    print("   python app.py")
    sys.exit(1)
