with products as (
    select * from {{ ref('stg_products') }}
),

images as (
    select * from {{ ref('stg_images') }}
),

joined as (
    select
        p.product_id,
        p.product_name,
        p.category,
        p.actual_price,
        p.discounted_price,
        p.discount_percentage,
        p.rating,
        p.rating_count,
        p.img_link,
        i.brightness_mean,
        i.saturation_mean,
        i.blur_score,
        i.edge_density,
        i.entropy,
        i.contrast
    from products p
    left join images i
        on p.product_id = i.product_id
)

select * from joined
