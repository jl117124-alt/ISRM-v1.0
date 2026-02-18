"""
ISRM v1.0 (Minimal, fully-defined) — Public Release Pipeline


Implements a reproducible, executable version of ISRM v1.0 with NO undefined variables.
Canonical equation implemented here:


    SP = S / (IRD * M)


Where:
    S   = mean(minmax(log(pop)), minmax(density), minmax(%urban), minmax(%metro>1M))
    IRD = mean(minmax(volunteerism), minmax(two-parent), minmax(turnout))
    M   = minmax(marriage_rate)


Enforcement is validation-only:
    enforcement_norm = mean(minmax(police_per_100k), minmax(incarceration_per_100k))


This script expects a pre-merged panel:
    raw_data/combined_panel.csv


Outputs:
    output/full_panel_with_sp.csv
    output/regime_summary_q5_q1.csv
    figures/q5_vs_q1_enforcement.png
"""


from __future__ import annotations


import os
from dataclasses import dataclass
from typing import Dict, Tuple, Optional


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt




REQUIRED_COLUMNS = [
    "state", "year",
    "population", "density", "pct_urban", "pct_metro_gt1m",
    "volunteerism_pct", "two_parent_children_pct", "voter_turnout_pct",
    "marriage_rate",
    "enforcement_police_per_100k", "enforcement_incarceration_per_100k",
]




@dataclass(frozen=True)
class FrozenBounds:
    """Holds min/max bounds for minmax normalization."""
    bounds: Dict[str, Tuple[float, float]]




def _to_num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")




def minmax_norm(s: pd.Series, bounds: Optional[Tuple[float, float]] = None) -> pd.Series:
    """
    Min-max normalize a numeric series.
    If bounds are provided, uses them; otherwise uses series min/max.
    Returns zeros if degenerate or missing.
    """
    s = _to_num(s)
    if bounds is None:
        mn, mx = float(np.nanmin(s.values)), float(np.nanmax(s.values))
    else:
        mn, mx = bounds


    if np.isnan(mn) or np.isnan(mx) or mx == mn:
        return pd.Series(np.zeros(len(s), dtype=float), index=s.index)


    return (s - mn) / (mx - mn)




def compute_S(df: pd.DataFrame, fb: Optional[FrozenBounds] = None) -> pd.Series:
    log_pop = np.log(_to_num(df["population"]).replace(0, np.nan))
    comps = {
        "log_population": log_pop,
        "density": df["density"],
        "pct_urban": df["pct_urban"],
        "pct_metro_gt1m": df["pct_metro_gt1m"],
    }


    normed = []
    for name, series in comps.items():
        b = fb.bounds.get(name) if fb else None
        normed.append(minmax_norm(series, b))
    return sum(normed) / len(normed)




def compute_IRD(df: pd.DataFrame, fb: Optional[FrozenBounds] = None) -> pd.Series:
    comps = {
        "volunteerism_pct": df["volunteerism_pct"],
        "two_parent_children_pct": df["two_parent_children_pct"],
        "voter_turnout_pct": df["voter_turnout_pct"],
    }
    normed = []
    for name, series in comps.items():
        b = fb.bounds.get(name) if fb else None
        normed.append(minmax_norm(series, b))
    return sum(normed) / len(normed)




def compute_M(df: pd.DataFrame, fb: Optional[FrozenBounds] = None) -> pd.Series:
    b = fb.bounds.get("marriage_rate") if fb else None
    return minmax_norm(df["marriage_rate"], b)




def compute_enforcement_norm(df: pd.DataFrame, fb: Optional[FrozenBounds] = None) -> pd.Series:
    comps = {
        "enforcement_police_per_100k": df["enforcement_police_per_100k"],
        "enforcement_incarceration_per_100k": df["enforcement_incarceration_per_100k"],
    }
    normed = []
    for name, series in comps.items():
        b = fb.bounds.get(name) if fb else None
        normed.append(minmax_norm(series, b))
    return sum(normed) / len(normed)




