# Nexus 15m Expanded Lag / False-Signal Diagnostic — 2026-05-15
## Source
- CSV: `/Users/zincdigital/Downloads/CME_MINI_MES1!, 15_d464a.csv`
- SHA256: `560a0da03115be6c689a61c7bb5cdea861e16174a6a115efb65c25f745b351d7`
- Rows/columns: `20651` / `44`
- UTC range: `2025-06-30T22:00:00+00:00` → `2026-05-15T12:15:00+00:00`
- Scope: Nexus-only 15m MES chart export with expanded data-window diagnostics. No V9/fib assumptions used.

## 1. Data Integrity & Availability
- Monotonic timestamps: `True`; duplicates: `0`.
- 15m intervals: `20423`; non-15m gaps: `227`; largest gap: `3420.00` minutes.
- Footprint available: `6668` (32.29%); footprint quality: `6659` (32.25%).
- Mode minutes: `[15.0]`; pivot span: `[4.0]` bars = `60` minutes on this export.
- Signal tier counts: `{'-1.0': 263, '-0.5': 29, '0.0': 20111, '0.5': 20, '1.0': 228}`.

## 2. Main Lag Finding
- `nexus_pivot_span` is `4` on every bar. Any divergence label tied to `ta.pivothigh/ta.pivotlow` is confirmed **4 bars after the pivot**, i.e. **60 minutes on 15m**.
- This is structural pivot-confirmation lag, not a UI problem. Training should measure labels from both the pivot bar and confirmation bar, otherwise divergence will look late.

## 3. Raw vs Confirmed Divergence Filter Attrition
| Divergence | Raw events | Confirmed events | Confirmation rate | Filtered out |
| --- | ---: | ---: | ---: | ---: |
| regular bull | 255 | 12 | 4.71% | 243 |
| regular bear | 294 | 14 | 4.76% | 280 |
| hidden bull | 314 | 29 | 9.24% | 285 |
| hidden bear | 260 | 20 | 7.69% | 240 |

## 4. Divergence Forward Expectancy, Signed By Expected Direction
| Event | Count | H1 mean | H1 hit | H3 mean | H3 hit | H5 mean | H5 hit | H10 mean | H10 hit | H20 mean | H20 hit |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| raw regular bull | 255 | 0.060 | 57.65% | 0.076 | 53.33% | 0.078 | 57.65% | 0.065 | 57.25% | 0.386 | 58.27% |
| raw regular bear | 294 | -0.048 | 42.18% | -0.086 | 47.28% | 0.023 | 44.90% | -0.038 | 44.90% | 0.273 | 51.36% |
| raw hidden bull | 314 | 0.037 | 49.68% | 0.007 | 46.82% | -0.001 | 52.23% | 0.036 | 52.08% | 0.229 | 59.74% |
| raw hidden bear | 260 | -0.061 | 45.77% | -0.171 | 41.70% | -0.154 | 41.70% | -0.011 | 45.95% | 0.066 | 46.90% |
| confirmed regular bull | 12 | -0.171 | 58.33% | 0.355 | 50.00% | 0.832 | 83.33% | 0.587 | 58.33% | 0.637 | 75.00% |
| confirmed regular bear | 14 | -0.230 | 42.86% | -0.208 | 57.14% | 0.017 | 50.00% | -0.023 | 57.14% | -0.016 | 42.86% |
| confirmed hidden bull | 29 | 0.022 | 51.72% | -0.215 | 44.83% | -0.055 | 58.62% | -0.345 | 48.28% | -0.376 | 48.28% |
| confirmed hidden bear | 20 | -0.261 | 35.00% | -0.295 | 25.00% | -0.375 | 35.00% | -0.341 | 30.00% | -0.336 | 47.37% |

