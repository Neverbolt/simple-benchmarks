#!/usr/bin/env python3
"""
Transform phblog_*.json benchmark summaries into LaTeX tables.

For each JSON file (e.g. phblog_simple.json, phblog_shell.json,
phblog_advanced.json) this script produces **two** tables:

1. A per-model summary table with:
      - n_valid, n_invalid
      - sum_flags, mean_flags, std_flags, max_flags
      - mean_cost, cost_per_flag
      - invalid_rate

2. A dense per-flag table with:
      - rows: models
      - columns: each flag in that benchmark
      - entries: how many valid runs of that model discovered that flag
      - cells coloured via \flagcell{intensity}{count}
        where intensity ∈ [0, 100] is normalised by the maximum cell
        value in that table.

Termination states:

  Valid runs (included in metrics and per-flag counts):
    - "success"
    - "Cancelled"
    - "Reached maximum rounds (100)"

  Invalid runs (excluded from metrics, but counted as n_invalid):
    - "exception occurred"
    - "in progress"
    - any unknown state is conservatively treated as invalid.

LaTeX prerequisites (in your preamble):

    \usepackage{booktabs}
    \usepackage[table]{xcolor}
    \usepackage{graphicx}
    \newcommand{\flagcell}[2]{\cellcolor{blue!#1}#2}

Usage:
    python make_tables.py phblog_simple.json phblog_shell.json phblog_advanced.json
"""

import json
import math
from multiprocessing import Value
import os
import statistics
import sys
from typing import Dict, List, Tuple


# States treated as "valid" terminations and included in metrics.
VALID_STATES = {
    "success",
    "Cancelled",
    "Reached maximum rounds (100)",
}

# States treated as invalid runs (excluded from metrics).
INVALID_STATES = {
    "exception occurred",
    "in progress",
}


# Mapping from internal model id (from path in JSON) to LaTeX display name.
MODEL_DISPLAY_NAMES: Dict[str, str] = {
    "gpt-oss-120b": "GPT-oss-120b",
    "gemini-2.5": "Gemini~2.5",
    "gpt-4.1": "GPT-4.1",
    "claude": "Claude (Sonnet~4.5)",
    "gpt-5.1": "GPT-5.1",
    "gpt-5.1-codex": "GPT-5.1 Codex",
    "deepseek-r1": "DeepSeek-R1",
    "deepseek-v3.2-exp": "DeepSeek-v3.2-exp",
    "glm": "GLM-4.7",
}


def latex_escape(s: str) -> str:
    """Escape characters that are problematic in LaTeX tables."""
    # For these datasets we mostly care about underscores.
    return s.replace("_", r"\_")


def format_float(x: float, digits: int) -> str:
    """Format a float for LaTeX, returning '-' for NaN."""
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "-"
    fmt = "{:." + str(digits) + "f}"
    return fmt.format(x)


