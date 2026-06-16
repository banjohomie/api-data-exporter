import argparse
import csv
from pathlib import Path
from typing import Any

import requests


API_TIMEOUT = 20


class ApiError(RuntimeError):
    pass


def fetch_json(url: str, params: dict[str, Any] | None = None) -> Any:
    try:
        response = requests.get(url, params=params, timeout=API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise ApiError(f"API request failed: {exc}") from exc

    try:
        return response.json()
    except ValueError as exc:
        raise ApiError("API returned invalid JSON") from exc


def fetch_rates(base: str, symbols: str | None) -> list[dict[str, Any]]:
    params: dict[str, str] = {"base": base.upper()}
    if symbols:
        params["symbols"] = symbols.upper()

    data = fetch_json("https://api.frankfurter.dev/v1/latest", params=params)
    if not isinstance(data, dict):
        raise ApiError("API returned an unexpected response")

    rates = data.get("rates", {})
    if not isinstance(rates, dict):
        raise ApiError("API returned an unexpected response")

    return [
        {
            "date": data.get("date"),
            "base_currency": data.get("base"),
            "currency": currency,
            "rate": rate,
        }
        for currency, rate in sorted(rates.items())
    ]


def fetch_weather(latitude: float, longitude: float) -> list[dict[str, Any]]:
    data = fetch_json(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
            "timezone": "auto",
        },
    )
    if not isinstance(data, dict):
        raise ApiError("API returned an unexpected response")

    current = data.get("current", {})
    units = data.get("current_units", {})
    if not isinstance(current, dict) or not isinstance(units, dict):
        raise ApiError("API returned an unexpected response")

    return [
        {
            "time": current.get("time"),
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            "timezone": data.get("timezone"),
            "temperature": current.get("temperature_2m"),
            "temperature_unit": units.get("temperature_2m"),
            "humidity": current.get("relative_humidity_2m"),
            "humidity_unit": units.get("relative_humidity_2m"),
            "wind_speed": current.get("wind_speed_10m"),
            "wind_speed_unit": units.get("wind_speed_10m"),
            "weather_code": current.get("weather_code"),
        }
    ]


def fetch_countries(limit: int) -> list[dict[str, Any]]:
    data = fetch_json(
        "https://restcountries.com/v3.1/all",
        params={"fields": "name,capital,region,subregion,population,area,cca2"},
    )
    if not isinstance(data, list):
        raise ApiError("Countries API returned an unexpected response")

    countries = sorted(data, key=lambda item: item.get("name", {}).get("common", ""))

    rows = []
    for country in countries[:limit]:
        rows.append(
            {
                "name": country.get("name", {}).get("common"),
                "official_name": country.get("name", {}).get("official"),
                "code": country.get("cca2"),
                "capital": ", ".join(country.get("capital", [])),
                "region": country.get("region"),
                "subregion": country.get("subregion"),
                "population": country.get("population"),
                "area": country.get("area"),
            }
        )
    return rows


def fetch_github_repos(username: str, limit: int) -> list[dict[str, Any]]:
    data = fetch_json(
        f"https://api.github.com/users/{username}/repos",
        params={"sort": "updated", "per_page": min(limit, 100)},
    )
    if not isinstance(data, list):
        message = (
            data.get("message", "unexpected response")
            if isinstance(data, dict)
            else "unexpected response"
        )
        raise ApiError(f"GitHub API returned {message}")

    rows = []
    for repo in data[:limit]:
        rows.append(
            {
                "name": repo.get("name"),
                "full_name": repo.get("full_name"),
                "description": repo.get("description"),
                "language": repo.get("language"),
                "stars": repo.get("stargazers_count"),
                "forks": repo.get("forks_count"),
                "open_issues": repo.get("open_issues_count"),
                "updated_at": repo.get("updated_at"),
                "url": repo.get("html_url"),
            }
        )
    return rows


def write_csv(rows: list[dict[str, Any]], output_path: Path) -> None:
    if not rows:
        raise ApiError("No rows to export")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_excel(rows: list[dict[str, Any]], output_path: Path) -> None:
    if not rows:
        raise ApiError("No rows to export")

    try:
        from openpyxl import Workbook
    except ImportError as exc:
        raise ApiError("openpyxl is required for Excel export. Run: pip install -r requirements.txt") from exc

    output_path.parent.mkdir(parents=True, exist_ok=True)
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "api_data"

    headers = list(rows[0].keys())
    sheet.append(headers)
    for row in rows:
        sheet.append([row.get(header) for header in headers])

    for column_cells in sheet.columns:
        max_length = max(len(str(cell.value or "")) for cell in column_cells)
        sheet.column_dimensions[column_cells[0].column_letter].width = min(max_length + 2, 60)

    workbook.save(output_path)


def export_rows(rows: list[dict[str, Any]], output: str, output_format: str) -> Path:
    output_path = Path(output)
    expected_suffix = f".{output_format}"
    if not output_path.suffix:
        output_path = output_path.with_suffix(expected_suffix)
    elif output_path.suffix.lower() != expected_suffix:
        raise ApiError(f"Output extension must be {expected_suffix} for --format {output_format}")

    if output_format == "csv":
        write_csv(rows, output_path)
    elif output_format == "xlsx":
        write_excel(rows, output_path)
    else:
        raise ApiError(f"Unsupported format: {output_format}")

    return output_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fetch data from public APIs and export it to CSV or Excel."
    )
    parser.add_argument(
        "--source",
        choices=("rates", "weather", "countries", "github"),
        default="rates",
        help="API data source to export.",
    )
    parser.add_argument(
        "--format",
        choices=("csv", "xlsx"),
        default="csv",
        help="Output file format.",
    )
    parser.add_argument(
        "--output",
        default="api_output",
        help="Output file path. Extension is added automatically if omitted.",
    )

    parser.add_argument("--base", default="USD", help="Base currency for rates.")
    parser.add_argument(
        "--symbols",
        default="EUR,GBP,JPY",
        help="Comma-separated currencies for rates, for example EUR,GBP,JPY.",
    )

    parser.add_argument("--latitude", type=float, default=47.0105, help="Latitude for weather.")
    parser.add_argument("--longitude", type=float, default=28.8638, help="Longitude for weather.")

    parser.add_argument("--username", default="octocat", help="GitHub username.")
    parser.add_argument("--limit", type=int, default=20, help="Maximum number of rows.")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.limit < 1:
            raise ApiError("--limit must be greater than 0")
        if args.source == "github" and args.limit > 100:
            raise ApiError("--limit for GitHub cannot be greater than 100")

        if args.source == "rates":
            rows = fetch_rates(args.base, args.symbols)
        elif args.source == "weather":
            rows = fetch_weather(args.latitude, args.longitude)
        elif args.source == "countries":
            rows = fetch_countries(args.limit)
        elif args.source == "github":
            rows = fetch_github_repos(args.username, args.limit)
        else:
            raise ApiError(f"Unknown source: {args.source}")

        output_path = export_rows(rows, args.output, args.format)
    except ApiError as exc:
        parser.exit(1, f"Error: {exc}\n")

    print(f"Saved {len(rows)} rows to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
