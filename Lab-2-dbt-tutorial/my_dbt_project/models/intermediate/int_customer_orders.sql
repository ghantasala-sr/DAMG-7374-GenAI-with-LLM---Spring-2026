with orders as (

    select * from {{ ref('stg_orders') }}

),

payments as (

    select * from {{ ref('stg_payments') }}

),

order_payments as (
    select 
        order_id,
        sum(amount) as total_amount
    from payments
    group by 1
),

customer_orders as (

    select
        orders.customer_id,
        min(orders.order_date) as first_order_date,
        max(orders.order_date) as most_recent_order_date,
        count(orders.order_id) as number_of_orders,
        sum(order_payments.total_amount) as lifetime_value

    from orders
    left join order_payments using (order_id)
    group by 1

)

select * from customer_orders
