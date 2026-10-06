from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

project_root = Path(__file__).resolve().parents[1]
data = pd.read_csv(project_root / "outputs" / "long_view_by_activity.csv")

segments = ["full_active", "high_active", "middle_active"]
plot_data = (
    data[data["activity_segment"].isin(segments)]
    .set_index("activity_segment")
    .loc[segments]
)

y = np.arange(len(plot_data))
height = 0.34

random_values = plot_data["avg_user_random_long_view_rate"].to_numpy() * 100
standard_values = plot_data["avg_user_standard_long_view_rate"].to_numpy() * 100
counts = plot_data["common_users"].to_numpy()

fig, ax = plt.subplots(figsize=(10, 5))

random_bars = ax.barh(
    y - height / 2,
    random_values,
    height,
    label="Random exposure",
    color="#45A29E",
)
standard_bars = ax.barh(
    y + height / 2,
    standard_values,
    height,
    label="Standard recommendation",
    color="#4056A1",
)

ax.bar_label(random_bars, labels=[f"{v:.1f}%" for v in random_values], padding=4)
ax.bar_label(standard_bars, labels=[f"{v:.1f}%" for v in standard_values], padding=4)

ax.set_yticks(
    y,
    [f"{segment}  (n={count:,})"
     for segment, count in zip(segments, counts)],
)
ax.invert_yaxis()
ax.set_xlabel("Average user-level long-view signal rate (%)")
ax.set_title("Observed Long-View Rates by User Segment — Tab 1")
ax.legend(frameon=False)
ax.spines[["top", "right"]].set_visible(False)
ax.set_xlim(0, max(standard_values) * 1.22)

fig.text(
    0.5,
    0.01,
    "Common users in each segment; descriptive comparison, not a causal estimate.",
    ha="center",
    fontsize=9,
)
fig.tight_layout(rect=[0, 0.06, 1, 1])

output = project_root / "outputs" / "activity_segment_comparison.png"
fig.savefig(output, dpi=180, bbox_inches="tight")
print(f"Saved chart: {output}")