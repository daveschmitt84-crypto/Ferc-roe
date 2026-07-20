"""Analyze how FERC has set electric transmission return on equity (ROE) over time.

Data covers the two most heavily litigated FERC base-ROE tracks -- the New England
Transmission Owners (NETO) and MISO Transmission Owners cases -- which together span
2002-2026 and illustrate FERC's shift from settlement-based ROEs in the ~11-12% range
to composite DCF/CAPM-based ROEs around 9.5-10%. See data/ferc_roe_data.csv for
sourcing and README.md for scope/limitations.
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
}
TRACK_LABELS = {
    "NETO": "New England Transmission Owners",
    "MISO": "MISO Transmission Owners",
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
        print(f"\n{label} ({track}):")
        for _, r in rows.iterrows():
            zone = (
                f" [zone {r.zone_low_pct:.2f}%-{r.zone_high_pct:.2f}%]"
                if pd.notna(r.zone_low_pct)
                else ""
            )
            print(
                f"  {r.decision_date.date()}  {r.docket_opinion:55s} "
                f"ROE={r.base_roe_pct:.2f}%{zone}"
            )
        first, last = rows.iloc[0], rows.iloc[-1]
        change = last.base_roe_pct - first.base_roe_pct
        print(
            f"  -> Net change {first.decision_year}-{last.decision_year}: "
            f"{change:+.2f} percentage points"
        )


def plot_timeline(df: pd.DataFrame, output_path: str = OUTPUT_PATH) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))

    for track, color in TRACK_COLORS.items():
        rows = df[df["case_track"] == track].sort_values("decision_date")
        ax.plot(
            rows["decision_date"], rows["base_roe_pct"],
            marker="o", color=color, label=TRACK_LABELS[track], linewidth=2,
        )
        has_zone = rows["zone_low_pct"].notna()
        if has_zone.any():
            zr = rows[has_zone]
            ax.errorbar(
                zr["decision_date"], zr["base_roe_pct"],
                yerr=[zr["base_roe_pct"] - zr["zone_low_pct"],
                      zr["zone_high_pct"] - zr["base_roe_pct"]],
                fmt="none", ecolor=color, alpha=0.35, capsize=4,
            )
        for _, r in rows.iterrows():
            ax.annotate(
                r["docket_opinion"].split("(")[0].strip(),
                (r["decision_date"], r["base_roe_pct"]),
                textcoords="offset points", xytext=(6, 6), fontsize=7, color=color,
            )

    ax.set_title("FERC Base Return on Equity Over Time\n(Electric Transmission Owners)")
    ax.set_xlabel("Decision date")
    ax.set_ylabel("Base ROE (%)")
    ax.legend(loc="upper right")
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
