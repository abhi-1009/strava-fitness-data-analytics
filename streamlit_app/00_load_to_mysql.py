import os
import sys
from urllib.parse import quote_plus
import pandas as pd
import toml
from sqlalchemy import create_engine, text
_secrets_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.streamlit', 'secrets.toml')
if not os.path.exists(_secrets_path):
    print(f'ERROR: {_secrets_path} not found. Copy secrets.toml.example to secrets.toml and fill in your values.')
    sys.exit(1)
_cfg = toml.load(_secrets_path)['mysql']
MYSQL_HOST = _cfg['host']
MYSQL_PORT = str(_cfg.get('port', 3306))
MYSQL_USER = _cfg['user']
MYSQL_PASSWORD = _cfg['password']
MYSQL_DATABASE = _cfg['database']
MYSQL_SSL_CA = _cfg.get('ssl_ca', '')
DAILY_CSV = 'bellabeat_daily_clean.csv'
HOURLY_CSV = 'bellabeat_hourly_clean.csv'

def build_engine():
    url = f'mysql+pymysql://{quote_plus(MYSQL_USER)}:{quote_plus(MYSQL_PASSWORD)}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}'
    connect_args = {}
    if MYSQL_SSL_CA:
        connect_args['ssl'] = {'ca': MYSQL_SSL_CA}
    return create_engine(url, connect_args=connect_args, pool_pre_ping=True)

def load_table(engine, csv_path, table_name, date_cols):
    if not os.path.exists(csv_path):
        print(f'ERROR: {csv_path} not found. Run 01_eda_bellabeat.py first.')
        sys.exit(1)
    df = pd.read_csv(csv_path, parse_dates=date_cols)
    print(f'Loading {table_name}: {len(df):,} rows, {df.shape[1]} columns')
    with engine.begin() as conn:
        conn.execute(text(f'TRUNCATE TABLE {table_name}'))
        df.to_sql(table_name, con=conn, if_exists='append', index=False, chunksize=1000)
    with engine.connect() as conn:
        count = conn.execute(text(f'SELECT COUNT(*) FROM {table_name}')).scalar()
    print(f'  -> {table_name} now has {count:,} rows in MySQL')
    if count != len(df):
        print(f'  WARNING: row count mismatch (CSV had {len(df)}, table has {count})')

def main():
    engine = build_engine()
    try:
        with engine.connect() as conn:
            conn.execute(text('SELECT 1'))
        print(f'Connected to MySQL at {MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}\n')
    except Exception as e:
        print(f'Could not connect to MySQL: {e}')
        sys.exit(1)
    load_table(engine, DAILY_CSV, 'daily_activity', date_cols=['ActivityDate'])
    load_table(engine, HOURLY_CSV, 'hourly_activity', date_cols=['ActivityHour', 'ActivityDate'])
    print('\nDone. Both tables are loaded and ready for the Streamlit app.')
if __name__ == '__main__':
    main()