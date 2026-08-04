with fact_audio as (
    select * from {{ ref('fact_audio_analysis') }}
),

dim_machines as (
    select * from {{ ref('dim_machines') }}
),

joined as (
    select
        fa.file_id,
        fa.machine_type,
        fa.model_id,
        fa.condition,
        fa.condition_binary,
        fa.duration_sec,
        fa.zcr_mean,
        fa.rms_mean,
        fa.spectral_centroid_mean,
        fa.spectral_bandwidth_mean,
        fa.spectral_rolloff_mean,
        fa.mfcc_1_mean,
        fa.mfcc_2_mean,
        fa.mfcc_3_mean,
        fa.mfcc_4_mean,
        fa.mfcc_5_mean,
        fa.mfcc_6_mean,
        fa.mfcc_7_mean,
        fa.mfcc_8_mean,
        fa.mfcc_9_mean,
        fa.mfcc_10_mean,
        fa.mfcc_11_mean,
        fa.mfcc_12_mean,
        fa.mfcc_13_mean,
        fa.mfcc_1_std,
        fa.mfcc_2_std,
        fa.mfcc_3_std,
        fa.mfcc_4_std,
        fa.mfcc_5_std,
        dm.total_samples,
        dm.anomaly_count,
        dm.normal_count,
        dm.avg_duration_sec
    from fact_audio fa
    left join dim_machines dm
        on fa.machine_type = dm.machine_type
        and fa.model_id = dm.model_id
)

select * from joined
