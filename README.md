
# 💰 Wallet API

> REST API для работы с кошельками пользователей на FastAPI.
> Тестовое задание для позиции Python-разработчика.

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)
![Tests](https://img.shields.io/badge/tests-pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white)

---

## 📖 О проекте

Простое и надёжное API для работы с кошельками:

- Создание кошелька
- Пополнение и списание средств
- Получение текущего баланса

Особое внимание уделено **корректной работе при параллельных запросах** — за это
отвечает блокировка строки в БД (`SELECT ... FOR UPDATE`).

---

## 🧰 Технологии

| Слой                     | Технология           |
| ---------------------------- | ------------------------------ |
| Язык                     | Python 3.12                    |
| Веб-фреймворк    | FastAPI + Uvicorn              |
| ORM                          | SQLAlchemy 2.0 (async)         |
| Драйвер БД          | asyncpg                        |
| Миграции             | Alembic                        |
| БД                         | PostgreSQL 16                  |
| Валидация           | Pydantic v2, pydantic-settings |
| Тесты                   | pytest, pytest-asyncio, httpx  |
| Инфраструктура | Docker, Docker Compose         |

---

## 🚀 Быстрый старт

### 1. Клонировать репозиторий

```bash
git clone https://github.com/ТВОЙ_НИК/wallet_api.git
cd wallet_api
```

### 2. Поднять всё одной командой

```bash
docker compose up --build -d
```

Docker сам:

- соберёт образ приложения,
- запустит PostgreSQL,
- применит миграции,
- поднимет Uvicorn.

### 3. Открыть документацию

Swagger UI — [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🔌 Эндпоинты

| Метод | URL                                         | Описание                                                      |
| ---------- | ------------------------------------------- | --------------------------------------------------------------------- |
| `POST`   | `/api/v1/wallets/`                        | Создать новый кошелёк                              |
| `POST`   | `/api/v1/wallets/{wallet_uuid}/operation` | Пополнить (`DEPOSIT`) или списать (`WITHDRAW`) |
| `GET`    | `/api/v1/wallets/{wallet_uuid}`           | Получить баланс кошелька                        |

### Пример: пополнение

```bash
curl -X POST http://localhost:8000/api/v1/wallets/<UUID>/operation \
  -H "Content-Type: application/json" \
  -d '{"operation_type": "DEPOSIT", "amount": 1000}'
```

Ответ:

```json
{
  "id": "2f1c...",
  "balance": "1000.00"
}
```

### Пример: списание

```bash
curl -X POST http://localhost:8000/api/v1/wallets/<UUID>/operation \
  -H "Content-Type: application/json" \
  -d '{"operation_type": "WITHDRAW", "amount": 500}'
```

Если денег недостаточно — вернётся `400 Недостаточно средств`.

### Пример: получить баланс

```bash
curl http://localhost:8000/api/v1/wallets/<UUID>
```

---

## 🔒 Конкурентность

Когда два запроса одновременно меняют баланс одного кошелька, легко получить гонку:
оба читают старый баланс, оба пишут новый — и одно изменение теряется.

Решение — блокировка строки на уровне БД:

```python
result = await db.execute(
    select(Wallet).where(Wallet.id == wallet_id).with_for_update()
)
```

`with_for_update()` превращается в `SELECT ... FOR UPDATE`. Второй запрос
ждёт, пока первый не закроет транзакцию, поэтому баланс всегда корректен.

Тест `test_concurrent_deposits` проверяет это: 10 параллельных пополнений по 100
всегда дают ровно 1000.

---

## 🧪 Тесты

Создать тестовую БД:

```bash
docker compose exec db psql -U postgres -c "CREATE DATABASE wallets_test;"
```

Запустить тесты:

```bash
docker compose exec app pytest -v
```

Покрыты все эндпоинты, включая негативные сценарии и проверку конкурентности.

---

## 📂 Структура проекта

```
wallet_api/
├── app/
│   ├── api/                 # Роутеры и зависимости FastAPI
│   │   ├── deps.py
│   │   └── v1/
│   │       ├── router.py
│   │       └── endpoints/
│   │           └── wallets.py
│   ├── core/                # Конфиг и подключение к БД
│   │   ├── config.py
│   │   └── db.py
│   ├── crud/                # Работа с БД (запросы)
│   │   └── wallet.py
│   ├── models/              # SQLAlchemy-модели
│   │   └── wallet.py
│   ├── schemas/             # Pydantic-схемы
│   │   └── wallet.py
│   ├── services/            # Бизнес-логика
│   │   └── wallet.py
│   └── main.py              # Точка входа
├── alembic/                 # Миграции
├── tests/                   # Тесты
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env
```

Слои разделены как в учебных проектах: **api → services → crud → models**.
Так проще тестировать и развивать.

---

## ⚙️ Переменные окружения

Файл `.env`:

```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/wallets
```

---

## 🛑 Остановить проект

```bash
docker compose down
```

С удалением данных БД:

```bash
docker compose down -v
```
