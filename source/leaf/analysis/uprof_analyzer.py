"""Analysis and visualization tool for AMDuProf energy & power profiling data.

Parses AMDuProf timechart CSV reports, computes descriptive statistics (mean, median,
percentiles, sampling jitter, total energy in Joules and Watt-hours), and generates
individual and comparative multi-panel scientific figures.
"""

import os
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path
from typing import Any

# Ensure source root is on sys.path when executed as a standalone script
source_root = Path(__file__).resolve().parents[2]
if str(source_root) not in sys.path:
    sys.path.insert(0, str(source_root))

# Avoid Matplotlib cache warnings on Windows accounts with special characters
if "MPLCONFIGDIR" not in os.environ:
    os.environ["MPLCONFIGDIR"] = os.path.join(tempfile.gettempdir(), "leaf_matplotlib_cache")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from leaf.core.units import joules_to_watt_hours


def _parse_timestamp_seconds(ts_str: str) -> float:
    """Parse AMDuProf timestamp string 'H:M:S:ms' into elapsed seconds.

    Example: '4:40:1:975' -> 4*3600 + 40*60 + 1 + 975/1000 = 16801.975
    """
    try:
        parts = [float(p) for p in str(ts_str).strip().split(":")]
        if len(parts) == 4:
            h, m, s, ms = parts
            return h * 3600.0 + m * 60.0 + s + (ms / 1000.0)
    except (ValueError, TypeError):
        pass
    return 0.0


def parse_uprof_timechart(csv_path: str | Path) -> tuple[dict[str, Any], pd.DataFrame]:
    """Parse AMDuProf power profile CSV report.

    Extracts metadata from the header, parses timestamps into elapsed wall-clock
    seconds, computes empirical sampling intervals (dt), and loads the records section.

    Args:
        csv_path: Path to the AMDuProf timechart.csv file.

    Returns:
        A tuple of (metadata_dict, records_dataframe).
    """
    path = Path(csv_path)
    if not path.is_file():
        raise FileNotFoundError(f"AMDuProf CSV file not found: {path}")

    metadata: dict[str, Any] = {}
    records_start_line = 0

    with open(path, encoding="utf-8", errors="ignore") as f:
        for idx, line in enumerate(f):
            stripped = line.strip()
            if stripped.startswith("CPU Details:"):
                metadata["cpu_details"] = stripped.split(":", 1)[1].strip().strip(",")
            elif stripped.startswith("Sampling Interval:"):
                raw_interval = stripped.split(":", 1)[1].strip().strip(",")
                metadata["sampling_interval"] = raw_interval
            elif stripped.startswith("Profile Duration:"):
                metadata["duration"] = stripped.split(":", 1)[1].strip().strip(",")
            elif stripped.startswith("Profile Start Time:"):
                metadata["start_time"] = stripped.split(":", 1)[1].strip().strip(",")
            elif stripped == "PROFILE RECORDS":
                records_start_line = idx + 1
                break

    if records_start_line == 0:
        raise ValueError(f"Could not find 'PROFILE RECORDS' section in {path}")

    # Read the data section
    df = pd.read_csv(path, skiprows=records_start_line, skipinitialspace=True)
    df.columns = df.columns.str.strip()

    # Parse nominal sampling interval (ms)
    interval_ms = 100.0
    if "sampling_interval" in metadata:
        raw_val = metadata["sampling_interval"]
        parts = raw_val.split()
        if parts:
            first_token = parts[0].lstrip(",").strip()
            try:
                interval_ms = float(first_token)
            except ValueError:
                interval_ms = 100.0
    metadata["nominal_interval_ms"] = interval_ms

    if df.empty or "Timestamp" not in df.columns:
        df["elapsed_time_s"] = np.arange(len(df)) * (interval_ms / 1000.0)
        df["dt_ms"] = interval_ms
        return metadata, df

    # Parse real wall-clock timestamps
    ts_seconds = df["Timestamp"].apply(_parse_timestamp_seconds)
    elapsed = ts_seconds - ts_seconds.iloc[0]

    # Handle clock wrap-around if any
    if (elapsed < -100).any():
        # Fallback to nominal if clock wrapped or parsed poorly
        elapsed = np.arange(len(df)) * (interval_ms / 1000.0)

    df["elapsed_time_s"] = elapsed
    dt_series = df["elapsed_time_s"].diff() * 1000.0
    # First record dt assigned to nominal or second record value
    dt_series.iloc[0] = dt_series.iloc[1] if len(dt_series) > 1 else interval_ms
    df["dt_ms"] = dt_series

    return metadata, df


