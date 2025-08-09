import pandas as pd
import numpy as np
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test
import matplotlib.pyplot as plt

# === Load data ===
full_df = pd.read_excel("new_ready_caracterstics.xlsx")
tma_df = pd.read_excel("tma_mortality_test.xlsx")

# Convert date columns to datetime
for col in ["tma_date", "date_follow-up", "date_hsct"]:
    if col in full_df.columns:
        full_df[col] = pd.to_datetime(full_df[col], errors='coerce')
    if col in tma_df.columns:
        tma_df[col] = pd.to_datetime(tma_df[col], errors='coerce')

# Tag group
full_df["Group"] = "Non-TMA"
full_df.loc[full_df["id"].isin(tma_df["id"]), "Group"] = "TMA"

# Define start date
full_df["start_date"] = full_df.apply(
    lambda x: x["tma_date"] if pd.notnull(x["tma_date"]) else x["date_hsct"],
    axis=1
)

# Calculate survival time in days
full_df["time"] = (full_df["date_follow-up"] - full_df["start_date"]).dt.days

# Event flag (Dead = 1, Alive = 0)
full_df["event"] = full_df["Dead"].fillna(0).astype(int)

# Remove missing or invalid times
full_df = full_df.dropna(subset=["time", "event"])
full_df = full_df[full_df["time"] >= 0]

# Limit follow-up to 365 days
full_df.loc[full_df["time"] > 365, "time"] = 365
full_df.loc[full_df["time"] == 365, "event"] = 0  # censor at 1 year

# Log-rank test
tma_mask = full_df["Group"] == "TMA"
non_tma_mask = full_df["Group"] == "Non-TMA"
results = logrank_test(
    full_df.loc[tma_mask, "time"], full_df.loc[non_tma_mask, "time"],
    event_observed_A=full_df.loc[tma_mask, "event"],
    event_observed_B=full_df.loc[non_tma_mask, "event"]
)
p_value = results.p_value

# Format p-value nicely
if p_value < 0.001:
    p_text = "p < 0.001"
else:
    p_text = f"p = {p_value:.3f}"

# === Kaplan–Meier plot ===
plt.figure(figsize=(9, 6))
kmf = KaplanMeierFitter()
stats_rows = []

for group in ["TMA", "Non-TMA"]:
    mask = full_df["Group"] == group
    kmf.fit(full_df.loc[mask, "time"], full_df.loc[mask, "event"], label=group)
    kmf.plot_survival_function(ci_show=True, linewidth=2)

    # Median survival & 1-year survival
    median_surv = kmf.median_survival_time_
    surv_1yr = kmf.predict(365)

    stats_rows.append({
        "Group": group,
        "N": mask.sum(),
        "Events": int(full_df.loc[mask, "event"].sum()),
        "Median_days": median_surv,
        "1yr_survival_%": round(surv_1yr * 100, 1)
    })

plt.title("Survival Comparison: TMA vs Non-TMA (365-day)", fontsize=14, fontweight="bold")
plt.xlabel("Days since start", fontsize=12)
plt.ylabel("Survival probability", fontsize=12)
plt.grid(True, linestyle="--", alpha=0.6)

# === Build and place table ===
table_lines = ["Group      N   Events   Median(d)   1yr surv"]
for r in stats_rows:
    med = "∞" if (pd.isnull(r["Median_days"]) or np.isinf(r["Median_days"])) else str(int(r["Median_days"]))
    surv_pct = f"{r['1yr_survival_%']}%"
    table_lines.append(f"{r['Group']:<8}  {r['N']:<3}  {r['Events']:<6}   {med:<9}   {surv_pct}")

# Empty line before p-value for readability
table_lines.append("")
table_lines.append(f"{p_text}")

table_text = "\n".join(table_lines)

plt.gca().text(1.05, 0.5, table_text, transform=plt.gca().transAxes,
               fontsize=10, va="center", ha="left",
               bbox=dict(boxstyle="round,pad=0.6", fc="#f9f9f9", ec="gray", alpha=0.95),
               fontfamily="monospace")

plt.tight_layout()
plt.show()






