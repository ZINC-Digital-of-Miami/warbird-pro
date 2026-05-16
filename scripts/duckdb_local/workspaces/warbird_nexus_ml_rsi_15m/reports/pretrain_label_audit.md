# Nexus 15m Pre-Training Label Audit — 2026-05-15
## Source And Scope
- Source CSV: `/Users/zincdigital/Downloads/CME_MINI_MES1!, 15_d464a.csv`
- Source SHA256: `560a0da03115be6c689a61c7bb5cdea861e16174a6a115efb65c25f745b351d7`
- Dataset parquet: `/Volumes/Satechi Hub/warbird-pro/scripts/duckdb_local/workspaces/warbird_nexus_ml_rsi_15m/exports/nexus_15m_dataset.parquet`
- Trigger family: `NEXUS_FOOTPRINT_DELTA`
- Scope: Nexus-only 15m dataset. No V9 Pine/trainer/export/model files are touched.

## Dataset Validation
- `row_count`: `20651`
- `date_start`: `2025-06-30T22:00:00+00:00`
- `date_end`: `2026-05-15T12:15:00+00:00`
- `duplicate_timestamps`: `0`
- `interval_900s_count`: `20423`
- `non_900s_gap_count`: `227`
- `largest_gap_minutes`: `3420.0`
- `nexus_mode_minutes`: `[15.0]`
- `fp_available_rows`: `6668`
- `fp_quality_rows`: `6659`
- `fp_quality_ratio`: `0.3224541184446274`
- `pivot_span_values`: `[4.0]`

## Chronological Split Plan
- Embargo bars: `21`
| Split | Rows | FP quality rows | Date start | Date end |
| --- | ---: | ---: | --- | --- |
| not_footprint_quality | 13992 | 0 | 2025-06-30T22:00:00+00:00 | 2026-02-03T15:45:00+00:00 |
| train | 4661 | 4661 | 2026-02-03T16:00:00+00:00 | 2026-04-15T18:45:00+00:00 |
| embargo_train_val | 21 | 21 | 2026-04-15T19:00:00+00:00 | 2026-04-16T01:00:00+00:00 |
| validation | 978 | 978 | 2026-04-16T01:15:00+00:00 | 2026-04-30T15:30:00+00:00 |
| embargo_val_test | 21 | 21 | 2026-04-30T15:45:00+00:00 | 2026-04-30T20:45:00+00:00 |
| test | 978 | 978 | 2026-04-30T22:00:00+00:00 | 2026-05-15T12:15:00+00:00 |

## Label Counts
### `label_dir_1b`
| Class/value | Rows |
| --- | ---: |
| down_0p5atr | 3682 |
| flat | 13059 |
| up_0p5atr | 3896 |
| <NA> | 14 |
### `label_abs_move_ge_0p5atr_1b`
| Class/value | Rows |
| --- | ---: |
| 0 | 13059 |
| 1 | 7578 |
| <NA> | 14 |
### `label_abs_move_ge_1p0atr_1b`
| Class/value | Rows |
| --- | ---: |
| 0 | 18131 |
| 1 | 2506 |
| <NA> | 14 |
### `label_dir_3b`
| Class/value | Rows |
| --- | ---: |
| down_0p5atr | 5795 |
| flat | 8362 |
| up_0p5atr | 6478 |
| <NA> | 16 |
### `label_abs_move_ge_0p5atr_3b`
| Class/value | Rows |
| --- | ---: |
| 0 | 8362 |
| 1 | 12273 |
| <NA> | 16 |
### `label_abs_move_ge_1p0atr_3b`
| Class/value | Rows |
| --- | ---: |
| 0 | 14048 |
| 1 | 6587 |
| <NA> | 16 |
### `label_dir_5b`
| Class/value | Rows |
| --- | ---: |
| down_0p5atr | 6538 |
| flat | 6607 |
| up_0p5atr | 7488 |
| <NA> | 18 |
### `label_abs_move_ge_0p5atr_5b`
| Class/value | Rows |
| --- | ---: |
| 0 | 6607 |
| 1 | 14026 |
| <NA> | 18 |
### `label_abs_move_ge_1p0atr_5b`
| Class/value | Rows |
| --- | ---: |
| 0 | 11707 |
| 1 | 8926 |
| <NA> | 18 |
### `label_dir_10b`
| Class/value | Rows |
| --- | ---: |
| down_0p5atr | 7309 |
| flat | 4534 |
| up_0p5atr | 8785 |
| <NA> | 23 |
### `label_abs_move_ge_0p5atr_10b`
| Class/value | Rows |
| --- | ---: |
| 0 | 4534 |
| 1 | 16094 |
| <NA> | 23 |
### `label_abs_move_ge_1p0atr_10b`
| Class/value | Rows |
| --- | ---: |
| 0 | 8638 |
| 1 | 11990 |
| <NA> | 23 |
### `label_dir_20b`
| Class/value | Rows |
| --- | ---: |
| down_0p5atr | 7789 |
| flat | 3112 |
| up_0p5atr | 9717 |
| <NA> | 33 |
### `label_abs_move_ge_0p5atr_20b`
| Class/value | Rows |
| --- | ---: |
| 0 | 3112 |
| 1 | 17506 |
| <NA> | 33 |
### `label_abs_move_ge_1p0atr_20b`
| Class/value | Rows |
| --- | ---: |
| 0 | 6083 |
| 1 | 14535 |
| <NA> | 33 |
### `label_volume_expansion_next_12b`
| Class/value | Rows |
| --- | ---: |
| 0 | 17724 |
| 1 | 2915 |
| <NA> | 12 |
### `label_swing_low_next_12b`
| Class/value | Rows |
| --- | ---: |
| 0 | 3989 |
| 1 | 16650 |
| <NA> | 12 |
### `label_swing_high_next_12b`
| Class/value | Rows |
| --- | ---: |
| 0 | 4634 |
| 1 | 16005 |
| <NA> | 12 |

