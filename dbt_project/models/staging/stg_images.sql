with source_data as (
    select * from public.ml_features_raw
),

image_features as (
    select
        product_id,
        img_link,
        cast(brightness_mean as numeric) as brightness_mean,
        cast(saturation_mean as numeric) as saturation_mean,
        cast(blur_score as numeric) as blur_score,
        cast(edge_density as numeric) as edge_density,
        cast(entropy as numeric) as entropy,
        cast(contrast as numeric) as contrast
    from source_data
    where img_link is not null
)

select * from image_features
