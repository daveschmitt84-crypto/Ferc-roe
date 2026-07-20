# FERC Return on Equity (ROE) Analysis

Analyzes how the Federal Energy Regulatory Commission (FERC) has set the base
return on equity (ROE) for electric transmission owners over time.

## Why this scope

FERC does not publish a single, clean "ROE over the years" time series. ROE is
litigated case-by-case under Federal Power Act Section 205/206, docket by
docket, utility by utility. Rather than approximate a broad multi-decade
average (which would require guessing at figures), this project tracks the
**two most heavily litigated and best-documented base-ROE case histories**:

- **NETO** -- New England Transmission Owners (Docket EL11-66 and related)
- **MISO** -- Midcontinent ISO Transmission Owners (Docket EL14-12 / EL15-45)

Together these span 2002-2026 and capture the core story: FERC's shift from
settlement-based ROEs in the 11-12.5% range toward composite DCF/CAPM-derived
ROEs around 9.5-10%, driven by a series of D.C. Circuit remands (notably
*Emera Maine v. FERC*) that forced FERC to repeatedly revise its methodology.

A generic 2020 policy statement on natural gas/oil pipeline ROE methodology is
included for context but has no numeric ROE (it governs *how* ROE is
calculated in individual pipeline cases, not a specific rate).

## Data

`data/ferc_roe_data.csv` -- each row is one FERC decision setting or revising
a base ROE, with:

- `decision_date` / `effective_date` (FERC has repeatedly applied ROE
  decisions retroactively, sometimes by over a decade -- both dates matter)
- `base_roe_pct` and, where FERC published one, the `zone_low_pct` /
  `zone_high_pct` composite zone of reasonableness
- `methodology` and `notes` summarizing the case
- `source_url` for verification

All figures were checked against news coverage and FERC-adjacent legal
publications (Utility Dive, RTO Insider, law firm client alerts, FERC.gov)
during research for this project -- see the `source_url` column. For
authoritative text, pull the underlying opinion from FERC eLibrary using the
docket/opinion number.

**This is a curated subset, not an exhaustive record.** FERC issues ROE
decisions for individual gas pipelines, oil pipelines, and other RTOs/ISOs
(PJM, SPP, CAISO) that are not included here. To extend:

1. Add a row to `data/ferc_roe_data.csv` with the same columns.
2. Use `case_track` values consistently (add a new track name for a new
   RTO/pipeline case family) so the plot picks it up automatically.

For research-grade completeness across all dockets, supplement with FERC
eLibrary, S&P Global Market Intelligence (SNL), or Regulatory Research
Associates (RRA) ROE trackers.

## Usage

```bash
pip install -r requirements.txt
python3 ferc_roe_analysis.py
```

This prints a summary of each case track's decisions and writes a timeline
chart to `output/ferc_roe_timeline.png`.
