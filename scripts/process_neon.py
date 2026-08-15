import pandas as pd
import glob
import os

INPUT_DIR = "neon_raw"
OUTPUT = "neon_clean.csv"

files = glob.glob(f"{INPUT_DIR}/*waq_instantaneous*.csv")

print(f"Found {len(files)} files")

data = []

for file in files:
    print("Reading:", os.path.basename(file))

    df = pd.read_csv(file)

    # Extract metadata from filename
    name = os.path.basename(file)

    parts = name.split("_")

    site = parts[0]
    month = parts[1]

    df["site"] = site
    df["month"] = month

    data.append(df)


print("Combining files...")

df = pd.concat(data, ignore_index=True)


print("Original rows:", len(df))


# Convert time
df["timestamp"] = pd.to_datetime(df["startDateTime"])


# Keep only useful ML columns

columns = [
    "timestamp",
    "site",
    "sensorDepth",
    "specificConductance",
    "dissolvedOxygen",
    "pH",
    "chlorophyll",
    "turbidity",
    "fDOM",

    "specificCondFinalQF",
    "dissolvedOxygenFinalQF",
    "pHFinalQF",
    "chlorophyllFinalQF",
    "turbidityFinalQF",
    "fDOMFinalQF"
]


df = df[columns]


# Remove failed quality measurements

qf_columns = [
    "specificCondFinalQF",
    "dissolvedOxygenFinalQF",
    "pHFinalQF",
    "chlorophyllFinalQF",
    "turbidityFinalQF",
    "fDOMFinalQF"
]


for col in qf_columns:
    df = df[(df[col] == 0) | (df[col].isna())]


print("After quality filtering:", len(df))


# Remove rows with no main measurements

features = [
    "pH",
    "dissolvedOxygen",
    "specificConductance",
    "turbidity",
    "fDOM"
]


df = df.dropna(subset=features)


print("After removing missing values:", len(df))


# Sort by time

df = df.sort_values(
    ["site", "timestamp"]
)


# Save

df.to_csv(
    OUTPUT,
    index=False
)


print("Saved:", OUTPUT)