def summarize_dataset(ds_key: str, ds: dict) -> dict:
    """
    Summarize one dataset (= one model) inside a single JSON file.

    ds_key example:
        "phblog_simple/gpt-oss-120b/phblog_simple_gpt-oss-120b.sqlite3"

    We extract the model id as the second path component (e.g. "gpt-oss-120b").
    """
    parts = ds_key.split("/")
    if len(parts) >= 2:
        model_id = parts[1]
    else:
        model_id = ds_key

    model_display = MODEL_DISPLAY_NAMES.get(model_id, model_id)

    runs: Dict[str, dict] = ds["runs"]
    flags_list: List[int] = []
    invalid_flags_list: List[int] = []
    cost_list: List[float] = []
    n_valid = 0
    n_invalid = 0

    for run_id, run in runs.items():
        state = run.get("state", "")
        if state in VALID_STATES:
            n_valid += 1
            flags_list.append(run.get("#flags", 0))
            invalid_flags_list.append(run.get("#invalid_flags", 0))
            cost_list.append(run.get("cost", 0.0))
        elif state in INVALID_STATES:
            n_invalid += 1
        else:
            raise ValueError(f"UNKNOWN STATE: {state}")

    sum_flags = sum(flags_list)
    mean_flags = sum_flags / n_valid if n_valid > 0 else 0.0

    # Population standard deviation of flags per valid run.
    if len(flags_list) > 1:
        std_flags = statistics.pstdev(flags_list)
    else:
        std_flags = 0.0

    max_flags = max(flags_list) if flags_list else 0
    total_cost = sum(cost_list)
    mean_cost = total_cost / n_valid if n_valid > 0 else 0.0
    cost_per_flag = (total_cost / sum_flags) if sum_flags > 0 else math.nan

    sum_invalid_flags = sum(invalid_flags_list)
    denom = sum_flags + sum_invalid_flags
    invalid_rate = (sum_invalid_flags / denom) if denom > 0 else math.nan

    return {
        "model_id": model_id,
        "model_display": model_display,
        "n_valid": n_valid,
        "n_invalid": n_invalid,
        "sum_flags": sum_flags,
        "mean_flags": mean_flags,
        "std_flags": std_flags,
        "max_flags": max_flags,
        "mean_cost": mean_cost,
        "cost_per_flag": cost_per_flag,
        "invalid_rate": invalid_rate,
    }


