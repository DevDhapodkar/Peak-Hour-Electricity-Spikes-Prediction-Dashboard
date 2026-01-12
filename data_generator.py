import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_dorm_data(dorm_name, days=14):
    np.random.seed(hash(dorm_name) % 2**32)
    end_date = datetime.now().replace(minute=0, second=0, microsecond=0)
    start_date = end_date - timedelta(days=days)
    
    date_range = pd.date_range(start=start_date, end=end_date, freq='H')
    
    # Base load + Daily Seasonality (peaks in evening 18:00 - 22:00)
    # Sinusoidal baseline + peak Gaussian centered at 20:00
    base_load = 50 + 20 * np.sin(2 * np.pi * (date_range.hour - 6) / 24)
    peak_gaussian = 100 * np.exp(-0.5 * ((date_range.hour - 20) / 2)**2)
    
    noise = np.random.normal(0, 10, len(date_range))
    
    usage = base_load + peak_gaussian + noise
    usage = np.maximum(0, usage) # Ensure no negative usage
    
    df = pd.DataFrame({
        'timestamp': date_range,
        'dorm': dorm_name,
        'usage_kwh': usage
    })
    
    return df

def main():
    dorms = ['Dorm A', 'Dorm B', 'Dorm C']
    all_data = []
    
    for dorm in dorms:
        all_data.append(generate_dorm_data(dorm))
    
    df = pd.concat(all_data, ignore_index=True)
    df.to_csv('electricity_data.csv', index=False)
    print(f"Generated {len(df)} rows of data and saved to electricity_data.csv")

if __name__ == "__main__":
    main()
