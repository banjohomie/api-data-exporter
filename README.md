# API Data Exporter

A Python command-line tool that fetches data from public APIs and exports it to CSV or Excel files.

## Supported Data Sources

* Currency exchange rates from Frankfurter API
* Current weather data from Open-Meteo API
* Country information from REST Countries API
* GitHub user repositories from GitHub REST API

## Features

* Fetches JSON data from public REST APIs
* Exports data to CSV or Excel
* Supports command-line arguments
* Handles HTTP and JSON errors
* Automatically creates output directories
* Automatically adds file extensions if they are missing
* Adjusts Excel column widths automatically

## Requirements

* Python 3.10 or newer
* requests
* openpyxl

## Installation

Clone the repository:

```bash
git clone https://github.com/banjohomie/api-data-exporter.git
cd api-data-exporter
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment on Windows:

```bash
.\.venv\Scripts\Activate.ps1
```

Activate the virtual environment on macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Export currency exchange rates to CSV

```bash
python main.py --source rates --base USD --symbols EUR,GBP,JPY --format csv --output rates.csv
```

### Export currency exchange rates to Excel

```bash
python main.py --source rates --base EUR --symbols USD,GBP --format xlsx --output rates.xlsx
```

### Export current weather data by coordinates

```bash
python main.py --source weather --latitude 47.0105 --longitude 28.8638 --format csv --output weather.csv
```

### Export country information

```bash
python main.py --source countries --limit 30 --format xlsx --output countries.xlsx
```

### Export GitHub repositories

```bash
python main.py --source github --username octocat --limit 10 --format csv --output github_repos.csv
```

## Command-Line Arguments

| Argument      | Description                                               |
| ------------- | --------------------------------------------------------- |
| `--source`    | Data source: `rates`, `weather`, `countries`, or `github` |
| `--format`    | Output format: `csv` or `xlsx`                            |
| `--output`    | Output file path                                          |
| `--base`      | Base currency for exchange rates                          |
| `--symbols`   | Comma-separated currency symbols for exchange rates       |
| `--latitude`  | Latitude for weather data                                 |
| `--longitude` | Longitude for weather data                                |
| `--username`  | GitHub username for repository export                     |
| `--limit`     | Maximum number of rows for `countries` and `github`       |

## Example Output

Example CSV output for currency exchange rates:

```csv
date,base_currency,currency,rate
2026-06-16,USD,EUR,0.8625
2026-06-16,USD,GBP,0.7458
2026-06-16,USD,JPY,157.42
```

## Project Structure

```text
api-data-exporter/
├── main.py
├── requirements.txt
├── examples/
│   └── example_output.csv
├── .gitignore
└── README.md
```

## License

This project is open source and available under the MIT License.
