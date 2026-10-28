#%%
import numpy as np
import pandas as pd

df_review=pd.read_csv('/Users/hfg/Desktop/olist datasets/olist_order_reviews_dataset_clean.csv')
df_item=pd.read_csv('/Users/hfg/Desktop/olist datasets/olist_order_items_dataset.csv')
df_payment=pd.read_csv('/Users/hfg/Desktop/olist datasets/olist_order_payments_dataset.csv')
df_order=pd.read_csv('/Users/hfg/Desktop/olist datasets/olist_orders_dataset.csv')
df_customer=pd.read_csv('/Users/hfg/Desktop/olist datasets/olist_customers_dataset.csv')
df_product=pd.read_csv('/Users/hfg/Desktop/olist datasets/olist_products_dataset.csv')
df_seller=pd.read_csv('/Users/hfg/Desktop/olist datasets/olist_sellers_dataset.csv')
df_category=pd.read_csv('/Users/hfg/Desktop/olist datasets/product_category_name_translation.csv')

# %%
#查看每个表的形状
print(df_review.shape)
print(df_item.shape)
print(df_payment.shape)
print(df_order.shape)
print(df_customer.shape)
print(df_product.shape)
print(df_seller.shape)
print(df_category.shape)
# %%
#4.1.1订单情况
import matplotlib.pyplot as plt
df_order['order_status'].value_counts()
# 绘制柱状图
plt.figure(figsize=(8, 5))
df_order['order_status'].value_counts().plot(kind='bar', color="#1f77b4")

plt.title("Distribution of Order Status", fontsize=13)
plt.xlabel("Order Status", fontsize=11)
plt.ylabel("Order Count", fontsize=11)
plt.xticks(rotation=30) # 标签旋转防止文字重叠
plt.grid(axis='y', alpha=0.3)
plt.tight_layout() # 自动调整布局，避免标签被截断
plt.show()
# %%
#4.1.2.GMV,看年-月分布
delivered_orders = df_order.loc[
    df_order['order_status'] == 'delivered',
    ['order_id', 'order_purchase_timestamp']
].copy()
gmv_data = delivered_orders.merge(
    df_item[['order_id', 'price']],
    on='order_id',
    how='inner'
)
gmv_data['order_purchase_timestamp'] = pd.to_datetime(
    gmv_data['order_purchase_timestamp']
)

gmv_data['year_month'] = (
    gmv_data['order_purchase_timestamp']
    .dt.to_period('M')
)
monthly_gmv = (
    gmv_data
    .groupby('year_month')['price']
    .sum()
    .reset_index(name='gmv')
)

print(monthly_gmv)

#GMV可视化
monthly_gmv['year_month'] = monthly_gmv['year_month'].astype(str)

plt.figure(figsize=(12, 5))

plt.plot(
    monthly_gmv['year_month'],
    monthly_gmv['gmv'],
    marker='o'
)

plt.title('Monthly GMV of Delivered Orders')
plt.xlabel('Month')
plt.ylabel('GMV')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
# %%
#月度订单量
# 转换日期
delivered_orders['order_purchase_timestamp'] = pd.to_datetime(
    delivered_orders['order_purchase_timestamp']
)

# 构造年月
delivered_orders['year_month'] = (
    delivered_orders['order_purchase_timestamp']
    .dt.to_period('M')
)

# 每月订单数
monthly_orders = (
    delivered_orders
    .groupby('year_month')['order_id']
    .nunique()
    .reset_index(name='order_count')
)

#月度订单量可视化
plt.figure(figsize=(12, 5))

plt.plot(
    monthly_orders['year_month'].astype(str),
    monthly_orders['order_count'],
    marker='o'
)

plt.title('Monthly Delivered Orders')
plt.xlabel('Month')
plt.ylabel('Number of Orders')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
# %%
# %%
#AOV
#合并GMV和月度order
monthly_gmv['year_month'] = pd.to_datetime(
    monthly_gmv['year_month']
).dt.to_period('M')#变为同样period[M]

