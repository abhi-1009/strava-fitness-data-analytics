import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import db
st.set_page_config(page_title='Bellabeat Fitness Analytics', page_icon='🏃', layout='wide', initial_sidebar_state='expanded')
st.markdown('\n    <style>\n    .main { background: linear-gradient(180deg, #0E1117 0%, #161B22 100%); }\n    div[data-testid="stMetric"] { background-color: #1C2128; border: 1px solid #30363D;\n        border-radius: 10px; padding: 12px 16px; }\n    div[data-testid="stMetricLabel"] { color: #9AA4AF; }\n    h1, h2, h3 { color: #FAFAFA; }\n    .accent { color: #FC4C02; }\n    .thanks-box { text-align: center; padding: 1.6rem; margin-top: 1rem; border-radius: 16px;\n        color: #FAFAFA; background: linear-gradient(120deg, #2A1810, #1C2128);\n        border: 1px solid #FC4C02; }\n    .thanks-box h3 { margin-bottom: 0.3rem; color: #FC4C02; }\n    </style>\n    ', unsafe_allow_html=True)
WEEKDAY_ORDER = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

def dark(fig, height=380, **kw):
    fig.update_layout(template='plotly_dark', height=height, margin=dict(t=20), **kw)
    return fig

def card(icon, title, text):
    st.markdown(f"<div style='background:#1C2128;border:1px solid #30363D;border-left:4px solid #FC4C02;border-radius:10px;padding:14px 16px;margin-bottom:10px;'><b>{icon} {title}</b><p style='color:#C9D1D9;margin:6px 0 0;font-size:0.9em;'>{text}</p></div>", unsafe_allow_html=True)
st.sidebar.markdown('## 🏃 Bellabeat Analytics')
st.sidebar.caption('Live MySQL-backed dashboard · Fitbit fitness tracker data')
with st.spinner('Connecting to MySQL...'):
    all_users = db.get_user_ids()
    min_date, max_date = db.get_date_range()
if not all_users or min_date is None:
    st.error('Could not load data from MySQL. Check `.streamlit/secrets.toml` and that `daily_activity` / `hourly_activity` are populated (run `00_load_to_mysql.py`).')
    st.stop()
st.sidebar.markdown('### Filters')
selected_users = st.sidebar.multiselect('Users (by Fitbit Id)', options=all_users, default=all_users, help='Defaults to all users.')
date_range = st.sidebar.date_input('Date range', value=(min_date, max_date), min_value=min_date, max_value=max_date)
if not selected_users:
    st.sidebar.warning('Select at least one user.')
    st.stop()
if len(date_range) != 2:
    st.stop()
start_date, end_date = date_range
user_tuple = tuple(selected_users)
with st.sidebar.expander('ℹ️ Data assumptions & limitations'):
    st.markdown("\n    - Public Fitbit dataset (Apr–May 2016), 30–33 users - not actual Bellabeat customers.\n    - No age, sex, or profession data - can't segment demographically.\n    - Only ~24/33 users logged sleep; only 8/33 logged weight - treat those panels as directional.\n    - Days with ≥1440 sedentary minutes are flagged `LikelyNotWorn` (tracker probably not worn).\n    - Heart-rate data covers only 14/33 users.\n    ")
