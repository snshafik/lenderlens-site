-- LenderLens Decision Lab
-- Snowflake-oriented reference model: spend -> lead -> application -> funded loan.
-- All sample entities are synthetic. Adapt source names/keys to the warehouse in use.

WITH spend AS (
    SELECT
        spend_date,
        LOWER(TRIM(channel)) AS channel,
        LOWER(TRIM(campaign_id)) AS campaign_id,
        SUM(spend_usd) AS spend_usd,
        SUM(impressions) AS impressions,
        SUM(clicks) AS clicks
    FROM analytics.marketing_spend
    GROUP BY 1, 2, 3
),

lead_touch AS (
    SELECT
        lead_id,
        created_at::DATE AS lead_date,
        LOWER(TRIM(COALESCE(utm_medium, 'unknown'))) AS channel,
        LOWER(TRIM(COALESCE(utm_campaign_id, 'unknown'))) AS campaign_id,
        ROW_NUMBER() OVER (
            PARTITION BY lead_id
            ORDER BY event_timestamp ASC
        ) AS touch_rank
    FROM analytics.lead_events
    QUALIFY touch_rank = 1
),

application_rollup AS (
    SELECT
        lead_id,
        MIN(application_created_at) AS first_application_at,
        MAX(IFF(application_status IN ('submitted', 'approved', 'funded'), 1, 0)) AS applied_flag
    FROM core.applications
    GROUP BY 1
),

funded_rollup AS (
    SELECT
        lead_id,
        MIN(funded_at) AS first_funded_at,
        SUM(IFF(loan_status = 'funded', funded_amount, 0)) AS funded_volume,
        MAX(IFF(loan_status = 'funded', 1, 0)) AS funded_flag
    FROM core.loans
    GROUP BY 1
),

journey AS (
    SELECT
        l.lead_date,
        l.channel,
        l.campaign_id,
        l.lead_id,
        COALESCE(a.applied_flag, 0) AS applied_flag,
        COALESCE(f.funded_flag, 0) AS funded_flag,
        COALESCE(f.funded_volume, 0) AS funded_volume,
        DATEDIFF('day', l.lead_date, f.first_funded_at::DATE) AS days_to_fund
    FROM lead_touch l
    LEFT JOIN application_rollup a USING (lead_id)
    LEFT JOIN funded_rollup f USING (lead_id)
),

funnel AS (
    SELECT
        lead_date,
        channel,
        campaign_id,
        COUNT(DISTINCT lead_id) AS leads,
        SUM(applied_flag) AS applications,
        SUM(funded_flag) AS funded_loans,
        SUM(funded_volume) AS funded_volume,
        MEDIAN(IFF(funded_flag = 1, days_to_fund, NULL)) AS median_days_to_fund
    FROM journey
    GROUP BY 1, 2, 3
),

channel_day AS (
    SELECT
        COALESCE(s.spend_date, f.lead_date) AS activity_date,
        COALESCE(s.channel, f.channel) AS channel,
        COALESCE(s.campaign_id, f.campaign_id) AS campaign_id,
        COALESCE(s.spend_usd, 0) AS spend_usd,
        COALESCE(s.impressions, 0) AS impressions,
        COALESCE(s.clicks, 0) AS clicks,
        COALESCE(f.leads, 0) AS leads,
        COALESCE(f.applications, 0) AS applications,
        COALESCE(f.funded_loans, 0) AS funded_loans,
        COALESCE(f.funded_volume, 0) AS funded_volume,
        f.median_days_to_fund
    FROM spend s
    FULL OUTER JOIN funnel f
        ON s.spend_date = f.lead_date
       AND s.channel = f.channel
       AND s.campaign_id = f.campaign_id
),

metrics AS (
    SELECT
        *,
        spend_usd / NULLIF(leads, 0) AS cost_per_lead,
        applications / NULLIF(leads, 0) AS application_rate,
        funded_loans / NULLIF(applications, 0) AS funded_from_application_rate,
        funded_loans / NULLIF(leads, 0) AS funded_from_lead_rate,
        spend_usd / NULLIF(funded_loans, 0) AS cost_per_funded_loan,
        funded_volume / NULLIF(spend_usd, 0) AS funded_volume_per_ad_dollar
    FROM channel_day
),

with_baselines AS (
    SELECT
        *,
        AVG(cost_per_funded_loan) OVER (
            PARTITION BY channel
            ORDER BY activity_date
            ROWS BETWEEN 28 PRECEDING AND 1 PRECEDING
        ) AS trailing_cpf_baseline,
        STDDEV_SAMP(cost_per_funded_loan) OVER (
            PARTITION BY channel
            ORDER BY activity_date
            ROWS BETWEEN 28 PRECEDING AND 1 PRECEDING
        ) AS trailing_cpf_stddev
    FROM metrics
)

SELECT
    *,
    (cost_per_funded_loan - trailing_cpf_baseline)
        / NULLIF(trailing_cpf_stddev, 0) AS cpf_anomaly_zscore,
    CASE
        WHEN funded_loans = 0 AND spend_usd >= 1000 THEN 'NO_FUNDED_OUTCOME'
        WHEN (cost_per_funded_loan - trailing_cpf_baseline)
             / NULLIF(trailing_cpf_stddev, 0) >= 2 THEN 'EFFICIENCY_DEGRADATION'
        WHEN funded_from_lead_rate >= 1.25 * AVG(funded_from_lead_rate) OVER (PARTITION BY channel)
             THEN 'SCALE_CANDIDATE'
        ELSE 'NORMAL'
    END AS decision_flag
FROM with_baselines;