monthly_business = pd.merge(
    monthly_gmv,
    monthly_orders,
    on='year_month',
    how='inner'
)
#%%
#计算AOV
monthly_business['aov'] = (
    monthly_business['gmv'] / monthly_business['order_count']
)
#AOV可视化
# %%
plt.figure(figsize=(12, 5))

plt.plot(
    monthly_business['year_month'].astype(str),
    monthly_business['aov'],
    marker='o'
)

plt.title('Monthly Average Order Value (AOV)')
plt.xlabel('Month')
plt.ylabel('AOV')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
# %%
#4.1.3.月度客户数
# delivered订单
delivered_customer = df_order.loc[
    df_order['order_status'] == 'delivered',
    ['order_id', 'customer_id', 'order_purchase_timestamp']
].copy()

# join customer，获得customer_unique_id
delivered_customer = delivered_customer.merge(
    df_customer[['customer_id', 'customer_unique_id']],
    on='customer_id',
    how='left'
)

# 日期处理
delivered_customer['order_purchase_timestamp'] = pd.to_datetime(
    delivered_customer['order_purchase_timestamp']
)

delivered_customer['year_month'] = (
    delivered_customer['order_purchase_timestamp']
    .dt.to_period('M')
)
#计算月度unique customer
monthly_customers = (
    delivered_customer
    .groupby('year_month')['customer_unique_id']
    .nunique()
    .reset_index(name='customer_count')
)
#月度客户数可视化
plt.figure(figsize=(12, 5))

plt.plot(
    monthly_customers['year_month'].astype(str),
    monthly_customers['customer_count'],
    marker='o'
)

plt.title('Monthly Active Customers')
plt.xlabel('Month')
plt.ylabel('Number of Customers')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
# %%
#4.1.4.各品类销量
# delivered order id
delivered_id = df_order.loc[
    df_order['order_status'] == 'delivered',
    ['order_id']
]

# item + product
category_data = (
    df_item
    .merge(delivered_id, on='order_id', how='inner')
    .merge(
        df_product[['product_id', 'product_category_name']],
        on='product_id',
        how='left'
    )
    .merge(
        df_category,
        on='product_category_name',
        how='left'
    )
)
#查看缺失category分类的产品
category_data[
    ['product_id', 'product_category_name', 'product_category_name_english']
].isna().sum()
#缺失分类标为unknown
category_data[
    ['product_category_name', 'product_category_name_english']
] = category_data[
    ['product_category_name', 'product_category_name_english']
].fillna('Unknown')
# %%
# %%
#top10销量的种类
category_sales = (
    category_data
    .groupby('product_category_name_english')
    .size()
    .reset_index(name='items_sold')
    .sort_values('items_sold', ascending=False)
)

category_sales.head(10)
#种类销量可视化top10
top10_sales = category_sales.head(10)

plt.figure(figsize=(10, 6))

plt.barh(
    top10_sales['product_category_name_english'],
    top10_sales['items_sold']
)

plt.title('Top 10 Product Categories by Sales Volume')
plt.xlabel('Number of Items Sold')
plt.ylabel('Product Category')

plt.gca().invert_yaxis()
plt.tight_layout()
plt.show()
# %%
#4.1.5.各品类GMV top10
category_gmv = (
    category_data
    .groupby('product_category_name_english', as_index=False)
    .agg(gmv=('price', 'sum'))
    .sort_values('gmv', ascending=False)
)
#各品类GMV可视化
top10_gmv = category_gmv.head(10)

plt.figure(figsize=(10, 6))

plt.barh(
    top10_gmv['product_category_name_english'],
    top10_gmv['gmv']
)

plt.title('Top 10 Product Categories by GMV')
plt.xlabel('GMV (BRL)')
plt.ylabel('Product Category')
plt.gca().invert_yaxis()

plt.tight_layout()
plt.show()
# %%
#4.2客户体验
#客户评分分布
review_count = (
    df_review['review_score']
    .value_counts()
    .sort_index()
)
#各评分占比
review_pct = (
    df_review['review_score']
    .value_counts(normalize=True)
    .sort_index()
    .mul(100)
)
#评分可视化
plt.figure(figsize=(7, 7))

