"""Analyze how FERC has set electric transmission return on equity (ROE) over time.

Data covers base-ROE history across five RTO/ISO footprints -- NETO (New England),
MISO, SPP, PJM, and CAISO (PG&E). NETO, MISO, and the SPP-AEP track are litigated,
RTO/utility-wide base-ROE case histories (data_type=decision) that trended down from
settlement-era levels around 11-12.5% to composite DCF/CAPM levels around 9.5-10%.
PJM and the broader SPP footprint have no single RTO-wide base ROE -- each
transmission owner sets its own via an individual formula rate -- so those are
represented as point-in-time cross-company ranges (data_type=snapshot_range) rather
than a trend line. See data/ferc_roe_data.csv for sourcing and README.md for scope
and limitations.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

DATA_PATH = "data/ferc_roe_data.csv"
OUTPUT_PATH = "output/ferc_roe_timeline.png"

TRACK_COLORS = {
    "NETO": "#1f77b4",
    "MISO": "#d62728",
    "SPP-AEP": "#2ca02c",
    "SPP-ALL": "#17becf",
    "PJM": "#9467bd",
    "CAISO-PGE": "#ff7f0e",
}
TRACK_LABELS = {
    "NETO": "New England Transmission Owners",
    "MISO": "MISO Transmission Owners",
    "SPP-AEP": "SPP - AEP subsidiaries",
    "SPP-ALL": "SPP - all TOs (range)",
    "PJM": "PJM TOs (range)",
    "CAISO-PGE": "CAISO - PG&E",
}


def load_data(path: str = DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["decision_date", "effective_date"])
    df["decision_year"] = df["decision_date"].dt.year
    return df


def summarize(df: pd.DataFrame) -> None:
    cases = df[df["case_track"].isin(TRACK_COLORS)].sort_values("decision_date")
    print("FERC Base ROE Decisions by Case Track\n" + "=" * 40)
    for track, label in TRACK_LABELS.items():
        rows = cases[cases["case_track"] == track]
        if rows.empty:
            continue
        print(f"\n{label} ({track}):")
        for _, r in rows.iterrows():
            roe = f"{r.base_roe_pct:.2f}%" if pd.notna(r.base_roe_pct) else "n/a"
            zone = (
                f" [range {r.zone_low_pct:.2f}%-{r.zone_high_pct:.2f}%]"
                if pd.notna(r.zone_low_pct)
                else ""
            )
            print(
                f"  {r.decision_date.date()}  {r.docket_opinion:55s} "
                f"ROE={roe}{zone}"
            )
        decisions = rows[rows["data_type"] == "decision"].dropna(subset=["base_roe_pct"])
        if len(decisions) >= 2:
            first, last = decisions.iloc[0], decisions.iloc[-1]
            change = last.base_roe_pct - first.base_roe_pct
            print(
                f"  -> Net change {first.decision_year}-{last.decision_year}: "
                f"{change:+.2f} percentage points"
            )
        elif rows.iloc[0]["data_type"] == "snapshot_range":
            print("  -> No single RTO-wide base ROE; figures are set company-by-company.")


def plot_timeline(df: pd.DataFrame, output_path: str = OUTPUT_PATH) -> None:
    fig, ax = plt.subplots(figsize=(11, 6.5))

    for track, color in TRACK_COLORS.items():
        rows = df[df["case_track"] == track].sort_values("decision_date")
        if rows.empty:
            continue
        is_snapshot = (rows["data_type"] == "snapshot_range").all()

        # Snapshot rows have no single base_roe_pct -- plot the range midpoint
        # as a marker instead of drawing a (misleading) trend line through it.
        y = rows["base_roe_pct"].fillna(
            (rows["zone_low_pct"] + rows["zone_high_pct"]) / 2
        )
        ax.plot(
            rows["decision_date"], y,
            marker="s" if is_snapshot else "o",
            linestyle="none" if is_snapshot else "-",
            color=color, label=TRACK_LABELS[track], linewidth=2, markersize=7,
        )

        has_zone = rows["zone_low_pct"].notna()
        if has_zone.any():
            zr = rows[has_zone]
            zy = y[has_zone]
            ax.errorbar(
                zr["decision_date"], zy,
                yerr=[zy - zr["zone_low_pct"], zr["zone_high_pct"] - zy],
                fmt="none", ecolor=color, alpha=0.35, capsize=4,
            )

        for i, ((_, r), yy) in enumerate(zip(rows.iterrows(), y)):
            y_offset = 9 if i % 2 == 0 else -13
            ax.annotate(
                r["short_label"],
                (r["decision_date"], yy),
                textcoords="offset points", xytext=(6, y_offset), fontsize=7.5,
                color=color, bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                                        edgecolor="none", alpha=0.75),
            )

    ax.set_title("FERC Base Return on Equity Over Time\n(Electric Transmission Owners)")
    ax.set_xlabel("Decision date")
    ax.set_ylabel("Base ROE (%)")
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), fontsize=9, borderaxespad=0)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    print(f"\nSaved chart to {output_path}")


def main() -> None:
    df = load_data()
    summarize(df)
    plot_timeline(df)


if __name__ == "__main__":
    main()
