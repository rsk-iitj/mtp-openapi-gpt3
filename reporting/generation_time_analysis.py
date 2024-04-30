import pandas as pd

# Load the CSV data into a pandas DataFrame
csv_file_path = '../output/analysis/KeepPass/updated_combined_data.csv'  # Update with your actual file path
df = pd.read_csv(csv_file_path)

# Ensure 'Generation Time' is a numeric type for calculations
df['Generation Time'] = pd.to_numeric(df['Generation Time'], errors='coerce')

# Sum the 'Generation Time' for the first 20 sections for each model
# Assuming the sections are ordered and the first 20 rows for each model are the sections to be summed
df['Overall Test Plan Time'] = df.groupby('Model Name')['Generation Time'].transform(lambda x: x.iloc[:20].sum())

# Now, group by 'Section' and calculate the mean 'Generation Time' for each section
section_times = df.groupby('Section')['Generation Time'].mean().reset_index(name='Average Generation Time')

# Separately, calculate the average of 'Overall Test Plan Time' across all models
overall_average_time = df[['Model Name', 'Overall Test Plan Time']].drop_duplicates()
overall_average_time = overall_average_time.groupby('Model Name').mean().reset_index()
overall_average_time.columns = ['Model Name', 'Average Overall Test Plan Time']  # Renaming the columns correctly

# Concatenate the two DataFrames
complete_average_times = pd.concat([section_times, overall_average_time], ignore_index=True)

# Save the DataFrame to an Excel file
excel_file_path = '../output/analysis/KeepPass/average_generation_time_including_overall.xlsx'
complete_average_times.to_excel(excel_file_path, index=False)

# Confirmation message
print(f"Average generation time per section, including overall test plan time, has been saved to {excel_file_path}")
