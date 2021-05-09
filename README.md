# Cultr
Укоротитель ссылок (backend)

# Установка и запуск
  - Без Docker (скорее всего вам нужно это)
    - Установите Python3.8+ на вашу машину
    - (опционально) создайте виртуальное окружение `python -m "venv" venv` и активируйте его `./venv/scripts/activate` (\*nix: `./venv/bin/activate`)
    - Установите зависимости `pip install -r requirements.txt`
    - (опционально) отредактируйте переменные в `cultr/config.py` или в переменных среды
    - Запустите приложение `uvicorn cultr.app:app --port 5000`
  - Docker
    - Установите [Docker](https://www.docker.com/)
    - (опционально) отредактируйте переменные в `cultr/config.py` или в `docker-compose.yaml`
    - `docker-compose up -d`

# Документация
Документация backend приложения доступна по ссылке `http://127.0.0.1:5000/docs` после запуска

Краткое описание методов API:
- **POST /api/users** - регистрация пользователя
- **POST /api/token** - получение JWT
- **GET /api/users/@me** - получение информации о текущем пользователе
- **PUT /api/users/@me** - изменение текущего пользователя (username и пароль)
- **GET /api/v1/urls** - получение списка ссылок постранично
- **GET /api/v1/urls/{url_name}** - получение одной ссылки по ее имени
- **POST /api/v1/urls** - создание ссылки
- **PUT /api/v1/urls/{url_name}** - изменение ссылки
- **DELETE /api/v1/urls/{url_name}** - удаление ссылки
- **GET /u/{url_name}** - получить redirect на конечную точку ссылки