def build_frozen_bounds(train_df: pd.DataFrame) -> FrozenBounds:
    """
    Create frozen min/max bounds for each normalized component, computed only on train_df.
    """
    train_df = train_df.copy()


    # Derived column used in S
    train_df["log_population"] = np.log(_to_num(train_df["population"]).replace(0, np.nan))


    cols = [
        "log_population", "density", "pct_urban", "pct_metro_gt1m",
        "volunteerism_pct", "two_parent_children_pct", "voter_turnout_pct",
        "marriage_rate",
        "enforcement_police_per_100k", "enforcement_incarceration_per_100k",
    ]


    bounds: Dict[str, Tuple[float, float]] = {}
    for c in cols:
        s = _to_num(train_df[c])
        mn = float(np.nanmin(s.values))
        mx = float(np.nanmax(s.values))
        bounds[c] = (mn, mx)
    return FrozenBounds(bounds=bounds)




def add_sp_columns(df: pd.DataFrame, fb: Optional[FrozenBounds] = None) -> pd.DataFrame:
    out = df.copy()
    out["S"] = compute_S(out, fb)
    out["IRD"] = compute_IRD(out, fb)
    out["M"] = compute_M(out, fb)


    denom = (out["IRD"] * out["M"]).replace(0, np.nan)
    out["SP"] = (out["S"] / denom).replace([np.inf, -np.inf], np.nan)


    out["enforcement_norm"] = compute_enforcement_norm(out, fb)
    return out




def assign_quintiles_per_year(df: pd.DataFrame, col: str = "SP") -> pd.Series:
    """
    Assign quintiles (1..5) per year. If qcut fails due to ties, falls back to rank-based bins.
    """
    def _qcut_safe(x: pd.Series) -> pd.Series:
        try:
            return pd.qcut(x, 5, labels=[1, 2, 3, 4, 5])
        except Exception:
            r = x.rank(method="average")
            return pd.qcut(r, 5, labels=[1, 2, 3, 4, 5])


    return df.groupby("year")[col].transform(_qcut_safe).astype(int)




def regime_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Produce Q5 vs Q1 enforcement means per year, plus difference.
    """
    pivot = df.pivot_table(
        index="year",
        columns="SP_quintile",
        values="enforcement_norm",
        aggfunc="mean",
    ).rename(columns={1: "Q1", 5: "Q5"})
    pivot["Q5_minus_Q1"] = pivot["Q5"] - pivot["Q1"]
    return pivot.reset_index()




def plot_q5_q1(df: pd.DataFrame, out_path: str) -> None:
    q = df[df["SP_quintile"].isin([1, 5])].copy()
    series = q.groupby(["year", "SP_quintile"])["enforcement_norm"].mean().unstack()
    plt.figure(figsize=(10, 5))
    plt.plot(series.index, series.get(5), marker="o", label="Q5 enforcement mean")
    plt.plot(series.index, series.get(1), marker="o", label="Q1 enforcement mean")
    plt.title("Enforcement Regime Separation: Q5 vs Q1 (by year)")
    plt.xlabel("Year")
    plt.ylabel("Enforcement (normalized)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=160)
    plt.close()




def main() -> None:
    os.makedirs("output", exist_ok=True)
    os.makedirs("figures", exist_ok=True)


    in_path = os.path.join("raw_data", "combined_panel.csv")
    if not os.path.exists(in_path):
        raise FileNotFoundError(
            f"Missing {in_path}. Create raw_data/combined_panel.csv with required columns:\n"
            + ", ".join(REQUIRED_COLUMNS)
        )


    df = pd.read_csv(in_path)


    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"combined_panel.csv missing required columns: {missing}")


    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype(int)


    # Compute SP + enforcement (full-sample normalization)
    df_full = add_sp_columns(df, fb=None)


    # Drop rows where SP is undefined due to zeros/missing denom
    df_full = df_full.dropna(subset=["SP", "enforcement_norm"]).copy()


    # Assign quintiles per year
    df_full["SP_quintile"] = assign_quintiles_per_year(df_full, col="SP")


    # Outputs
    df_full.to_csv(os.path.join("output", "full_panel_with_sp.csv"), index=False)


    summary = regime_summary(df_full)
    summary.to_csv(os.path.join("output", "regime_summary_q5_q1.csv"), index=False)


    plot_q5_q1(df_full, os.path.join("figures", "q5_vs_q1_enforcement.png"))


    print("ISRM v1.0 (Minimal) replication complete.")
    print("Wrote: output/full_panel_with_sp.csv")
    print("Wrote: output/regime_summary_q5_q1.csv")
    print("Wrote: figures/q5_vs_q1_enforcement.png")




if __name__ == "__main__":
    main()