wedges, texts, autotexts = plt.pie(
    review_count.values,
    autopct='%1.1f%%',
    startangle=90
)

plt.legend(
    wedges,
    review_count.index,
    title='Review Score'
)

plt.title('Distribution of Review Scores')
plt.tight_layout()
plt.show()
# %%
#4.2.2配送时长分布
# 只取 delivered orders
delivery_data = df_order.loc[
    df_order['order_status'] == 'delivered',
    [
        'order_id',
        'order_purchase_timestamp',
        'order_delivered_customer_date'
    ]
].copy()

# 转换时间格式
delivery_data['order_purchase_timestamp'] = pd.to_datetime(
    delivery_data['order_purchase_timestamp']
)

delivery_data['order_delivered_customer_date'] = pd.to_datetime(
    delivery_data['order_delivered_customer_date']
)
#timestamp有空值
delivery_data[
    ['order_purchase_timestamp', 'order_delivered_customer_date']
].isna().sum()
#只有8条，去掉不影响
delivery_valid = delivery_data.dropna(
    subset=['order_delivered_customer_date']
).copy()
delivery_valid['delivery_days'] = (
    delivery_valid['order_delivered_customer_date']
    - delivery_valid['order_purchase_timestamp']
).dt.total_seconds() / 86400
# %%
delivery_valid['delivery_days'].describe()
#配送时间可视化
plt.figure(figsize=(10, 5))

plt.hist(
    delivery_valid['delivery_days'],
    bins=50,
    edgecolor='black'
)

plt.title('Distribution of Delivery Days')
plt.xlabel('Delivery Days')
plt.ylabel('Number of Orders')

plt.tight_layout()
plt.show()

# %%
#4.2.3配送延迟
delay_data = df_order.loc[
    df_order['order_status'] == 'delivered',
    [
        'order_id',
        'order_delivered_customer_date',
        'order_estimated_delivery_date'
    ]
].copy()

delay_data['order_delivered_customer_date'] = pd.to_datetime(
    delay_data['order_delivered_customer_date']
)

delay_data['order_estimated_delivery_date'] = pd.to_datetime(
    delay_data['order_estimated_delivery_date']
)
#查空值
delay_data[
    ['order_delivered_customer_date', 'order_estimated_delivery_date']
].isna().sum()
#只有8条，删去不影响
delay_valid = delay_data.dropna(
    subset=['order_delivered_customer_date']
).copy()
delay_valid['delay_days'] = (
    delay_valid['order_delivered_customer_date']
    - delay_valid['order_estimated_delivery_date']
).dt.total_seconds() / 86400
# %%
delay_valid['delay_days'].describe()
#计算延迟天数
delay_valid['late_delivery'] = (
    delay_valid['delay_days'] > 0
)
late_count = delay_valid['late_delivery'].value_counts()
#计算延迟占比
late_pct = (
    delay_valid['late_delivery']
    .value_counts(normalize=True)
    .mul(100)
)
#false=on-time/early, true=late
print(late_count)
print(late_pct)
# %%
#4.3.1客户购买次数
# %%
customer_purchase = (
    df_order.loc[
        df_order['order_status'] == 'delivered',
        ['order_id', 'customer_id']
    ]
    .merge(
        df_customer[['customer_id', 'customer_unique_id']],
        on='customer_id',
        how='left'
    )
)
purchase_frequency = (
    customer_purchase
    .groupby('customer_unique_id')['order_id']
    .nunique()
)

purchase_frequency.describe()
#计算买不同次数的人数
purchase_count_distribution = (
    purchase_frequency
    .value_counts()
    .sort_index()
)

print(purchase_count_distribution)
# %%
#复购率
repeat_purchase_rate = (
    (purchase_frequency >= 2).mean() * 100
)

print(f'Repeat Purchase Rate: {repeat_purchase_rate:.2f}%')
# %%
purchase_type = pd.Series({
    'Single Purchase': (purchase_frequency == 1).sum(),
    'Repeat Purchase': (purchase_frequency >= 2).sum()
})
#复购占比可视化
plt.figure(figsize=(7, 7))

