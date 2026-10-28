# Olist E-Commerce Customer Experience and Retention Analysis

An exploratory analysis of Brazilian e-commerce transactions examining business growth, delivery performance, customer satisfaction, repeat purchasing, and customer value.

The analysis identifies delivery delays and interstate shipping as priorities for operational investigation. It also finds that first-order experience alone does not explain low repeat purchasing, motivating an RFM segmentation approach to customer engagement.

## Business Questions

- Is GMV growth driven primarily by more orders or higher average order value?
- How are delivery delays and delay severity associated with customer ratings?
- Which fulfillment stages and shipment characteristics are associated with delays?
- How does first-order experience relate to subsequent purchasing?
- Which customer segments should be prioritized for retention efforts?
- Which payment methods do customers use most frequently?

## Data

The project uses the public Olist Brazilian e-commerce dataset, covering historical transactions from September 2016 to September 2018. Eight relational tables provide information about orders, customers, items, payments, reviews, products, sellers, and product category translations.

| Source table | Main analytical use |
| --- | --- |
| `olist_orders_dataset` | Order status, purchase dates, and fulfillment timestamps |
| `olist_customers_dataset` | Customer identity and geographic attributes |
| `olist_order_items_dataset` | Items, product prices, freight charges, and seller links |
| `olist_order_payments_dataset` | Payment methods, amounts, and installments |
| `olist_order_reviews_dataset` | Customer review scores |
| `olist_products_dataset` | Product categories, weight, and dimensions |
| `olist_sellers_dataset` | Seller identity and location |
| `product_category_name_translation` | Portuguese-to-English category labels |

The orders table contains more than 99,000 records. The analysis reports 96,478 delivered orders, of which 96,470 have the timestamps required for the delivery-status comparison. Customer purchase-frequency and RFM analyses cover 93,358 customers.

Review titles and review text are excluded; this project does not perform sentiment analysis. The dataset does not include advertising exposure, marketing spend, browsing behavior, or traffic acquisition sources.

## Analytical Workflow

1. **Prepare and integrate data:** Align relational tables for order-, item-, payment-, and customer-level analysis. Supplement missing category translations for `pc_gamer` and `portateis_cozinha_e_preparadores_de_alimentos`.
2. **Explore business performance:** Examine monthly GMV, delivered orders, average order value, active purchasing customers, and category performance.
3. **Investigate customer experience:** Compare ratings by delivery status and delay severity; examine fulfillment stages, interstate shipping, product weight, product volume, and freight burden.
4. **Examine repeat purchasing:** Compare subsequent purchase rates by first-order rating and first-order delivery status.
5. **Segment customers:** Build Recency, Frequency, and Monetary scores and translate the resulting segments into differentiated engagement strategies.
6. **Assess payment preferences:** Summarize payment-method shares as an additional perspective on the transaction experience.

## Metric Definitions and Scope

| Metric | Interpretation |
| --- | --- |
| GMV | Merchandise transaction value; assessed alongside order volume and AOV |
| Average order value (AOV) | GMV divided by the relevant order count |
| Active purchasing customers | Distinct customers with purchases in the period |
| Delivery duration | Elapsed time from purchase to customer delivery |
| Carrier transit time | Elapsed time from carrier handoff to customer delivery |
| Late delivery | Delivery after the estimated delivery date; delivery on that date counts as on time |
| Low rating | A review score of 1 or 2 |
| Repeat purchaser | A customer with at least two purchases in the observed analysis window |
| Recency | Days since the customer's most recent purchase, relative to an analysis reference date |
| Frequency | Number of purchases per customer |
| Monetary | Customer purchase value in Brazilian reais (R$) |

Business performance and delivery analyses focus on delivered orders. Review comparisons require available review scores; delivery comparisons require valid timestamps. Consequently, denominators differ across analyses. Payment-method shares are based on payment records, not unique customers or orders.

## Key Findings

### 1. Growth was primarily associated with order and customer expansion

Monthly GMV and delivered-order volume moved together, while AOV generally remained around R$125–150. Both GMV and order volume peaked in November 2017. These patterns suggest that growth was primarily driven by more transactions and purchasing customers rather than a sustained increase in basket value.

December 2016 is an unstable monthly comparison: it contains only one delivered order, worth R$10.90.

### 2. Late deliveries were associated with substantially lower ratings

Of the 96,470 delivered orders eligible for the delivery-status comparison, 7,826 were late: a delay rate of **8.11%**.

| Delivery status | Orders | Share | Low-rating rate |
| --- | ---: | ---: | ---: |
| On time or early | 88,644 | 91.89% | 9.19% |
| Late | 7,826 | 8.11% | 53.99% |

Order counts and shares describe delivery-status eligibility; low-rating rates use the corresponding review-eligible observations.

Low-rating rates increased sharply after three days of delay: approximately 19.1% for delays of 1–3 days, 61.3% for 4–7 days, and 78–82% for 8–30 days. The rate fell to 68.5% for delays above 30 days, a smaller group containing 343 orders. The relationship is strong but not strictly monotonic.

### 3. The largest fulfillment difference occurred after carrier handoff

| Delivery status | Purchase to carrier handoff | Carrier handoff to delivery |
| --- | ---: | ---: |
| On time or early | 3.00 days | 7.88 days |
| Late | 5.82 days | 25.56 days |

Carrier transit time differed more substantially than the pre-handoff stage, making transportation performance a priority for further investigation.

