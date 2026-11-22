# Лабораторная работа 2. Docker Compose

TaskFlow API из ЛР 1 разворачивается вместе с PostgreSQL. `Dockerfile` рядом с Compose-файлом — копия `lab1/Dockerfile.good`. Контекст сборки — корень репозитория, откуда Docker берёт исходники сабмодуля и зависимости.

| Сервис | Контейнер | Что делает |
| --- | --- | --- |
| `db` | `lab2-taskflow-db` | Запускает PostgreSQL. Готовность проверяет `pg_isready`. Данные хранятся в томе `postgres-data` |
| `migrate` | `lab2-taskflow-migrate` | Ждёт готовности БД, выполняет `alembic upgrade head` и завершается |
| `api` | `lab2-taskflow-api` | Запускает TaskFlow после успешных миграций. Healthcheck запрашивает `/openapi.json` |
| `nginx` | `lab2-taskflow-nginx` | Ждёт готовности API и проксирует HTTP-запросы на `api:8000`. Healthcheck проверяет этот маршрут |

`migrate` и `api` используют один образ `itmo-taskflow:lab2`. Все четыре сервиса подключены к сети `taskflow`. TaskFlow и PostgreSQL получают переменные из локального `.env`, демо-значения лежат в `.env.example`. Nginx читает `nginx.conf` и принимает запросы с хоста на `127.0.0.1:18082`.

## Запуск

Из корня репозитория:

```sh
git submodule update --init
cd lab2
cp -n .env.example .env
docker compose up --build --wait
docker compose ps -a
```

У `db`, `api` и `nginx` ожидается статус `healthy`, у `migrate` — `Exited (0)`. В [Swagger UI](http://127.0.0.1:18082/docs) можно зарегистрироваться, войти и создать задачу.

`docker compose down` остановит проект. Том PostgreSQL сохранится, поэтому задача будет доступна после следующего запуска.

## Вопросы

**Можно ли ограничить CPU и память?** Да. Например, эти поля в конфигурации `api` ограничат его половиной CPU и 256 МБ памяти. [Документация Docker Compose](https://docs.docker.com/reference/compose-file/services/)

```yaml
services:
  api:
    cpus: 0.5
    mem_limit: 256m
```

**Как запустить один сервис?** Передать его имя и флаг `--no-deps`, например `docker compose up -d --no-deps db`. Флаг пропускает зависимости выбранного сервиса. [Документация Docker](https://docs.docker.com/reference/cli/docker/compose/up/)
