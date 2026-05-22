"""Render eval summary → markdown table + JSON file."""

import json
import math
from datetime import datetime
from pathlib import Path

from src.eval.metrics import summarise


def _fmt(val) -> str:
    if isinstance(val, float):
        return "N/A" if math.isnan(val) else f"{val:.1%}"
    return str(val)


def render_markdown(summary: dict) -> str:
    lines = [
        "## Results",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| Total attacks | {summary['total_attacks']} |",
        f"| Attack Success Rate (ASR) | {_fmt(summary['asr'])} |",
        f"| Refusal Rate | {_fmt(summary['refusal_rate'])} |",
        f"| Mean rounds to success | {_fmt(summary['mean_rounds_to_success'])} |",
        "",
        "### By Category",
        "",
        "| Category | Total | ASR | Mean Rounds |",
        "|---|---|---|---|",
    ]
    for cat, stats in summary["by_category"].items():
        lines.append(f"| {cat} | {stats['total']} | {_fmt(stats['asr'])} | {_fmt(stats['mean_rounds'])} |")
    return "\n".join(lines)


def write_report(results: list[dict], run_dir: Path) -> Path:
    run_dir.mkdir(parents=True, exist_ok=True)
    summary = summarise(results)

    json_path = run_dir / "results.json"
    json_path.write_text(json.dumps({"summary": summary, "raw": results}, indent=2))

    md_path = run_dir / "report.md"
    md_path.write_text(render_markdown(summary))

    return md_path
