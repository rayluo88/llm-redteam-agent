# LLM Red-Team Agent — Development Tracker

**Goal:** Close CV gaps (vLLM, LangGraph, Llama 4, Gemma 4, LLM safety) for GovTech AI Innovation application.  
**Target duration:** 10–14 days  
**Status legend:** `[ ]` todo · `[~]` in progress · `[x]` done · `[!]` blocked

---

## Pre-work (before coding)

- [ ] Apply for Llama 4 Scout HF gated access (meta-llama/Llama-4-Scout-17B-16E-Instruct)
- [ ] Verify Kaggle account has GPU enabled (Settings → Phone verify → GPU quota)
- [ ] Confirm Ollama running: `ollama list` — check gemma4 models available
- [ ] Pull attacker model: `ollama pull gemma4:e4b`
- [ ] Pull target model: `ollama pull gemma4:26b-a4b` (or `llama4:scout` if 64GB+ RAM)
- [ ] Create GitHub repo: `llm-redteam-agent` (public, MIT license)

---

## Phase 1 — Scaffold (Days 1–2)

**Deliverable:** Repo structure, uv project, Ollama endpoints verified end-to-end.

- [ ] `uv init` in project dir, configure `pyproject.toml`
- [ ] Add core deps: `langgraph`, `langchain`, `langchain-openai`, `openai`, `python-dotenv`, `rich`
- [ ] Create `.env.example` with `TARGET_BASE_URL`, `ATTACKER_BASE_URL`, `TARGET_MODEL`, `ATTACKER_MODEL`
- [ ] Create `src/serving/vllm_client.py` — thin OpenAI-compatible wrapper, reads from env
- [ ] Smoke test: `curl http://localhost:11434/v1/chat/completions` with both models
- [ ] Create project dir structure (all empty `__init__.py` files, folder skeleton)
- [ ] Set up `.gitignore` (exclude `.env`, `results/`, `__pycache__`)
- [ ] First commit: scaffold

---

## Phase 2 — Single-Shot Attack (Days 3–4)

**Deliverable:** One attacker → target → judge pass works end-to-end, printed to console.

- [ ] `src/attacks/library.py` — 10 seed attack prompts across 5 OWASP LLM Top 10 categories
- [ ] `src/agents/attacker.py` — takes category + history, returns adversarial prompt
- [ ] `src/agents/judge.py` — takes (attack, response), returns `{"success": bool, "reason": str}`
- [ ] `scripts/single_shot.py` — run one attack cycle, print results
- [ ] Verify judge is not trivially always-true or always-false on 5 manual examples
- [ ] Commit: single-shot attack working

---

## Phase 3 — LangGraph Loop (Days 5–6)

**Deliverable:** Multi-round red-team graph with state, retry logic, termination.

- [ ] `src/graph/redteam_graph.py` — define `RedTeamState` TypedDict
- [ ] Implement nodes: `generate_attack` · `query_target` · `judge_response` · `refine_or_terminate`
- [ ] Wire edges: linear flow + conditional edge (success → terminate, fail → refine, max_rounds → terminate)
- [ ] `src/graph/redteam_graph.py` — compile graph with `langgraph>=1.2.0` `StateGraph`
- [ ] `scripts/run_campaign.py` — run N attacks from library through graph, collect results
- [ ] Test: 3-round loop on 3 prompts, verify state transitions correct
- [ ] Commit: LangGraph loop working

---

## Phase 4 — Attack Library (Days 7–8)

**Deliverable:** OWASP-categorised attack library + AdvBench integration (100+ attacks).

- [ ] Expand `src/attacks/library.py` to cover all OWASP LLM Top 10 categories (min 5 per category)
- [ ] `src/attacks/advbench_loader.py` — load `hkunlp/instructor-xl` AdvBench harmful-behaviours subset from HF datasets
- [ ] Deduplicate + tag attacks with category metadata
- [ ] `src/attacks/library.py` — `get_attacks(category=None, n=50)` sampling function
- [ ] Commit: attack library complete

---

## Phase 5 — Eval + Metrics (Days 9–10)

**Deliverable:** ASR, refusal rate, per-category breakdown → JSON + markdown report.

- [ ] `src/eval/metrics.py` — `compute_asr()`, `compute_refusal_rate()`, `per_category_breakdown()`
- [ ] `src/eval/report.py` — render results dict → markdown table + JSON file
- [ ] `scripts/run_eval.py` — full eval pipeline: load attacks → run graph → compute metrics → write report
- [ ] Run eval locally (Ollama): 50 attacks, record baseline numbers
- [ ] **Switch to Kaggle / vLLM**: re-run eval with `gemma-4-E4B-it` served via `vllm serve`
- [ ] **Modal run** (Llama 4 Scout, $5 credit): run targeted 30-attack subset, record numbers
- [ ] Spot-check 20% of judge decisions manually — record inter-rater agreement
- [ ] Commit: eval pipeline complete + results in `results/`

---

## Phase 6 — Hardening + Docs (Days 11–12)

**Deliverable:** Clean repo, reproducible setup, README with results table.

- [ ] Error handling: retry on API timeout, graceful skip on model refusal to load
- [ ] `README.md`: project overview, architecture diagram, setup instructions (`uv sync` + `ollama pull`), results table
- [ ] `docker-compose.yml`: vLLM target + attacker services (for cloud/reproducible eval)
- [ ] Add `notebooks/results_analysis.ipynb` — visualise ASR by category
- [ ] Final repo cleanup: no secrets, no large files, clean commit history
- [ ] Commit: v1.0 release tag

---

## Phase 7 — Blog Post (Days 13–14)

**Deliverable:** Published post covering design decisions, results, lessons learned.

- [ ] Draft `blog/post.md`: intro → architecture → attack library → results → limitations
- [ ] Include: LangGraph state diagram, ASR table, code snippet of `redteam_graph.py`
- [ ] Explain *why* LangGraph over CrewAI/AutoGen (opinionated take)
- [ ] Explain *why* Gemma 4 as attacker (lightweight, capable, Apache 2)
- [ ] Publish to Medium or personal site
- [ ] Add link to blog post in README
- [ ] Commit: blog post link added

---

## Post-project

- [ ] Update CV: add project entry with quantified ASR result
- [ ] Update `gaps.md`: mark vLLM ✅, LangGraph ✅, Llama 4 ✅, Gemma 4 ✅, LLM safety ✅
- [ ] Apply to GovTech role

---

## Notes / Blockers

| Date | Note |
|---|---|
| | |
