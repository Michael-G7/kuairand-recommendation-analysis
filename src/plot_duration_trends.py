from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import PercentFormatter

project_root = Path(__file__).resolve().parents[1]
data = pd.read_csv(project_root / "outputs" / "watch_depth_by_duration.csv")

duration_groups = ["<=7s", "7-18s", ">18s"]
metrics = [
    ("long_view_rate", "Long-view signal rate"),
    ("like_rate", "Like signal rate"),
    ("median_watch_duration_ratio", "Median play time / video duration"),
]
colors = {"random": "#45A29E", "standard": "#4056A1"}

fig, axes = plt.subplots(1, 3, figsize=(13, 4))

for ax, (metric, title) in zip(axes, metrics):
    for log_type in ["random", "standard"]:
        values = (
            data[data["log_type"] == log_type]
            .set_index("duration_group")
            .reindex(duration_groups)[metric]
        )
        ax.plot(
            duration_groups,
            values,
            marker="o",
            linewidth=2,
            label=log_type.replace("_", " ").title(),
            color=colors[log_type],
        )

    ax.set_title(title)
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=1))
    ax.spines[["top", "right"]].set_visible(False)

axes[0].set_ylabel("Share / ratio")
axes[0].legend(frameon=False)

fig.suptitle("Observed Feedback by Video Duration — Tab 1", fontweight="bold")
fig.text(
    0.5,
    0.01,
    "Positive-duration rows only; point counts are in watch_depth_by_duration.csv. "
    "Descriptive comparison, not a causal estimate.",
    ha="center",
    fontsize=8,
)
fig.tight_layout(rect=[0, 0.08, 1, 0.90])

output = project_root / "outputs" / "duration_feedback_trends.png"
fig.savefig(output, dpi=180, bbox_inches="tight")
print(f"Saved chart: {output}")