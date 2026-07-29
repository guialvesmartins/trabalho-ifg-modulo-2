with products as (
    select * from {{ ref('stg_products') }}
),

aggregated as (
    select
        category as category_name,
        count(distinct product_id) as total_products,
        round(avg(rating), 2) as avg_rating,
        min(actual_price) as min_price,
        max(actual_price) as max_price,
        round(avg(discount_percentage), 2) as avg_discount
    from products
    group by category
)

select * from aggregated
