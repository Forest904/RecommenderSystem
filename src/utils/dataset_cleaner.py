import pandas as pd

# Load your dataset into a DataFrame
df = pd.read_csv('')  # Replace with your data source

# Dictionary to keep track of deletions per attribute
deletions = {}

# Iterate over each column in the DataFrame
for column in df.columns:
    # Count the number of NaNs in the current column
    num_nans = df[column].isna().sum()
    deletions[column] = num_nans
    
    # Remove rows where the current column has NaN values
    df = df[df[column].notna()].reset_index(drop=True)

# Display the number of deletions per attribute
print("Number of deletions per attribute:")
for attr, num in deletions.items():
    print(f"{attr}: {num}")

# Optionally, save the cleaned DataFrame to a new CSV file
df.to_csv('cleaned_dataset.csv', index=False)