| Shipping scope | Average carrier transit time | Delay rate |
| --- | ---: | ---: |
| Within the same state | 4.79 days | 6.03% |
| Interstate | 11.86 days | 9.16% |

Weight and volume showed weaker descriptive relationships with delivery performance than shipping scope. Among on-time orders, lower-rated orders also had somewhat longer delivery durations, while differences in relative freight charges were small.

### 4. Repeat purchasing was low, with limited differences by first-order experience

Of 93,358 customers, **90,557 purchased once (97.0%)** and **2,801 purchased at least twice (approximately 3.0%)** during the observed window.

| First-order characteristic | Subsequent repeat-purchase rate |
| --- | ---: |
| Non-low rating | 3.03% |
| Low rating | 2.76% |
| On-time or early delivery | 3.04% |
| Late delivery | 2.51% |

The differences are **0.27 percentage points** by rating and **0.53 percentage points** by delivery status. They do not establish causation or statistical significance. First-order experience alone offers a limited explanation for the overall low repeat-purchase rate.

### 5. RFM segmentation identified a sizable second-purchase opportunity

Customer purchase frequency was highly concentrated at one purchase. To reflect that distribution, Frequency scores use purchase counts directly rather than forcing customers into equal-sized groups.

- **Recency:** Five distribution-based score groups; more recent purchases receive higher scores.
- **Frequency:** One to four purchases receive scores of 1–4; five or more receive a score of 5.
- **Monetary:** Five distribution-based score groups; higher purchase value receives a higher score.

| Segment | Score rules | Interpretation | Reported share |
| --- | --- | --- | ---: |
| High-value Active | R ≥ 3, F ≥ 2, M ≥ 4 | Recent repeat purchasers with higher spending | Combined with Repeat Active: below 2% |
| Repeat Active | R ≥ 3, F ≥ 2, M ≤ 3 | Recent repeat purchasers with lower spending | Included above |
| High-potential | R ≥ 3, F = 1, M ≥ 4 | Recent, higher-spending customers who have not repurchased | 22.9% |
| Active | R ≥ 3, F = 1, M ≤ 3 | Recent single-purchase customers with lower spending | 35.3% |
| Inactive | R ≤ 2 | Customers with less recent purchases | 39.9% |

Shares are rounded. The High-potential segment is a practical audience for testing second-purchase incentives; it does not represent a measured campaign uplift or a prediction of future conversion.

### 6. Credit cards dominated payment records

Credit cards accounted for **73.9%** of payment records, followed by boleto at **19.0%** and vouchers at **5.6%**. Other methods accounted for the remaining share.

## Business Recommendations

| Priority area | Proposed action |
| --- | --- |
| Delivery exception management | Flag orders approaching their estimated delivery date; follow up on shipment exceptions and proactively communicate delivery progress. |
| Interstate fulfillment | Investigate high-risk routes and carrier performance; calibrate delivery promises using historical transit patterns. |
| Second-purchase conversion | Test time-limited incentives and relevant product recommendations for High-potential customers. |
| High-value customer engagement | Evaluate loyalty benefits, exclusive offers, and early product access for High-value Active customers. |
| Segmented retention | Use bundles and spending thresholds for Repeat Active customers, lower-cost outreach for Active customers, and value-based reactivation priorities for Inactive customers. |
| Payment experience | Prioritize reliable credit-card checkout while retaining boleto and voucher options for customers with different preferences. |

These are recommendations for future validation. The project does not report deployed interventions, campaign results, or realized business impact.

## Limitations

- **Observational evidence:** Findings describe associations. They do not prove that delivery changes cause better ratings or increased retention.
- **Historical scope:** Results reflect the 2016–2018 dataset and should not be presented as current Olist performance.
- **Unequal follow-up windows:** Customers purchasing near the end of the dataset have less time to repurchase. The reported repeat-purchase rates are observed-window measures, not standardized cohort retention estimates.
- **Review availability:** Rating-based analyses cover orders with usable reviews and may not represent all customers.
- **Missing explanatory data:** Browsing, acquisition, marketing, and review-text information are unavailable or excluded, limiting explanations of dissatisfaction and low repeat purchasing.
- **RFM reproducibility:** The analysis reference date, exact Recency/Monetary cutoffs, and tie-handling rules should accompany the implementation for exact reproduction.
- **Metric reproducibility:** Exact GMV/Monetary value fields, freight inclusion, review-selection rules, and join aggregation rules should be documented with the analysis code. The supplied report does not fully specify these choices.

## Repository and Reproduction Notes

This README summarizes the supplied analytical report. Source code, notebooks, dependency files, and a repository directory structure were not supplied with it, so no unverified setup commands or file links are included.

To reproduce the reported analysis, the repository should provide:

1. The eight source tables and their data-source attribution.
2. Data preparation and analysis scripts or notebooks, with the execution order.
3. Dependency versions and setup instructions.
4. Customer identity rules, table join keys, and safeguards against double-counting item or payment records.
5. Analysis filters, timestamp handling, metric definitions, and RFM scoring settings.
6. Exported figures or tables supporting the reported findings.

## Project Outcome

The project translates transaction-level evidence into two complementary priorities: improve delivery reliability, especially during carrier transit and interstate shipping, and test targeted retention strategies for recent, higher-spending single-purchase customers. It separates measured findings from proposed actions and recognizes the limits of explaining retention through first-order experience alone.
