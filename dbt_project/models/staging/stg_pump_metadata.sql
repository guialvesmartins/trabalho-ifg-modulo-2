with source_data as (
    select * from public.ml_features_raw
),

renamed as (
    select
        file_id,
        machine_type,
        model_id,
        condition,
        condition_binary,
        cast(duration_sec as numeric) as duration_sec,
        cast(sample_rate as integer) as sample_rate
    from source_data
    where file_id is not null
),

deduplicated as (
    select distinct on (file_id)
        file_id,
        machine_type,
        model_id,
        condition,
        condition_binary,
        duration_sec,
        sample_rate
    from renamed
    order by file_id
)

select * from deduplicated
