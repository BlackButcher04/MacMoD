import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib

print("1. Pumping the raw fuel (Reading local NASA data)...")
# --- UPDATED: Pointing to your local file instead of the internet ---
# Make sure the file name perfectly matches what you downloaded
local_file_path = r"K:\vHack2026\SourceCode\MacMoD-New\NASA_CMAPSS_Data_Set\train_FD001.txt"

cols = ['engine_id', 'cycle', 'set1', 'set2', 'set3'] + [f'sensor_{i}' for i in range(1, 22)]
df = pd.read_csv(local_file_path, sep=r'\s+', header=None, names=cols)

print("2. Refining the fuel (Calculating RUL)...")
max_cycles = df.groupby('engine_id')['cycle'].max()
df['RUL'] = df.apply(lambda row: max_cycles[row['engine_id']] - row['cycle'], axis=1)

print("3. Assembling the engine (Selecting useful sensors)...")
useful_sensors = ['sensor_2', 'sensor_3', 'sensor_4', 'sensor_7', 'sensor_11', 'sensor_12', 'sensor_15']
X = df[useful_sensors] 
y = df['RUL']          

print("4. Creating the Final Exam (Splitting train/test data)...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("5. Starting combustion (Training the Random Forest)...")
model = RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42)
model.fit(X_train, y_train)

print("6. Validating the Model (Calculating MAE & RMSE)...")
predictions = model.predict(X_test)

mae = mean_absolute_error(y_test, predictions)
rmse = np.sqrt(mean_squared_error(y_test, predictions))

print("\n" + "="*40)
print("🏆 MODEL PERFORMANCE METRICS (FOR JUDGES)")
print("="*40)
print(f"Mean Absolute Error (MAE):      {mae:.2f} Cycles")
print(f"Root Mean Squared Error (RMSE): {rmse:.2f} Cycles")
print("="*40 + "\n")

print("7. Engine built! Saving to disk...")
joblib.dump(model, 'sme_engine.pkl')
print("Success! The validated 'sme_engine.pkl' is ready.")