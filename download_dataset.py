from datasets import load_dataset
import pandas as pd
import os

# Create data folder
os.makedirs("data", exist_ok=True)

# Load healthcare dataset
dataset = load_dataset("medalpaca/medical_meadow_medqa")

# Convert dataset into dataframe
df = pd.DataFrame(dataset["train"])

# Save dataset locally
df.to_csv("data/medical_dataset.csv", index=False)

print("Dataset downloaded successfully!")
print(df.head())