## Leakage Exclusions
These columns are excluded from feature training inputs because they are timestamps, future-looking labels/returns, split metadata, or event labels.

- `event_swing_high`
- `event_swing_low`
- `event_volume_expansion`
- `fwd_ret_1`
- `fwd_ret_10`
- `fwd_ret_20`
- `fwd_ret_3`
- `fwd_ret_5`
- `fwd_ret_atr_1`
- `fwd_ret_atr_10`
- `fwd_ret_atr_20`
- `fwd_ret_atr_3`
- `fwd_ret_atr_5`
- `label_abs_move_ge_0p5atr_10b`
- `label_abs_move_ge_0p5atr_1b`
- `label_abs_move_ge_0p5atr_20b`
- `label_abs_move_ge_0p5atr_3b`
- `label_abs_move_ge_0p5atr_5b`
- `label_abs_move_ge_1p0atr_10b`
- `label_abs_move_ge_1p0atr_1b`
- `label_abs_move_ge_1p0atr_20b`
- `label_abs_move_ge_1p0atr_3b`
- `label_abs_move_ge_1p0atr_5b`
- `label_dir_10b`
- `label_dir_1b`
- `label_dir_20b`
- `label_dir_3b`
- `label_dir_5b`
- `label_swing_high_next_12b`
- `label_swing_low_next_12b`
- `label_volume_expansion_next_12b`
- `split`
- `time`
- `ts`