wedges, texts, autotexts = plt.pie(
    purchase_type.values,
    autopct='%1.1f%%',
    startangle=90
)

plt.legend(
    wedges,
    purchase_type.index,
    title='Customer Type'
)

plt.title('Customer Purchase Frequency')
plt.tight_layout()
plt.show()

#复购次数可视化
purchase_count_distribution = (
    purchase_frequency
    .value_counts()
    .sort_index()
)
plt.figure(figsize=(10, 5))

plt.bar(
    purchase_count_distribution.index,
    purchase_count_distribution.values,
    edgecolor='black'
)

plt.title('Distribution of Customer Purchase Frequency')
plt.xlabel('Number of Purchases')
plt.ylabel('Number of Customers')

plt.xticks(purchase_count_distribution.index)

plt.tight_layout()
plt.show()
# %%
#5.1订单与各自综合评分相join
review_order = (
    df_review
    .groupby('order_id', as_index=False)
    .agg(
        review_score=('review_score', 'mean')
    )
)

experience_data = delay_valid.merge(
    review_order,
    on='order_id',
    how='inner'
)
#判断低综合评分
experience_data['low_rating'] = (
    experience_data['review_score'] <= 2
)
# %%
#综合低分订单数占（非）延迟订单总数=low rate numbers/is(not)late numbers
late_low_rating = (
    experience_data
    .groupby('late_delivery')['low_rating']
    .agg(['count', 'sum', 'mean'])
)

late_low_rating['low_rating_rate'] = (
    late_low_rating['mean'] * 100
)

late_low_rating
# %%
#上述可视化
rating_by_delivery = (
    experience_data
    .groupby('late_delivery')['low_rating']
    .mean()
    .mul(100)
)

plt.figure(figsize=(7, 5))

plt.bar(
    ['On-time / Early', 'Late'],
    rating_by_delivery.values,
    edgecolor='black'
)

plt.title('Low Rating Rate by Delivery Status')
plt.xlabel('Delivery Status')
plt.ylabel('Low Rating Rate (%)')

plt.tight_layout()
plt.show()
# %%
#判断属于延迟多少天的组
late_orders = experience_data[
    experience_data['delay_days'] > 0
].copy()

bins = [0, 3, 7, 14, 30, float('inf')]
labels = ['1-3 days', '4-7 days', '8-14 days', '15-30 days', '30+ days']

late_orders['delay_group'] = pd.cut(
    late_orders['delay_days'],
    bins=bins,
    labels=labels
)
#根据分好的不同延迟时间组，计算订单低分率
delay_rating = (
    late_orders
    .groupby('delay_group', observed=True)
    .agg(
        order_count=('order_id', 'count'),
        low_rating_rate=('low_rating', 'mean')
    )
    .reset_index()
)

delay_rating['low_rating_rate'] *= 100

delay_rating
# %%
#延迟组可视化
plt.figure(figsize=(8, 5))

plt.plot(
    delay_rating['delay_group'].astype(str),
    delay_rating['low_rating_rate'],
    marker='o',
    color='red'
)

plt.title('Low Rating Rate by Delay Severity')
plt.xlabel('Delay Severity')
plt.ylabel('Low Rating Rate (%)')

plt.tight_layout()
plt.show()
# %%
#将原本order表的三个时间join在一起，购买时间、交付货运时间、送达时间
experience_data = experience_data.merge(
    df_order[
        ['order_id',
         'order_purchase_timestamp',
         'order_delivered_carrier_date']
    ],
    on='order_id',
    how='left'
)
experience_data['order_purchase_timestamp'] = pd.to_datetime(
    experience_data['order_purchase_timestamp']
)

experience_data['order_delivered_carrier_date'] = pd.to_datetime(
    experience_data['order_delivered_carrier_date']
)
#%%
#有一个缺失，去掉不影响
experience_data[
    ['order_purchase_timestamp',
     'order_delivered_carrier_date',
     'order_delivered_customer_date']
].isna().sum()

