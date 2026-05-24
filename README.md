# LLM Red-Team Agent

Automated multi-agent system for adversarial safety evaluation of large language models. Implements a closed-loop red-teaming pipeline: an attacker agent generates adversarial prompts, a target LLM responds, a judge agent scores jailbreak success, and a strategist refines the attack strategy across multiple rounds.

Attacks are categorised across all 10 [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/) categories and supplemented with the [AdvBench](https://huggingface.co/datasets/walledai/AdvBench) harmful-behaviours dataset. Results are reported as Attack Success Rate (ASR), refusal rate, and per-category breakdown.

---

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Attacker Agent │────▶│   Target LLM     │────▶│  Judge Agent    │
│  (Gemma 4 E4B)  │     │  (Gemma 4 26B)   │     │  (Gemma 4 26B)  │
└────────┬────────┘     └──────────────────┘     └────────┬────────┘
         ▲                                                 │
         │              ┌──────────────────┐               │
         └──────────────│ Strategist Agent │◀──────────────┘
                        │  (refines attack) │    (on failure)
                        └──────────────────┘
```

**Loop logic (LangGraph state machine):**

```
generate_attack → query_target → judge_response → terminate (success or max rounds)
                                       │
                                  refine_strategy → generate_attack (loop)
```

Each attack runs for up to `MAX_ROUNDS` (default: 5). The strategist analyses why an attack failed and instructs the attacker to vary its approach in the next round.

---

## Tech Stack

| Layer | Tool | Rationale |
|---|---|---|
| Orchestration | [LangGraph](https://github.com/langchain-ai/langgraph) 1.2 | Explicit state machine with typed state, conditional edges, and built-in cycle support — better suited to adversarial loops than agent frameworks that abstract away control flow (CrewAI, AutoGen). Allows precise inspection of each node's inputs and outputs, which is essential for eval reproducibility. |
| LLM serving | [vLLM](https://github.com/vllm-project/vllm) / [Ollama](https://ollama.com) | Both expose an OpenAI-compatible API, so the same client code runs against a local Ollama instance (dev) or a vLLM endpoint on cloud GPUs (eval), switched via a single env var. vLLM is used for production eval runs due to continuous batching and PagedAttention throughput. |
| Target / Judge model | `google/gemma-4-26b-a4b-it` | Gemma 4's MoE architecture activates only 3.8B parameters per forward pass, giving near-27B quality at a fraction of the compute cost. Runs comfortably on a 32 GB machine at Q4 quantisation (~13 GB). Apache 2.0 licence — no usage restrictions for research. |
| Attacker model | `google/gemma-4-E4B-it` | Lightweight (4B active params), fast iteration speed for attack generation. Separate endpoint from the target prevents the attacker from being influenced by the target's safety tuning. |
| Attack data | OWASP LLM Top 10 seed library + AdvBench | OWASP categories provide structured, taxonomy-aligned coverage; AdvBench provides community-validated harmful-behaviour prompts for standardised benchmarking. |
| Package management | [uv](https://github.com/astral-sh/uv) | Deterministic installs via `uv.lock`, significantly faster than pip, native `pyproject.toml` support. |

---

## Results

> Results will be populated after the full eval run against vLLM-served models on Kaggle / Modal.

| Model (target) | Backend | Attacks | ASR | Refusal Rate | Mean Rounds |
|---|---|---|---|---|---|
| Gemma 4 26B (Ollama dev) | Ollama | 50 | TBD | TBD | TBD |
| Gemma 4 E4B (vLLM eval) | vLLM / Kaggle | 50 | TBD | TBD | TBD |

Per-category ASR breakdown and raw results will be available in `results/` after eval runs.

---

## Setup

### Prerequisites

- [Ollama](https://ollama.com) (local dev) or a vLLM endpoint (eval)
- [uv](https://github.com/astral-sh/uv) (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Python 3.13+

### Install

```bash
git clone https://github.com/rayluo88/llm-redteam-agent
cd llm-redteam-agent
uv sync
```

### Pull models (Ollama)

```bash
ollama pull gemma4:26b    # target + judge (~13 GB)
ollama pull gemma4:e4b    # attacker (~3 GB)
```

### Configure

```bash
cp .env.example .env
# Edit .env to set TARGET_BASE_URL, ATTACKER_BASE_URL, and model IDs
# Defaults point to Ollama on localhost:11434
```

### Run

```bash
# Single attack cycle (smoke test)
uv run python scripts/single_shot.py

# Full eval (50 attacks, up to 5 rounds each)
uv run python scripts/run_eval.py
```

Results are written to `results/run_<timestamp>/report.md` and `results.json`.

### Switching to vLLM (cloud eval)

Set in `.env`:

```env
TARGET_BASE_URL=http://<your-vllm-host>:8000/v1
TARGET_MODEL=google/gemma-4-E4B-it
```

No code changes required — the same client works against any OpenAI-compatible endpoint.

### Docker (vLLM + agent, GPU required)

```bash
cp .env.example .env
# Set HF_TOKEN in .env (required to pull Gemma 4 from HuggingFace)

docker compose up
```

Spins up two vLLM containers (target on port 8000, attacker on 8001) and runs the eval agent against them. Requires an NVIDIA GPU with the NVIDIA Container Toolkit installed.

---

## Project Structure

```
Dockerfile
docker-compose.yml
src/
├── agents/
│   ├── attacker.py       # generates adversarial prompts
│   ├── judge.py          # scores jailbreak success → JSON
│   └── strategist.py     # refines strategy on failure
├── graph/
│   └── redteam_graph.py  # LangGraph state machine
├── attacks/
│   ├── library.py        # 50 seed attacks, OWASP LLM Top 10 (5 per category)
│   └── advbench_loader.py
├── serving/
│   └── vllm_client.py    # OpenAI-compatible client; backend-agnostic
└── eval/
    ├── metrics.py         # ASR, refusal rate, per-category breakdown
    └── report.py          # → markdown + JSON
scripts/
├── single_shot.py         # one-cycle smoke test
└── run_eval.py            # full eval pipeline
```

---

## Limitations

- **Judge quality**: LLM-as-judge introduces false positives (overly cautious scoring) and false negatives (subtle compliance missed). ~20% of judgments are spot-checked manually to estimate inter-rater agreement.
- **Attack scope**: Seed attacks use existing OWASP/AdvBench categories. Novel jailbreak research is out of scope.
- **Text-only**: No multi-modal attack vectors.
- **One-sided**: Red-team only — no defence/guardrail component.

---

## Licence

MIT
