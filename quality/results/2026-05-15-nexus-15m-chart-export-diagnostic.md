# Nexus 15m Chart Export Quantitative Diagnostic — 2026-05-15
## Source
- CSV: `/Users/zincdigital/Downloads/CME_MINI_MES1!, 15_0adbb.csv`
- SHA256: `59b7841d8fe4d03bd2ae011f6a44477ed983e8be5a8d98d558f923189075dbee`
- Rows/columns: `20650` / `30`
- UTC range: `2025-06-30T22:00:00+00:00` → `2026-05-15T12:00:00+00:00`
- Scope: Nexus-only 15m MES chart export with OHLC + visible Nexus plots + data-window/export-only `nexus_*` footprint evidence. No V9/fib assumptions used.

## 1. Data Integrity & Alignment
- Monotonic timestamps: `True`; duplicates: `0`.
- 15m intervals: `20422`; non-15m intervals: `227`; largest gap: `3420.00` minutes.
- Interval count top values: `{'900': 20422, '4500': 174, '177300': 40, '18900': 4, '18000': 1, '191700': 1, '180900': 1, '39600': 1}`. Non-15m gaps align with futures session/weekend breaks, not duplicate/misaligned bars.
- Footprint available rows: `6668` (32.29%); footprint-quality rows: `6659` (32.25%).
- Mode minutes unique: `[15.0]`.
- Signal-tier counts: `{'-1.0': 263, '-0.5': 29, '0.0': 20110, '0.5': 20, '1.0': 228}`.
- Repaint cannot be proven or disproven from one static export; it requires repeated exports or live/replay snapshots of the same bars.
- Anomaly: footprint evidence is available only for the later `~32.3%` of bars. Diagnostics using `nexus_fp_*` are therefore footprint-valid only on that subset.

## 2. Price Regime Segmentation
| Regime | Bars | Share |
| --- | ---: | ---: |
| neutral | 11222 | 54.34% |
| contraction_chop | 2638 | 12.77% |
| quiet_trend | 2417 | 11.70% |
| trend_expansion | 2362 | 11.44% |
| volatile_chop | 2011 | 9.74% |

## 3. Nexus vs Price Diagnostics
### Top absolute Spearman IC values
| Feature | Horizon bars | IC | N | Shuffled null p95 abs | Verdict |
| --- | ---: | ---: | ---: | ---: | --- |
| nexus_fp_total_volume | 20 | -0.0311 | 6648 | 0.0243 | above null |
| nexus_delta_slope Δ | 1 | 0.0167 | 6657 | 0.0241 | within null/no edge |
| nexus_fp_bar_delta | 20 | 0.0139 | 6648 | 0.0246 | within null/no edge |
| nexus_fp_bar_delta | 5 | 0.0124 | 6663 | 0.0230 | within null/no edge |
| NFE Oscillator Δ | 3 | -0.0116 | 20634 | 0.0148 | within null/no edge |
| nexus_norm_cum_delta Δ | 10 | -0.0101 | 6648 | 0.0238 | within null/no edge |
| nexus_delta_dir | 20 | 0.0099 | 20617 | 0.0146 | within null/no edge |
| nexus_delta_slope Δ | 5 | 0.0094 | 6653 | 0.0244 | within null/no edge |
| nexus_signal_tier | 1 | -0.0092 | 20636 | 0.0143 | within null/no edge |
| nexus_delta_slope Δ | 10 | -0.0088 | 6648 | 0.0242 | within null/no edge |
| NFE Oscillator Δ | 10 | -0.0075 | 20627 | 0.0137 | within null/no edge |
| nexus_fp_total_volume | 10 | -0.0067 | 6658 | 0.0244 | within null/no edge |
| nexus_bar_delta_ratio Δ | 5 | 0.0066 | 6662 | 0.0223 | within null/no edge |
| NFE Oscillator Δ | 1 | -0.0062 | 20636 | 0.0138 | within null/no edge |
| nexus_bar_delta_ratio Δ | 10 | -0.0054 | 6657 | 0.0223 | within null/no edge |

### Signal-event expectancy, signed by expected direction, in ATR units
| Event | Events | H1 mean | H1 hit | H3 mean | H3 hit | H5 mean | H5 hit | H10 mean | H10 hit | H20 mean | H20 hit |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Tier 1 bullish exhaustion | 228 | 0.008 | 49.12% | 0.025 | 53.07% | 0.091 | 52.63% | 0.107 | 48.25% | 0.216 | 53.51% |
| Tier 1 bearish exhaustion | 263 | -0.028 | 45.25% | 0.055 | 47.15% | 0.121 | 46.77% | 0.077 | 47.91% | 0.079 | 43.73% |
| Tier 2 bullish cross | 20 | -0.038 | 70.00% | -0.285 | 60.00% | -0.656 | 65.00% | -1.126 | 50.00% | -1.150 | 50.00% |
| Tier 2 bearish cross | 29 | -0.589 | 17.24% | -0.552 | 31.03% | -0.592 | 31.03% | 0.057 | 37.93% | -0.239 | 41.38% |
| Any directional signal | 540 | -0.043 | 46.30% | -0.003 | 49.26% | 0.041 | 49.07% | 0.044 | 47.59% | 0.074 | 47.96% |
| Gas-out bull flag | 634 | -0.013 | 45.58% | 0.006 | 47.63% | -0.049 | 45.90% | -0.204 | 44.95% | -0.201 | 43.06% |
| Gas-out bear flag | 591 | 0.023 | 50.59% | 0.026 | 53.56% | 0.021 | 51.86% | 0.087 | 51.95% | 0.294 | 55.29% |