stage_data = experience_data.dropna(
    subset=['order_delivered_carrier_date']
).copy()
#下单到交付运输
stage_data['fulfillment_days'] = (
    stage_data['order_delivered_carrier_date']
    - stage_data['order_purchase_timestamp']
).dt.total_seconds() / 86400
#运输到送达
stage_data['carrier_delivery_days'] = (
    stage_data['order_delivered_customer_date']
    - stage_data['order_delivered_carrier_date']
).dt.total_seconds() / 86400
# %%
#对比延迟和非延迟订单中平均花费在下单-送货、送货-到达的时间
stage_compare = (
    stage_data
    .groupby('late_delivery')
    .agg(
        avg_fulfillment_days=('fulfillment_days', 'mean'),
        avg_carrier_delivery_days=('carrier_delivery_days', 'mean')
    )
)

stage_compare
# %%
#item+seller得出seller的state
item_seller = (
    df_item[['order_id', 'seller_id']]
    .merge(
        df_seller[['seller_id', 'seller_state']],
        on='seller_id',
        how='left'
    )
)
#item表一个order对应多个seller，但是对应多个占比极少（510个：98156个）
seller_state_per_order = (
    item_seller
    .groupby('order_id')['seller_state']
    .nunique()
)

seller_state_per_order.value_counts().sort_index()
# %%
#直接取第一个对应的state当作该订单的state
single_state_orders = seller_state_per_order[
    seller_state_per_order == 1
].index

order_seller_state = (
    item_seller[
        item_seller['order_id'].isin(single_state_orders)
    ]
    .groupby('order_id', as_index=False)#order_id 不当index
    .agg(
        seller_state=('seller_state', 'first')# 取了seller_state_per_order == 1后，剩下一个id对多个state的都是同样的state，取第一个即可
    )
)
order_seller_state
# %%
#获取customer的state
order_customer_state = (
    df_order[['order_id', 'customer_id']]
    .merge(
        df_customer[['customer_id', 'customer_state']],
        on='customer_id',
        how='left'
    )
)
#seller和customer的地理位置和之前算下单-送货，送货-送达两个时间的表join
geo_data = (
    stage_data
    .merge(
        order_seller_state,
        on='order_id',
        how='inner'
    )
    .merge(
        order_customer_state[['order_id', 'customer_state']],
        on='order_id',
        how='left'
    )
)
#判断是否跨州
geo_data['cross_state'] = (
    geo_data['seller_state'] != geo_data['customer_state']
)
# %%
#对比同州/跨州分别的平均送货时长，并对比延迟订单数分别在同州/跨州的占比
geo_compare = (
    geo_data
    .groupby('cross_state')
    .agg(
        avg_carrier_delivery_days=('carrier_delivery_days', 'mean'),
        late_delivery_rate=('late_delivery', 'mean')
    )
)

geo_compare['late_delivery_rate'] *= 100

geo_compare
# %%
#item+product(长宽高换成体积)，得每个订单重量+体积
item_product = (
    df_item[['order_id', 'order_item_id', 'product_id']]
    .merge(
        df_product[
            ['product_id',
             'product_weight_g',
             'product_length_cm',
             'product_height_cm',
             'product_width_cm']
        ],
        on='product_id',
        how='left'
    )
)

item_product['product_volume_cm3'] = (
    item_product['product_length_cm']
    * item_product['product_height_cm']
    * item_product['product_width_cm']
)
#长宽高和重量都有18个缺失
item_product[
    [
        'product_weight_g',
        'product_length_cm',
        'product_height_cm',
        'product_width_cm'
    ]
].isna().sum()
# %%
#判断上述18个缺失是不是同为18条
item_product.loc[
    item_product['product_weight_g'].isna(),
    [
        'product_weight_g',
        'product_length_cm',
        'product_height_cm',
        'product_width_cm'
    ]
].isna().all(axis=1).value_counts()
# %%
#18条空值中，来自16条不同的order，排除掉16个对应order_id
invalid_order_ids = item_product.loc[
    item_product['product_weight_g'].isna(),
    'order_id'
].unique()

