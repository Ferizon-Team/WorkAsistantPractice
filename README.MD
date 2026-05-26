Запуск приложения происходит через docker compose

### Первый запуск
    docker compose up --build

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
