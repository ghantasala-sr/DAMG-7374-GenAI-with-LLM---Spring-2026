with source as (

    select * from {{ source('snowflake', 'payments') }}

),

renamed as (

    select
        id as payment_id,
        order_id,
        payment_method,
        amount / 100 as amount -- amounts are stored in cents, convert to dollars

    from source

)

select * from renamed
