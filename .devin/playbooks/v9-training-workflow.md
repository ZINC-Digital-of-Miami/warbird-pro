# V9 Core Training Workflow

Step-by-step for V9 Core training work.

1. **Confirm approval** — Do not run training without explicit approval in the current session
2. **Verify Pine settings** — Live Pine settings must match dataset builder constants. Reference the authoritative settings table in `AGENTS.md` lines 181–204.
3. **Training sequence is locked** — ES 15m FIRST, then 5m only after 15m success is documented (fit + SHAP + Monte Carlo)
4. **Run production trainer** — `python3 scripts/ag/train_v9_locked.py`
5. **Run SHAP gate** — `python3 scripts/ag/shap_v9.py`
6. **Run Monte Carlo gate** — `python3 scripts/ag/monte_carlo_v9.py`
7. **Both gates must pass** before enabling any TradingView alert
8. **Run contract tests:**
   ```bash
   pytest tests/ag/test_v9_core_indicator_input_contract.py -q
   pytest tests/ag/test_v9_core_training_targets.py -q
   ```
