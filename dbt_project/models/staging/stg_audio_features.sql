with source_data as (
    select * from public.ml_features_raw
),

audio_features as (
    select
        file_id,
        cast(zcr_mean as numeric) as zcr_mean,
        cast(rms_mean as numeric) as rms_mean,
        cast(spectral_centroid_mean as numeric) as spectral_centroid_mean,
        cast(spectral_bandwidth_mean as numeric) as spectral_bandwidth_mean,
        cast(spectral_rolloff_mean as numeric) as spectral_rolloff_mean,
        cast(mfcc_1_mean as numeric) as mfcc_1_mean,
        cast(mfcc_2_mean as numeric) as mfcc_2_mean,
        cast(mfcc_3_mean as numeric) as mfcc_3_mean,
        cast(mfcc_4_mean as numeric) as mfcc_4_mean,
        cast(mfcc_5_mean as numeric) as mfcc_5_mean,
        cast(mfcc_6_mean as numeric) as mfcc_6_mean,
        cast(mfcc_7_mean as numeric) as mfcc_7_mean,
        cast(mfcc_8_mean as numeric) as mfcc_8_mean,
        cast(mfcc_9_mean as numeric) as mfcc_9_mean,
        cast(mfcc_10_mean as numeric) as mfcc_10_mean,
        cast(mfcc_11_mean as numeric) as mfcc_11_mean,
        cast(mfcc_12_mean as numeric) as mfcc_12_mean,
        cast(mfcc_13_mean as numeric) as mfcc_13_mean,
        cast(mfcc_1_std as numeric) as mfcc_1_std,
        cast(mfcc_2_std as numeric) as mfcc_2_std,
        cast(mfcc_3_std as numeric) as mfcc_3_std,
        cast(mfcc_4_std as numeric) as mfcc_4_std,
        cast(mfcc_5_std as numeric) as mfcc_5_std
    from source_data
    where file_id is not null
      and rms_mean is not null
)

select * from audio_features
