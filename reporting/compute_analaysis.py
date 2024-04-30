import pandas as pd

# Load the CSV data into a pandas DataFrame
csv_file_path = '../output/analysis/KeepPass/updated_combined_data.csv'
df = pd.read_csv(csv_file_path)

# Define cost factors for each model based on model complexity
cost_factors = {
    'gpt-3.5-turbo': 1.0,
    'gpt-3.5-turbo-1106': 1.05,
    'gpt-3.5-turbo-16k-0613': 1.1,
    'gpt-3.5-turbo-16k': 1.1,
    'gpt-3.5-turbo-0125': 1.0,
    'gpt-4-turbo-preview': 1.5,
    'gpt-4-turbo-2024-04-09': 1.55,
    'gpt-4-turbo': 1.5,
}

# Calculate the 'Overall Feedback' Generation Time by summing the Generation Times of the 20 sections
overall_feedback_time = df.groupby('Model Name')['Generation Time'].sum()

# Append the 'Overall Feedback' Generation Time to the original dataframe
# Assuming 'Overall Feedback' is a section in the dataset
df_overall_feedback = df[df['Section'] == 'Overall Feedback'].copy()
df_overall_feedback['Generation Time'] = df_overall_feedback['Model Name'].map(overall_feedback_time)

# Append this back to the original dataframe
df = df.append(df_overall_feedback, ignore_index=True)

# Exclude 'Overall Feedback' section when calculating average processing time and cost
df_without_overall = df[df['Section'] != 'Overall Feedback']

# Function to calculate computational cost
def compute_cost(row):
    base_cost_per_word = 0.0005  # base cost per word for GPT-3.5, adjust based on actual data
    model_factor = cost_factors.get(row['Model Name'], 1)  # default to 1 if model not in cost_factors
    return row['Word Count'] * base_cost_per_word * model_factor

# Calculate the computational cost for each row
df_without_overall['Computational Cost'] = df_without_overall.apply(compute_cost, axis=1)

# Calculate the average processing time for each model
average_processing_time = df_without_overall.groupby('Model Name')['Generation Time'].mean()

# Calculate the average computational cost for each model
average_computational_cost = df_without_overall.groupby('Model Name')['Computational Cost'].mean()

# Create the summary DataFrame
computational_efficiency = pd.DataFrame({
    'Model Name': average_processing_time.index,
    'Average Processing Time (sec)': average_processing_time.values,
    'Average Computational Cost ($)': average_computational_cost.values
})

# Reset index to have a nice table
computational_efficiency.reset_index(drop=True, inplace=True)

# Save the DataFrame to an Excel file
excel_file_path = '../output/analysis/KeepPass/computational_efficiency.xlsx'
computational_efficiency.to_excel(excel_file_path, index=False)

# Display the DataFrame
computational_efficiency.head()
