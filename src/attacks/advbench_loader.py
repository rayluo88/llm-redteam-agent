"""Load AdvBench harmful-behaviours dataset from HuggingFace."""

from src.attacks.library import Attack


def load_advbench(n: int = 50, seed: int = 42) -> list[Attack]:
    """
    Load n prompts from the AdvBench harmful-behaviours subset.
    Requires: `datasets` package and internet access.
    """
    from datasets import load_dataset
    import random

    ds = load_dataset("walledai/AdvBench", split="train")
    random.seed(seed)
    sample = random.sample(list(ds), min(n, len(ds)))

    return [
        Attack(
            id=f"ADVBENCH-{i:03d}",
            category="LLM01",
            description="AdvBench harmful behaviour",
            prompt=row["prompt"] if "prompt" in row else row["goal"],
        )
        for i, row in enumerate(sample)
    ]
