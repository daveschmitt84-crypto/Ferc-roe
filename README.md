# FERC Return on Equity (ROE) Analysis

Analyzes how the Federal Energy Regulatory Commission (FERC) has set the base
return on equity (ROE) for electric transmission owners over time.

## Why this scope

FERC does not publish a single, clean "ROE over the years" time series. ROE is
litigated case-by-case under Federal Power Act Section 205/206, docket by
docket, utility by utility -- and different RTOs/ISOs use fundamentally
different structures for setting it. This project tracks two kinds of history:

**RTO-wide litigated base-ROE tracks** (`data_type=decision`) -- a single base
ROE applies to (nearly) all transmission owners in the footprint, and FERC has
revised it through a chain of Section 206 complaints and opinions:

- **NETO** -- New England Transmission Owners (Docket EL11-66 and related)
- **MISO** -- Midcontinent ISO Transmission Owners (Docket EL14-12 / EL15-45)
- **SPP-AEP** -- AEP's four SPP-zone transmission subsidiaries (Docket
  ER20-928 lineage); the only comparable RTO-wide-style track available for SPP
- **CAISO-PGE** -- Pacific Gas & Electric's CAISO transmission rate case
  (Docket ER19-13 lineage)
- **SOUTHERN** -- Southern Company's traditional operating companies (Alabama
  Power, Georgia Power, Gulf Power, Mississippi Power), Docket ER19-1427
  lineage. Southern Company is **not** in an RTO/ISO for its transmission
  function (it runs its own balancing authority footprint), making this the
  clearest non-RTO example found with a documented before/after base ROE.

Together these span 2002-2026 and capture the core story: FERC's shift from
settlement-based ROEs in the 11-13% range toward composite DCF/CAPM-derived
ROEs around 9.3-10%, driven by a series of D.C. Circuit remands (notably
*Emera Maine v. FERC*) that forced FERC to repeatedly revise its methodology.
Across every litigated track, FERC's outcome consistently lands well short of
what complainants asked for and well below what utilities were defending or
requesting -- e.g. PG&E asked for 13.3% and got 9.3%; MISO customers asked
for 9.15% and got 10.32%-9.98% across three re-decisions. NETOs are currently
asking FERC to reverse course entirely: after Opinion No. 594 cut their ROE
to 9.57% in March 2026, they filed weeks later to raise it to 11.39%
(`data_type=pending`, unresolved as of this dataset's compilation).

**Cross-company range snapshots** (`data_type=snapshot_range`) -- PJM and SPP
overall have **no single RTO-wide base ROE**. Each transmission owner sets its
own ROE through its own individual formula rate, so there is no trend line to
draw; instead these rows record a point-in-time range across companies:

- **PJM** -- ~26 transmission owners, base ROEs ranging 9.80% (MAIT) to 11.20%
  (TrAILCo) as of ~2025, plus a common 50 bp RTO-participation adder and
  project-specific adders (25-150 bp) at 10 companies
- **SPP-ALL** -- ~14 transmission owners, base ROEs ranging 9.72% (Xcel's
  PSCo) to 10.80% (Prairie Wind Transmission) as of 2020, unchanged since

CAISO is structurally similar to PJM/SPP (its three participating transmission
owners -- PG&E, SCE, SDG&E -- are rate-regulated individually, not via one
CAISO-wide ROE); PG&E is included as one well-documented example, not a
CAISO-wide figure. SCE's requested/settled ROE figures were excluded here
because they bundle in incentive adders (e.g. wildfire risk) that aren't
comparable to the "base ROE" figures used elsewhere in this dataset.

A generic 2020 policy statement on natural gas/oil pipeline ROE methodology is
included for context but has no numeric ROE (it governs *how* ROE is
calculated in individual pipeline cases, not a specific rate).

**Other non-RTO utilities** (Duke Energy Carolinas/Progress, PacifiCorp, NV
Energy, Puget Sound Energy, etc.) were researched but not included: their
transmission ROEs are set through individual formula-rate settlements that
rarely produce the kind of public, dated, docket-attributable figure this
dataset requires, and the only Duke Energy ROE figures found in public
reporting were state-jurisdictional *retail* ROEs (North Carolina Utilities
Commission rate cases) -- a different rate base than FERC transmission ROE,
so they were deliberately excluded rather than conflated. If you have a
specific non-RTO utility/docket in mind, add a row per the instructions below.

## RTO vs. non-RTO average

The script computes each footprint's *current* (most recently settled) base
ROE, then averages those across the RTO tracks (ISO-NE, MISO, SPP, PJM,
CAISO) and separately for the non-RTO track (Southern Company), plotted as
two dashed reference lines. SPP-AEP and SPP-ALL are collapsed into one "SPP"
figure first so SPP doesn't count twice against the single-footprint NETO,
MISO, PJM, and CAISO entries. As of this dataset: RTO footprints average
**9.90%**, non-RTO (Southern Company alone) is **10.60%**.

Treat the non-RTO side as a single data point, not a statistical average --
Southern Company is the only non-RTO utility with a documented, dated,
docket-attributable base ROE in this dataset (see below). A real "non-RTO
average" would need several more non-RTO utilities.

## Data

`data/ferc_roe_data.csv` -- each row is one FERC decision setting or revising
a base ROE, with:

- `decision_date` / `effective_date` (FERC has repeatedly applied ROE
  decisions retroactively, sometimes by over a decade -- both dates matter)
- `base_roe_pct` -- what FERC actually granted, and where FERC published one,
  the `zone_low_pct` / `zone_high_pct` composite zone of reasonableness
- `requested_roe_pct` / `requested_by` -- what was actually asked for, and by
  whom (`customers` for a complainant seeking a cut, `utility` for a utility
  seeking an increase), that led to (or, for `data_type=pending`, is still
  awaiting) that row's decision. Charted as a hollow marker connected to the
  granted value by a dotted line, so you can see how far FERC's outcome
  landed from each side's opening position. Left blank for baseline rows (no
  complaint was pending) and for snapshot/policy rows (no single complaint to
  point to).
