with products as (
    select * from {{ ref('stg_products') }}
),

sales_metrics as (
    select
        product_id,
        actual_price,
        discounted_price,
        discount_percentage as discount_pct,
        rating,
        rating_count
    from products
)

select * from sales_metrics
