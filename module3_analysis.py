import pandas as pd
from scipy import stats
import json

df = pd.read_csv("sample_preprocessed_data.csv")

numeric_cols = df.select_dtypes(include="number").columns.tolist()
if "Year" in numeric_cols:
    numeric_cols.remove("Year")

all_findings = []

for col in numeric_cols:
    values = df[col].dropna().values
    x = range(len(values))

    slope, intercept, r, p, se = stats.linregress(x, values)
    r_squared = round(r ** 2, 4)

    if p > 0.05:
        direction = "Stable"
    elif slope > 0:
        direction = "Increasing"
    else:
        direction = "Decreasing"

    all_findings.append({
        "type": "Trend",
        "column": col,
        "direction": direction,
        "slope": round(slope, 4),
        "p_value": round(p, 4),
        "r_squared": r_squared,
        "score": r_squared
    })

corr_matrix = df[numeric_cols].corr(method="pearson").round(3)
cols = numeric_cols

for i in range(len(cols)):
    for j in range(i + 1, len(cols)):
        r_val = round(float(corr_matrix.loc[cols[i], cols[j]]), 3)

        if abs(r_val) >= 0.8:
            strength = "Very Strong"
        elif abs(r_val) >= 0.6:
            strength = "Strong"
        elif abs(r_val) >= 0.4:
            strength = "Moderate"
        else:
            strength = "Weak"

        if r_val > 0:
            direction = "positive"
        else:
            direction = "negative"

        all_findings.append({
            "type": "Correlation",
            "col_a": cols[i],
            "col_b": cols[j],
            "r": r_val,
            "strength": strength,
            "direction": direction,
            "score": round(abs(r_val), 4)
        })

all_findings.sort(key=lambda x: x["score"], reverse=True)
top_10 = all_findings[:10]

print("TOP 10 FINDINGS")
print("=" * 55)
for i, f in enumerate(top_10, 1):
    if f["type"] == "Trend":
        print(f"  {i}. [Trend] {f['column']} is {f['direction']} (R²={f['r_squared']})")
    else:
        print(f"  {i}. [Correlation] {f['col_a']} & {f['col_b']}: {f['strength']} {f['direction']} (r={f['r']})")

with open("results.json", "w") as f:
    json.dump(top_10, f, indent=2)

def run_analysis():
    return top_10

result = run_analysis()
