import pandas as pd
import os

input_path = "R:/OneDrive/Desktop/fd/PS_20174392719_1491204439457_log.csv"
output_path = "R:/OneDrive/Desktop/fd/reduced_dataset.csv"

# Load dataset
df = pd.read_csv(input_path)

# ✅ 1. Select important features (based on fraud detection relevance)
df = df[
    [
        "step",
        "type",
        "amount",
        "oldbalanceOrg",
        "newbalanceOrig",
        "oldbalanceDest",
        "newbalanceDest",
        "isFraud"
    ]
]

# ✅ 2. Optimize data types (reduce size)
df["step"] = df["step"].astype("int32")
df["amount"] = df["amount"].astype("float32")
df["oldbalanceOrg"] = df["oldbalanceOrg"].astype("float32")
df["newbalanceOrig"] = df["newbalanceOrig"].astype("float32")
df["oldbalanceDest"] = df["oldbalanceDest"].astype("float32")
df["newbalanceDest"] = df["newbalanceDest"].astype("float32")
df["isFraud"] = df["isFraud"].astype("int8")

# Convert categorical column
df["type"] = df["type"].astype("category")

# ✅ 3. Stratified sampling (VERY IMPORTANT)
fraud_df = df[df["isFraud"] == 1]
nonfraud_df = df[df["isFraud"] == 0]

# Keep ALL fraud cases (rare → important)
fraud_sample = fraud_df

# Reduce non-fraud cases
nonfraud_sample = nonfraud_df.sample(frac=0.2, random_state=42)

# Combine
df_reduced = pd.concat([fraud_sample, nonfraud_sample])

# Shuffle dataset
df_reduced = df_reduced.sample(frac=1, random_state=42)

# ✅ 4. Save file
df_reduced.to_csv(output_path, index=False)

# Check size
size_mb = os.path.getsize(output_path) / (1024 * 1024)
print(f"✅ Final dataset size: {size_mb:.2f} MB")
print("Saved at:", output_path)