def compute_uprof_statistics(df: pd.DataFrame) -> dict[str, Any]:
    """Compute summary statistics and energy integrations from AMDuProf records.

    Args:
        df: DataFrame parsed by `parse_uprof_timechart`.

    Returns:
        Dictionary of summary metrics (means, medians, dispersion, jitter, integrated energy).
    """
    if df.empty:
        return {"record_count": 0, "total_duration_s": 0.0, "package_power": {}, "core_power": {}, "sampling_jitter": {}}

    pkg_col = "socket0-package-power"
    if pkg_col not in df.columns:
        power_cols = [c for c in df.columns if "power" in c.lower()]
        pkg_col = power_cols[0] if power_cols else df.columns[2]

    pkg_series = df[pkg_col]
    core_cols = [c for c in df.columns if c.startswith("core") and c.endswith("-power")]

    # Real time integration using trapezoidal rule: E = integral P(t) dt in Joules
    if len(df) > 1 and "elapsed_time_s" in df.columns:
        total_energy_j = float(np.trapezoid(pkg_series.values, df["elapsed_time_s"].values))
    else:
        total_energy_j = 0.0
    total_energy_wh = joules_to_watt_hours(total_energy_j)

    # Jitter metrics
    dt_vals = df["dt_ms"].iloc[1:] if len(df) > 1 else df["dt_ms"]

    stats = {
        "record_count": len(df),
        "total_duration_s": float(df["elapsed_time_s"].iloc[-1]) if not df.empty else 0.0,
        "sampling_jitter": {
            "dt_mean_ms": float(dt_vals.mean()),
            "dt_median_ms": float(dt_vals.median()),
            "dt_std_ms": float(dt_vals.std()) if len(dt_vals) > 1 else 0.0,
            "dt_min_ms": float(dt_vals.min()),
            "dt_max_ms": float(dt_vals.max()),
            "dt_p05_ms": float(dt_vals.quantile(0.05)),
            "dt_p25_ms": float(dt_vals.quantile(0.25)),
            "dt_p75_ms": float(dt_vals.quantile(0.75)),
            "dt_p95_ms": float(dt_vals.quantile(0.95)),
            "dt_p99_ms": float(dt_vals.quantile(0.99)),
        },
        "package_power": {
            "mean_w": float(pkg_series.mean()),
            "std_w": float(pkg_series.std()),
            "median_w": float(pkg_series.median()),
            "min_w": float(pkg_series.min()),
            "max_w": float(pkg_series.max()),
            "p25_w": float(pkg_series.quantile(0.25)),
            "p75_w": float(pkg_series.quantile(0.75)),
            "iqr_w": float(pkg_series.quantile(0.75) - pkg_series.quantile(0.25)),
            "total_energy_j": total_energy_j,
            "total_energy_wh": total_energy_wh,
        },
        "core_power": {
            c: {
                "mean_w": float(df[c].mean()),
                "max_w": float(df[c].max()),
                "median_w": float(df[c].median()),
            }
            for c in core_cols
        },
    }
    return stats


