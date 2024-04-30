import pandas as pd
import numpy as np

# Example data loading (replace this with the path to your actual CSV file)
data = pd.read_csv('output/feedback/KeepPass/combined_data.csv')

# Group by 'Section' and calculate mean and standard deviation for each section's generation time
section_stats = data.groupby('Section')['Generation Time'].agg(['mean', 'std'])

# Function to generate a random time based on section stats
def generate_random_time(section, mean, std):
    # If standard deviation is NaN (only one value for section), just return the mean
    if pd.isna(std):
        return mean
    # Otherwise, draw from a normal distribution around the mean with the given standard deviation
    return max(0, np.random.normal(mean, std))

# Apply the function to rows with missing generation times
for index, row in data[data['Generation Time'].isnull()].iterrows():
    section = row['Section']
    mean, std = section_stats.loc[section]
    data.at[index, 'Generation Time'] = generate_random_time(section, mean, std)

# Check the data and save it to a new CSV file
print(data.head())
data.to_csv('output/feedback/KeepPass/updated_combined_data.csv', index=False)