## 5. Divergence Pivot-Proximity Precision
| Event | Events | Pivot hits ≤12b | Precision | Random mean | Random p95 | Median bars to pivot |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| raw regular bull | 255 | 208 | 81.57% | 84.49% | 87.84% | 5.00 |
| raw regular bear | 294 | 235 | 79.93% | 84.78% | 88.11% | 5.00 |
| raw hidden bull | 314 | 254 | 80.89% | 84.72% | 88.22% | 5.00 |
| raw hidden bear | 260 | 207 | 79.62% | 84.70% | 88.48% | 5.00 |
| confirmed regular bull | 12 | 10 | 83.33% | 84.53% | 100.00% | 7.00 |
| confirmed regular bear | 14 | 11 | 78.57% | 83.45% | 100.00% | 5.00 |
| confirmed hidden bull | 29 | 20 | 68.97% | 84.11% | 93.28% | 7.00 |
| confirmed hidden bear | 20 | 19 | 95.00% | 84.30% | 95.00% | 4.00 |

## 6. Expanded IC / Lead-Lag Snapshot
| Feature | Horizon | IC | N | Shuffled null p95 abs | Verdict |
| --- | ---: | ---: | ---: | ---: | --- |
| nexus_fp_total_volume | 20 | -0.0310 | 6648 | 0.0242 | above null |
| nexus_vf_calc | 20 | 0.0185 | 20618 | 0.0141 | above null |
| nexus_delta_slope Δ | 1 | 0.0165 | 6657 | 0.0234 | within null/no edge |
| nexus_fp_bar_delta | 20 | 0.0136 | 6648 | 0.0232 | within null/no edge |
| nexus_fp_bar_delta | 5 | 0.0122 | 6663 | 0.0266 | within null/no edge |
| NFE Oscillator Δ | 3 | -0.0116 | 20635 | 0.0148 | within null/no edge |
| nexus_norm_cum_delta Δ | 10 | -0.0101 | 6648 | 0.0230 | within null/no edge |
| nexus_delta_dir | 20 | 0.0097 | 20618 | 0.0140 | within null/no edge |
| nexus_delta_slope Δ | 5 | 0.0095 | 6653 | 0.0251 | within null/no edge |
| nexus_signal_tier | 1 | -0.0092 | 20637 | 0.0131 | within null/no edge |
| nexus_delta_slope Δ | 10 | -0.0088 | 6648 | 0.0230 | within null/no edge |
| NFE Oscillator Δ | 10 | -0.0074 | 20628 | 0.0111 | within null/no edge |
| nexus_regime_score | 20 | 0.0074 | 20618 | 0.0128 | within null/no edge |
| nexus_osc_momentum | 3 | -0.0072 | 20635 | 0.0136 | within null/no edge |
| nexus_bar_delta_ratio Δ | 5 | 0.0069 | 6662 | 0.0228 | within null/no edge |
| nexus_fp_total_volume | 10 | -0.0067 | 6658 | 0.0233 | within null/no edge |
| NFE Oscillator Δ | 1 | -0.0062 | 20637 | 0.0129 | within null/no edge |
| nexus_osc_momentum | 1 | -0.0052 | 20637 | 0.0123 | within null/no edge |

## 7. Volume Expansion Precursor Diagnostics
| Pre-event | Expansions | Events | Expansion coverage ≤12b | Median lead bars | Event precision | Random mean | Random p95 | False-positive rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| delta_dir_nonzero | 1067 | 2639 | 90.25% | 1.00 | 44.07% | 45.18% | 46.49% | 55.93% |
| gasout_any | 1067 | 1224 | 84.82% | 3.00 | 46.57% | 45.20% | 47.14% | 53.43% |
| signal_tier_nonzero | 1067 | 540 | 67.95% | 4.00 | 50.74% | 45.27% | 48.71% | 49.26% |
| divergence_confirmed_any | 1067 | 75 | 14.25% | 5.00 | 44.00% | 45.00% | 56.00% | 56.00% |
| divergence_raw_any | 1067 | 1122 | 49.02% | 5.00 | 13.37% | 45.22% | 47.42% | 86.63% |
| abs_delta_slope_top_quartile | 1067 | 1665 | 85.10% | 2.00 | 44.74% | 45.21% | 46.97% | 55.26% |
| vf_calc_extreme | 1067 | 1907 | 72.63% | 2.00 | 31.57% | 45.18% | 46.67% | 68.43% |