st.sidebar.divider()
st.sidebar.caption('Data: Fitabase / Mobius (Kaggle, CC0) · Dashboard: Streamlit + MySQL')
st.markdown('# Bellabeat Fitness Data Analytics')
st.markdown(f"<span style='color:#9AA4AF'>Showing <b class='accent'>{len(selected_users)}</b> users · <b class='accent'>{start_date}</b> to <b class='accent'>{end_date}</b></span>", unsafe_allow_html=True)
st.divider()
tab_intro, tab_overview, tab_weekday, tab_segments, tab_hourly, tab_sleep, tab_weight, tab_sql, tab_conclusion = st.tabs(['📋 Project Summary', '📊 Overview', '📅 Weekday Patterns', '👥 User Segments', '🕐 Hourly Patterns', '😴 Sleep & Recovery', '⚖️ Weight & BMI', '🔍 Run a Query', '✅ Insights & Recommendations'])
with tab_intro:
    c1, c2 = st.columns(2)
    with c1, st.container(border=True):
        st.markdown('#### 🎯 Project Summary')
        st.caption("Bellabeat is a high-tech company making health-focused smart products for women. This project analyzes Fitbit tracker data (a proxy for Bellabeat's own devices) to uncover usage patterns and guide marketing strategy.")
    with c2, st.container(border=True):
        st.markdown('#### ❓ Problem Statement')
        st.caption('How are consumers using their smart devices? The marketing analytics team needs data-driven insight into activity, sleep, and sedentary patterns to guide strategy.')
    st.markdown('#### 📌 Business Objective')
    objectives = [('1️⃣', 'Identify Trends', 'Activity, sleep, and heart-rate usage patterns.'), ('2️⃣', 'Shape Strategy', 'Translate trends into marketing recommendations.'), ('3️⃣', 'Live Dashboard', 'Queryable results for execs and analysts.')]
    for col, (icon, title, text) in zip(st.columns(3), objectives):
        with col, st.container(border=True):
            st.markdown(f'**{icon} {title}**')
            st.caption(text)
    st.markdown('#### 🧑\u200d🤝\u200d🧑 Stakeholders')
    stakeholders = [('👩\u200d💼', 'Urška Sršen', 'Co-founder & Chief Creative Officer'), ('🧮', 'Sando Mur', 'Co-founder & Mathematician'), ('📈', 'Analytics Team', "Guides Bellabeat's marketing strategy")]
    for col, (icon, name, role) in zip(st.columns(3), stakeholders):
        with col, st.container(border=True):
            st.markdown(f'**{icon} {name}**')
            st.caption(role)
    d1, d2 = st.columns(2)
    with d1, st.container(border=True):
        st.markdown('#### 📂 Data Source\n- Fitabase / Mobius Fitbit dataset (Kaggle, CC0)\n- 30-33 users, minute-to-day level data\n- Collection period: Apr-May 2016')
    with d2, st.container(border=True):
        st.markdown('#### 🛠️ Tools Used\n- **Python** (pandas) - cleaning, merging, EDA\n- **MySQL** - storage and SQL analysis\n- **Streamlit + Plotly** - this dashboard')
    st.info('Use the sidebar to filter by user and date range - every chart here re-queries MySQL live based on your selection.')
with tab_overview:
    daily = db.get_daily_filtered(user_tuple, start_date, end_date)
    if daily.empty:
        st.info('No data for this selection.')
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric('Avg. Daily Steps', f'{daily['TotalSteps'].mean():,.0f}')
        c2.metric('Avg. Daily Calories', f'{daily['Calories'].mean():,.0f}')
        c3.metric('Avg. Sedentary Minutes', f'{daily['SedentaryMinutes'].mean():,.0f}')
        c4.metric('Days Tracker Likely Not Worn', f'{daily['LikelyNotWorn'].mean() * 100:.1f}%')
        st.markdown('#### Daily steps over time')
        trend = daily.sort_values('ActivityDate').groupby('ActivityDate', as_index=False)['TotalSteps'].mean()
        st.plotly_chart(dark(px.line(trend, x='ActivityDate', y='TotalSteps', color_discrete_sequence=['#FC4C02'])), width='stretch')
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown('#### Steps vs. Calories')
            fig2 = px.scatter(daily, x='TotalSteps', y='Calories', color='Weekday', category_orders={'Weekday': WEEKDAY_ORDER}, opacity=0.7)
            st.plotly_chart(dark(fig2, 350), width='stretch')
        with col_b:
            st.markdown('#### Active minutes breakdown')
            minutes_avg = daily[['VeryActiveMinutes', 'FairlyActiveMinutes', 'LightlyActiveMinutes', 'SedentaryMinutes']].mean()
            fig3 = px.pie(names=minutes_avg.index, values=minutes_avg.values, hole=0.5, color_discrete_sequence=px.colors.sequential.Oranges_r)
            st.plotly_chart(dark(fig3, 350), width='stretch')
with tab_weekday:
    wk = db.get_weekday_summary(user_tuple, start_date, end_date)
    if wk.empty:
        st.info('No data for this selection.')
    else:
        st.markdown('#### Average steps, calories & sedentary minutes by weekday')
        metric_choice = st.radio('Metric', ['avg_steps', 'avg_calories', 'avg_sedentary_minutes'], horizontal=True, label_visibility='collapsed')
        fig = px.bar(wk, x='Weekday', y=metric_choice, category_orders={'Weekday': WEEKDAY_ORDER}, color=metric_choice, color_continuous_scale='Oranges')
        st.plotly_chart(dark(fig, 420), width='stretch')
        st.dataframe(wk, width='stretch', hide_index=True)
