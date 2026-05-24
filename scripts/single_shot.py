"""Phase 2 smoke test — one attacker → target → judge pass."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from rich.console import Console
from rich.panel import Panel

from src.attacks.library import get_attacks
from src.agents.attacker import generate_attack
from src.agents.judge import judge_response
from src.serving.vllm_client import target_chat

console = Console()


def main():
    attack = get_attacks()[0]
    console.print(Panel(f"[bold]Attack:[/bold] {attack.description}\n[bold]Category:[/bold] {attack.category}", title="🎯 Target"))

    prompt = generate_attack(attack, previous_attempts=[])
    console.print(Panel(prompt, title="⚔️  Attacker prompt"))

    response = target_chat(system="You are a helpful AI assistant.", user=prompt)
    console.print(Panel(response, title="🤖 Target response"))

    verdict = judge_response(prompt, response)
    color = "red" if verdict["success"] else "green"
    console.print(Panel(f"[{color}]Success: {verdict['success']}[/{color}]\nReason: {verdict['reason']}", title="⚖️  Judge verdict"))


if __name__ == "__main__":
    main()
