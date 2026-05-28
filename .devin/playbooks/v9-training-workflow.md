# V9 Core Training Workflow

Step-by-step for V9 Core training work.

> **NOTE (2026-05-28):** The AutoGluon full-zoo config is no longer locked. Model selection is TBD pending deep research on data sources, fib indicator polishing, and architecture decisions. This playbook covers the general training flow; specific model/config details will evolve.

1. **Confirm approval** — Do not run training without explicit approval in the current session
2. **Verify Pine settings** — Live Pine settings must match dataset builder constants. Reference the authoritative settings table in `AGENTS.md` lines 181–204.
3. **Training sequence** — ES 15m is the stronger baseline (PF 1.143 vs 5m PF 0.91). Start with 15m.
4. **Data research first** — Before training, confirm what data sources and features are approved for this run. Model selection depends on data decisions.
5. **Run trainer** — Use the appropriate training script with the selected model configuration
6. **Run SHAP gate** — `python3 scripts/ag/shap_v9.py` — validates feature causality and stability
7. **Run Monte Carlo gate** — `python3 scripts/ag/monte_carlo_v9.py` — validates P&L distribution and drawdown
8. **Both gates must pass** before enabling any TradingView alert or dashboard trigger
9. **Run contract tests:**
   ```bash
   pytest tests/ag/test_v9_core_indicator_input_contract.py -q
   pytest tests/ag/test_v9_core_training_targets.py -q
   ```
