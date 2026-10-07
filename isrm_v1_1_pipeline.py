"""ISRM v1.1 ambiguity correction; no canonical model has been established.

Explicit legacy reproduction only. See Formal_Model_Specification_v1.1.md.
Archived v1.0 code and numerical behavior remain unchanged.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import pandas as pd

import isrm_v1_pipeline as legacy

METADATA = json.loads(Path(__file__).with_name("ISRM v1.1.json").read_text())


def add_sp_columns(df, fb=None, *, model):
    if model != "v1.0-minimal":
        raise ValueError("Canonical model unresolved; select v1.0-minimal explicitly.")
    unsupported = {"tl", "n", "p"}.intersection(str(c).casefold() for c in df.columns)
    if unsupported:
        raise ValueError(f"Legacy minimal model cannot consume TL/N/P: {sorted(unsupported)}")
    out = legacy.add_sp_columns(df, fb)
    out["implementation_version"] = METADATA["implementation_version"]
    out["model_id"] = METADATA["available_model_id"]
    out["canonical_model_status"] = METADATA["canonical_model_status"]
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, choices=["v1.0-minimal"])
    args = parser.parse_args()
    print("ISRM v1.1: canonical model unresolved; reproducing legacy-minimal.")
    in_path = Path("raw_data/combined_panel.csv")
    df = pd.read_csv(in_path)
    missing = [c for c in legacy.REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"combined_panel.csv missing required columns: {missing}")
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype(int)
    out = add_sp_columns(df, model=args.model)
    out = out.dropna(subset=["SP", "enforcement_norm"]).copy()
    out["SP_quintile"] = legacy.assign_quintiles_per_year(out)
    os.makedirs("output/v1.1", exist_ok=True)
    os.makedirs("figures/v1.1", exist_ok=True)
    out.to_csv("output/v1.1/full_panel_with_sp.csv", index=False)
    legacy.regime_summary(out).to_csv("output/v1.1/regime_summary_q5_q1.csv", index=False)
    legacy.plot_q5_q1(out, "figures/v1.1/q5_vs_q1_enforcement.png")
    print("Wrote labeled legacy reproduction to output/v1.1 and figures/v1.1.")


if __name__ == "__main__":
    main()
