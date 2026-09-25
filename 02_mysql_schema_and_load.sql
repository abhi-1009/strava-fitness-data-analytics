-- ============================================================
-- Bellabeat / Fitbit Fitness Data - Step 2: Schema + Data Load
-- ============================================================
CREATE DATABASE IF NOT EXISTS bellabeat_fitness;
USE bellabeat_fitness;

-- ------------------------------------------------------------
-- 1. DAILY TABLE
-- ------------------------------------------------------------
CREATE TABLE daily_activity (
    Id                          BIGINT,
    ActivityDate                DATE,
    TotalSteps                  INT,
    TotalDistance                FLOAT,
    TrackerDistance               FLOAT,
    LoggedActivitiesDistance      FLOAT,
    VeryActiveDistance             FLOAT,
    ModeratelyActiveDistance        FLOAT,
    LightActiveDistance              FLOAT,
    SedentaryActiveDistance           FLOAT,
    VeryActiveMinutes                  INT,
    FairlyActiveMinutes                 INT,
    LightlyActiveMinutes                 INT,
    SedentaryMinutes                      INT,
    Calories                               INT,
    LikelyNotWorn                           TINYINT(1),
    TotalSleepRecords                        FLOAT,
    TotalMinutesAsleep                        FLOAT,
    TotalTimeInBed                             FLOAT,
    WeightKg                                    FLOAT,
    BMI                                          FLOAT,
    IsManualReport                                VARCHAR(10),
    AvgHeartRate                                   FLOAT,
    MinHeartRate                                    FLOAT,
    MaxHeartRate                                     FLOAT,
    AvgMET                                            FLOAT,
    AvgIntensity                                       FLOAT,
    TotalIntensity                                      FLOAT,
    Weekday                                              VARCHAR(10),
    PRIMARY KEY (Id, ActivityDate)
);

-- ------------------------------------------------------------
-- 2. HOURLY TABLE  (from bellabeat_hourly_clean.csv, 22,099 rows)
-- ------------------------------------------------------------
CREATE TABLE hourly_activity (
    Id                  BIGINT,
    ActivityHour        DATETIME,
    Calories             INT,
    StepTotal             INT,
    TotalIntensity         INT,
    AverageIntensity        FLOAT,
    AvgHeartRate              FLOAT,
    ActivityDate               DATE,
    Hour                        TINYINT,
    Weekday                      VARCHAR(10),
    PRIMARY KEY (Id, ActivityHour)
);

-- ------------------------------------------------------------
-- 3. CHECK secure_file_priv (tells you where LOAD DATA INFILE is allowed to read from on your server)
-- ------------------------------------------------------------
SHOW VARIABLES LIKE 'secure_file_priv';

-- ------------------------------------------------------------
-- 4. LOAD DATA
-- ------------------------------------------------------------
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/bellabeat_daily_clean.csv'
INTO TABLE daily_activity
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(Id, @ActivityDate, TotalSteps, TotalDistance, TrackerDistance, LoggedActivitiesDistance,
 VeryActiveDistance, ModeratelyActiveDistance, LightActiveDistance, SedentaryActiveDistance,
 VeryActiveMinutes, FairlyActiveMinutes, LightlyActiveMinutes, SedentaryMinutes, Calories,
 @LikelyNotWorn, @TotalSleepRecords, @TotalMinutesAsleep, @TotalTimeInBed, @WeightKg, @BMI,
 IsManualReport, @AvgHeartRate, @MinHeartRate, @MaxHeartRate, @AvgMET, @AvgIntensity,
 @TotalIntensity, Weekday)
SET
    ActivityDate = STR_TO_DATE(@ActivityDate, '%Y-%m-%d'),
    LikelyNotWorn = CASE WHEN @LikelyNotWorn = 'True' THEN 1 ELSE 0 END,
    TotalSleepRecords = NULLIF(@TotalSleepRecords, ''),
    TotalMinutesAsleep = NULLIF(@TotalMinutesAsleep, ''),
    TotalTimeInBed = NULLIF(@TotalTimeInBed, ''),
    WeightKg = NULLIF(@WeightKg, ''),
    BMI = NULLIF(@BMI, ''),
    AvgHeartRate = NULLIF(@AvgHeartRate, ''),
    MinHeartRate = NULLIF(@MinHeartRate, ''),
    MaxHeartRate = NULLIF(@MaxHeartRate, ''),
    AvgMET = NULLIF(@AvgMET, ''),
    AvgIntensity = NULLIF(@AvgIntensity, ''),
    TotalIntensity = NULLIF(@TotalIntensity, '');

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/bellabeat_hourly_clean.csv'
INTO TABLE hourly_activity
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(Id, @ActivityHour, Calories, StepTotal, TotalIntensity, AverageIntensity,
 @AvgHeartRate, @ActivityDate, Hour, Weekday)
SET
    ActivityHour = STR_TO_DATE(@ActivityHour, '%Y-%m-%d %H:%i:%s'),
    ActivityDate = STR_TO_DATE(@ActivityDate, '%Y-%m-%d'),
    AvgHeartRate = NULLIF(@AvgHeartRate, '');

-- ------------------------------------------------------------
-- 5. VERIFY
-- ------------------------------------------------------------
SELECT COUNT(*) AS daily_rows FROM daily_activity;      
SELECT COUNT(*) AS hourly_rows FROM hourly_activity;    
SELECT * FROM daily_activity LIMIT 5;
SELECT * FROM hourly_activity LIMIT 5;