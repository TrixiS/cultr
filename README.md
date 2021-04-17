# [cultr](https://trixis.xyz)
Простой укоротитель ссылок

[Пример приложения клиента](https://github.com/TrixiS/cultr_frontend)

# Установка и запуск
1. Установите Python 3.8+ на вашу машину
2. Установите зависимости `pip install -r requirements.txt`
3. Создайте файл `cultr/config.py` и заполните его по примеру из файла `cultr/config_example.py`
```Python
from typing import Any, Dict, List

JWT_SECRET: str = "случайная строка"
JWT_ALGO: str = "HS256"
JWT_EXPIRE_MINUTES: int = 30

CORS_ORIGINS: List[str] = [
    "http://localhost:8000"
]

DATABASE_URI: str = "sqlite+aiosqlite:///database.db"
DATABASE_CONNECT_ARGS: Dict[Any, Any] = {"check_same_thread": False}
```
4. Запустите сервер `uvicorn cultr.app:app`

# Развернутое приложение
[Работающий клиент + сервер](https://trixis.xyz)

Логин и пароль тестового аккаунта: user, user
