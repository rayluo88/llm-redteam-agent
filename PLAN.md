# LLM Safety Red-Team Multi-Agent System — Project Plan

## Context

Raymond is applying for GovTech AI Innovation Data Scientist (Singapore). CV gaps (per `gaps.md`) needing **project evidence** before applying:

- Llama 3.x / Gemma / Deepseek hands-on (essential, zero today)
- vLLM serving (preferred, zero today)
- LangGraph multi-agent orchestration (zero today)
- LLM safety / red-teaming domain (matches JD example project verbatim)
- External knowledge sharing (no published blog posts)
- Research methods framing (no explicit experimental writeup)

This project closes 6 of 7 remaining gaps in a single 2-week sprint, and **maps directly** to GovTech's stated example project: *"working with the Responsible AI team to develop context-aware, automated approach to LLM safety testing"*.

## Why This Project (Single-Project Pick)

1. **Direct JD map.** Mirrors GovTech's Responsible AI example project. Interviewer connects dots immediately.
2. **Max gap coverage per project.** Closes vLLM, LangGraph, Llama 4, Gemma 4, multi-agent, LLM safety, research framing, blog-post gaps.
3. **Strongest narrative.** "I built an automated red-team agent" beats "I built a benchmark harness" as an interview story. Demonstrates JD's "Taking Ownership" trait — open-ended, end-to-end PoC.
4. **Reusable scaffold.** vLLM + LangGraph base extends to follow-on projects (eval harness, pentest recon) later.
5. **Deepseek bonus path.** Swap Gemma 4 attacker → DeepSeek-V4-Flash to cover Deepseek gap too (+1 gap closed, ~same effort).

## Target Location

**Save this plan to:** `/Users/raymondluo/Documents/jobs/govtech-ai-ds/llm-redteam-agent/PLAN.md`

The `llm-redteam-agent/` subdir becomes the project root for the implementation that follows.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Attacker Agent │────▶│   Target LLM     │────▶│  Judge Agent    │
│  (Gemma 4-E4B   │     │ (Llama 4 Scout   │     │  (Llama 4 Scout │
│   via vLLM)     │     │  via vLLM)       │     │   via vLLM)     │
└────────┬────────┘     └──────────────────┘     └────────┬────────┘
         ▲                                                 │
         │                                                 ▼
         │              ┌──────────────────┐     ┌─────────────────┐
         └──────────────│ Strategist Agent │◀────│  State Tracker  │
                        │ (refines attack) │     │  (LangGraph)    │
                        └──────────────────┘     └─────────────────┘
```

- **Target model**: `google/gemma-4-26b-a4b-it` (Gemma 4 26B MoE, **3.8B active per inference**, near-27B quality) — via Ollama locally (free dev) or vLLM on Kaggle T4 (free eval). Optional upgrade: `meta-llama/Llama-4-Scout-17B-16E-Instruct` if 64GB+ unified memory available.
- **Attacker model**: `google/gemma-4-E4B-it` (Gemma 4, ~4B active, runs on any 8GB+ GPU) — already covered by existing Ollama setup. Optional swap → `deepseek-ai/DeepSeek-V4-Flash` to cover Deepseek gap.
- **Judge model**: Same as target (separate system prompt, reused endpoint) OR Claude API for higher quality
- **Backend**: OpenAI-compatible API for both — switch via `LLM_BASE_URL` env var. Same code works against Ollama (`localhost:11434/v1`) and vLLM (`localhost:8000/v1`) with zero changes.
- **Orchestration**: LangGraph state machine. Nodes: `generate_attack` → `query_target` → `judge_response` → `refine_or_terminate`. Termination: success OR max N rounds.
- **Attack library**: seeded from OWASP LLM Top 10 jailbreak categories + AdvBench harmful-behaviours dataset (HuggingFace)
- **Metrics**: Attack Success Rate (ASR), Refusal Rate, mean rounds-to-jailbreak, per-category breakdown

## Tech Stack

| Layer | Tool | Cost | Gap Closed |
|---|---|---|---|
| Dev serving | Ollama (existing local setup) | Free | — |
| Eval serving | vLLM ≥0.21.0 on Kaggle free T4 (30hr/week) | Free | ✅ vLLM |
| Orchestration | LangGraph 1.2.0 | Free | ✅ LangGraph |
| LLM wrappers | LangChain | Free | (already in CV) |
| Target model | `google/gemma-4-26b-a4b-it` (Ollama dev) / `google/gemma-4-E4B-it` (vLLM eval) | Free | ✅ Gemma 4 |
| Llama 4 upgrade | `meta-llama/Llama-4-Scout-17B-16E-Instruct` if 64GB+ RAM | Free | ✅ Llama 4 |
| Attacker model | `google/gemma-4-E4B-it` (or `deepseek-ai/DeepSeek-V4-Flash`) | Free | ✅ Gemma 4 (or Deepseek V4) |
| Eval data | AdvBench, HarmBench (HF datasets) | — |
| Package mgmt | uv (per user CLAUDE.md) | — |
| Containerization | Docker Compose (vLLM + agent runtime) | — |

## Project Structure (to be created in subdir)

```
llm-redteam-agent/
├── PLAN.md                      ← this plan file
├── README.md                    ← project overview, setup, results table
├── pyproject.toml               ← uv-managed deps
├── docker-compose.yml           ← vLLM target + attacker + agent runtime
├── src/
│   ├── agents/
│   │   ├── attacker.py          ← attack generation logic
│   │   ├── judge.py             ← success scoring
│   │   └── strategist.py        ← attack refinement
│   ├── graph/
│   │   └── redteam_graph.py     ← LangGraph state machine
│   ├── attacks/
│   │   ├── library.py           ← seed attack templates (OWASP LLM Top 10)
│   │   └── advbench_loader.py   ← AdvBench dataset loader
│   ├── serving/
│   │   └── vllm_client.py       ← OpenAI-compatible client wrappers
│   └── eval/
│       ├── metrics.py           ← ASR, refusal rate, etc.
│       └── report.py            ← results aggregation → markdown
├── notebooks/
│   └── results_analysis.ipynb   ← exploration + visualisation
├── results/
│   └── run_<timestamp>/         ← per-run logs, metrics, attack traces
└── blog/
    └── post.md                  ← draft blog post for external sharing
