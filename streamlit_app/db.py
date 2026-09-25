from contextlib import contextmanager
from typing import Optional
from urllib.parse import quote_plus
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

@st.cache_resource(show_spinner=False)
def get_engine() -> Engine:
    cfg = st.secrets['mysql']
    connect_args = {}
    if cfg.get('ssl_ca'):
        connect_args['ssl'] = {'ca': cfg['ssl_ca']}
    url = f'mysql+pymysql://{quote_plus(cfg['user'])}:{quote_plus(cfg['password'])}@{cfg['host']}:{cfg.get('port', 3306)}/{cfg['database']}'
    return create_engine(url, connect_args=connect_args, pool_pre_ping=True, pool_recycle=280)

@contextmanager
def get_connection():
    engine = get_engine()
    conn = engine.connect()
    try:
        yield conn
    finally:
        conn.close()

def run_query(sql: str, params: Optional[dict]=None) -> pd.DataFrame:
    try:
        with get_connection() as conn:
            return pd.read_sql(text(sql), conn, params=params or {})
    except Exception as e:
        st.error(f'Database query failed: {e}')
        return pd.DataFrame()

@st.cache_data(ttl=600, show_spinner='Querying MySQL...')
def get_user_ids() -> list:
    df = run_query('SELECT DISTINCT Id FROM daily_activity ORDER BY Id')
    return df['Id'].tolist() if not df.empty else []

@st.cache_data(ttl=600, show_spinner='Querying MySQL...')
def get_date_range() -> tuple:
    df = run_query('SELECT MIN(ActivityDate) AS min_d, MAX(ActivityDate) AS max_d FROM daily_activity')
    if df.empty:
        return (None, None)
    return (df.loc[0, 'min_d'], df.loc[0, 'max_d'])

@st.cache_data(ttl=600, show_spinner='Querying MySQL...')
def get_daily_filtered(user_ids: tuple, start_date, end_date) -> pd.DataFrame:
    id_placeholders = ', '.join((str(i) for i in user_ids)) if user_ids else 'NULL'
    sql = f'\n        SELECT *\n        FROM daily_activity\n        WHERE Id IN ({id_placeholders})\n          AND ActivityDate BETWEEN :start_date AND :end_date\n    '
    return run_query(sql, {'start_date': start_date, 'end_date': end_date})

@st.cache_data(ttl=600, show_spinner='Querying MySQL...')
def get_hourly_filtered(user_ids: tuple, start_date, end_date) -> pd.DataFrame:
    id_placeholders = ', '.join((str(i) for i in user_ids)) if user_ids else 'NULL'
    sql = f'\n        SELECT *\n        FROM hourly_activity\n        WHERE Id IN ({id_placeholders})\n          AND ActivityDate BETWEEN :start_date AND :end_date\n    '
    return run_query(sql, {'start_date': start_date, 'end_date': end_date})

@st.cache_data(ttl=600, show_spinner='Querying MySQL...')
def get_weekday_summary(user_ids: tuple, start_date, end_date) -> pd.DataFrame:
    id_placeholders = ', '.join((str(i) for i in user_ids)) if user_ids else 'NULL'
    sql = f"\n        SELECT\n            Weekday,\n            ROUND(AVG(TotalSteps), 0)       AS avg_steps,\n            ROUND(AVG(Calories), 0)         AS avg_calories,\n            ROUND(AVG(SedentaryMinutes), 0) AS avg_sedentary_minutes\n        FROM daily_activity\n        WHERE Id IN ({id_placeholders})\n          AND ActivityDate BETWEEN :start_date AND :end_date\n        GROUP BY Weekday\n        ORDER BY FIELD(Weekday, 'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday')\n    "
    return run_query(sql, {'start_date': start_date, 'end_date': end_date})

@st.cache_data(ttl=600, show_spinner='Querying MySQL...')
def get_activity_segments() -> pd.DataFrame:
    sql = "\n        SELECT activity_segment, COUNT(*) AS num_users\n        FROM (\n            SELECT\n                Id,\n                CASE\n                    WHEN AVG(TotalSteps) < 5000  THEN 'Sedentary'\n                    WHEN AVG(TotalSteps) < 7500  THEN 'Lightly Active'\n                    WHEN AVG(TotalSteps) < 10000 THEN 'Fairly Active'\n                    ELSE 'Very Active'\n                END AS activity_segment\n            FROM daily_activity\n            GROUP BY Id\n        ) AS segments\n        GROUP BY activity_segment\n    "
    return run_query(sql)

@st.cache_data(ttl=600, show_spinner='Querying MySQL...')
def get_hourly_pattern(user_ids: tuple, start_date, end_date) -> pd.DataFrame:
    id_placeholders = ', '.join((str(i) for i in user_ids)) if user_ids else 'NULL'
    sql = f'\n        SELECT\n            Hour,\n            ROUND(AVG(Calories), 1)         AS avg_calories,\n            ROUND(AVG(StepTotal), 0)        AS avg_steps,\n            ROUND(AVG(AvgHeartRate), 1)     AS avg_heart_rate\n        FROM hourly_activity\n        WHERE Id IN ({id_placeholders})\n          AND ActivityDate BETWEEN :start_date AND :end_date\n        GROUP BY Hour\n        ORDER BY Hour\n    '
    return run_query(sql, {'start_date': start_date, 'end_date': end_date})

@st.cache_data(ttl=600, show_spinner='Querying MySQL...')
def get_sleep_vs_sedentary(user_ids: tuple, start_date, end_date) -> pd.DataFrame:
    id_placeholders = ', '.join((str(i) for i in user_ids)) if user_ids else 'NULL'
    sql = f'\n        SELECT Id, ActivityDate, TotalMinutesAsleep, SedentaryMinutes, TotalSteps\n        FROM daily_activity\n        WHERE TotalMinutesAsleep IS NOT NULL\n          AND Id IN ({id_placeholders})\n          AND ActivityDate BETWEEN :start_date AND :end_date\n    '
    return run_query(sql, {'start_date': start_date, 'end_date': end_date})

@st.cache_data(ttl=600, show_spinner='Querying MySQL...')
def get_weight_log(user_ids: tuple) -> pd.DataFrame:
    id_placeholders = ', '.join((str(i) for i in user_ids)) if user_ids else 'NULL'
    sql = f'\n        SELECT Id, ActivityDate, WeightKg, BMI, IsManualReport\n        FROM daily_activity\n        WHERE WeightKg IS NOT NULL AND Id IN ({id_placeholders})\n        ORDER BY Id, ActivityDate\n    '
    return run_query(sql)