------------------------- dash1-1
select
    o.order_id,
    c.customer_unique_id,
    o.order_purchase_timestamp,
    i.order_value
FROM olist_orders_dataset o
LEFT JOIN olist_customers_dataset c
    ON o.customer_id = c.customer_id
LEFT JOIN (
    SELECT
        order_id,
        SUM(price) AS order_value
    FROM olist_order_items_dataset
    GROUP BY order_id
) i
    ON o.order_id = i.order_id
WHERE o.order_status = 'delivered';
------------------------------dash1-2
SELECT
    t.product_category_name_english product_category,
    SUM(i.price) category_gmv
FROM olist_orders_dataset o
JOIN olist_order_items_dataset i
    ON o.order_id = i.order_id
JOIN olist_products_dataset p
    ON i.product_id = p.product_id
LEFT JOIN product_category_name_translation t
    ON p.product_category_name = t.product_category_name
WHERE o.order_status = 'delivered'
GROUP BY
    t.product_category_name_english
ORDER BY
    category_gmv desc;
---------------------------------dash2
WITH review_per_order AS (
    SELECT
        order_id,
        AVG(review_score) AS review_score
    FROM olist_order_reviews_dataset
    GROUP BY order_id
),
seller_state_per_order AS (
    SELECT
        i.order_id,
        MIN(s.seller_state) AS seller_state
    FROM olist_order_items_dataset i
    JOIN olist_sellers_dataset s
        ON i.seller_id = s.seller_id
    GROUP BY i.order_id
    HAVING COUNT(DISTINCT s.seller_state) = 1
)
SELECT
    o.order_id,
    -- ==========================================
    -- 1. Customer Review
    -- ==========================================
    r.review_score,
    CASE
        WHEN r.review_score IS NULL THEN NULL
        WHEN r.review_score <= 2 THEN 1
        ELSE 0
    END AS low_rating,
    -- ==========================================
    -- 2. Delivery Status
    -- ==========================================
    CASE
        WHEN CAST(NULLIF(o.order_delivered_customer_date, '') AS TIMESTAMP)
             > CAST(NULLIF(o.order_estimated_delivery_date, '') AS TIMESTAMP)
        THEN 1
        ELSE 0
    END AS late_delivery,
    -- Actual Delivery Date - Estimated Delivery Date
    -- > 0  = Late
    -- <= 0 = On-time / Early
    EXTRACT(
        EPOCH FROM (
            CAST(NULLIF(o.order_delivered_customer_date, '') AS TIMESTAMP)
            - CAST(NULLIF(o.order_estimated_delivery_date, '') AS TIMESTAMP)
        )
    ) / 86400.0 AS delay_days,
    -- ==========================================
    -- 3. Delay Severity
    -- ==========================================
    CASE
        WHEN CAST(NULLIF(o.order_delivered_customer_date, '') AS TIMESTAMP)
             <= CAST(NULLIF(o.order_estimated_delivery_date, '') AS TIMESTAMP)
        THEN 'On-time / Early'
        WHEN EXTRACT(
            EPOCH FROM (
                CAST(NULLIF(o.order_delivered_customer_date, '') AS TIMESTAMP)
                - CAST(NULLIF(o.order_estimated_delivery_date, '') AS TIMESTAMP)
            )
        ) / 86400.0 <= 3
        THEN '1-3 days'
        WHEN EXTRACT(
            EPOCH FROM (
                CAST(NULLIF(o.order_delivered_customer_date, '') AS TIMESTAMP)
                - CAST(NULLIF(o.order_estimated_delivery_date, '') AS TIMESTAMP)
            )
        ) / 86400.0 <= 7
        THEN '4-7 days'
        WHEN EXTRACT(
            EPOCH FROM (
                CAST(NULLIF(o.order_delivered_customer_date, '') AS TIMESTAMP)
                - CAST(NULLIF(o.order_estimated_delivery_date, '') AS TIMESTAMP)
            )
        ) / 86400.0 <= 14
        THEN '8-14 days'
        WHEN EXTRACT(
            EPOCH FROM (
                CAST(NULLIF(o.order_delivered_customer_date, '') AS TIMESTAMP)
                - CAST(NULLIF(o.order_estimated_delivery_date, '') AS TIMESTAMP)
            )
        ) / 86400.0 <= 30
        THEN '15-30 days'
        ELSE '30+ days'
    END AS delay_group,
    -- ==========================================
    -- 4. Delivery Stage
    -- ==========================================
    -- Purchase -> Carrier
    EXTRACT(
        EPOCH FROM (
            CAST(NULLIF(o.order_delivered_carrier_date, '') AS TIMESTAMP)
            - CAST(NULLIF(o.order_purchase_timestamp, '') AS TIMESTAMP)
        )
    ) / 86400.0 AS purchase_to_carrier_days,
    -- Carrier -> Customer
    EXTRACT(
        EPOCH FROM (
            CAST(NULLIF(o.order_delivered_customer_date, '') AS TIMESTAMP)
            - CAST(NULLIF(o.order_delivered_carrier_date, '') AS TIMESTAMP)
        )
    ) / 86400.0 AS carrier_delivery_days,
    -- Purchase -> Customer
    EXTRACT(
        EPOCH FROM (
            CAST(NULLIF(o.order_delivered_customer_date, '') AS TIMESTAMP)
            - CAST(NULLIF(o.order_purchase_timestamp, '') AS TIMESTAMP)
        )
    ) / 86400.0 AS total_delivery_days,
    -- ==========================================
    -- 5. Geographic Delivery
    -- ==========================================
    c.customer_state,
    ss.seller_state,
    CASE
        WHEN ss.seller_state IS NULL THEN NULL
        WHEN c.customer_state = ss.seller_state
        THEN 'Same State'
        ELSE 'Cross State'
    END AS delivery_scope,
    -- ==========================================
    -- 6. Original timestamps
    -- Convert VARCHAR -> TIMESTAMP for Tableau
    -- ==========================================
    CAST(
        NULLIF(o.order_purchase_timestamp, '')
        AS TIMESTAMP
    ) AS order_purchase_timestamp,
    CAST(
        NULLIF(o.order_delivered_carrier_date, '')
        AS TIMESTAMP
    ) AS order_delivered_carrier_date,
    CAST(
        NULLIF(o.order_delivered_customer_date, '')
        AS TIMESTAMP
    ) AS order_delivered_customer_date,
    CAST(
        NULLIF(o.order_estimated_delivery_date, '')
        AS TIMESTAMP
    ) AS order_estimated_delivery_date
