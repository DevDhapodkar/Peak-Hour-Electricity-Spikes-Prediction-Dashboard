import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import timedelta

def apply_moving_average(df, window=3):
    """Applies moving average smoothing to the usage_kwh column."""
    df = df.copy()
    df['smoothed_usage'] = df.groupby('dorm')['usage_kwh'].transform(
        lambda x: x.rolling(window=window, center=True).mean()
    )
    # Fill NaNs from rolling window at edges
    df['smoothed_usage'] = df['smoothed_usage'].fillna(df['usage_kwh'])
    return df

def predict_peak(dorm_df):
    """
    Predicts today's evening peak usage base on the past week.
    Uses linear regression on peak values from previous days.
    """
    # Identify daily peaks (usually in 18:00 - 22:00 range)
    dorm_df = dorm_df.copy()
    dorm_df['date'] = dorm_df['timestamp'].dt.date
    dorm_df['hour'] = dorm_df['timestamp'].dt.hour
    
    # Filter for evening hours to find peaks
    evening_df = dorm_df[(dorm_df['hour'] >= 18) & (dorm_df['hour'] <= 22)]
    daily_peaks = evening_df.groupby('date')['usage_kwh'].max().reset_index()
    
    # We need at least 2 days to regress
    if len(daily_peaks) < 2:
        return None
    
    # Prepare data for Linear Regression
    # X: days since start, y: peak usage
    daily_peaks['day_index'] = np.arange(len(daily_peaks))
    X = daily_peaks[['day_index']]
    y = daily_peaks['usage_kwh']
    
    model = LinearRegression()
    model.fit(X, y)
    
    # Predict next day's peak
    next_day_df = pd.DataFrame({'day_index': [len(daily_peaks)]})
    predicted_peak = model.predict(next_day_df)[0]
    
    return float(predicted_peak)

def get_processed_data(file_path='electricity_data.csv'):
    df = pd.read_csv(file_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Apply smoothing
    df = apply_moving_average(df)
    
    # Get predictions for each dorm
    predictions = {}
    for dorm in df['dorm'].unique():
        dorm_df = df[df['dorm'] == dorm]
        pred = predict_peak(dorm_df)
        predictions[dorm] = pred
        
    return df, predictions

if __name__ == "__main__":
    # Test run
    import os
    if os.path.exists('electricity_data.csv'):
        df, preds = get_processed_data()
        print("Predictions for tomorrow's peaks:")
        for dorm, val in preds.items():
            print(f"{dorm}: {val:.2f} kwh")
    else:
        print("electricity_data.csv not found. Run data_generator.py first.")