len(invalid_order_ids)

item_product_valid = item_product[
    ~item_product['order_id'].isin(invalid_order_ids)
].copy()

order_logistics = (
    item_product_valid
    .groupby('order_id', as_index=False)
    .agg(
        item_count=('order_item_id', 'count'),
        total_weight_g=('product_weight_g', 'sum'),
        total_volume_cm3=('product_volume_cm3', 'sum')
    )
)
order_logistics
# %%
#原本包含timestamp和各送达时间的表与重量/体积join
logistics_data = stage_data.merge(
    order_logistics,
    on='order_id',
    how='inner'
)
#看看大致分布，发现有重量最小为0的
logistics_data[
    ['item_count', 'total_weight_g', 'total_volume_cm3']
].describe()
# %%
#查找重量为0的6条记录，进行去除
logistics_data.loc[
    logistics_data['total_weight_g'] == 0,
    ['order_id', 'item_count', 'total_weight_g', 'total_volume_cm3']
]
logistics_valid = logistics_data[
    logistics_data['total_weight_g'] > 0
].copy()
# %%
#重量分四组
logistics_valid['weight_group'] = pd.qcut(
    logistics_valid['total_weight_g'],
    q=4,
    labels=['Q1 Light', 'Q2', 'Q3', 'Q4 Heavy']
)
#和同州/跨州一样，对比不同重量的延迟和不同重量组的延迟率
weight_compare = (
    logistics_valid
    .groupby('weight_group', observed=True)
    .agg(
        avg_carrier_delivery_days=('carrier_delivery_days', 'mean'),
        late_delivery_rate=('late_delivery', 'mean')
    )
    .reset_index()
)

weight_compare['late_delivery_rate'] *= 100

weight_compare
# %%
#体积同上重量的思路
logistics_valid['volume_group'] = pd.qcut(
    logistics_valid['total_volume_cm3'],
    q=4,
    labels=['Q1 Small', 'Q2', 'Q3', 'Q4 Large']
)

volume_compare = (
    logistics_valid
    .groupby('volume_group', observed=True)
    .agg(
        avg_carrier_delivery_days=('carrier_delivery_days', 'mean'),
        late_delivery_rate=('late_delivery', 'mean')
    )
    .reset_index()
)

volume_compare['late_delivery_rate'] *= 100

volume_compare
#%%
experience_data

# %%
#看没有延迟的送达时间
experience_data['delivery_days'] = (
    experience_data['order_delivered_customer_date']
    - experience_data['order_purchase_timestamp']
).dt.total_seconds() / 86400

ontime_data = experience_data[
    experience_data['late_delivery'] == False
].copy()
#没有延迟中低评分和非低评分对比
ontime_delivery_compare = (
    ontime_data
    .groupby('low_rating')
    .agg(
        order_count=('order_id', 'count'),
        avg_delivery_days=('delivery_days', 'mean'),
        median_delivery_days=('delivery_days', 'median')
    )
)

ontime_delivery_compare
# %%
#看没有延迟的运费
order_cost = (
    df_item
    .groupby('order_id', as_index=False)
    .agg(
        total_price=('price', 'sum'),
        total_freight=('freight_value', 'sum')
    )
)
#运费占比
order_cost['freight_ratio'] = (
    order_cost['total_freight']
    / (order_cost['total_price'] + order_cost['total_freight'])
)
#再再和之前的有timestamp，送达天数等的大表join，不过是只保留未延迟的
ontime_freight = ontime_data.merge(
    order_cost,
    on='order_id',
    how='inner'
)
ontime_freight['freight_ratio'].describe()
# %%
ontime_freight.groupby('low_rating').agg(
    order_count=('order_id', 'count'),
    avg_freight_ratio=('freight_ratio', 'mean'),
    median_freight_ratio=('freight_ratio', 'median')
)
# %%
#客户留存
#排序订单-客户
customer_orders = (
    df_order.loc[
        df_order['order_status'] == 'delivered',
        ['order_id', 'customer_id', 'order_purchase_timestamp']
    ]
    .merge(
        df_customer[['customer_id', 'customer_unique_id']],
        on='customer_id',
        how='left'
    )
)