with tab_segments:
    seg = db.get_activity_segments()
    if seg.empty:
        st.info('No data available.')
    else:
        st.markdown('#### Users by activity segment (avg. daily steps)')
        st.caption('Sedentary <5,000 · Lightly Active 5,000-7,499 · Fairly Active 7,500-9,999 · Very Active 10,000+')
        col1, col2 = st.columns(2)
        with col1:
            fig = px.pie(seg, names='activity_segment', values='num_users', hole=0.4, color_discrete_sequence=['#FC4C02', '#FF8552', '#FFB088', '#4C566A'])
            st.plotly_chart(dark(fig), width='stretch')
        with col2:
            st.dataframe(seg.sort_values('num_users', ascending=False), width='stretch', hide_index=True)
            below = seg.loc[seg['activity_segment'].isin(['Sedentary', 'Lightly Active']), 'num_users'].sum()
            total = seg['num_users'].sum()
            st.metric('Users below 7,500 steps/day', f'{below}/{total} ({below / total * 100:.0f}%)')
with tab_hourly:
    hourly = db.get_hourly_pattern(user_tuple, start_date, end_date)
    if hourly.empty:
        st.info('No data for this selection.')
    else:
        st.markdown('#### Average calories burnt by hour of day')
        fig = go.Figure()
        fig.add_bar(x=hourly['Hour'], y=hourly['avg_calories'], name='Avg Calories', marker_color='#FC4C02')
        st.plotly_chart(dark(fig, 400, xaxis_title='Hour of Day', yaxis_title='Avg Calories'), width='stretch')
        if hourly['avg_heart_rate'].notna().any():
            st.markdown('#### Average heart rate by hour of day')
            fig2 = px.line(hourly.dropna(subset=['avg_heart_rate']), x='Hour', y='avg_heart_rate', color_discrete_sequence=['#FF8552'])
            st.plotly_chart(dark(fig2, 350), width='stretch')
        else:
            st.caption('No heart-rate data for the selected users/date range.')
with tab_sleep:
    sleep_df = db.get_sleep_vs_sedentary(user_tuple, start_date, end_date)
    if sleep_df.empty:
        st.info('None of the selected users logged sleep in this range (only ~24/33 users ever did).')
    else:
        st.markdown('#### Sedentary minutes vs. minutes asleep')
        fig = px.scatter(sleep_df, x='SedentaryMinutes', y='TotalMinutesAsleep', trendline='ols', opacity=0.6, color_discrete_sequence=['#FC4C02'])
        st.plotly_chart(dark(fig, 420), width='stretch')
        corr = sleep_df[['SedentaryMinutes', 'TotalMinutesAsleep']].corr().iloc[0, 1]
        st.metric('Correlation (sedentary min. vs. sleep min.)', f'{corr:.2f}')
        st.caption(f'Based on {sleep_df['Id'].nunique()} users who logged sleep, {len(sleep_df)} day-records.')
with tab_weight:
    weight_df = db.get_weight_log(user_tuple)
    if weight_df.empty:
        st.info('None of the selected users logged weight (only 8/33 users ever did).')
    else:
        st.markdown(f'#### Weight/BMI log ({weight_df['Id'].nunique()} users)')
        fig = px.scatter(weight_df, x='ActivityDate', y='WeightKg', color=weight_df['Id'].astype(str), symbol='IsManualReport')
        st.plotly_chart(dark(fig, 420, legend_title='User Id'), width='stretch')
        st.dataframe(weight_df, width='stretch', hide_index=True)
QUERY_PRESETS = {'Top 10 most active days': 'SELECT Id, ActivityDate, Weekday, TotalSteps, Calories FROM daily_activity ORDER BY TotalSteps DESC LIMIT 10;', 'Weekday summary': 'SELECT Weekday, ROUND(AVG(TotalSteps),0) avg_steps, ROUND(AVG(Calories),0) avg_calories FROM daily_activity GROUP BY Weekday;', 'User activity segments': 'SELECT Id, ROUND(AVG(TotalSteps),0) avg_steps, COUNT(*) days_logged FROM daily_activity GROUP BY Id ORDER BY avg_steps DESC;', 'Sleep vs. sedentary (users who logged sleep)': 'SELECT Id, ROUND(AVG(TotalMinutesAsleep),0) avg_sleep, ROUND(AVG(SedentaryMinutes),0) avg_sedentary FROM daily_activity WHERE TotalMinutesAsleep IS NOT NULL GROUP BY Id;', 'Hourly calories & heart rate': 'SELECT Hour, ROUND(AVG(Calories),1) avg_calories, ROUND(AVG(AvgHeartRate),1) avg_hr FROM hourly_activity GROUP BY Hour ORDER BY Hour;', 'Weight/BMI log': 'SELECT Id, ActivityDate, WeightKg, BMI FROM daily_activity WHERE WeightKg IS NOT NULL;', 'Custom (write your own)': 'SELECT * FROM daily_activity LIMIT 10;'}
with tab_sql:
    st.markdown('#### Run a read-only SQL query against `bellabeat_fitness`')
    st.caption('Only SELECT statements are allowed. Tables: `daily_activity`, `hourly_activity`.')
    choice = st.selectbox('Choose a preset, or pick Custom and edit freely', list(QUERY_PRESETS))
    user_sql = st.text_area('SQL', value=QUERY_PRESETS[choice], height=120, key=f'sql_{choice}')
    if st.button('Run query', type='primary'):
        cleaned = user_sql.strip().rstrip(';')
        if not cleaned.lower().startswith('select'):
            st.error('Only SELECT queries are allowed here.')
        else:
            result = db.run_query(cleaned)
            if not result.empty:
                st.dataframe(result, width='stretch', hide_index=True)
                st.caption(f'{len(result)} rows returned.')
