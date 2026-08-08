"""Compare what a utility asked for in a FERC Section 205 rate case to what it
actually received.

FERC rate changes reach the Commission through two different procedural
doors, and they pull in opposite directions:

- **Section 205** -- the utility itself files to change its own rate
  (almost always an *increase* ask).
- **Section 206** -- a customer, state commission, or FERC itself complains
  that an existing rate is unjust/unreasonable (almost always a *decrease*
  ask).

`data/ferc_roe_data.csv` (built for ferc_roe_analysis.py) already records
`requested_roe_pct` / `requested_by` for every litigated ROE row, and a
`section` column (205/206) derived from `requested_by`: a utility's own ask
is a Section 205 filing, a customer's ask is a Section 206 complaint. This
script isolates the Section 205 rows -- utility asked, FERC decided (or
hasn't yet) -- and reports the gap between ask and outcome, plus anything
else FERC disallowed in that case beyond the ROE number itself
(`disallowed_items`, e.g. a denied rate adder).

See README.md for full sourcing/scope notes; this script adds no new data,
it just re-slices ferc_roe_data.csv along the 205/206 line.
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from ferc_roe_analysis import DATA_PATH, TRACK_LABELS, load_data

OUTPUT_PATH = "output/ferc_205_ask_vs_received.png"


def section_205_cases(df: pd.DataFrame) -> pd.DataFrame:
    """Utility-initiated (Section 205) rate filings: what the utility asked
    for (requested_roe_pct) vs. what FERC granted (base_roe_pct, blank if
    the case is still pending)."""
    cases = df[df["section"] == 205].copy()
    cases["granted_roe_pct"] = cases["base_roe_pct"]
    cases["gap_pct_points"] = cases["granted_roe_pct"] - cases["requested_roe_pct"]
    cases["pct_of_ask_granted"] = cases["granted_roe_pct"] / cases["requested_roe_pct"] * 100
    return cases.sort_values("decision_date")


def summarize(cases: pd.DataFrame) -> None:
    print("FERC Section 205 Rate Cases: Utility Ask vs. What FERC Granted")
    print("=" * 64)
    if cases.empty:
        print("No Section 205 rows found in the dataset.")
        return

    for _, r in cases.iterrows():
        track_label = TRACK_LABELS.get(r["case_track"], r["case_track"])
        print(f"\n{track_label} -- {r['docket_opinion']}")
        print(f"  Filed/decided: {r['decision_date'].date()}")
        print(f"  Utility asked for: {r['requested_roe_pct']:.2f}%")
        if pd.notna(r["granted_roe_pct"]):
            print(
                f"  FERC granted:       {r['granted_roe_pct']:.2f}% "
                f"({r['gap_pct_points']:+.2f} pct pts, "
                f"{r['pct_of_ask_granted']:.0f}% of the ask)"
            )
        else:
            print("  FERC granted:       pending -- no decision yet")
        if pd.notna(r["disallowed_items"]):
            print(f"  Also disallowed:    {r['disallowed_items']}")

    decided = cases.dropna(subset=["granted_roe_pct"])
    if not decided.empty:
        avg_gap = decided["gap_pct_points"].mean()
        avg_pct = decided["pct_of_ask_granted"].mean()
        print(f"\n-> Across {len(decided)} decided Section 205 case(s): "
              f"avg gap {avg_gap:+.2f} pct pts, "
              f"utilities received {avg_pct:.0f}% of their ask on average.")
    pending = cases[cases["granted_roe_pct"].isna()]
    if not pending.empty:
        print(f"-> {len(pending)} Section 205 case(s) still pending, not counted above.")


def plot_ask_vs_received(cases: pd.DataFrame, output_path: str = OUTPUT_PATH) -> None:
    decided = cases.dropna(subset=["granted_roe_pct"])
    pending = cases[cases["granted_roe_pct"].isna()]
    if cases.empty:
        return

    fig, ax = plt.subplots(figsize=(8, 0.9 * len(cases) + 1.5))
    labels = [f"{TRACK_LABELS.get(r['case_track'], r['case_track'])}\n{r['short_label']}"
              for _, r in cases.iterrows()]
    y_pos = range(len(cases))

    for i, (_, r) in enumerate(cases.iterrows()):
        ask = r["requested_roe_pct"]
        granted = r["granted_roe_pct"]
        if pd.notna(granted):
            ax.plot([granted, ask], [i, i], color="#999999", linewidth=1.5, zorder=1)
            ax.scatter([granted], [i], color="#1f77b4", s=90, zorder=3, label="FERC granted" if i == 0 else None)
        else:
            ax.scatter([], [])  # keep legend ordering stable
        ax.scatter([ask], [i], facecolors="none", edgecolors="#d62728", marker="o",
                   s=90, linewidths=1.6, zorder=3,
                   label="Utility asked for" if i == 0 else None)
        if pd.isna(granted):
            ax.annotate("pending", (ask, i), textcoords="offset points",
                        xytext=(8, 0), fontsize=8, color="#d62728", va="center")
        elif pd.notna(r["disallowed_items"]):
            ax.annotate(f"also disallowed: {r['disallowed_items']}", (granted, i),
                        textcoords="offset points", xytext=(0, -14), fontsize=7,
                        color="#555555", ha="center", va="top", style="italic")

    ax.set_yticks(list(y_pos))
    ax.set_yticklabels(labels, fontsize=8.5)
    ax.invert_yaxis()
    ax.set_xlabel("Base ROE (%)")
    ax.set_title("FERC Section 205 Rate Cases:\nUtility Ask vs. What FERC Granted")
    ax.legend(loc="lower right", fontsize=8.5)
    ax.grid(True, axis="x", alpha=0.3)
    fig.tight_layout()
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    fig.savefig(output_path, dpi=150)
    print(f"\nSaved chart to {output_path}")


def main() -> None:
    df = load_data(DATA_PATH)
    cases = section_205_cases(df)
    summarize(cases)
    plot_ask_vs_received(cases)


if __name__ == "__main__":
    main()
