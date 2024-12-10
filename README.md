# Запуск 

## Шаг 1
```docker-compose up -d --build db rabbitmq```

## Шаг 2
Запуск сервисов

```docker compose up --build bet_maker line_provider```

## Тесты
Запуск тестов

```docker compose up --build bet_maker_tests line_provider_tests```

## Возможные ошибки
Если тесты для bet_maker_tests не проходя, то перезапустите образ бд

```docker-compose down db```

```docker-compose up -d --build db```

Если line_provider_tests не работает, убедитесь что RabbitMQ активен

```docker-compose up -d --build RabbitMQ```

```docker-compose up --build line_provider_tests```