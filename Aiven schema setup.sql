-- ============================================================
-- Bellabeat / Fitbit Fitness Data - Aiven Schema Setup
-- Run this in MySQL Workbench, connected to your AIVEN service
-- (the same mysql-2b460e3f service used for food_wastage/cricbuzz).
-- Do NOT run the LOAD DATA INFILE version here - Aiven blocks it.
-- Data loading happens via 00_load_to_mysql.py instead.
-- ============================================================

USE bellabeat_fitness;

DROP TABLE IF EXISTS daily_activity;
CREATE TABLE daily_activity (
    Id                       BIGINT,
    ActivityDate             DATE,
    TotalSteps               INT,
    TotalDistance            FLOAT,
    TrackerDistance          FLOAT,
    LoggedActivitiesDistance FLOAT,
    VeryActiveDistance       FLOAT,
    ModeratelyActiveDistance FLOAT,
    LightActiveDistance      FLOAT,
    SedentaryActiveDistance  FLOAT,
    VeryActiveMinutes        INT,
    FairlyActiveMinutes      INT,
    LightlyActiveMinutes     INT,
    SedentaryMinutes         INT,
    Calories                 INT,
    LikelyNotWorn            TINYINT(1),
    TotalSleepRecords        FLOAT,
    TotalMinutesAsleep       FLOAT,
    TotalTimeInBed           FLOAT,
    WeightKg                 FLOAT,
    BMI                      FLOAT,
    IsManualReport           VARCHAR(10),
    AvgHeartRate             FLOAT,
    MinHeartRate             FLOAT,
    MaxHeartRate             FLOAT,
    AvgMET                   FLOAT,
    AvgIntensity             FLOAT,
    TotalIntensity           FLOAT,
    Weekday                  VARCHAR(10),
    PRIMARY KEY (Id, ActivityDate)
);

DROP TABLE IF EXISTS hourly_activity;
CREATE TABLE hourly_activity (
    Id               BIGINT,
    ActivityHour     DATETIME,
    Calories         INT,
    StepTotal        INT,
    TotalIntensity   INT,
    AverageIntensity FLOAT,
    AvgHeartRate     FLOAT,
    ActivityDate     DATE,
    Hour             TINYINT,
    Weekday          VARCHAR(10),
    PRIMARY KEY (Id, ActivityHour)
);

SELECT 'Tables created successfully' AS status;
SELECT COUNT(*) AS daily_rows FROM daily_activity;      
SELECT COUNT(*) AS hourly_rows FROM hourly_activity;