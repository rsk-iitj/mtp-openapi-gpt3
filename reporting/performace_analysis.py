import pandas as pd
# Load the combined data
file_path = 'output/feedback/KeepPass/combined_data.csv'
combined_data = pd.read_csv(file_path)

# Calculate the average ratings for each model
performance_overview = combined_data.groupby('Model Name').agg({
    'Detail Rating': 'mean',
    'Clarity Rating': 'mean',
    'Relevance Rating': 'mean',
    'Overall Quality': 'mean'
}).reset_index()

# Rename columns to match the required table format
performance_overview.columns = [
    'Model Name', 'Average Detail Rating', 'Average Clarity Rating',
    'Average Relevance Rating', 'Overall Quality'
]

performance_overview.to_excel('output/feedback/KeepPass/performance_overview.xlsx', index=False)

# Show the table

print(performance_overview)



