import pandas as pd

# Path to the CSV file (adjust the path to your actual CSV file location)
csv_file_path = '../output/analysis/KeepPass/updated_combined_data.csv'

# Load the CSV data into a pandas DataFrame
df = pd.read_csv(csv_file_path)

# Pivot the data to have 'Section' as the index and 'Model Name' as the columns,
# with 'Detail Rating' as the values. We'll use the mean for aggregation.
pivot_df = df.pivot_table(index='Section', columns='Model Name', values='Relevance Rating', aggfunc='mean')

# Fill any missing values with a predefined constant or an average. Here we use the average of the column.
pivot_df = pivot_df.fillna(pivot_df.mean(axis=0))

# Optionally, sort the index or columns if required for better readability.
# For example, sort by Section name
pivot_df = pivot_df.sort_index()

# Save the pivoted DataFrame to a new CSV file if needed
output_csv_path = '../output/analysis/Relevance.csv'
pivot_df.to_csv(output_csv_path)

print(pivot_df.head())  # Display the first few entries
