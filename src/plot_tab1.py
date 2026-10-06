from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

project_root = Path(__file__).resolve().parents[1]
data = pd.read_csv(project_root / "outputs" / "engagement_by_tab.csv")

tab1 = (
    data[data["tab"] == 1]
    .set_index("log_type")
    .loc[["random", "standard"]]
)

metrics = [
    ("long_view_rate", "Long-view signal"),
    ("like_rate", "Like signal"),
    ("hate_rate", "Hate signal"),
]
colors = ["#45A29E", "#4056A1"]
labels = ["Random exposure\n1.18M logged rows", "Standard recommendation\n224K logged rows"]

fig, axes = plt.subplots(1, 3, figsize=(13, 4))
fig.suptitle(
    "Observed Feedback Signals in Tab 1 (Apr 22–May 8, 2022)",
    fontsize=14,
    fontweight="bold",
)

for ax, (metric, title) in zip(axes, metrics):
    values = tab1[metric].to_numpy() * 100
    bars = ax.bar(labels, values, color=colors, width=0.62)

    ax.bar_label(bars, labels=[f"{value:.2f}%" for value in values], padding=4)
    ax.set_title(title)
    ax.set_ylabel("Share of logged rows (%)")
    ax.set_ylim(0, max(values) * 1.3 if max(values) > 0 else 1)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(axis="x", labelsize=8)

fig.text(
    0.5,
    0.01,
    "Descriptive comparison of logged feedback; rows are not confirmed to be all feed impressions. "
    "This is not a causal estimate.",
    ha="center",
    fontsize=8,
)
fig.tight_layout(rect=[0, 0.08, 1, 0.90])

output = project_root / "outputs" / "tab1_feedback_comparison.png"
fig.savefig(output, dpi=180, bbox_inches="tight")
print(f"Saved chart: {output}")