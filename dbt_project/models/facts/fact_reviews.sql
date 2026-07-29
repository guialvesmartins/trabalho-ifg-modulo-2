with source_data as (
    select * from public.ml_features_raw
),

with_review_id as (
    select
        product_id,
        row_number() over () as review_id,
        cast(rating as integer) as rating,
        review_title,
        review_content,
        cast(polarity as numeric) as polarity,
        cast(subjectivity as numeric) as subjectivity,
        length(review_content) as review_length,
        array_length(string_to_array(review_content, ' '), 1) as word_count
    from source_data
    where review_content is not null
)

select * from with_review_id
