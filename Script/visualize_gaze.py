#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV Feature Visualizer

This script
  • reads a CSV file,
  • prints a quick data overview,
  • draws histograms for every numeric column,
  • shows a correlation heat-map, and
  • (optionally) plots a pair-plot for a subset of columns.

Edit the “USER SETTINGS” block if you want to change the input path or
tweak how many plots are drawn.
"""

import math
import pandas as pd
import matplotlib.pyplot as plt
from pandas.plotting import scatter_matrix

# ============== USER SETTINGS ============== #
CSV_PATH = "/mnt/data/feature_0.csv"   # Path to the CSV file
HIST_COLS_PER_ROW = 4                  # How many histogram panels per row
PAIRPLOT_MAX_COLS = 10                 # Max columns included in the pair-plot
# ========================================== #

def main() -> None:
    """Main entry point: load data and call the individual plot helpers."""
    # ------------------------------------------------------------------ #
    # 1) Load the CSV and keep only numeric columns (avoid text columns). #
    # ------------------------------------------------------------------ #
    df = pd.read_csv(CSV_PATH)
    num_df = df.select_dtypes(include="number")  # numeric-only view

    # Print a quick summary so the user knows what is inside the file.
    print("\n=== DataFrame info ===")
    print(num_df.info())
    print("\n=== Descriptive statistics ===")
    print(num_df.describe())

    # ------------------------------------------------------------------ #
    # 2) Draw one histogram per numeric column.                          #
    # ------------------------------------------------------------------ #
    draw_histograms(num_df)

    # ------------------------------------------------------------------ #
    # 3) Draw a correlation matrix heat-map.                             #
    # ------------------------------------------------------------------ #
    draw_correlations(num_df)

    # ------------------------------------------------------------------ #
    # 4) Optionally draw a pair-plot (can be expensive if many columns). #
    # ------------------------------------------------------------------ #
    if num_df.shape[1] > 1:
        draw_pairplot(num_df)

# ---------------------------------------------------------------------- #
# ----------------------------- PLOTTING --------------------------------#
# ---------------------------------------------------------------------- #

def draw_histograms(num_df: pd.DataFrame) -> None:
    """Create a grid of histograms, one per numeric column."""
    num_cols = num_df.shape[1]               # total numeric columns
    ncols = HIST_COLS_PER_ROW                # panels per row
    nrows = math.ceil(num_cols / ncols)      # rows needed so every
                                             # column has a panel

    # The figure size scales with grid dimensions so the plots stay legible.
    fig, axes = plt.subplots(
        nrows,
        ncols,
        figsize=(4 * ncols, 3 * nrows),
        squeeze=False                       # ensures 2-D array of axes
    )
    axes = axes.flatten()                    # easier to iterate

    # Plot each numeric feature in its own axis.
    for ax, col in zip(axes, num_df.columns):
        num_df[col].plot(kind="hist", ax=ax, edgecolor="black")
        ax.set_title(col)
        ax.set_xlabel("")  # no x-label to save space

    # Remove any empty axes (when num_cols is not an exact multiple of ncols).
    for ax in axes[num_cols:]:
        fig.delaxes(ax)

    plt.suptitle("Histograms of numeric features", y=1.02, fontsize=14)
    plt.tight_layout()
    plt.show()

def draw_correlations(num_df: pd.DataFrame) -> None:
    """Plot a heat-map of the Pearson correlation matrix."""
    corr = num_df.corr(numeric_only=True)

    plt.figure(figsize=(10, 8))
    im = plt.imshow(corr, interpolation="none", aspect="auto")
    plt.colorbar(im, fraction=0.046, pad=0.04)
    plt.xticks(range(len(corr)), corr.columns, rotation=90, fontsize=6)
    plt.yticks(range(len(corr)), corr.columns, fontsize=6)
    plt.title("Feature correlation heat-map")
    plt.tight_layout()
    plt.show()

def draw_pairplot(num_df: pd.DataFrame) -> None:
    """Scatter-matrix of a subset of columns for quick pairwise inspection."""
    # We limit column count for speed and readability; tweak if desired.
    cols_to_plot = num_df.columns[:PAIRPLOT_MAX_COLS]

    scatter_matrix(
        num_df[cols_to_plot],
        figsize=(12, 12),
        diagonal="hist"  # histograms on the diagonal
    )
    plt.suptitle(
        f"Pair-plot (first {len(cols_to_plot)} numeric features)",
        y=0.92
    )
    plt.tight_layout()
    plt.show()

# ---------------------------------------------------------------------- #
# ------------------------------ ENTRY ----------------------------------#
# ---------------------------------------------------------------------- #
if __name__ == "__main__":
    main()
