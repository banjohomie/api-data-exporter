# API Data Exporter

Python-скрипт получает данные из публичных API и сохраняет их в CSV или Excel.

Поддерживаемые источники:

- курсы валют через Frankfurter API;
- текущая погода через Open-Meteo API;
- данные о странах через REST Countries API;
- репозитории пользователя GitHub через GitHub REST API.

## Установка

Нужен Python 3.10 или новее.

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

На macOS/Linux активация окружения:

```bash
source .venv/bin/activate
```

## Примеры запуска

Курсы валют в CSV:

```bash
python main.py --source rates --base USD --symbols EUR,GBP,JPY --format csv --output rates.csv
```

Курсы валют в Excel:

```bash
python main.py --source rates --base EUR --symbols USD,GBP --format xlsx --output rates.xlsx
```

Погода по координатам:

```bash
python main.py --source weather --latitude 47.0105 --longitude 28.8638 --format csv --output weather.csv
```

Страны:

```bash
python main.py --source countries --limit 30 --format xlsx --output countries.xlsx
```

GitHub-репозитории пользователя:

```bash
python main.py --source github --username octocat --limit 10 --format csv --output github_repos.csv
```

## Аргументы

- `--source`: источник данных: `rates`, `weather`, `countries`, `github`.
- `--format`: формат файла: `csv` или `xlsx`.
- `--output`: путь к выходному файлу.
- `--base`: базовая валюта для `rates`.
- `--symbols`: список валют через запятую для `rates`.
- `--latitude`, `--longitude`: координаты для `weather`.
- `--username`: имя пользователя GitHub для `github`.
- `--limit`: максимальное количество строк для `countries` и `github`.

## Структура

```text
api-data-exporter/
├── main.py
├── requirements.txt
├── examples/
│   └── example_output.csv
├── .gitignore
└── README.md
```
