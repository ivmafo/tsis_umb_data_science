import pandas as pd
import numpy as np

# Read the data
data = pd.read_csv('c:/Users/LENOVO/Documents/proyecto4/proyecto/workspace/tsis_umb_data_science/resultados/data.csv')

# Calculate percentiles
lower_bound = np.percentile(data['revenue'], 1)
upper_bound = np.percentile(data['revenue'], 99)

# Get non-outlier values
normal_values = data[(data['revenue'] >= lower_bound) & (data['revenue'] <= upper_bound)]['revenue']

# Get min and max of normal values
min_normal = normal_values.min()
max_normal = normal_values.max()

print(f"Original revenue range: {data['revenue'].min():.2f} to {data['revenue'].max():.2f}")
print(f"1st percentile: {lower_bound:.2f}")
print(f"99th percentile: {upper_bound:.2f}")
print(f"Normal range: {min_normal:.2f} to {max_normal:.2f}")
print(f"Number of lower outliers: {len(data[data['revenue'] < lower_bound])}")
print(f"Number of upper outliers: {len(data[data['revenue'] > upper_bound])}")

# Replace outliers
data.loc[data['revenue'] < lower_bound, 'revenue'] = min_normal
data.loc[data['revenue'] > upper_bound, 'revenue'] = max_normal

# Save updated data
data.to_csv('c:/Users/LENOVO/Documents/proyecto4/proyecto/workspace/tsis_umb_data_science/resultados/data.csv', index=False)

print("\nData has been updated and saved.")