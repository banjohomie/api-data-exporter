from __future__ import annotations

import threading
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from main import (
    ApiError,
    export_rows,
    fetch_countries,
    fetch_github_repos,
    fetch_rates,
    fetch_weather,
)


SOURCE_FIELDS = {
    "rates": (
        ("base", "Base currency", "USD"),
        ("symbols", "Currency symbols", "EUR,GBP,JPY"),
    ),
    "weather": (
        ("latitude", "Latitude", "47.0105"),
        ("longitude", "Longitude", "28.8638"),
    ),
    "countries": (
        ("limit", "Row limit", "20"),
    ),
    "github": (
        ("username", "GitHub username", "octocat"),
        ("limit", "Repository limit", "10"),
    ),
}

SOURCE_DESCRIPTIONS = {
    "rates": "Export latest exchange rates from Frankfurter API.",
    "weather": "Export current weather by latitude and longitude.",
    "countries": "Export country information from REST Countries API.",
    "github": "Export public repositories for a GitHub user.",
}


class ApiDataExporterApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        self.title("API Data Exporter")
        self.geometry("680x620")
        self.minsize(620, 560)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.source_var = ctk.StringVar(value="rates")
        self.format_var = ctk.StringVar(value="csv")
        self.output_var = ctk.StringVar(value="api_output.csv")
        self.entries: dict[str, ctk.CTkEntry] = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_body()
        self._build_footer()
        self._render_source_fields("rates")

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=28, pady=(24, 10))
        header.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header,
            text="API Data Exporter",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        title.grid(row=0, column=0, sticky="w")

        subtitle = ctk.CTkLabel(
            header,
            text="Fetch public API data and export it to CSV or Excel.",
            text_color=("gray35", "gray70"),
            font=ctk.CTkFont(size=14),
        )
        subtitle.grid(row=1, column=0, sticky="w", pady=(4, 0))

    def _build_body(self) -> None:
        self.body = ctk.CTkFrame(self, corner_radius=12)
        self.body.grid(row=1, column=0, sticky="nsew", padx=28, pady=12)
        self.body.grid_columnconfigure(0, weight=1)
        self.body.grid_columnconfigure(1, weight=1)

        source_label = ctk.CTkLabel(self.body, text="Data source")
        source_label.grid(row=0, column=0, sticky="w", padx=22, pady=(22, 6))

        self.source_menu = ctk.CTkOptionMenu(
            self.body,
            variable=self.source_var,
            values=list(SOURCE_FIELDS),
            command=self._render_source_fields,
        )
        self.source_menu.grid(row=1, column=0, sticky="ew", padx=22)

        format_label = ctk.CTkLabel(self.body, text="Output format")
        format_label.grid(row=0, column=1, sticky="w", padx=22, pady=(22, 6))

        self.format_switch = ctk.CTkSegmentedButton(
            self.body,
            variable=self.format_var,
            values=["csv", "xlsx"],
            command=self._sync_output_suffix,
        )
        self.format_switch.grid(row=1, column=1, sticky="ew", padx=22)
        self.format_switch.set("csv")

        self.description_label = ctk.CTkLabel(
            self.body,
            text="",
            text_color=("gray35", "gray70"),
            anchor="w",
        )
        self.description_label.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=22,
            pady=(16, 8),
        )

        self.fields_frame = ctk.CTkFrame(self.body, fg_color="transparent")
        self.fields_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=22)
        self.fields_frame.grid_columnconfigure(0, weight=1)
        self.fields_frame.grid_columnconfigure(1, weight=1)

        output_label = ctk.CTkLabel(self.body, text="Output file")
        output_label.grid(row=4, column=0, columnspan=2, sticky="w", padx=22, pady=(18, 6))

        output_row = ctk.CTkFrame(self.body, fg_color="transparent")
        output_row.grid(row=5, column=0, columnspan=2, sticky="ew", padx=22)
        output_row.grid_columnconfigure(0, weight=1)

        self.output_entry = ctk.CTkEntry(output_row, textvariable=self.output_var)
        self.output_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        browse_button = ctk.CTkButton(
            output_row,
            text="Browse",
            width=96,
            command=self._choose_output_file,
        )
        browse_button.grid(row=0, column=1)

    def _build_footer(self) -> None:
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=2, column=0, sticky="ew", padx=28, pady=(4, 24))
        footer.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(
            footer,
            text="Ready.",
            text_color=("gray35", "gray70"),
            anchor="w",
        )
        self.status_label.grid(row=0, column=0, sticky="ew", padx=(2, 14))

        self.export_button = ctk.CTkButton(
            footer,
            text="Export Data",
            width=150,
            command=self._start_export,
        )
        self.export_button.grid(row=0, column=1)

    def _render_source_fields(self, source: str) -> None:
        for widget in self.fields_frame.winfo_children():
            widget.destroy()

        self.entries.clear()
        self.description_label.configure(text=SOURCE_DESCRIPTIONS[source])

        fields = SOURCE_FIELDS[source]
        for index, (name, label_text, default_value) in enumerate(fields):
            column = index % 2
            row = (index // 2) * 2

            label = ctk.CTkLabel(self.fields_frame, text=label_text)
            label.grid(row=row, column=column, sticky="w", padx=(0, 14), pady=(8, 6))

            entry = ctk.CTkEntry(self.fields_frame)
            entry.insert(0, default_value)
            entry.grid(row=row + 1, column=column, sticky="ew", padx=(0, 14), pady=(0, 6))
            self.entries[name] = entry

        self._sync_output_suffix(self.format_var.get())

    def _sync_output_suffix(self, output_format: str) -> None:
        current = self.output_var.get().strip()
        if not current:
            self.output_var.set(f"api_output.{output_format}")
            return

        path = Path(current)
        if path.suffix.lower() in {".csv", ".xlsx"}:
            self.output_var.set(str(path.with_suffix(f".{output_format}")))

    def _choose_output_file(self) -> None:
        output_format = self.format_var.get()
        filetypes = (
            ("CSV files", "*.csv"),
            ("Excel files", "*.xlsx"),
            ("All files", "*.*"),
        )

        selected = filedialog.asksaveasfilename(
            title="Choose output file",
            defaultextension=f".{output_format}",
            filetypes=filetypes,
        )

        if selected:
            self.output_var.set(selected)
            self._sync_output_suffix(output_format)

    def _start_export(self) -> None:
        try:
            options = self._collect_options()
        except ValueError as error:
            self._set_status(str(error), "error")
            return

        self.export_button.configure(state="disabled", text="Exporting...")
        self._set_status("Fetching data from API...", "info")

        thread = threading.Thread(target=self._export_worker, args=(options,), daemon=True)
        thread.start()

    def _collect_options(self) -> dict[str, str]:
        output = self.output_var.get().strip()
        if not output:
            raise ValueError("Output file is required.")

        options = {
            "source": self.source_var.get(),
            "format": self.format_var.get(),
            "output": output,
        }

        for name, entry in self.entries.items():
            value = entry.get().strip()
            if not value:
                raise ValueError(f"{name.replace('_', ' ').title()} is required.")
            options[name] = value

        return options

    def _export_worker(self, options: dict[str, str]) -> None:
        try:
            rows = self._fetch_rows(options)
            output_path = export_rows(rows, options["output"], options["format"])
        except (ApiError, ValueError) as error:
            self.after(0, self._finish_export, f"Error: {error}", "error")
            return
        except Exception as error:
            self.after(0, self._finish_export, f"Unexpected error: {error}", "error")
            return

        message = f"Saved {len(rows)} rows to {output_path}"
        self.after(0, self._finish_export, message, "success")

    def _fetch_rows(self, options: dict[str, str]):
        source = options["source"]

        if source == "rates":
            return fetch_rates(options["base"], options["symbols"])

        if source == "weather":
            latitude = float(options["latitude"])
            longitude = float(options["longitude"])
            return fetch_weather(latitude, longitude)

        if source == "countries":
            limit = self._parse_limit(options["limit"])
            return fetch_countries(limit)

        if source == "github":
            limit = self._parse_limit(options["limit"])
            if limit > 100:
                raise ValueError("GitHub limit cannot be greater than 100.")
            return fetch_github_repos(options["username"], limit)

        raise ValueError(f"Unknown source: {source}")

    @staticmethod
    def _parse_limit(value: str) -> int:
        limit = int(value)
        if limit < 1:
            raise ValueError("Limit must be greater than 0.")
        return limit

    def _finish_export(self, message: str, status_type: str) -> None:
        self.export_button.configure(state="normal", text="Export Data")
        self._set_status(message, status_type)

    def _set_status(self, message: str, status_type: str) -> None:
        colors = {
            "info": ("gray35", "gray70"),
            "success": ("#1f7a3f", "#6ee7a8"),
            "error": ("#b42318", "#ff8a80"),
        }
        self.status_label.configure(text=message, text_color=colors[status_type])


if __name__ == "__main__":
    app = ApiDataExporterApp()
    app.mainloop()
