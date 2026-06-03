Запуск приложения происходит через docker compose

### Первый запуск
1. Создаем .env файл со своими данными, или оставляем те что есть. Берем их из .env.example.
2. Переходим в директорию backend и запускаем скрипт download_models.py
3.
```
docker compose up --build
```
4. После запуска контейнеров
```
docker compose exec fastapi-app alembic upgrade head
```
### Все последующие
    docker compose up

### Обновление зависимостей
При установки пакетов через poetry нужно обновить сборку приложения так как там не будет новых зависимостей. 
```
docker compose build --no-cache fastapi-app
```
После как обычно запускаем приложение
```
docker compose up
```