def plot_uprof_analysis(
    df: pd.DataFrame,
    stats: dict[str, Any],
    metadata: dict[str, Any],
    output_path: Path,
) -> None:
    """Generate 4-panel analysis figure from AMDuProf data."""
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig, axes = plt.subplots(2, 2, figsize=(16, 10), dpi=300)
    fig.suptitle(
        f"AMDuProf Idle Telemetry Baseline (CPU: {metadata.get('cpu_details', 'AMD Zen 4')})",
        fontsize=16,
        fontweight="bold",
        y=0.98,
    )

    pkg_stats = stats["package_power"]
    core_cols = [c for c in df.columns if c.startswith("core") and c.endswith("-power")]

    # --- Panel 1: Package Power Time-Series ---
    ax1 = axes[0, 0]
    ax1.plot(df["elapsed_time_s"], df["socket0-package-power"], color="#1f77b4", linewidth=1.2, label="Package Power (W)")
    ax1.axhline(pkg_stats["mean_w"], color="#d62728", linestyle="--", linewidth=1.5, label=f"Mean: {pkg_stats['mean_w']:.2f} W")
    ax1.axhline(pkg_stats["median_w"], color="#2ca02c", linestyle=":", linewidth=1.5, label=f"Median: {pkg_stats['median_w']:.2f} W")
    ax1.fill_between(
        df["elapsed_time_s"],
        pkg_stats["p25_w"],
        pkg_stats["p75_w"],
        color="#1f77b4",
        alpha=0.15,
        label=f"IQR Band ({pkg_stats['p25_w']:.2f} - {pkg_stats['p75_w']:.2f} W)",
    )
    ax1.set_title("Package Power Time Series", fontsize=12, fontweight="bold")
    ax1.set_xlabel("Elapsed Time (seconds)", fontsize=10)
    ax1.set_ylabel("Power (Watts)", fontsize=10)
    ax1.legend(loc="upper right", frameon=True)
    ax1.grid(True, linestyle="--", alpha=0.6)

    # --- Panel 2: Per-Core Power Breakdown ---
    ax2 = axes[0, 1]
    cmap = plt.get_cmap("tab10")
    for i, c in enumerate(core_cols):
        ax2.plot(df["elapsed_time_s"], df[c], label=c.replace("-power", ""), linewidth=1.0, color=cmap(i % 10))
    ax2.set_title("Individual Core Power Dissipation", fontsize=12, fontweight="bold")
    ax2.set_xlabel("Elapsed Time (seconds)", fontsize=10)
    ax2.set_ylabel("Power (Watts)", fontsize=10)
    ax2.legend(loc="upper right", ncol=2, frameon=True, fontsize=8)
    ax2.grid(True, linestyle="--", alpha=0.6)

    # --- Panel 3: Package Power Distribution ---
    ax3 = axes[1, 0]
    counts, bin_edges, _ = ax3.hist(
        df["socket0-package-power"],
        bins=35,
        density=True,
        alpha=0.65,
        color="#3b528b",
        edgecolor="black",
        linewidth=0.5,
    )
    # Approximate smoothed line using bin centers
    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
    ax3.plot(bin_centers, counts, color="#e34a33", linewidth=1.8, label="Binned Density")
    ax3.axvline(pkg_stats["median_w"], color="#2ca02c", linestyle="--", linewidth=1.5, label=f"Median ({pkg_stats['median_w']:.2f} W)")
    ax3.set_title("Package Power Probability Density", fontsize=12, fontweight="bold")
    ax3.set_xlabel("Power (Watts)", fontsize=10)
    ax3.set_ylabel("Probability Density", fontsize=10)
    ax3.legend(loc="upper right", frameon=True)
    ax3.grid(True, linestyle="--", alpha=0.6)

    summary_text = (
        f"Samples: {stats['record_count']}\n"
        f"Nominal dt: {metadata.get('nominal_interval_ms', 100):.0f} ms\n"
        f"Real dt mean: {stats['sampling_jitter']['dt_mean_ms']:.1f} ms\n"
        f"Mean: {pkg_stats['mean_w']:.2f} W (+/- {pkg_stats['std_w']:.2f})\n"
        f"Median: {pkg_stats['median_w']:.2f} W\n"
        f"IQR: {pkg_stats['iqr_w']:.2f} W\n"
        f"Range: [{pkg_stats['min_w']:.2f}, {pkg_stats['max_w']:.2f}] W\n"
        f"Total E: {pkg_stats['total_energy_j']:.2f} J\n"
        f"        ({pkg_stats['total_energy_wh']:.4f} Wh)"
    )
    ax3.text(
        0.05,
        0.95,
        summary_text,
        transform=ax3.transAxes,
        fontsize=9.5,
        verticalalignment="top",
        bbox={"boxstyle": "round,pad=0.5", "facecolor": "white", "edgecolor": "gray", "alpha": 0.9},
    )

    # --- Panel 4: Per-Core Comparison ---
    ax4 = axes[1, 1]
    core_labels = [c.replace("-power", "") for c in core_cols]
    core_means = [stats["core_power"][c]["mean_w"] for c in core_cols]
    core_peaks = [stats["core_power"][c]["max_w"] for c in core_cols]
    x_indices = np.arange(len(core_cols))
    width = 0.35

    ax4.bar(x_indices - width / 2, core_means, width, label="Mean Power (W)", color="#2b83ba")
    ax4.bar(x_indices + width / 2, core_peaks, width, label="Peak Power (W)", color="#d7191c", alpha=0.85)
    ax4.set_xticks(x_indices)
    ax4.set_xticklabels(core_labels, rotation=45, ha="right", fontsize=9)
    ax4.set_title("Per-Core Average vs Peak Activity", fontsize=12, fontweight="bold")
    ax4.set_ylabel("Power (Watts)", fontsize=10)
    ax4.legend(loc="upper left", frameon=True)
    ax4.grid(True, linestyle="--", alpha=0.6)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def generate_comparison_report(
    sample_definitions: list[tuple[str, Path]],
    out_fig_path: Path,
    out_csv_path: Path,
) -> pd.DataFrame:
    """Generate comparative visualization and statistics across multiple sampling runs.

    Args:
        sample_definitions: List of (label, csv_path) tuples.
        out_fig_path: Path to save the multi-run comparison figure.
        out_csv_path: Path to save the comparison summary table.

    Returns:
        DataFrame containing summary statistics for all samples.
    """
    results: list[dict[str, Any]] = []
    loaded_data: list[tuple[str, dict[str, Any], pd.DataFrame, dict[str, Any]]] = []

    for label, path in sample_definitions:
        if not path.is_file():
            continue
        try:
            meta, df = parse_uprof_timechart(path)
            if df.empty or len(df) < 5:
                continue
            st = compute_uprof_statistics(df)
            loaded_data.append((label, meta, df, st))

            pkg = st["package_power"]
            jit = st["sampling_jitter"]
            results.append({
                "condition": label,
                "nominal_dt_ms": meta.get("nominal_interval_ms", np.nan),
                "record_count": st["record_count"],
                "duration_s": round(st["total_duration_s"], 2),
                "dt_mean_ms": round(jit["dt_mean_ms"], 2),
                "dt_median_ms": round(jit["dt_median_ms"], 2),
                "dt_std_ms": round(jit["dt_std_ms"], 2),
                "dt_min_ms": round(jit["dt_min_ms"], 2),
                "dt_max_ms": round(jit["dt_max_ms"], 2),
                "dt_p95_ms": round(jit["dt_p95_ms"], 2),
                "power_mean_w": round(pkg["mean_w"], 2),
                "power_std_w": round(pkg["std_w"], 2),
                "power_median_w": round(pkg["median_w"], 2),
                "power_iqr_w": round(pkg["iqr_w"], 2),
                "power_min_w": round(pkg["min_w"], 2),
                "power_max_w": round(pkg["max_w"], 2),
                "total_energy_j": round(pkg["total_energy_j"], 2),
                "total_energy_wh": round(pkg["total_energy_wh"], 4),
            })
        except (ValueError, KeyError, OSError, RuntimeError) as e:
            print(f"Warning: Failed to process {path}: {e}", file=sys.stderr)

    comp_df = pd.DataFrame(results)
    out_csv_path.parent.mkdir(parents=True, exist_ok=True)
    comp_df.to_csv(out_csv_path, index=False)

    if not loaded_data:
        return comp_df

    # Plot 4-panel comparison figure
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig, axes = plt.subplots(2, 2, figsize=(16, 11), dpi=300)
    fig.suptitle(
        "AMDuProf Idle Telemetry Comparison: 10ms vs 100ms Sampling & Background Apps",
        fontsize=15,
        fontweight="bold",
        y=0.98,
    )

    palette = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]

    # --- Panel 1: Time Series comparison (first 20 seconds normalized) ---
    ax1 = axes[0, 0]
    for i, (label, _meta, df, _st) in enumerate(loaded_data):
        sub_df = df[df["elapsed_time_s"] <= 20.0]
        ax1.plot(
            sub_df["elapsed_time_s"],
            sub_df["socket0-package-power"],
            label=label,
            color=palette[i % len(palette)],
            alpha=0.75,
            linewidth=1.1 if "10ms" not in label else 0.7,
        )
    ax1.set_title("Package Power Traces (First 20 Seconds Normalized)", fontsize=12, fontweight="bold")
    ax1.set_xlabel("Elapsed Time (s)", fontsize=10)
    ax1.set_ylabel("Power (W)", fontsize=10)
    ax1.legend(loc="upper right", frameon=True, fontsize=8.5)
    ax1.grid(True, linestyle="--", alpha=0.6)

    # --- Panel 2: Sampling Interval Jitter Distribution (Boxplot) ---
    ax2 = axes[0, 1]
    jitter_data = [df["dt_ms"].iloc[1:] for _label, _meta, df, _st in loaded_data]
    labels_short = [label.split(":")[0].strip() for label, _, _, _ in loaded_data]

    box = ax2.boxplot(jitter_data, tick_labels=labels_short, patch_artist=True, showfliers=False)
    for patch, color in zip(box["boxes"], palette, strict=False):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)
    ax2.set_title("Sampling Interval Distribution (Excluding Outliers > IQR*1.5)", fontsize=12, fontweight="bold")
    ax2.set_ylabel("Actual Sampling Interval dt (ms)", fontsize=10)
    ax2.grid(True, linestyle="--", alpha=0.6)

    # Add text on max spikes
    for i, (_label, _meta, df, st) in enumerate(loaded_data):
        jit = st["sampling_jitter"]
        ax2.text(
            i + 1,
            jit["dt_median_ms"] + (3 if jit["dt_median_ms"] < 50 else -15),
            f"Med: {jit['dt_median_ms']:.0f}ms\nMax: {jit['dt_max_ms']:.0f}ms\nStd: {jit['dt_std_ms']:.1f}ms",
            ha="center",
            fontsize=8,
            bbox={"boxstyle": "round,pad=0.2", "facecolor": "white", "edgecolor": "gray", "alpha": 0.8},
        )

    # --- Panel 3: Probability Density Comparison ---
    ax3 = axes[1, 0]
    for i, (label, _meta, df, _st) in enumerate(loaded_data):
        pkg_vals = df["socket0-package-power"].dropna()
        counts, bin_edges = np.histogram(pkg_vals, bins=35, range=(1.0, 12.0), density=True)
        bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
        ax3.plot(bin_centers, counts, label=label, color=palette[i % len(palette)], linewidth=2.0)
    ax3.set_title("Package Power Density Comparison (Normalized Frequency)", fontsize=12, fontweight="bold")
    ax3.set_xlabel("Package Power (Watts)", fontsize=10)
    ax3.set_ylabel("Probability Density", fontsize=10)
    ax3.legend(loc="upper right", frameon=True, fontsize=8.5)
    ax3.grid(True, linestyle="--", alpha=0.6)

    # --- Panel 4: Statistical Metrics Summary (Mean, Median, IQR) ---
    ax4 = axes[1, 1]
    x_pos = np.arange(len(loaded_data))
    bar_width = 0.25

    means = [st["package_power"]["mean_w"] for _, _, _, st in loaded_data]
    medians = [st["package_power"]["median_w"] for _, _, _, st in loaded_data]
    iqrs = [st["package_power"]["iqr_w"] for _, _, _, st in loaded_data]

    ax4.bar(x_pos - bar_width, means, bar_width, label="Mean Power (W)", color="#3182bd")
    ax4.bar(x_pos, medians, bar_width, label="Median Power (W)", color="#31a354")
    ax4.bar(x_pos + bar_width, iqrs, bar_width, label="IQR Dispersion (W)", color="#fd8d3c")

    ax4.set_xticks(x_pos)
    ax4.set_xticklabels(labels_short, rotation=15, ha="right", fontsize=9)
    ax4.set_ylabel("Power (Watts)", fontsize=10)
    ax4.set_title("Central Tendency & Dispersion Across Test Conditions", fontsize=12, fontweight="bold")
    ax4.legend(loc="upper right", frameon=True, fontsize=9)
    ax4.grid(True, linestyle="--", alpha=0.6)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    out_fig_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_fig_path, dpi=300, bbox_inches="tight")
    plt.close()

    return comp_df


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for AMDuProf telemetry analyzer."""
    # Define sample files
    base_dir = Path("results") / "uprof_idle"
    sample_defs = [
        ("Run 1: Clean Idle (120s / 100ms)", base_dir / "AMDuProf-SWP-Timechart_Nov-03-2026_04-24-03" / "timechart.csv"),
        ("Run 2: Idle + GPT in Taskbar (20s / 10ms)", base_dir / "AMDuProf-SWP-Timechart_Nov-03-2026_04-40-01" / "timechart.csv"),
        ("Run 3: Idle + GPT in Taskbar (120s / 100ms)", base_dir / "AMDuProf-SWP-Timechart_Nov-03-2026_04-41-52" / "timechart.csv"),
        ("Run 4: Idle + VSCode + GPT (20s / 10ms)", base_dir / "AMDuProf-SWP-Timechart_Nov-03-2026_04-44-03" / "timechart.csv"),
    ]

    out_fig_dir = Path("results") / "figures"
    out_analysis_dir = Path("results") / "analysis"

    # Run multi-sample comparison
    print("=" * 70)
    print("LEAF AMDuProf Telemetry Comparative Analysis")
    print("Evaluating Sampling Rates (10ms vs 100ms) and Idle Jitter & Bias")
    print("=" * 70)

    comp_fig = out_fig_dir / "uprof_sampling_comparison.png"
    comp_csv = out_analysis_dir / "uprof_sampling_comparison.csv"

    comp_df = generate_comparison_report(sample_defs, comp_fig, comp_csv)

    print("\nSummary Comparison Table:")
    print(comp_df.to_string(index=False))

    print(f"\n[+] Saved comparative visualization: {comp_fig}")
    print(f"[+] Saved comparative metrics CSV: {comp_csv}")

    # Also re-generate single baseline figure for Run 1
    single_csv = sample_defs[0][1]
    if single_csv.is_file():
        meta, df = parse_uprof_timechart(single_csv)
        st = compute_uprof_statistics(df)
        single_fig = out_fig_dir / "uprof_idle_baseline.png"
        plot_uprof_analysis(df, st, meta, single_fig)
        print(f"[+] Re-generated baseline figure: {single_fig}")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
