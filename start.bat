@echo off

REM Создаем виртуальное окружение
python -m venv venv

REM Активируем виртуальное окружение
call venv\Scripts\activate.bat

REM Создаем основные папки
mkdir src tests

REM В папке src создаем файлы
echo. > src\__init__.py
echo. > src\tdes.py

REM В папке tests создаем файлы
echo. > tests\__init__.py
echo. > tests\test_tdes.py

REM Устанавливаем необходимые зависимости
pip install pytest

REM Создаем файл README
echo. > README.md

REM Создаем файл .gitignore
echo venv/ > .gitignore
echo __pycache__/ >> .gitignore

echo "Структура проекта создана успешно."
