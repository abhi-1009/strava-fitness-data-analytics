import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
DATA_DIR = 'CSV_DATA'
OUT_DIR = 'plots'
os.makedirs(OUT_DIR, exist_ok=True)
sns.set_theme(style='whitegrid')
DT_FMT_DATE = '%m/%d/%Y'
DT_FMT_DATETIME = '%m/%d/%Y %I:%M:%S %p'

def read(name):
    return pd.read_csv(f'{DATA_DIR}/{name}')
daily_activity = read('dailyActivity_merged.csv')
sleep_day = read('sleepDay_merged.csv')
weight_log = read('weightLogInfo_merged.csv')
hourly_cal = read('hourlyCalories_merged.csv')
hourly_int = read('hourlyIntensities_merged.csv')
hourly_steps = read('hourlySteps_merged.csv')
heart_sec = read('heartrate_seconds_merged.csv')
minute_mets = read('minuteMETsNarrow_merged.csv')
print('Raw row counts:')
for name, df in [('daily_activity', daily_activity), ('sleep_day', sleep_day), ('weight_log', weight_log), ('hourly_cal', hourly_cal), ('hourly_int', hourly_int), ('hourly_steps', hourly_steps), ('heart_sec', heart_sec), ('minute_mets', minute_mets)]:
    print(f'  {name:15s}: {len(df):>9,} rows, {df['Id'].nunique():2d} unique Ids')
daily_activity['ActivityDate'] = pd.to_datetime(daily_activity['ActivityDate'], format=DT_FMT_DATE).dt.date
sleep_day['ActivityDate'] = pd.to_datetime(sleep_day['SleepDay'], format=DT_FMT_DATETIME).dt.date
weight_log['ActivityDate'] = pd.to_datetime(weight_log['Date'], format=DT_FMT_DATETIME).dt.date
for df, col in [(hourly_cal, 'ActivityHour'), (hourly_int, 'ActivityHour'), (hourly_steps, 'ActivityHour')]:
    df[col] = pd.to_datetime(df[col], format=DT_FMT_DATETIME)
