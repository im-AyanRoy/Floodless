import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# Load the dataset
data = pd.read_csv("/Users/anikchand/Documents/Floodless/floodless/prediction/templates/apply_models/drought_cleaned.csv")

# Step 1: Feature Engineering
# Encode categorical variables
label_encoder_country = LabelEncoder()
label_encoder_location = LabelEncoder()

data['Country'] = label_encoder_country.fit_transform(data['Country'])
data['Location'] = label_encoder_location.fit_transform(data['Location'])

# Features and targets
X = data[['Year', 'Country', 'Location']]
y_total_affected = data['Total Affected']
y_magnitude = data['Magnitude']

# Train-test split
X_train, X_test, y_train_total, y_test_total = train_test_split(X, y_total_affected, test_size=0.2, random_state=42)
_, _, y_train_magnitude, y_test_magnitude = train_test_split(X, y_magnitude, test_size=0.2, random_state=42)

# Step 2: Train XGBoost Regressors
xgb_total_affected = XGBRegressor(random_state=42, n_estimators=100, learning_rate=0.1, max_depth=6)
xgb_magnitude = XGBRegressor(random_state=42, n_estimators=100, learning_rate=0.1, max_depth=6)

xgb_total_affected.fit(X_train, y_train_total)
xgb_magnitude.fit(X_train, y_train_magnitude)

# Evaluate the models
print("Total Affected R^2 Score:", xgb_total_affected.score(X_test, y_test_total))
print("Magnitude R^2 Score:", xgb_magnitude.score(X_test, y_test_magnitude))

# Step 3: Generate Future Predictions
future_years = list(range(2026, 2034))  # Predict for 2026–2033

# Get unique combinations of Country and Location from historical data
unique_combinations = data[['Country', 'Location']].drop_duplicates().reset_index(drop=True)

# Randomly sample a subset of unique combinations to limit the output size
num_samples = 10  # Number of unique combinations to sample
sampled_combinations = unique_combinations.sample(n=num_samples, random_state=42).reset_index(drop=True)

# Create future data using only sampled combinations
future_data = []
for year in future_years:
    for _, row in sampled_combinations.iterrows():
        country = row['Country']
        location = row['Location']
        future_data.append([year, country, location])

# Convert to DataFrame
future_df = pd.DataFrame(future_data, columns=['Year', 'Country', 'Location'])

# Predict Total Affected and Magnitude
future_df['Total Affected'] = xgb_total_affected.predict(future_df[['Year', 'Country', 'Location']])
future_df['Magnitude'] = xgb_magnitude.predict(future_df[['Year', 'Country', 'Location']])

# Decode categorical variables back to original names
future_df['Country'] = label_encoder_country.inverse_transform(future_df['Country'].astype(int))
future_df['Location'] = label_encoder_location.inverse_transform(future_df['Location'].astype(int))

# Save the future dataset
future_df.to_csv("draught_final.csv", index=False)

print("Future predictions saved to 'draught_final.csv'")