import pandas as pd
import numpy as np

# Assuming 'combined_data.csv' is the path to the combined CSV file
csv_file_path = '../output/analysis/KeepPass/updated_combined_data.csv'

# Load the CSV data into a pandas DataFrame
df = pd.read_csv(csv_file_path)

# Filter out specific sections
excluded_sections = ['Approvals', 'Test Plan Identifier', 'Glossary', 'References']
df = df[~df['Section'].isin(excluded_sections)]

# Define the ratings columns
rating_columns = ['Detail Rating', 'Clarity Rating', 'Relevance Rating', 'Overall Quality']

# Melt the DataFrame to make it easier to aggregate ratings
melted_df = pd.melt(df, id_vars=['Model Name', 'Section'], value_vars=rating_columns,
                    var_name='Rating Type', value_name='Rating')

# Calculate the total number of sections rated per model
total_sections_rated = melted_df.groupby('Model Name')['Section'].nunique()

# Find the highest rating received by each model
highest_rating = melted_df.groupby('Model Name')['Rating'].max()

# Find the lowest rating received by each model
lowest_rating = melted_df.groupby('Model Name')['Rating'].min()

# Find the most consistent section rating (mode) for each model
most_consistent_section = melted_df.groupby(['Model Name', 'Section'])['Rating'].agg(lambda x: pd.Series.mode(x)[0])
most_consistent_section = most_consistent_section.reset_index().groupby('Model Name')['Rating'].agg(pd.Series.mode)

# Create a summary DataFrame
feedback_summary = pd.DataFrame({
    'Model Name': total_sections_rated.index,
    'Total Sections Rated': total_sections_rated.values,
    'Highest Rating Received': highest_rating.values,
    'Lowest Rating Received': lowest_rating.values,
    'Most Consistent Section Rating': most_consistent_section.values
})

# Reset index to have a nice table
feedback_summary.reset_index(drop=True, inplace=True)

# Save the DataFrame to an Excel file
excel_file_path = '../output/analysis/KeepPass/feedback_summary.xlsx'
feedback_summary.to_excel(excel_file_path, index=False)

# Show the DataFrame
feedback_summary.head()
