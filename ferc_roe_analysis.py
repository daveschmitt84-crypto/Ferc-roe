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
    "SOUTHERN": "#8c564b",
}
TRACK_LABELS = {
    "NETO": "New England Transmission Owners",
    "MISO": "MISO Transmission Owners",
    "SPP-AEP": "SPP - AEP subsidiaries",
    "SPP-ALL": "SPP - all TOs (range)",
    "PJM": "PJM TOs (range)",
    "CAISO-PGE": "CAISO - PG&E",
    "SOUTHERN": "Southern Company (non-RTO)",
}

# RTO/ISO membership for each track, and the footprint it belongs to. SPP-AEP
# and SPP-ALL are two views of the same footprint (SPP), so they're collapsed
# to one "SPP" figure before averaging -- otherwise SPP would count twice
# toward the RTO average relative to NETO/MISO/PJM/CAISO.
TRACK_RTO_STATUS = {
    "NETO": "RTO", "MISO": "RTO", "SPP-AEP": "RTO", "SPP-ALL": "RTO",
    "PJM": "RTO", "CAISO-PGE": "RTO", "SOUTHERN": "non-RTO",
}
TRACK_FOOTPRINT = {
    "NETO": "ISO-NE", "MISO": "MISO", "SPP-AEP": "SPP", "SPP-ALL": "SPP",
    "PJM": "PJM", "CAISO-PGE": "CAISO", "SOUTHERN": "Southern (non-RTO)",
}


def load_data(path: str = DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["decision_date", "effective_date"])
    df["decision_year"] = df["decision_date"].dt.year
    return df


def current_roe_by_footprint(df: pd.DataFrame) -> pd.DataFrame:
    """Each track's most recent settled ROE (decision or snapshot_range;
    excludes still-pending filings, which have no outcome), collapsed to one
    value per RTO/ISO footprint."""
    settled = df[df["data_type"].isin(["decision", "snapshot_range"])].copy()
    settled["current_value"] = settled["base_roe_pct"].fillna(
        (settled["zone_low_pct"] + settled["zone_high_pct"]) / 2
    )
    latest = (
        settled[settled["case_track"].isin(TRACK_RTO_STATUS)]
        .sort_values("decision_date")
        .groupby("case_track")
        .tail(1)
    )
    latest["footprint"] = latest["case_track"].map(TRACK_FOOTPRINT)
    latest["rto_status"] = latest["case_track"].map(TRACK_RTO_STATUS)
    footprints = latest.groupby(["footprint", "rto_status"])["current_value"].mean().reset_index()
    return footprints


def rto_vs_non_rto_averages(footprints: pd.DataFrame) -> pd.DataFrame:
    return footprints.groupby("rto_status")["current_value"].agg(["mean", "count"])


def summarize(df: pd.DataFrame) -> None:
    cases = df[df["case_track"].isin(TRACK_COLORS)].sort_values("decision_date")
    print("FERC Base ROE Decisions by Case Track\n" + "=" * 40)
    for track, label in TRACK_LABELS.items():
        rows = cases[cases["case_track"] == track]
        if rows.empty:
            continue
        print(f"\n{label} ({track}):")
        for _, r in rows.iterrows():
            if r["data_type"] == "pending":
                roe = "pending (no outcome yet)"
            else:
                roe = f"{r.base_roe_pct:.2f}%" if pd.notna(r.base_roe_pct) else "n/a"
            zone = (
                f" [range {r.zone_low_pct:.2f}%-{r.zone_high_pct:.2f}%]"
                if pd.notna(r.zone_low_pct)
                else ""
            )
            asked = (
                f" ({r.requested_by} sought {r.requested_roe_pct:.2f}%)"
                if pd.notna(r.requested_roe_pct)
                else ""
            )
            print(
                f"  {r.decision_date.date()}  {r.docket_opinion:55s} "
                f"ROE={roe}{zone}{asked}"
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

    footprints = current_roe_by_footprint(df)
    averages = rto_vs_non_rto_averages(footprints)
    print("\nCurrent Base ROE: RTO vs. non-RTO\n" + "=" * 40)
    print("(most recent settled base ROE per footprint; excludes the pending NETO filing)")
    for status in ("RTO", "non-RTO"):
        print(f"\n{status}:")
        for _, r in footprints[footprints["rto_status"] == status].iterrows():
            print(f"  {r.footprint:20s} {r.current_value:.2f}%")
        row = averages.loc[status]
        print(f"  -> Average across {int(row['count'])} footprint(s): {row['mean']:.2f}%")
    if averages.loc["non-RTO", "count"] == 1:
        print(
            "\nNote: the non-RTO average rests on a single footprint (Southern "
            "Company) -- treat it as one data point, not a statistically robust average."
        )


def plot_timeline(df: pd.DataFrame, output_path: str = OUTPUT_PATH) -> None:
    fig, ax = plt.subplots(figsize=(11, 6.5))

    for track, color in TRACK_COLORS.items():
        rows = df[df["case_track"] == track].sort_values("decision_date")
        if rows.empty:
            continue
        is_snapshot = (rows["data_type"] == "snapshot_range").all()

        # Fall back for y-position: granted ROE, else the zone midpoint, else
        # (for a still-pending filing with no outcome yet) the requested ROE.
        y = rows["base_roe_pct"]
        y = y.fillna((rows["zone_low_pct"] + rows["zone_high_pct"]) / 2)
        y = y.fillna(rows["requested_roe_pct"])

        plotted = rows["data_type"] != "pending"
        ax.plot(
            rows.loc[plotted, "decision_date"], y[plotted],
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

        # Hollow marker for the requested/proposed ROE that led to each
        # decision, with a dotted connector showing the gap to the outcome.
        has_ask = rows["requested_roe_pct"].notna()
        if has_ask.any():
            ar = rows[has_ask]
            ay = y[has_ask]
            ax.scatter(
                ar["decision_date"], ar["requested_roe_pct"],
                facecolors="none", edgecolors=color, marker="o", s=70,
                linewidths=1.4, zorder=5,
            )
            for date, granted_y, req_y, pending in zip(
                ar["decision_date"], ay, ar["requested_roe_pct"], ar["data_type"] == "pending"
            ):
                if not pending:
                    ax.plot([date, date], [granted_y, req_y], linestyle=":",
                            color=color, alpha=0.6, linewidth=1)

        for i, ((_, r), yy) in enumerate(zip(rows.iterrows(), y)):
            y_offset = 9 if i % 2 == 0 else -13
            label = r["short_label"] + (" (pending)" if r["data_type"] == "pending" else "")
            ax.annotate(
                label,
                (r["decision_date"], yy),
                textcoords="offset points", xytext=(6, y_offset), fontsize=7.5,
                color=color, bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                                        edgecolor="none", alpha=0.75),
            )

    ax.scatter([], [], facecolors="none", edgecolors="black", marker="o", s=70,
               linewidths=1.4, label="Requested / proposed ROE")

    footprints = current_roe_by_footprint(df)
    averages = rto_vs_non_rto_averages(footprints)
    avg_style = {
        "RTO": dict(color="black", linestyle="--"),
        "non-RTO": dict(color="#8c564b", linestyle="--"),
    }
    for status, style in avg_style.items():
        row = averages.loc[status]
        n_label = f"n={int(row['count'])} footprint" + ("s" if row["count"] != 1 else "")
        ax.axhline(
            row["mean"], linewidth=1.5, alpha=0.7, **style,
            label=f"{status} current avg: {row['mean']:.2f}% ({n_label})",
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
