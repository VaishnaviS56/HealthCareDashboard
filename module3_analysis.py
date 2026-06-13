# Module 3: Trend and Correlation Analysis


import pandas as pd
from scipy import stats
import json

df = pd.read_csv("sample_preprocessed_data.csv")

print("Data loaded successfully!")
print("Number of rows:", len(df))
print("Columns found:", list(df.columns))
print()


numeric_cols = df.select_dtypes(include="number").columns.tolist()


if "Year" in numeric_cols:
    numeric_cols.remove("Year")

print("Columns I will analyse:", numeric_cols)
print()



print("=" * 50)
print("TREND ANALYSIS")
print("=" * 50)

trend_results = {}

for col in numeric_cols:
    values = df[col].dropna().values          # get the values
    x = range(len(values))                    # 0, 1, 2, 3 ... (position in time)

    slope, intercept, r, p, se = stats.linregress(x, values)

    # Decide direction based on slope and p-value
    if p > 0.05:
        direction = "Stable"
    elif slope > 0:
        direction = "Increasing"
    else:
        direction = "Decreasing"

    trend_results[col] = {
        "direction": direction,
        "slope": round(slope, 4),
        "p_value": round(p, 4)
    }

    print(f"  {col}: {direction}  (slope={round(slope,4)}, p={round(p,4)})")

print()



print("=" * 50)
print("CORRELATION ANALYSIS")
print("=" * 50)

corr_matrix = df[numeric_cols].corr(method="pearson").round(3)


pairs = []
cols = numeric_cols

for i in range(len(cols)):
    for j in range(i + 1, len(cols)):
        r_value = corr_matrix.loc[cols[i], cols[j]]
        pairs.append((cols[i], cols[j], r_value))


pairs.sort(key=lambda x: abs(x[2]), reverse=True)

print("Top correlated column pairs:")
for col_a, col_b, r_val in pairs[:8]:
    if abs(r_val) >= 0.8:
        strength = "Very Strong"
    elif abs(r_val) >= 0.6:
        strength = "Strong"
    elif abs(r_val) >= 0.4:
        strength = "Moderate"
    else:
        strength = "Weak"

    direction = "positive" if r_val > 0 else "negative"
    print(f"  {col_a} & {col_b}: r={r_val} → {strength} {direction}")

print()

output = {
    "trend_analysis": trend_results,
    "top_correlations": [
        {"col_a": a, "col_b": b, "r": r} for a, b, r in pairs[:8]
    ]
}

with open("results.json", "w") as f:
    json.dump(output, f, indent=2)

print("Results saved to results.json")
print("Done!")
