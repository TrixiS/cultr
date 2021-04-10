# cultr
Простой укоротитель ссылок

[Пример приложения клиента](https://github.com/TrixiS/cultr_frontend)

# Установка и запуск
1. Установите Python 3.8+ на вашу машину
2. Установите зависимости `pip install -r requirements.txt`
3. Создайте .env файл в корневой директории 
```
JWT_SECRET="случайная строка"
JWT_ALGO="HS256"
TOKEN_EXPIRE_MINUTES=30
APP_ORIGIN="http://localhost:3000"
```
4. Запустите сервер `uvicorn cultr.app:app`
