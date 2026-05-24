"""Full eval pipeline — runs all attacks through the LangGraph red-team loop."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
import logging
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

from rich.console import Console
from rich.progress import track

from src.attacks.library import get_attacks
from src.graph.redteam_graph import graph
from src.eval.report import write_report

console = Console()
logging.basicConfig(level=logging.WARNING)


def main():
    n = int(os.getenv("NUM_ATTACKS", "50"))
    attacks = get_attacks(n=n)
    console.print(f"[bold]Running eval:[/bold] {len(attacks)} attacks, max {os.getenv('MAX_ROUNDS', 5)} rounds each")

    results = []
    skipped = 0
    for attack in track(attacks, description="Running attacks..."):
        try:
            state = graph.invoke({
                "attack": attack,
                "attempts": [],
                "responses": [],
                "judgments": [],
                "strategy_notes": [],
                "round": 0,
                "success": False,
            })
            results.append({
                "id": attack.id,
                "category": attack.category,
                "description": attack.description,
                "success": state["success"],
                "round": state["round"],
                "attempts": state["attempts"],
            })
        except Exception as e:
            console.print(f"[yellow]Skipped {attack.id}: {e}[/yellow]")
            skipped += 1

    if skipped:
        console.print(f"[yellow]Skipped {skipped} attacks due to errors.[/yellow]")

    if not results:
        console.print("[red]No results — check backend connectivity.[/red]")
        return

    run_dir = Path("results") / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    report_path = write_report(results, run_dir)
    console.print(f"\n[green]Report written:[/green] {report_path}")
    console.print(f"[green]JSON data:[/green] {run_dir / 'results.json'}")


if __name__ == "__main__":
    main()
