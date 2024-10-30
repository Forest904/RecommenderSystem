

#script to remove specified columns from a CSV file
import pandas as pd

# Load the CSV file
input_file = 'src/imdb.csv'  # Replace with your input file path
output_file = 'src/datasets/output.csv'  # Replace with your desired output file path

# Specify the columns you want to remove
columns_to_remove = ['Poster_Link']  # Replace with the names of columns you want to drop

# Read the data
df = pd.read_csv(input_file)

# Remove the specified columns
df = df.drop(columns=columns_to_remove, errors='ignore')  # `errors='ignore'` avoids errors if column not found

# Save the modified DataFrame to a new CSV file
df.to_csv(output_file, index=False)

print(f"The file with specified columns removed has been saved as {output_file}.")
