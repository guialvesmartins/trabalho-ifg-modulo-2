with dim_products as (
    select * from {{ ref('dim_products') }}
),

fact_reviews as (
    select * from {{ ref('fact_reviews') }}
),

stg_images as (
    select * from {{ ref('stg_images') }}
),

joined as (
    select
        fr.review_id,
        fr.product_id,
        fr.rating,
        fr.review_title,
        fr.review_content,
        fr.polarity,
        fr.subjectivity,
        fr.review_length,
        fr.word_count,
        si.brightness_mean,
        si.saturation_mean,
        si.blur_score,
        si.edge_density,
        si.entropy,
        si.contrast,
        dp.product_name,
        dp.category,
        dp.actual_price,
        dp.discounted_price,
        dp.discount_percentage,
        dp.rating_count,
        dp.img_link
    from fact_reviews fr
    left join stg_images si
        on fr.product_id = si.product_id
    left join dim_products dp
        on fr.product_id = dp.product_id
)

select * from joined
