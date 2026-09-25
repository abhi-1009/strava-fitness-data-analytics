-- ============================================================
-- Bellabeat / Fitbit Fitness Data - Step 2: SQL Analysis Queries
-- ============================================================
USE bellabeat_fitness;

-- ------------------------------------------------------------
-- Q1. Average steps, calories, and sedentary minutes by weekday
-- ------------------------------------------------------------
SELECT
    Weekday,
    ROUND(AVG(TotalSteps), 0)        AS avg_steps,
    ROUND(AVG(Calories), 0)          AS avg_calories,
    ROUND(AVG(SedentaryMinutes), 0)  AS avg_sedentary_minutes
FROM daily_activity
GROUP BY Weekday
ORDER BY FIELD(Weekday, 'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday');

-- ------------------------------------------------------------
-- Q2. Per-user activity summary + segment classification (Sedentary / Lightly Active / Fairly Active / Very Active
-- based on avg daily steps, per CDC-style step benchmarks)
-- ------------------------------------------------------------
SELECT
    Id,
    ROUND(AVG(TotalSteps), 0)           AS avg_daily_steps,
    ROUND(AVG(Calories), 0)             AS avg_daily_calories,
    ROUND(AVG(SedentaryMinutes), 0)     AS avg_sedentary_minutes,
    COUNT(*)                            AS days_logged,
    CASE
        WHEN AVG(TotalSteps) < 5000  THEN 'Sedentary'
        WHEN AVG(TotalSteps) < 7500  THEN 'Lightly Active'
        WHEN AVG(TotalSteps) < 10000 THEN 'Fairly Active'
        ELSE 'Very Active'
    END AS activity_segment
FROM daily_activity
GROUP BY Id
ORDER BY avg_daily_steps DESC;

-- ------------------------------------------------------------
-- Q3. How many users fall into each activity segment (feeds a pie/bar chart in the Streamlit app)
-- ------------------------------------------------------------
SELECT activity_segment, COUNT(*) AS num_users
FROM (
    SELECT
        Id,
        CASE
            WHEN AVG(TotalSteps) < 5000  THEN 'Sedentary'
            WHEN AVG(TotalSteps) < 7500  THEN 'Lightly Active'
            WHEN AVG(TotalSteps) < 10000 THEN 'Fairly Active'
            ELSE 'Very Active'
        END AS activity_segment
    FROM daily_activity
    GROUP BY Id
) AS segments
GROUP BY activity_segment
ORDER BY num_users DESC;

-- ------------------------------------------------------------
-- Q4. Sleep vs. sedentary minutes (only users who logged sleep)
-- ------------------------------------------------------------
SELECT
    Id,
    ROUND(AVG(TotalMinutesAsleep), 0)  AS avg_minutes_asleep,
    ROUND(AVG(SedentaryMinutes), 0)    AS avg_sedentary_minutes,
    ROUND(AVG(TotalSteps), 0)          AS avg_steps
FROM daily_activity
WHERE TotalMinutesAsleep IS NOT NULL
GROUP BY Id
ORDER BY avg_minutes_asleep;

-- ------------------------------------------------------------
-- Q5. % of days where the tracker was likely not worn (SedentaryMinutes >= 1440, per user)
-- ------------------------------------------------------------
SELECT
    Id,
    COUNT(*)                                          AS total_days,
    SUM(LikelyNotWorn)                                 AS not_worn_days,
    ROUND(100 * SUM(LikelyNotWorn) / COUNT(*), 1)      AS pct_not_worn
FROM daily_activity
GROUP BY Id
ORDER BY pct_not_worn DESC;

-- ------------------------------------------------------------
-- Q6. Average calories burnt by hour of day (all users)
-- ------------------------------------------------------------
SELECT
    Hour,
    ROUND(AVG(Calories), 1)          AS avg_calories,
    ROUND(AVG(StepTotal), 0)         AS avg_steps,
    ROUND(AVG(AverageIntensity), 2)  AS avg_intensity
FROM hourly_activity
GROUP BY Hour
ORDER BY Hour;

-- ------------------------------------------------------------
-- Q7. Active-minutes breakdown (very/fairly/lightly/sedentary) as a % of the day, averaged across all users
-- ------------------------------------------------------------
SELECT
    ROUND(AVG(VeryActiveMinutes), 1)    AS avg_very_active,
    ROUND(AVG(FairlyActiveMinutes), 1)  AS avg_fairly_active,
    ROUND(AVG(LightlyActiveMinutes), 1) AS avg_lightly_active,
    ROUND(AVG(SedentaryMinutes), 1)     AS avg_sedentary,
    ROUND(AVG(VeryActiveMinutes) / 1440 * 100, 1)    AS pct_very_active,
    ROUND(AVG(SedentaryMinutes) / 1440 * 100, 1)     AS pct_sedentary
FROM daily_activity;

-- ------------------------------------------------------------
-- Q8. Top 5 most active days (by steps) with weekday context
-- ------------------------------------------------------------
SELECT Id, ActivityDate, Weekday, TotalSteps, Calories
FROM daily_activity
ORDER BY TotalSteps DESC
LIMIT 5;

-- ------------------------------------------------------------
-- Q9. Weight / BMI trend for users who logged weight (small sample - only 8 of 33 users)
-- ------------------------------------------------------------
SELECT Id, ActivityDate, WeightKg, BMI, IsManualReport
FROM daily_activity
WHERE WeightKg IS NOT NULL
ORDER BY Id, ActivityDate;

-- ------------------------------------------------------------
-- Q10. Correlation proxy: steps vs. calories, bucketed
-- ------------------------------------------------------------
SELECT
    CASE
        WHEN TotalSteps < 2500  THEN '0-2.5k'
        WHEN TotalSteps < 5000  THEN '2.5k-5k'
        WHEN TotalSteps < 7500  THEN '5k-7.5k'
        WHEN TotalSteps < 10000 THEN '7.5k-10k'
        WHEN TotalSteps < 12500 THEN '10k-12.5k'
        ELSE '12.5k+'
    END AS step_bucket,
    COUNT(*)                    AS num_days,
    ROUND(AVG(Calories), 0)     AS avg_calories
FROM daily_activity
GROUP BY step_bucket
ORDER BY MIN(TotalSteps);

-- ------------------------------------------------------------
-- Q11. Weekend vs. weekday comparison
-- ------------------------------------------------------------
SELECT
    CASE WHEN Weekday IN ('Saturday','Sunday') THEN 'Weekend' ELSE 'Weekday' END AS day_type,
    ROUND(AVG(TotalSteps), 0)       AS avg_steps,
    ROUND(AVG(Calories), 0)         AS avg_calories,
    ROUND(AVG(SedentaryMinutes), 0) AS avg_sedentary_minutes,
    ROUND(AVG(TotalMinutesAsleep), 0) AS avg_minutes_asleep
FROM daily_activity
GROUP BY day_type;

-- ------------------------------------------------------------
-- Q12. Average heart rate by hour of day (users with HR data)
-- ------------------------------------------------------------
SELECT Hour, ROUND(AVG(AvgHeartRate), 1) AS avg_heart_rate
FROM hourly_activity
WHERE AvgHeartRate IS NOT NULL
GROUP BY Hour
ORDER BY Hour;