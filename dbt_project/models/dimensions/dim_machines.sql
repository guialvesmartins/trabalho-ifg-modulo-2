with metadata as (
    select * from {{ ref('stg_pump_metadata') }}
),

aggregated as (
    select
        machine_type,
        model_id,
        count(distinct file_id) as total_samples,
        sum(case when condition_binary = 1 then 1 else 0 end) as anomaly_count,
        sum(case when condition_binary = 0 then 1 else 0 end) as normal_count,
        round(avg(duration_sec), 4) as avg_duration_sec
    from metadata
    group by machine_type, model_id
)

select * from aggregated
