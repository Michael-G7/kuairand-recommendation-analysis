import duckdb
import numpy as np

con = duckdb.connect()

paired = con.execute("""
WITH random_user AS (
    SELECT user_id, AVG(long_view) AS random_rate
    FROM read_csv_auto(
        'data/raw/KuaiRand-Pure/data/log_random_4_22_to_5_08_pure.csv'
    )
    WHERE tab = 1
    GROUP BY user_id
),
standard_user AS (
    SELECT user_id, AVG(long_view) AS standard_rate
    FROM read_csv_auto(
        'data/raw/KuaiRand-Pure/data/log_standard_4_22_to_5_08_pure.csv'
    )
    WHERE tab = 1
    GROUP BY user_id
)
SELECT r.user_id, r.random_rate, s.standard_rate
FROM random_user r
INNER JOIN standard_user s USING (user_id)
""").fetchdf()

user_diffs = (
    paired["random_rate"] - paired["standard_rate"]
).to_numpy()

rng = np.random.default_rng(42)
boot_means = np.empty(2000)

for i in range(2000):
    sampled = rng.integers(0, len(user_diffs), size=len(user_diffs))
    boot_means[i] = user_diffs[sampled].mean()

low, high = np.quantile(boot_means, [0.025, 0.975])

print(f"共同用户数: {len(user_diffs):,}")
print(f"平均用户差异: {user_diffs.mean() * 100:.2f} 个百分点")
print(f"95% 用户级 bootstrap 区间: [{low * 100:.2f}, {high * 100:.2f}] 个百分点")