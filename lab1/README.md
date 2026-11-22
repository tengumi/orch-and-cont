# Лабораторная работа 1. Dockerfile

Собираем два образа TaskFlow API, сервиса управления задачами с регистрацией, JWT и хранением в PostgreSQL. Оба образа используют исходники из сабмодуля `taskflow-api/` и одинаковые зависимости. [TaskFlow API на GitHub](https://github.com/vintikzq/FastAPI-todo-API)

## Плохой и хороший Dockerfile

| Плохая практика | Почему плохо | Исправление |
| --- | --- | --- |
| `FROM python:latest` | Версия Python и содержимое образа могут измениться при следующей сборке | Используем конкретный тег `python:3.12.13-slim-bookworm` |
| Полноразмерный базовый образ | В образ попадают системные пакеты, которые приложению не нужны | Используем вариант `slim` |
| `COPY . .` до установки зависимостей | Любое изменение исходников сбрасывает кеш слоя установки | Сначала копируем список зависимостей, устанавливаем их, затем копируем нужные файлы |
| Сохранение кеша pip | Кеш увеличивает размер образа | Устанавливаем зависимости с `--no-cache-dir` |
| `CMD` в shell-форме | Uvicorn работает через промежуточную оболочку, которая может не передать сигнал остановки | Запускаем Uvicorn в exec-форме |

Оба образа запускают приложение с UID и GID `10001`. Корневой `.dockerignore` ограничивает контекст сборки исходниками и нужными для сборки файлами.

## Сборка и запуск

Команды выполняются из корня репозитория.

```sh
git submodule update --init
docker build -f lab1/Dockerfile.good -t itmo-taskflow:good .
docker build -f lab1/Dockerfile.bad -t itmo-taskflow:bad .
```

Скопируйте `lab1/.env.example` в `lab1/.env`. Замените три значения-заглушки независимыми случайными значениями (`openssl rand -hex 32`).

```sh
docker network create lab1-taskflow
docker volume create lab1-taskflow-data
docker run -d --name lab1-db --network lab1-taskflow \
  --env POSTGRES_USER=taskflow \
  --env POSTGRES_DB=taskflow \
  --env "POSTGRES_PASSWORD=$(sed -n 's/^DB_PASSWORD=//p' lab1/.env)" \
  --mount source=lab1-taskflow-data,target=/var/lib/postgresql/data \
  postgres:16-alpine
```

Дождитесь готовности PostgreSQL по TCP (`accepting connections`), затем примените миграции.

```sh
docker exec lab1-db pg_isready -h 127.0.0.1 -U taskflow -d taskflow
docker run --rm --network lab1-taskflow --env-file lab1/.env \
  itmo-taskflow:good alembic upgrade head
```

Запустите API и откройте [Swagger UI](http://127.0.0.1:8000/docs). Зарегистрируйте тестового пользователя, авторизуйтесь и создайте задачу.

```sh
docker run -d --rm --name lab1-api --network lab1-taskflow \
  --env-file lab1/.env -p 127.0.0.1:8000:8000 itmo-taskflow:good
```

Остановите API командой `docker stop lab1-api` и повторите запуск с `itmo-taskflow:bad`. Войдите тем же пользователем, проверьте список задач. PostgreSQL хранит данные в именованном томе и доступен только внутри Docker-сети.

После проверки остановите API и удалите контейнер БД и сеть. Том сохранит данные для следующего запуска.

```sh
docker stop lab1-api
docker rm -f lab1-db
docker network rm lab1-taskflow
```

## Плохие практики при запуске

1. Хранить данные PostgreSQL только в слое контейнера. При удалении контейнера данные пропадут. Именованный том переживает пересоздание контейнера.
2. Публиковать порт PostgreSQL на всех интерфейсах, когда к нему обращается только API. Это открывает лишнюю точку входа из сети.

## Когда контейнеры не нужны

1. Приложению требуется другое ядро ОС, например Windows-приложению на Linux-хосте. Подойдёт виртуальная машина с нужной ОС.
2. Нужно один раз запустить локальный скрипт без сложных зависимостей. Настройка контейнера займёт больше времени, чем сам запуск.
