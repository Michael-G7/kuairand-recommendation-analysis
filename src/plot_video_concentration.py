from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd

project_root = Path(__file__).resolve().parents[1]
data_dir = project_root / "data/raw/KuaiRand-Pure/data"

con = duckdb.connect()
curves = con.execute(f"""
WITH logs AS (
    SELECT 'random' AS log_type, video_id
    FROM read_csv_auto('{data_dir}/log_random_4_22_to_5_08_pure.csv')
    WHERE tab = 1

    UNION ALL

    SELECT 'standard', video_id
    FROM read_csv_auto('{data_dir}/log_standard_4_22_to_5_08_pure.csv')
    WHERE tab = 1
),
per_video AS (
    SELECT log_type, video_id, COUNT(*) AS log_rows
    FROM logs
    GROUP BY log_type, video_id
),
ranked AS (
    SELECT
        log_type,
        log_rows,
        ROW_NUMBER() OVER (
            PARTITION BY log_type ORDER BY log_rows, video_id
        ) AS item_rank,
        COUNT(*) OVER (PARTITION BY log_type) AS video_count,
        SUM(log_rows) OVER (PARTITION BY log_type) AS total_rows,
        SUM(log_rows) OVER (
            PARTITION BY log_type
            ORDER BY log_rows, video_id
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_rows
    FROM per_video
)
SELECT
    log_type,
    1.0 * item_rank / video_count AS cumulative_video_share,
    1.0 * cumulative_rows / total_rows AS cumulative_log_share
FROM ranked
ORDER BY log_type, item_rank
""").fetchdf()

summary = pd.read_csv(project_root / "outputs" / "video_log_concentration.csv")

fig, ax = plt.subplots(figsize=(7, 7))
colors = {"random": "#45A29E", "standard": "#4056A1"}

for log_type in ["random", "standard"]:
    curve = curves[curves["log_type"] == log_type]
    top10 = summary.loc[
        summary["log_type"] == log_type,
        "top_10pct_video_row_share",
    ].iloc[0]

    x = [0] + curve["cumulative_video_share"].tolist()
    y = [0] + curve["cumulative_log_share"].tolist()
    ax.plot(
        x,
        y,
        linewidth=2,
        color=colors[log_type],
        label=f"{log_type.title()} (top 10% share: {top10:.1%})",
    )

ax.plot([0, 1], [0, 1], "--", color="gray", label="Equal distribution")
ax.set(
    xlabel="Cumulative share of observed video IDs",
    ylabel="Cumulative share of log rows",
    title="Video-Level Log Concentration — Tab 1",
    xlim=(0, 1),
    ylim=(0, 1),
)
ax.set_aspect("equal", adjustable="box")
ax.legend(frameon=False, loc="upper left")
ax.spines[["top", "right"]].set_visible(False)

fig.text(
    0.5,
    0.01,
    "Distribution of logged rows, not verified impressions or exposure opportunities.",
    ha="center",
    fontsize=9,
)
fig.tight_layout(rect=[0, 0.04, 1, 1])

output = project_root / "outputs" / "video_log_lorenz.png"
fig.savefig(output, dpi=180, bbox_inches="tight")
print(f"Saved chart: {output}")