# Feature Catalog Contract

**Date:** 2026-04-26
**Status:** Active

## Purpose

Defines which fields are admitted into active modeling.

## Active Feature Rule

A feature is admitted only if it is present in, or deterministically derived
from, the manifest-backed source data used for the run.

Allowed feature families:

- Pine input settings
- Pine state-machine fields
- Pine `ml_*` hidden exports
- Strategy Tester trade fields
- OHLCV fields included in the TradingView export
- Databento ES 5m/15m market-data rows when the manifest identifies Databento as
  the source/capture kind
- deterministic transformations of the same approved source data

Approved under local-first data policy (2026-05-28):

- FRED, macro, news, options, and cross-asset data when manifest-backed

Disallowed feature families:

- Supabase runtime ingestion tables
- Databento rows mislabeled as TradingView/Pine indicator exports
- local `ag_training` columns
- Python reconstructed fib features not emitted by Pine

## Point-In-Time Rule

Every modeling column must declare:

- source export or data file
- source column
- whether it is a raw Pine field, Databento market-data field, or deterministic
  derived field
- timestamp / trade identity
- whether it is available before the label being modeled

If point-in-time validity cannot be proven from the source data, the field is
not admitted.
