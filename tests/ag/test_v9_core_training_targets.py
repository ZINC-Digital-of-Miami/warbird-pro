import pandas as pd

from scripts.ag.train_v9_locked import LABEL_COL, ML_FEATURES, build_trade_dataset


def _feature_defaults() -> dict[str, object]:
    out: dict[str, object] = {}
    for col in ML_FEATURES:
        if col in {"knob_nq_symbol", "knob_zn_symbol", "knob_dxy_symbol", "knob_vix_symbol"}:
            out[col] = "TEST"
        elif col == "knob_zn_gate_direction":
            out[col] = "Same Direction"
        else:
            out[col] = 0.0
    return out


def test_trade_dataset_uses_emitted_entry_tp_stop_and_adds_tp_sl_sidecar_labels():
    rows = []
    for i, (high, low, close) in enumerate(
        [
            (101.0, 99.0, 100.0),
            (108.5, 99.5, 108.0),
            (109.0, 100.0, 108.5),
        ]
    ):
        rec = _feature_defaults()
        rec.update(
            {
                "ts": pd.Timestamp("2026-01-01T00:00:00Z") + pd.Timedelta(minutes=15 * i),
                "high": high,
                "low": low,
                "close": close,
                "ml_entry_long_trigger": 1.0 if i == 0 else 0.0,
                "ml_entry_short_trigger": 0.0,
                "ml_trade_entry": 100.0 if i == 0 else 0.0,
                "ml_trade_tp": 108.0 if i == 0 else 0.0,
                "ml_trade_stop": 97.0 if i == 0 else 0.0,
            }
        )
        rows.append(rec)
    df = pd.DataFrame(rows)

    trades = build_trade_dataset(df, max_hold_bars=2)

    assert len(trades) == 1
    assert trades.loc[0, LABEL_COL] == 1
    assert trades.loc[0, "tp_hit"] == 1
    assert trades.loc[0, "stop_hit"] == 0
    assert trades.loc[0, "target_price"] == 108.0
    assert trades.loc[0, "stop_price"] == 97.0
    assert trades.loc[0, "time_to_tp_bars"] == 1
    assert trades.loc[0, "mfe_points"] == 9.0
    assert trades.loc[0, "mae_points"] == 0.5