## Feature Availability Summary
| Feature | Non-null | Non-null % | Non-null on FP quality | FP quality non-null % | Non-zero |
| --- | ---: | ---: | ---: | ---: | ---: |
| open | 20651 | 1.0000 | 6659 | 1.0000 | 20651 |
| high | 20651 | 1.0000 | 6659 | 1.0000 | 20651 |
| low | 20651 | 1.0000 | 6659 | 1.0000 | 20651 |
| close | 20651 | 1.0000 | 6659 | 1.0000 | 20651 |
| nexus_visible_vf_bull | 6668 | 0.3229 | 6659 | 1.0000 | 6668 |
| nexus_visible_vf_bear | 6668 | 0.3229 | 6659 | 1.0000 | 6509 |
| nexus_visible_vf_base | 6668 | 0.3229 | 6659 | 1.0000 | 6668 |
| nexus_visible_nfe_oscillator | 20651 | 1.0000 | 6659 | 1.0000 | 20651 |
| nexus_visible_signal_line | 20651 | 1.0000 | 6659 | 1.0000 | 20651 |
| nexus_visible_tier1_exhaustion | 491 | 0.0238 | 491 | 0.0737 | 414 |
| nexus_visible_delta_gasout | 1224 | 0.0593 | 1224 | 0.1838 | 1128 |
| nexus_visible_tier2_cross | 49 | 0.0024 | 49 | 0.0074 | 49 |
| nexus_visible_momentum_fatigue | 44 | 0.0021 | 44 | 0.0066 | 43 |
| nexus_visible_ob_level | 20651 | 1.0000 | 6659 | 1.0000 | 20651 |
| nexus_visible_midline | 20651 | 1.0000 | 6659 | 1.0000 | 20651 |
| nexus_visible_os_level | 20651 | 1.0000 | 6659 | 1.0000 | 20651 |
| nexus_fp_available | 20651 | 1.0000 | 6659 | 1.0000 | 6668 |
| nexus_fp_quality_ok | 20651 | 1.0000 | 6659 | 1.0000 | 6659 |
| nexus_fp_bar_delta | 6668 | 0.3229 | 6659 | 1.0000 | 6665 |
| nexus_fp_total_volume | 6668 | 0.3229 | 6659 | 1.0000 | 6668 |
| nexus_norm_cum_delta | 6659 | 0.3225 | 6659 | 1.0000 | 6659 |
| nexus_delta_slope | 6659 | 0.3225 | 6659 | 1.0000 | 6654 |
| nexus_bar_delta_ratio | 6668 | 0.3229 | 6659 | 1.0000 | 6665 |
| nexus_delta_dir | 20651 | 1.0000 | 6659 | 1.0000 | 2639 |
| nexus_gasout_bull | 20651 | 1.0000 | 6659 | 1.0000 | 633 |
| nexus_gasout_bear | 20651 | 1.0000 | 6659 | 1.0000 | 591 |
| nexus_mode_minutes | 20651 | 1.0000 | 6659 | 1.0000 | 20651 |
| nexus_signal_tier | 20651 | 1.0000 | 6659 | 1.0000 | 540 |
| nexus_pivot_span | 20651 | 1.0000 | 6659 | 1.0000 | 20651 |
| nexus_regime_score | 20651 | 1.0000 | 6659 | 1.0000 | 18326 |
| nexus_osc_momentum | 20651 | 1.0000 | 6659 | 1.0000 | 20644 |
| nexus_vf_calc | 20651 | 1.0000 | 6659 | 1.0000 | 20492 |
| nexus_div_reg_bull_raw | 20651 | 1.0000 | 6659 | 1.0000 | 255 |
| nexus_div_reg_bear_raw | 20651 | 1.0000 | 6659 | 1.0000 | 294 |
| nexus_div_hid_bull_raw | 20651 | 1.0000 | 6659 | 1.0000 | 314 |
| nexus_div_hid_bear_raw | 20651 | 1.0000 | 6659 | 1.0000 | 260 |
| nexus_div_reg_bull | 20651 | 1.0000 | 6659 | 1.0000 | 12 |
| nexus_div_reg_bear | 20651 | 1.0000 | 6659 | 1.0000 | 14 |
| nexus_div_hid_bull | 20651 | 1.0000 | 6659 | 1.0000 | 29 |
| nexus_div_hid_bear | 20651 | 1.0000 | 6659 | 1.0000 | 20 |
| price_tr | 20651 | 1.0000 | 6659 | 1.0000 | 20651 |
| price_atr14 | 20638 | 0.9994 | 6659 | 1.0000 | 20638 |
| price_er20 | 20631 | 0.9990 | 6659 | 1.0000 | 20504 |
| price_range20_atr | 20632 | 0.9991 | 6659 | 1.0000 | 20632 |
| price_ret_1_atr | 20638 | 0.9994 | 6659 | 1.0000 | 19902 |

## Training Readiness Gate
- `label_volume_expansion_next_12b` is the preferred first heavy-model target because the diagnostics showed mild precursor value and enough positives for chronological splits.
- Pivot-proximity labels are viable secondary targets, but divergence-specific labels are too sparse until confirmed-divergence examples are expanded or modeled as auxiliary features.
- Directional-return labels are available for side models, but direct IC was weak; do not use immediate directional return as the first primary target.
- Next step is a Nexus-only training config using this dataset and these split boundaries; no heavy training has been run by this audit.