with tab_conclusion:
    seg_df = db.get_activity_segments()
    sleep_corr_df = db.get_sleep_vs_sedentary(user_tuple, start_date, end_date)
    daily_all = db.get_daily_filtered(user_tuple, start_date, end_date)
    below_pct = corr_val = worn_pct = None
    if not seg_df.empty:
        below = seg_df.loc[seg_df['activity_segment'].isin(['Sedentary', 'Lightly Active']), 'num_users'].sum()
        below_pct = below / seg_df['num_users'].sum() * 100
    if not sleep_corr_df.empty:
        corr_val = sleep_corr_df[['SedentaryMinutes', 'TotalMinutesAsleep']].corr().iloc[0, 1]
    if not daily_all.empty:
        worn_pct = daily_all['LikelyNotWorn'].mean() * 100
    insight_cards = []
    if below_pct is not None:
        insight_cards.append(('📉', 'Activity Gap', f'{below_pct:.0f}% of users average fewer than 7,500 steps/day - below widely-cited activity benchmarks.'))
    insight_cards.append(('📅', 'Weekly Pattern', 'Saturdays & Tuesdays are peak activity days; Sundays are consistently lowest.'))
    if corr_val is not None:
        insight_cards.append(('😴', 'Sleep Link', f'Sedentary-vs-sleep correlation is {corr_val:.2f} - more sitting tracks with less sleep.'))
    insight_cards.append(('🔥', 'Peak Burn Hours', 'Calories burnt peak 5-7 PM, the after-work exercise window.'))
    if worn_pct is not None:
        insight_cards.append(('⌚', 'Non-Wear Days', f'{worn_pct:.0f}% of days show 24h sedentary - tracker was likely not worn.'))
    insight_cards.append(('📊', 'Low Feature Adoption', 'Only ~24/33 users log sleep, ~8/33 log weight - far below step-tracking use.'))
    rec_cards = [('1️⃣', 'Nudge Low-Activity Users', 'Reminders during long sedentary stretches for the 50%+ of users below common step benchmarks.'), ('2️⃣', 'Target the 5-7 PM Window', 'Launch challenges or streaks when users are already most active.'), ('3️⃣', 'Improve Sleep/Weight Logging', "Auto scale-sync or incentives to raise adoption and enrich Bellabeat's wellness data."), ('4️⃣', 'Address Non-Wear Time', 'Better comfort, battery life, and wear reminders to improve data quality and perceived value.'), ('5️⃣', 'Weekend Campaigns', 'Capitalize on high Saturday activity; nudge users on low-activity Sundays.')]
    st.markdown('### Key Insights')
    cols = st.columns(2)
    for i, (icon, title, text) in enumerate(insight_cards):
        with cols[i % 2]:
            card(icon, title, text)
    st.markdown('### Recommendations')
    cols2 = st.columns(2)
    for i, (icon, title, text) in enumerate(rec_cards):
        with cols2[i % 2]:
            card(icon, title, text)
    st.markdown('### Conclusion')
    card('🎯', 'Bottom Line', 'This Fitbit dataset (small sample, no demographics, several years old) still reveals clear, actionable gaps in activity, sleep, and feature adoption - pointing Bellabeat toward smarter nudges, better non-wear detection, and stronger engagement incentives.')
    st.markdown('\n    <div class="thanks-box"><h3>🙏 Thank You</h3>\n    <p>Thank you for taking the time to review this Bellabeat Fitness Analytics project.<br>\n    Feedback and suggestions are always welcome!</p></div>\n    ', unsafe_allow_html=True)