### Volume stacking / expansion lead diagnostics
| Pre-event | Expansion events | Event count | Expansion coverage ≤12b | Median lead bars | Event precision ≤12b | Random precision mean | Random precision p95 | Event false-positive |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| delta_dir_nonzero | 1067 | 2640 | 90.25% | 1.00 | 44.05% | 45.19% | 46.37% | 55.95% |
| gasout_any | 1067 | 1225 | 84.82% | 3.00 | 46.53% | 45.12% | 47.27% | 53.47% |
| signal_tier_nonzero | 1067 | 540 | 67.95% | 4.00 | 50.74% | 45.18% | 48.52% | 49.26% |
| abs_delta_slope_top_quartile | 1067 | 1665 | 85.10% | 2.00 | 44.74% | 45.29% | 46.91% | 55.26% |

### Exhaustion lead diagnostics
- `swing_low_count`: `1807`
- `swing_high_count`: `1735`
- `bullish_exhaustion_event_count`: `591`
- `bearish_exhaustion_event_count`: `634`
- `bullish_exhaustion_to_low_hits_12b`: `502`
- `bearish_exhaustion_to_high_hits_12b`: `530`
- `bullish_exhaustion_precision_12b`: `0.8494`
- `bearish_exhaustion_precision_12b`: `0.8360`
- `bullish_random_precision_mean`: `0.8473`
- `bullish_random_precision_p95`: `0.8697`
- `bearish_random_precision_mean`: `0.8450`
- `bearish_random_precision_p95`: `0.8644`
- `bullish_median_lead_bars`: `4.0000`
- `bearish_median_lead_bars`: `4.0000`

## 4. Settings Audit
| Setting area | Classification | Evidence |
| --- | --- | --- |
| Footprint row / VA / imbalance | material | nexus_fp_* fields non-empty on 6,668 bars; volume/delta states depend directly on footprint request. |
| Delta lookback / slope / flip / gas-out thresholds | material | delta_dir nonzero on 2,640 bars; gas-out flags on 1,225 total bars; signal_tier uses these gates. |
| Oscillator length/smoothing/preset/mode | material | NFE Oscillator and Signal Line drive candidate crosses and extreme-zone checks. |
| Volume flow lengths/thresholds | material | VF Base participates in divergence confirmation and visible flow context. |
| Divergence toggles/filters | material but under-exported | Divergence logic is code-present; current CSV has no separate regular/hidden divergence flag columns, so direct event frequency cannot be measured from this export. |
| Theme/color/fill/watermark | cosmetic | Affects display only; no export/evidence dependency. |
| Show Cross Dots | UI-only | Default OFF and excluded from nexus_signal_tier authority. |
| Alert settings | removed | No alert inputs or alertcondition/alert calls remain. |
| Sensitivity ±25% | not measurable from one export | Requires re-exporting the indicator under perturbed settings or a Pine-equivalent replay harness. |

## 5. Diagnostic Answers
1. **Volume stacking advance warning:** yes as a precursor/context feature, not as a standalone entry signal. `signal_tier_nonzero` had `67.95%` expansion coverage with median lead `4.00` bars and `50.74%` event precision vs random mean `45.18%`.
2. **Exhaustion advance warning:** yes for locating nearby swing pivots, weak for direct forward-return expectancy. Bullish exhaustion/gas-out precision to a swing low within 12 bars was `84.94%` vs random mean `84.73%`; bearish precision to swing high was `83.60%` vs random mean `84.50%`. Median lead was 4 bars both ways. However directional-signal H1/H3/H10 expectancy stayed near flat: H3 any-signal mean `-0.003` ATR, hit `49.26%`.
3. **Settings adequacy:** footprint, delta, oscillator, volume-flow, and signal-tier settings are wired and measurable. The export now proves `display.data_window` evidence capture works.
4. **Dead/weak settings:** alert settings are removed; theme/color/fill/watermark are cosmetic; cross dots are UI-only. Divergence settings are wired but under-exported — add explicit regular/hidden divergence flags before treating divergence as a training target.

## 6. Training & Improvement Plan
- Build an isolated Nexus 15m dataset from this export lineage; do not use V9 files/artifacts.
- Use chronological train/validation/test splits with embargo; no random shuffle, no IID AG bagging/stacking.
- Start with labels that match the strongest observed behavior: volume-expansion lead and swing-pivot proximity, not immediate raw forward return.
- Add explicit export flags for regular/hidden divergence if divergence quality is part of the heavy model target.
- A/B tests: (A) current fpQualityOk gate, (B) stricter consecutive-quality gate, (C) volatility-regime adaptive gas-out threshold, (D) volume z-score normalized delta slope, (E) divergence-only with footprint confirmation, (F) exhaustion-only as reversal target.
- Candidate labels: forward ATR bucket, directional continuation/reversal over 3/5/10/20 bars, swing-pivot proximity, volume-expansion lead target.

## Limitations
- This is a single exported settings state. It cannot quantify ±25% input sensitivity without additional exports/replays.
- No live TradingView chart replay or visual audit was automated.
- Footprint evidence exists on only 32.3% of bars; full-history claims must be restricted to the footprint-quality subset.


## Follow-up Instrumentation Added After This Diagnostic

This diagnostic was run before the new raw/confirmed divergence and lag-state exports existed. To avoid guessing through the large settings space, Nexus now exports `nexus_pivot_span`, `nexus_regime_score`, `nexus_osc_momentum`, `nexus_vf_calc`, raw `nexus_div_*_raw` flags, and confirmed `nexus_div_*` flags. Re-export TradingView data after loading the updated Pine before using divergence or pivot-lag as training targets.