- `data_type` -- `decision` (a FERC-decided base ROE), `pending` (a filed
  request with no outcome yet -- e.g. NETOs' April 2026 bid to raise their
  ROE to 11.39%, still unresolved as of this dataset's compilation),
  `snapshot_range` (a cross-company range, no single ROE), or `policy` (a
  methodology statement, no numeric ROE)
- `section` -- which Federal Power Act provision put the row's number in
  front of FERC: `205` when the utility itself filed to change its own rate
  (`requested_by=utility`, almost always an ask for *more*), `206` when a
  customer/complainant challenged an existing rate (`requested_by=customer`,
  almost always an ask for *less*). Blank for baseline rows, snapshot
  ranges, and the policy statement, which have no single filer to attribute.
- `methodology` and `notes` summarizing the case
- `source_url` for verification

All figures were checked against news coverage and FERC-adjacent legal
publications (Utility Dive, RTO Insider, law firm client alerts, FERC.gov)
during research for this project -- see the `source_url` column. For
authoritative text, pull the underlying opinion from FERC eLibrary using the
docket/opinion number.

**This is a curated subset, not an exhaustive record.** FERC issues ROE
decisions for individual gas pipelines, oil pipelines, and dozens of
individual transmission owners within PJM, SPP, and CAISO that are not
included here. To extend:

1. Add a row to `data/ferc_roe_data.csv` with the same columns. Set
   `data_type` to `decision` for a numeric base ROE at a point in time, or
   `snapshot_range` if you only have a cross-company range (leave
   `base_roe_pct` blank and fill `zone_low_pct`/`zone_high_pct`).
2. Use `case_track` values consistently (add a new track name for a new
   RTO/utility/pipeline case family) and give it a `short_label` per row --
   the plot picks up new tracks automatically once added to `TRACK_COLORS`/
   `TRACK_LABELS` in `ferc_roe_analysis.py`.

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

### Section 205: what the utility asked for vs. what it got

```bash
python3 ferc_205_analysis.py
```

Slices the same dataset down to Section 205 rows only (`section=205`) --
cases where the utility itself filed to raise its own rate, as opposed to a
customer complaint (Section 206) seeking a cut. For each, it reports the
utility's ask, FERC's decision (or "pending" if undecided), the gap in
percentage points, and what share of the ask FERC granted, then plots them
as an ask-vs-granted chart to `output/ferc_205_ask_vs_received.png`. As of
this dataset, there are two Section 205 rows: PG&E asked for 13.30% and got
9.30% (Docket ER19-13), and NETOs' April 2026 filing asking for 11.39% is
still pending. This is a thin sample -- extend it the same way as the rest
of the dataset (add a row with `section=205` and both
`requested_roe_pct`/`base_roe_pct` filled in) as more utility-initiated
cases are documented.