customer_orders['order_purchase_timestamp'] = pd.to_datetime(
    customer_orders['order_purchase_timestamp']
)

customer_orders = customer_orders.sort_values(
    ['customer_unique_id', 'order_purchase_timestamp']
)
#标记客户第n次购买
customer_orders['purchase_number'] = (
    customer_orders
    .groupby('customer_unique_id')
    .cumcount() + 1
)
#查是否复购
customer_order_count = (
    customer_orders
    .groupby('customer_unique_id')['order_id']
    .nunique()
    .reset_index(name='order_count')
)

customer_order_count['repeat_purchase'] = (
    customer_order_count['order_count'] >= 2
)
#取客户第一笔订单（后要取第一个评分）
first_orders = customer_orders[
    customer_orders['purchase_number'] == 1
].copy()
# %%
#将第一笔订单与评分、是否复购join
first_orders = first_orders.merge(
    customer_order_count[
        ['customer_unique_id', 'repeat_purchase']
    ],
    on='customer_unique_id',
    how='left'
)
first_orders = first_orders.merge(
    review_order,
    on='order_id',
    how='inner'
)

# %%
#进行（非）低分的复购率对比
first_orders['first_order_low_rating'] = (
    first_orders['review_score'] <= 2
)

rating_repeat = (
    first_orders
    .groupby('first_order_low_rating')
    .agg(
        customer_count=('customer_unique_id', 'count'),
        repeat_customers=('repeat_purchase', 'sum'),
        repeat_purchase_rate=('repeat_purchase', 'mean')
    )
)

rating_repeat['repeat_purchase_rate'] *= 100

rating_repeat
# %%
#首单+是否延迟
first_orders = first_orders.merge(
    delay_valid[['order_id', 'late_delivery']],
    on='order_id',
    how='inner'
)
# %%
#计算首单是否延迟的后续复购率
late_repeat = (
    first_orders
    .groupby('late_delivery')
    .agg(
        customer_count=('customer_unique_id', 'count'),
        repeat_customers=('repeat_purchase', 'sum'),
        repeat_purchase_rate=('repeat_purchase', 'mean')
    )
)

late_repeat['repeat_purchase_rate'] *= 100

late_repeat
# %%
#RFM指标构造
last_purchase_date = customer_orders[
    'order_purchase_timestamp'
].max()
#最近一个日期+1天当作recency的基准
snapshot_date = last_purchase_date + pd.Timedelta(days=1)
# %%
#构造R+F,frequency直接得到
rf = (
    customer_orders
    .groupby('customer_unique_id')
    .agg(
        last_purchase=('order_purchase_timestamp', 'max'),
        Frequency=('order_id', 'nunique')
    )
    .reset_index()
)
rf
#recency进一步得到
rf['Recency'] = (
    snapshot_date - rf['last_purchase']
).dt.days
# %%
#获取M，item+customer_order
# %%
order_monetary = (
    df_item
    .groupby('order_id', as_index=False)
    .agg(
        order_value=('price', 'sum')#不包括运费，纯price消费
    )
)
customer_monetary = customer_orders.merge(
    order_monetary,
    on='order_id',
    how='left'#也是以delivery_order为主
)
#customer level的M
monetary = (
    customer_monetary
    .groupby('customer_unique_id', as_index=False)
    .agg(
        Monetary=('order_value', 'sum')
    )
)
#合并R、F、M
rfm = rf.merge(
    monetary,
    on='customer_unique_id',
    how='left'
)
rfm = rfm[
    ['customer_unique_id', 'Recency', 'Frequency', 'Monetary']
]
# %%
rfm[['Recency', 'Frequency', 'Monetary']].describe()
# %%
#rfm评分，f集中1，右偏，特定设置
rfm['R_score'] = pd.qcut(
    rfm['Recency'],
    q=5,
    labels=[5, 4, 3, 2, 1]
)
rfm['M_score'] = pd.qcut(
    rfm['Monetary'],
    q=5,
    labels=[1, 2, 3, 4, 5]
)
#F极大多数人为1，2-5依次减少
def f_score(x):
    if x == 1:
        return 1
    elif x == 2:
        return 2
    elif x == 3:
        return 3
    elif x == 4:
        return 4
    else:
        return 5

