# PROFNIT 2027 Entrance Exam (ENA27) - Statistical Analysis & PDF Generator

A Python package managed with `uv` for parsing, analyzing, visualizing, and generating executive PDF reports for the PROFNIT 2027 Preliminary Entrance Exam results (`data/ENA27-Resultado-Preliminar-Prova-Nacional.pdf`).

All source code, functions, variable names, docstrings, and comments are written strictly in English with static type annotations.

---

## Key Features

- **PDF Data Extraction**: Clean parsing of candidate names, masked CPFs, and attendance/scores across 57 document pages.
- **Comprehensive Statistics**:
  - **Attendance**: Total, present, absent counts and percentages.
  - **Descriptive Metrics**: Mean, median, mode, standard deviation, variance, min, max, quartiles (Q1, Q3), and interquartile range (IQR).
  - **Score Cutoffs**: Score frequencies (0–20), cumulative percentiles, high-scorer counts.
  - **Geographic Breakdown**: Candidate distributions and average performance grouped by CPF issuing state code (9th digit).
- **High-Resolution Visualizations**: Matplotlib/Seaborn plots (Score distribution histogram, cumulative distribution curve, regional candidate volume, regional mean scores).
- **Executive PDF Report**: A 3-page publication-quality ReportLab document featuring KPI metric cards, formatted data tables, dynamic page numbering ("Page X of Y"), and embedded charts.

---

## Requirements & Environment Management

This project uses [`uv`](https://github.com/astral-sh/uv) for fast, reproducible Python environment management.

### Installation

Clone the repository and install dependencies with `uv`:

```bash
uv sync
```

---

## Usage

### Run Default Analysis Pipeline

To run the pipeline on the preliminary result document in `data/`:

```bash
uv run profnit-stats
```

Or execute directly via python module:

```bash
uv run python -m src.main
```

### Custom Options

You can specify custom input PDF paths or output directories:

```bash
uv run profnit-stats -i data/ENA27-Resultado-Preliminar-Prova-Nacional.pdf -o output/Report.pdf -c output/charts
```

---

## Generated Outputs

1. **PDF Report**: `output/PROFNIT_2027_Preliminary_Results_Report.pdf`
2. **Chart PNG Images**:
   - `output/charts/score_distribution.png`
   - `output/charts/cumulative_distribution.png`
   - `output/charts/regional_volume.png`
   - `output/charts/regional_means.png`

---

## Project Structure

```text
estatisticas-profnit27/
├── data/
│   └── ENA27-Resultado-Preliminar-Prova-Nacional.pdf
├── output/
│   ├── PROFNIT_2027_Preliminary_Results_Report.pdf
│   └── charts/
├── src/
│   ├── __init__.py
│   ├── parser.py          # PDF extraction module
│   ├── analyzer.py        # Statistical calculations & CPF region mapping
│   ├── charts.py          # Matplotlib/Seaborn plot generator
│   ├── pdf_generator.py   # ReportLab Platypus PDF document builder
│   └── main.py            # CLI entry point
├── pyproject.toml
└── README.md
```