```

## Compute Considerations

**Fully free path (recommended, $0 total):**

| Phase | Where | Model | Cost |
|---|---|---|---|
| Dev / iteration (phases 1–5) | Ollama local | `gemma4:26b-a4b-it` target + `gemma4:e4b` attacker | Free |
| vLLM eval run — small models | Kaggle P100 16GB (30 hrs/week) | `gemma-4-E4B-it` or `Llama-3.1-8B-Instruct` via `vllm serve` | Free |
| vLLM eval run — Llama 4 Scout | Modal.com A100 ($5 credit ≈ 1.5 hrs) | `Llama-4-Scout-17B-16E-Instruct` via vLLM | Free (credit) |
| Deepseek option | Ollama local | `ollama pull deepseek-r1:14b` (distilled, manageable) | Free |

**Platform notes:**
- **Kaggle**: 30 free GPU hrs/week (P100 16GB), 12hr continuous sessions — most reliable for running `vllm serve` as a persistent endpoint. Start here.
- **Modal**: $5 credit (GitHub signup, no CC). A100 at ~$2.80/hr → ~1.5 free hours. Use for **one targeted Llama 4 Scout run only** — spin up, run 50-attack benchmark, tear down. Zero idle cost; budget carefully.
- **Ollama local**: backend-agnostic code (`LLM_BASE_URL` env var) means zero rework switching to vLLM endpoint. Dev on Ollama, eval on vLLM — same code.

**Llama 4 Scout locally** (optional bonus): if machine has 64GB+ unified memory, `ollama pull llama4:scout` (Q4 ≈ 45–55GB) runs for free without Modal.

## Implementation Phases (≈10–14 days)

| Phase | Days | Deliverable |
|---|---|---|
| **1. Scaffold** | 1–2 | Repo init, uv project, Docker compose with vLLM target + attacker endpoints up |
| **2. Single-shot attack** | 2 | One attacker → target → judge pass works end-to-end |
| **3. LangGraph loop** | 2 | Multi-round red-team graph with state, termination conditions, retry logic |
| **4. Attack library** | 2 | OWASP-categorised seed attacks + AdvBench integration |
| **5. Eval + metrics** | 2 | ASR, refusal rate, per-category breakdown, JSON + markdown output |
| **6. Hardening + docs** | 1–2 | README with reproducible setup, results table, error handling |
| **7. Blog post** | 1–2 | Medium/personal-site post (covers external sharing gap) |

## Verification (acceptance bar)

A GovTech interviewer asks: *"talk me through your red-team agent design."* The answer must be:
1. **Concrete**: cite the LangGraph node names, the attack categories tested, the exact ASR numbers measured
2. **Opinionated**: explain *why* Gemma 4 E4B (or DeepSeek V4 Flash) chosen as attacker, *why* LangGraph 1.2 over CrewAI/AutoGen, *why* LLM-as-judge over rule-based
3. **Grounded in own code**: reference specific files/decisions, not generic concepts
4. **Honest about limits**: what the system *can't* defend against, where the eval is weak

Concrete deliverables:
- GitHub repo, public, with reproducible setup (`uv sync` + `docker compose up` → working demo)
- Results table in README (numbers, not vibes)
- Blog post published (Medium or personal site)
- CV update: 1 project entry with quantified outcome ("Achieved X% ASR against Llama 4 Scout using a 3-agent LangGraph orchestration over N attack categories")

## Out of Scope (explicit non-goals)

- Novel attack research (use existing OWASP/AdvBench categories — not inventing new jailbreaks)
- Defending the target (one-sided red-team only)
- Multi-modal attacks (text-only)
- Production deployment (PoC quality only — matches the JD's "proof-of-concept" framing)

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| GPU access | Ollama local (dev) + Kaggle P100 free 30hr/week (primary vLLM eval) + Modal $5 credit (one Llama 4 Scout run, ~1.5 hrs). $0 out of pocket. |
| Llama 4 Scout local | Only if machine has 64GB+ unified memory. Otherwise Gemma 4 26B-A4B is the free-path target (3.8B active, near-27B quality). |
| Llama 4 HF gating | Apply for access now if planning to use Scout. Fallback: Gemma 4 26B-A4B (no gating, Apache 2). |
| Kaggle T4 vLLM | T4 has 16GB VRAM → serves `gemma4:e4b` or `Llama-3.1-8B-Instruct` comfortably via vLLM. Kaggle gives 30 free GPU hrs/week. |
| LangGraph learning curve | Start from official LangGraph tutorial (multi-agent example); avoid bespoke graph design until basics solid |
| Judge quality (false negatives/positives) | Spot-check 20% of judgments manually; report inter-rater agreement |
| Scope creep | Hard cap at 14 days. Phase 7 (blog) is non-negotiable — gap-closing artifact |