FROM olist_orders_dataset o
JOIN olist_customers_dataset c
    ON o.customer_id = c.customer_id
LEFT JOIN review_per_order r
    ON o.order_id = r.order_id
LEFT JOIN seller_state_per_order ss
    ON o.order_id = ss.order_id
WHERE o.order_status = 'delivered'
  -- Remove both NULL and empty-string values
  -- for the two core delivery-status timestamps
  AND NULLIF(o.order_delivered_customer_date, '') IS NOT NULL
  AND NULLIF(o.order_estimated_delivery_date, '') IS NOT null;
----------------------------------dash3
WITH order_value AS (
    -- 1. Calculate value of each order
    SELECT
        order_id,
        SUM(price) AS order_value
    FROM olist_order_items_dataset
    GROUP BY order_id
),
customer_orders AS (
    -- 2. Join delivered orders to unique customers
    SELECT
        c.customer_unique_id,
        o.order_id,
        CAST(
            NULLIF(o.order_purchase_timestamp, '')
            AS TIMESTAMP
        ) AS order_purchase_timestamp,
        ov.order_value
    FROM olist_orders_dataset o
    JOIN olist_customers_dataset c
        ON o.customer_id = c.customer_id
    LEFT JOIN order_value ov
        ON o.order_id = ov.order_id
    WHERE o.order_status = 'delivered'
      AND NULLIF(o.order_purchase_timestamp, '') IS NOT NULL
),
reference_date AS (
    -- 3. Reference date = latest purchase date in the dataset
    SELECT
        MAX(order_purchase_timestamp) AS max_date
    FROM customer_orders
),
rfm_base AS (
    -- 4. Aggregate from order level to customer level
    SELECT
        customer_unique_id,
        MIN(order_purchase_timestamp) AS first_purchase_date,
        MAX(order_purchase_timestamp) AS last_purchase_date,
        COUNT(DISTINCT order_id) AS frequency,
        SUM(order_value) AS monetary
    FROM customer_orders
    GROUP BY customer_unique_id
),
customer_rfm AS (
    -- 5. Calculate Recency
    SELECT
        r.customer_unique_id,
        r.first_purchase_date,
        r.last_purchase_date,
        -- Number of days since the customer's last purchase
        (
            ref.max_date::DATE
            - r.last_purchase_date::DATE
        ) AS recency,
        r.frequency,
        r.monetary
    FROM rfm_base r
    CROSS JOIN reference_date ref
),
rfm_scores AS (
    -- 6. Calculate R / F / M scores
    SELECT
        customer_unique_id,
        first_purchase_date,
        last_purchase_date,
        recency,
        frequency,
        monetary,
        -- Recency:
        -- longer inactivity = lower score
        -- more recent purchase = higher score
        NTILE(5) OVER (
            ORDER BY recency DESC
        ) AS r_score,
        -- Frequency:
        -- 1 purchase = F1
        -- 2 purchases = F2
        -- ...
        -- 5+ purchases = F5
        CASE
            WHEN frequency = 1 THEN 1
            WHEN frequency = 2 THEN 2
            WHEN frequency = 3 THEN 3
            WHEN frequency = 4 THEN 4
            ELSE 5
        END AS f_score,
        -- Monetary:
        -- lower spending = lower score
        -- higher spending = higher score
        NTILE(5) OVER (
            ORDER BY monetary ASC
        ) AS m_score
    FROM customer_rfm
),
rfm_segments AS (
    -- 7. Segment customers using the report's rules
    SELECT
        customer_unique_id,
        first_purchase_date,
        last_purchase_date,
        recency,
        frequency,
        monetary,
        r_score,
        f_score,
        m_score,
        -- Combined RFM score, e.g. 514
        (
            r_score::TEXT
            || f_score::TEXT
            || m_score::TEXT
        ) AS rfm_score,
        CASE
            -- R <= 2
            WHEN r_score <= 2
            THEN 'Inactive'
            -- R >= 3, F >= 2, M >= 4
            WHEN r_score >= 3
                 AND f_score >= 2
                 AND m_score >= 4
            THEN 'High-value Active'
            -- R >= 3, F >= 2, M <= 3
            WHEN r_score >= 3
                 AND f_score >= 2
                 AND m_score <= 3
            THEN 'Repeat Active'
            -- R >= 3, F = 1, M >= 4
            WHEN r_score >= 3
                 AND f_score = 1
                 AND m_score >= 4
            THEN 'High-potential'
            -- R >= 3, F = 1, M <= 3
            WHEN r_score >= 3
                 AND f_score = 1
                 AND m_score <= 3
            THEN 'Active'
        END AS customer_segment,
        -- Useful for Tableau KPI
        CASE
            WHEN frequency >= 2 THEN 1
            ELSE 0
        END AS is_repeat_customer
    FROM rfm_scores
)
SELECT
    customer_unique_id,
    first_purchase_date,
    last_purchase_date,
    recency,
    frequency,
    monetary,
    r_score,
    f_score,
    m_score,
    rfm_score,
    customer_segment,
    is_repeat_customer
FROM rfm_segments;