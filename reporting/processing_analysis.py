import pandas as pd
import os

# Path to the directory containing CSV files
directory_path = '../output/feedback/KeepPass'

# List to hold data from each CSV
dataframes = []

# Loop through all files in the directory
for filename in os.listdir(directory_path):
    if filename.endswith('.csv'):
        file_path = os.path.join(directory_path, filename)
        # Read each CSV file and append it to the list
        dataframes.append(pd.read_csv(file_path))

# Combine all dataframes into one
combined_data = pd.concat(dataframes, ignore_index=True)

# Optionally, save the combined dataframe to a new CSV file
output_file = 'output/feedback/KeepPass/combined_data.csv'
combined_data.to_csv(output_file, index=False)

print(f"Data combined successfully and saved to {output_file}.")
