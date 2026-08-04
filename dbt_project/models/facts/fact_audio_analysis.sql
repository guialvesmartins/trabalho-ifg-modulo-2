with metadata as (
    select * from {{ ref('stg_pump_metadata') }}
),

audio as (
    select * from {{ ref('stg_audio_features') }}
),

joined as (
    select
        m.file_id,
        m.machine_type,
        m.model_id,
        m.condition,
        m.condition_binary,
        m.duration_sec,
        a.zcr_mean,
        a.rms_mean,
        a.spectral_centroid_mean,
        a.spectral_bandwidth_mean,
        a.spectral_rolloff_mean,
        a.mfcc_1_mean,
        a.mfcc_2_mean,
        a.mfcc_3_mean,
        a.mfcc_4_mean,
        a.mfcc_5_mean,
        a.mfcc_6_mean,
        a.mfcc_7_mean,
        a.mfcc_8_mean,
        a.mfcc_9_mean,
        a.mfcc_10_mean,
        a.mfcc_11_mean,
        a.mfcc_12_mean,
        a.mfcc_13_mean,
        a.mfcc_1_std,
        a.mfcc_2_std,
        a.mfcc_3_std,
        a.mfcc_4_std,
        a.mfcc_5_std
    from metadata m
    left join audio a
        on m.file_id = a.file_id
)

select * from joined