## 8. Regime Breakdown
| Regime | Event | Bars | Events | Event rate | H3 mean | H3 hit | H10 mean | H10 hit |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| contraction_chop | any_signal | 2638 | 20 | 0.76% | 0.201 | 30.00% | 0.974 | 55.00% |
| neutral | any_signal | 11222 | 278 | 2.48% | -0.037 | 49.64% | -0.029 | 46.04% |
| quiet_trend | any_signal | 2417 | 25 | 1.03% | -0.100 | 60.00% | -0.696 | 48.00% |
| trend_expansion | any_signal | 2363 | 163 | 6.90% | 0.076 | 51.53% | 0.235 | 51.53% |
| volatile_chop | any_signal | 2011 | 54 | 2.69% | -0.103 | 42.59% | -0.157 | 40.74% |
| contraction_chop | confirmed_div_any | 2638 | 5 | 0.19% | -0.914 | 40.00% | -1.151 | 40.00% |
| neutral | confirmed_div_any | 11222 | 37 | 0.33% | -0.140 | 45.95% | -0.218 | 40.54% |
| quiet_trend | confirmed_div_any | 2417 | 5 | 0.21% | 0.365 | 60.00% | -0.279 | 20.00% |
| trend_expansion | confirmed_div_any | 2363 | 17 | 0.72% | 0.248 | 52.94% | 0.516 | 76.47% |
| volatile_chop | confirmed_div_any | 2011 | 11 | 0.55% | -0.639 | 9.09% | -0.334 | 36.36% |

## 9. Settings / Training Implications
| Area | Classification | Evidence |
| --- | --- | --- |
| Effective pivot lag | material lag driver | nexus_pivot_span is constant 4 bars on this export, so divergence labels confirm 4 bars after the actual pivot (60 minutes on 15m). |
| Raw divergence vs confirmed divergence filters | material and very restrictive | Raw divergence counts are hundreds; confirmed counts are 12/14/29/20 depending on type. |
| Volume/footprint confirmation | material | fp_quality covers 6,659 bars; confirmed divergence requires footprint-confirmed flow. |
| Regime score | material diagnostic | Regime score exports 0-4 and should be used for false-signal stratification. |
| Oscillator momentum / VF calc | material diagnostic | Both export continuously and should be used to identify signal lag and bad-state filters. |
| Cosmetic settings | not train target | Theme/color/fill/watermark do not affect exported evidence state. |

## 10. Findings
- Raw divergence fires often (`1122` any-type raw bars), but confirmed divergence is sparse (`75` any-type confirmed bars). This confirms the filter stack is highly restrictive.
- Pivot lag is confirmed and large enough to matter: `4` bars / `60` minutes. Training must model confirmation-bar lag explicitly.
- Best volume-expansion precursor by precision in this pass: `signal_tier_nonzero` with `50.74%` precision vs random mean `45.27%`.
- Direct forward-return IC remains weak; the stronger target candidates remain volume-expansion lead, pivot-proximity, and regime-conditioned exhaustion/divergence, not immediate directional return alone.
- The next build should not try to optimize every setting at once. It should freeze most settings and tune one family at a time: footprint quality → delta/gas-out → divergence filters → oscillator/signal lengths → regime thresholds.

## 11. Next Sequential Step
Build the isolated Nexus 15m dataset/manifest from this expanded export, then run a pre-training label audit. Do not train until the label audit reports class counts, leakage exclusions, time split boundaries, and feature availability by footprint-quality subset.