def summarize_file(path: str) -> Tuple[List[dict], int, int, dict]:
    """
    Summarize all datasets (= all models) in a given JSON file.

    Returns:
        rows: per-model summary dicts
        overall_valid: total number of valid runs across all models
        overall_invalid: total number of invalid runs across all models
        data: the full JSON object
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    rows: List[dict] = []
    overall_valid = 0
    overall_invalid = 0

    for ds_key, ds in data["datasets"].items():
        summary = summarize_dataset(ds_key, ds)
        rows.append(summary)
        overall_valid += summary["n_valid"]
        overall_invalid += summary["n_invalid"]

    # Sort rows by model id for deterministic tables.
    rows.sort(key=lambda r: r["model_id"])
    return rows, overall_valid, overall_invalid, data


def make_summary_table(path: str) -> str:
    """Produce the per-model summary LaTeX table for a given JSON file."""
    rows, overall_valid, overall_invalid, _ = summarize_file(path)
    base = os.path.splitext(os.path.basename(path))[0]

    caption = (
        f"Per-model performance for {latex_escape(base)}. "
        f"Only runs with terminal states \\texttt{{success}}, "
        f"\\texttt{{Cancelled}} or \\texttt{{Reached maximum rounds (100)}} "
        f"are included in the metrics. "
        f"Overall valid runs: {overall_valid}, invalid runs: {overall_invalid}."
    )
    label = f"tab:{base}"

    lines: List[str] = []
    lines.append(r"\begin{table}[t]")
    lines.append(r"\centering")
    lines.append(r"\small")
    lines.append(r"\begin{tabular}{lrrrrrrrrr}")
    lines.append(r"\toprule")
    lines.append(
        r"Model & $n_{\text{valid}}$ & $n_{\text{invalid}}$ & "
        r"$\sum \text{flags}$ & $\mu_{\text{flags}}$ & "
        r"$\sigma_{\text{flags}}$ & $\max(\text{flags})$ & "
        r"$\mu_{\text{cost}}$ & cost/flag & $r_{\text{inv}}$ \\"
    )
    lines.append(r"\midrule")

    for r in rows:
        line = (
            f"{latex_escape(r['model_display'])} & "
            f"{r['n_valid']:d} & "
            f"{r['n_invalid']:d} & "
            f"{r['sum_flags']:d} & "
            f"{format_float(r['mean_flags'], 2)} & "
            f"{format_float(r['std_flags'], 2)} & "
            f"{r['max_flags']:d} & "
            f"{format_float(r['mean_cost'], 3)} & "
            f"{format_float(r['cost_per_flag'], 3)} & "
            f"{format_float(r['invalid_rate'], 2)} \\\\"
        )
        lines.append(line)

    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(rf"\caption{{{caption}}}")
    lines.append(rf"\label{{{label}}}")
    lines.append(r"\end{table}")

    return "\n".join(lines)


def make_flag_table(path: str, rotate_headers: bool = True) -> str:
    """
    Produce a dense per-flag LaTeX table for a given JSON file.

    - Rows: models
    - Columns: Total, then one column per flag
    - Cells: number of valid runs discovering that flag
    - Shading: via \flagcell{intensity}{value}, where intensity ∈ [0,100]
      is normalised by the maximum cell value in the table.

    rotate_headers:
        If True, uses \rotatebox{90}{...} for flag headers (requires graphicx).
    """
    rows, _, _, data = summarize_file(path)
    base = os.path.splitext(os.path.basename(path))[0]

    # Assume all datasets share the same flag set (true for your phblog_* JSON).
    any_ds = next(iter(data["datasets"].values()))
    flag_names = list(any_ds["flags"].keys())

    # Initialise counts[model_id][flag] = 0
    counts = {r["model_id"]: {flag: 0 for flag in flag_names} for r in rows}

    # Fill counts only from valid runs.
    max_count = 0
    for ds_key, ds in data["datasets"].items():
        parts = ds_key.split("/")
        model_id = parts[1] if len(parts) >= 2 else ds_key

        for run in ds["runs"].values():
            if run.get("state", "") in VALID_STATES:
                for flag_obj in run.get("flags", []):
                    flag = flag_obj.get("flag")
                    if flag in counts[model_id]:
                        counts[model_id][flag] += 1
                        if counts[model_id][flag] > max_count:
                            max_count = counts[model_id][flag]

    if max_count == 0:
        max_count = 1  # avoid division by zero; all cells will be 0 anyway

    caption = (
        f"Per-model flag discovery counts for {latex_escape(base)}. "
        f"Entries show how many valid runs (per model) discovered a given flag. "
        f"Cell shading intensity (via \\texttt{{\\flagcell}}) is proportional to the count, "
        f"normalised by the maximum cell value in this table."
    )
    label = f"tab:{base}-flags"

    # Column spec: Model + Total + one column per flag.
    col_spec = "l" + "r" * (1 + len(flag_names))

    lines: List[str] = []
    lines.append(r"\begin{table}[t]")
    lines.append(r"\centering")
    lines.append(r"\scriptsize")
    lines.append(r"\setlength{\tabcolsep}{3pt}")
    lines.append(r"\renewcommand{\arraystretch}{1.1}")
    lines.append(r"\begin{tabular}{%s}" % col_spec)
    lines.append(r"\toprule")

    # Header row.
    header = "Model & Total"
    for flag in flag_names:
        name = latex_escape(flag)
        if rotate_headers:
            header += " & " + r"\rotatebox{90}{" + name + "}"
        else:
            header += " & " + name
    header += r" \\"
    lines.append(header)
    lines.append(r"\midrule")

    # Data rows (one per model).
    for r in rows:
        model_id = r["model_id"]
        model_display = latex_escape(r["model_display"])
        model_counts = counts[model_id]
        total = sum(model_counts.values())

        row_cells: List[str] = [model_display, str(total)]

        for flag in flag_names:
            c = model_counts[flag]
            intensity = int(round(100 * c / max_count)) if c > 0 else 0
            if c > 0:
                cell = rf"\flagcell{{{intensity}}}{{{c}}}"
            else:
                cell = "0"
            row_cells.append(cell)

        lines.append(" & ".join(row_cells) + r" \\")

    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(rf"\caption{{{caption}}}")
    lines.append(rf"\label{{{label}}}")
    lines.append(r"\end{table}")

    return "\n".join(lines)


def main(argv: List[str]) -> None:
    if len(argv) < 2:
        print("Usage: python make_tables.py phblog_simple.json [more.json ...]")
        sys.exit(1)

    for path in argv[1:]:
        # Summary table.
        print(make_summary_table(path))
        print()  # blank line

        # Dense per-flag table.
        print(make_flag_table(path, rotate_headers=True))
        print()  # blank line between different JSON files


if __name__ == "__main__":
    main(sys.argv)
