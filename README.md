# Оркестрация и контейнеризация

## Клонирование и обновление

При первом клонировании заберите репозиторий вместе с сабмодулем TaskFlow API.

```sh
git clone --recurse-submodules https://github.com/tengumi/orch-and-cont.git
cd orch-and-cont
```

Если репозиторий уже склонирован, выполните из его корня:

```sh
git pull --ff-only
git submodule update --init --recursive
```

Команда `git submodule update` выставит ревизию TaskFlow, закреплённую в репозитории курса.

## Лабораторные

- [ЛР 1. Dockerfile](lab1/) — [решение](lab1/README.md)
- [ЛР 2. Docker Compose](lab2/) — [решение](lab2/README.md)
- [ЛР 3. Kubernetes](lab3/)
- [ЛР 4. More Kubernetes](lab4/)
