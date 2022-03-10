# invoice bot

## Installtion

Python 3.10 required.

Для начала нужно получить токен тестового бота и записать его в файл `.env`, типа так:

```
$ cp .env.ci .env
$ echo TELEGRAM_TOKEN=100500:secret-from-botfather >> .env
```

```
$ pip install --upgrade pip pip-tools
$ pip-sync dev-requirements.txt requirements.txt

$ make dev  # start your bot
```