rfm['F_score'] = rfm['Frequency'].apply(f_score)
rfm.groupby('F_score')['Frequency'].agg(
    ['count', 'min', 'max', 'mean']
)
# %%
rfm['RFM_score'] = (
    rfm['R_score'].astype(str)
    + rfm['F_score'].astype(str)
    + rfm['M_score'].astype(str)
)
#分类客户群体
def customer_segment(row):
    # R较低：较久未购买（R<=2)
    if row['R_score'] <= 2:
        return 'Inactive'

    # R较高且已经复购(R>=3,F>=2)
    elif row['F_score'] >= 2:
        if row['M_score'] >= 4:
            return 'High-value Active'
        else:
            return 'Repeat Active'

    # R较高但只购买一次(R>=3,F=1)
    else:
        if row['M_score'] >= 4:
            return 'High-potential'
        else:
            return 'Active'

rfm['segment'] = rfm.apply(
    customer_segment,
    axis=1
)
#%%
segment_profile = (
    rfm
    .groupby('segment')
    .agg(
        customer_count=('customer_unique_id', 'count'),
        avg_recency=('Recency', 'mean'),
        avg_frequency=('Frequency', 'mean'),
        avg_monetary=('Monetary', 'mean'),
        median_monetary=('Monetary', 'median')
    )
)
#检查占比
segment_summary = (
    rfm['segment']
    .value_counts()
    .to_frame('customer_count')
)

segment_summary['percentage'] = (
    segment_summary['customer_count']
    / len(rfm)
    * 100
)
#rfm分类可视化
import matplotlib.pyplot as plt

plt.figure(figsize=(9, 5))

colors = plt.cm.Oranges(
    segment_summary['customer_count']
    / segment_summary['customer_count'].max()
)

bars = plt.bar(
    segment_summary.index,
    segment_summary['customer_count'],
    color=colors,
    edgecolor='black'
)

for bar, pct in zip(
    bars,
    segment_summary['percentage']
):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 500,
        f'{pct:.1f}%',
        ha='center'
    )

plt.title('Customer Distribution by RFM Segment')
plt.xlabel('Customer Segment')
plt.ylabel('Number of Customers')
plt.xticks(rotation=20)

plt.tight_layout()
plt.show()
 
# %%
#可视化FxM
plt.figure(figsize=(10, 6))

for segment, group in rfm.groupby('segment'):
    plt.scatter(
        group['Frequency'],
        group['Monetary'],
        label=segment,
        alpha=0.5
    )

plt.title('RFM Customer Segmentation')
plt.xlabel('Frequency')
plt.ylabel('Monetary (BRL)')

plt.legend(title='Customer Segment')
plt.tight_layout()
plt.show()
# %%
##payment辅助研究
#支付方式
payment_type_count = (
    df_payment['payment_type']
    .value_counts()
)

payment_type_pct = (
    df_payment['payment_type']
    .value_counts(normalize=True)
    .mul(100)
)

payment_type_summary = pd.DataFrame({
    'count': payment_type_count,
    'percentage': payment_type_pct
})
#可视化
plt.figure(figsize=(7, 7))

colors = [
    '#F4A261',
    '#E9C46A',
    '#8AB17D',
    '#76C7C0',
    '#F2A7A0'
]

def show_pct(pct):
    return f'{pct:.1f}%' if pct >= 2 else ''

plt.pie(
    payment_type_summary['count'],
    autopct=show_pct,
    startangle=90,
    colors=colors[:len(payment_type_summary)],
    wedgeprops={'edgecolor': 'black'}
)

plt.title('Distribution of Payment Methods')

plt.legend(
    payment_type_summary.index,
    title='Payment Method',
    loc='upper left',
    bbox_to_anchor=(1, 1)
)

plt.tight_layout()
plt.show()

# %%