heart_sec['Time'] = pd.to_datetime(heart_sec['Time'], format=DT_FMT_DATETIME)
minute_mets['ActivityMinute'] = pd.to_datetime(minute_mets['ActivityMinute'], format=DT_FMT_DATETIME)
before = len(sleep_day)
sleep_day = sleep_day.drop_duplicates(subset=['Id', 'ActivityDate', 'TotalSleepRecords', 'TotalMinutesAsleep', 'TotalTimeInBed'])
print(f'\nsleep_day: dropped {before - len(sleep_day)} exact duplicate rows')
daily_activity['LikelyNotWorn'] = daily_activity['SedentaryMinutes'] >= 1440
weight_log = weight_log.drop(columns=['Fat'], errors='ignore')
heart_daily = heart_sec.assign(ActivityDate=heart_sec['Time'].dt.date).groupby(['Id', 'ActivityDate'], as_index=False).agg(AvgHeartRate=('Value', 'mean'), MinHeartRate=('Value', 'min'), MaxHeartRate=('Value', 'max'))
met_daily = minute_mets.assign(ActivityDate=minute_mets['ActivityMinute'].dt.date).groupby(['Id', 'ActivityDate'], as_index=False).agg(AvgMET=('METs', 'mean'))
met_daily['AvgMET'] = met_daily['AvgMET'] / 10
intensity_daily = hourly_int.assign(ActivityDate=hourly_int['ActivityHour'].dt.date).groupby(['Id', 'ActivityDate'], as_index=False).agg(AvgIntensity=('AverageIntensity', 'mean'), TotalIntensity=('TotalIntensity', 'sum'))
hourly_merged = hourly_cal.merge(hourly_steps, on=['Id', 'ActivityHour'], how='outer').merge(hourly_int, on=['Id', 'ActivityHour'], how='outer')
heart_hourly = heart_sec.assign(ActivityHour=heart_sec['Time'].dt.floor('h')).groupby(['Id', 'ActivityHour'], as_index=False).agg(AvgHeartRate=('Value', 'mean'))
hourly_merged = hourly_merged.merge(heart_hourly, on=['Id', 'ActivityHour'], how='left')
hourly_merged['ActivityDate'] = hourly_merged['ActivityHour'].dt.date
hourly_merged['Hour'] = hourly_merged['ActivityHour'].dt.hour
hourly_merged['Weekday'] = pd.to_datetime(hourly_merged['ActivityDate']).dt.day_name()
daily = daily_activity.merge(sleep_day[['Id', 'ActivityDate', 'TotalSleepRecords', 'TotalMinutesAsleep', 'TotalTimeInBed']], on=['Id', 'ActivityDate'], how='left')
daily = daily.merge(weight_log[['Id', 'ActivityDate', 'WeightKg', 'BMI', 'IsManualReport']], on=['Id', 'ActivityDate'], how='left')
daily = daily.merge(heart_daily, on=['Id', 'ActivityDate'], how='left')
daily = daily.merge(met_daily, on=['Id', 'ActivityDate'], how='left')
daily = daily.merge(intensity_daily, on=['Id', 'ActivityDate'], how='left')
daily['Weekday'] = pd.to_datetime(daily['ActivityDate']).dt.day_name()
print(f'\nFinal daily table: {len(daily):,} rows x {daily.shape[1]} columns')
print(f'Final hourly table: {len(hourly_merged):,} rows x {hourly_merged.shape[1]} columns')
print('\nDaily table missing-value % per column:')
print((daily.isna().mean() * 100).round(1).sort_values(ascending=False))
daily.to_csv('bellabeat_daily_clean.csv', index=False)
hourly_merged.to_csv('bellabeat_hourly_clean.csv', index=False)
print('\nSaved -> bellabeat_daily_clean.csv and bellabeat_hourly_clean.csv (load these into MySQL in Step 2)')
weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
plt.figure(figsize=(8, 5))
sns.barplot(data=daily, x='Weekday', y='TotalSteps', order=weekday_order, estimator=np.mean, errorbar=None, hue='Weekday', legend=False, palette='viridis')
plt.title('Average Daily Steps by Weekday')
plt.ylabel('Avg. Total Steps')
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/avg_steps_by_weekday.png', dpi=150)
plt.close()
plt.figure(figsize=(8, 5))
sns.histplot(daily['SedentaryMinutes'], bins=30, kde=True)
plt.title('Distribution of Sedentary Minutes')
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/sedentary_minutes_dist.png', dpi=150)
plt.close()
sleep_subset = daily.dropna(subset=['TotalMinutesAsleep'])
plt.figure(figsize=(8, 5))
sns.regplot(data=sleep_subset, x='SedentaryMinutes', y='TotalMinutesAsleep', scatter_kws={'alpha': 0.4})
plt.title('Sedentary Minutes vs. Minutes Asleep')
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/sedentary_vs_sleep.png', dpi=150)
plt.close()
num_cols = ['TotalSteps', 'TotalDistance', 'VeryActiveMinutes', 'FairlyActiveMinutes', 'LightlyActiveMinutes', 'SedentaryMinutes', 'Calories', 'TotalMinutesAsleep', 'AvgHeartRate', 'AvgIntensity', 'AvgMET']
plt.figure(figsize=(9, 7))
sns.heatmap(daily[num_cols].corr(), annot=True, fmt='.2f', cmap='coolwarm', center=0)
plt.title('Correlation Heatmap - Key Activity/Sleep/Heart Rate/MET Variables')
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/correlation_heatmap.png', dpi=150)
plt.close()
plt.figure(figsize=(9, 5))
sns.barplot(data=hourly_merged, x='Hour', y='Calories', estimator=np.mean, errorbar=None, color='#4C72B0')
plt.title('Average Calories Burnt by Hour of Day')
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/calories_by_hour.png', dpi=150)
plt.close()
print(f'\nSaved 5 EDA charts to ./{OUT_DIR}/')