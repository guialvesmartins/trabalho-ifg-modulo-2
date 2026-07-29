with source_data as (
    select * from public.ml_features_raw
),

renamed as (
    select
        product_id,
        product_name,
        category,
        cast(discounted_price as numeric) as discounted_price,
        cast(actual_price as numeric) as actual_price,
        cast(discount_percentage as numeric) as discount_percentage,
        cast(rating as integer) as rating,
        cast(rating_count as integer) as rating_count,
        review_title,
        review_content,
        img_link
    from source_data
    where product_id is not null
      and rating is not null
),

deduplicated as (
    select distinct on (product_id)
        product_id,
        product_name,
        category,
        discounted_price,
        actual_price,
        discount_percentage,
        rating,
        rating_count,
        review_title,
        review_content,
        img_link
    from renamed
    order by product_id
)

select * from deduplicated
