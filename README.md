# URL Shortener API

Сервис для сокращения ссылок на `FastAPI` с хранением данных в `PostgreSQL`, кешированием редиректов в `Redis` и проксированием через `nginx`.

## Стек

- `FastAPI`
- `PostgreSQL`
- `Redis`
- `SQLAlchemy` / `SQLModel`
- `Alembic`
- `Docker Compose`
- `nginx`

## Запуск

### Через Docker Compose

1. Создай `.env` в корне проекта.

Пример:

```env
DB_NAME=app_db
DB_USER=app_user
DB_PASS=strong_password
JWT_SECRET=super_secret_jwt_key
UNIQUE_SALT=super_secret_salt
INACTIVE_LINK_DAYS=30
```

2. Подними сервисы:

```bash
docker compose down -v
docker compose up -d --build
```

3. Приложение будет доступно по адресу:

```text
http://<host>:1111
```

Swagger UI:

```text
http://<host>:1111/docs
```

### Локально без Docker

1. Установи зависимости:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Подними `PostgreSQL` и `Redis`.

3. Примени миграции:

```bash
alembic upgrade head
```

4. Запусти приложение:

```bash
uvicorn src.main:app --reload
```

## Аутентификация

Используется JWT.

Поток такой:

1. Зарегистрировать пользователя через `POST /auth/register`
2. Получить токен через `POST /auth/jwt/login`
3. Передавать токен в заголовке:

```text
Authorization: Bearer <token>
```

## API

### Auth

#### `POST /auth/register`

Регистрация пользователя.

Тело:

```json
{
  "email": "user@example.com",
  "password": "strongpassword"
}
```

#### `POST /auth/jwt/login`

Логин пользователя, возвращает JWT.

Важно: endpoint ожидает `application/x-www-form-urlencoded`.

Поля формы:

- `username` = email
- `password` = пароль

Пример:

```bash
curl -X POST "http://localhost:1111/auth/jwt/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=strongpassword"
```

### Links

#### `POST /links/shorten`

Создать короткую ссылку.

Доступно всем. Если передан JWT, ссылка будет привязана к пользователю.

Тело:

```json
{
  "url": "https://example.com",
  "alias": "example",
  "expires_at": "2026-03-15T21:30:00+03:00"
}
```

Если `expires_at` не передан, ссылка живёт 1 час.

Пример:

```bash
curl -X POST "http://localhost:1111/links/shorten" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "alias": "example"
  }'
```

#### `GET /links/{short_code}`

Редирект на оригинальный URL.

При обращении:

- сначала используется кеш `Redis`
- если записи в кеше нет, ссылка ищется в `PostgreSQL`
- факт перехода сохраняется в таблицу `stats`

Пример:

```bash
curl -i "http://localhost:1111/links/example"
```

#### `GET /links/{short_code}/stats`

Статистика по короткой ссылке.

Возвращает:

- оригинальный URL
- дату создания
- количество переходов
- дату последнего использования

Пример ответа:

```json
{
  "url": "https://example.com",
  "created_at": "2026-03-15T20:10:00+03:00",
  "redirects_count": 5,
  "last_used_at": "2026-03-15T20:42:00+03:00"
}
```

#### `GET /links/search?original_url={url}`

Поиск короткой ссылки по оригинальному URL.

Пример:

```bash
curl "http://localhost:1111/links/search?original_url=https://example.com"
```

#### `GET /links/my`

Список ссылок пользователя.

Если токен не передан, возвращается пустой список.

Пример:

```bash
curl "http://localhost:1111/links/my" \
  -H "Authorization: Bearer <token>"
```

#### `PUT /links/{short_code}`

Обновление ссылки.

Требует JWT и доступно только владельцу ссылки.

Тело:

```json
{
  "url": "https://new-example.com",
  "alias": "new-alias"
}
```

Если `alias` передан, `short_code` синхронизируется с ним.
Если `alias` не передан, `short_code` генерируется автоматически.

#### `DELETE /links/{short_code}`

Удаление ссылки.

Требует JWT и доступно только владельцу ссылки.

## Примеры запросов

### Регистрация

```bash
curl -X POST "http://localhost:1111/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "strongpassword"
  }'
```

### Получение JWT

```bash
curl -X POST "http://localhost:1111/auth/jwt/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=strongpassword"
```

### Создание ссылки с токеном

```bash
curl -X POST "http://localhost:1111/links/shorten" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "url": "https://example.com",
    "alias": "example"
  }'
```

### Получение статистики

```bash
curl "http://localhost:1111/links/example/stats"
```

### Обновление ссылки

```bash
curl -X PUT "http://localhost:1111/links/example" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "alias": "example2"
  }'
```

### Удаление ссылки

```bash
curl -X DELETE "http://localhost:1111/links/example2" \
  -H "Authorization: Bearer <token>"
```

## База данных

Используются таблицы:

### `users`

Пользователи приложения.

Поля:

- `id`
- `email`
- `hashed_password`
- `is_active`
- `is_superuser`
- `is_verified`
- `registered_at`

### `urls`

Основные сокращённые ссылки.

Поля:

- `id`
- `url` — оригинальный URL
- `short_code` — короткий код
- `alias` — пользовательский алиас
- `created_at`
- `expires_at`
- `user_id` — владелец ссылки

### `stats`

Журнал переходов по ссылкам.

Поля:

- `id`
- `short_code`
- `redirected_at`

На основе `stats` считаются:

- число переходов: `count(*)`
- последнее использование: `max(redirected_at)`

## Дополнительно

- Время в приложении хранится в часовом поясе `Europe/Moscow`
- Ссылки по умолчанию живут 1 час, если не передан `expires_at`
- Неиспользуемые ссылки автоматически удаляются спустя `INACTIVE_LINK_DAYS`
- Частые редиректы кешируются в `Redis` по схеме `short_code -> original_url`
