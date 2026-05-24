"""Phase 5 — full eval pipeline."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

from rich.console import Console
from rich.progress import track

from src.attacks.library import get_attacks
from src.graph.redteam_graph import graph
from src.eval.report import write_report

console = Console()


def main():
    n = int(os.getenv("NUM_ATTACKS", "50"))
    attacks = get_attacks(n=n)
    console.print(f"[bold]Running eval:[/bold] {len(attacks)} attacks, max {os.getenv('MAX_ROUNDS', 5)} rounds each")

    results = []
    for attack in track(attacks, description="Running attacks..."):
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

    run_dir = Path("results") / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    report_path = write_report(results, run_dir)
    console.print(f"\n[green]Report written:[/green] {report_path}")
    console.print(f"[green]JSON data:[/green] {run_dir / 'results.json'}")


if __name__ == "__main__":
    main()
