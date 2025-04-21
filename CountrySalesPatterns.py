import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from kneed import KneeLocator
import matplotlib.pyplot as plt
import seaborn as sns
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Ülke Satış Desenleri API")

def get_country_data():
    engine = create_engine('postgresql://username:password@localhost:5432/database_name')
    
    query = """
    SELECT 
        c.country,
        COUNT(DISTINCT o.order_id) AS total_orders,
        SUM(od.quantity * od.unit_price) AS total_revenue,
        AVG(od.quantity * od.unit_price) AS avg_order_value,
        COUNT(DISTINCT o.customer_id) AS unique_customers,
        COUNT(DISTINCT p.category_id) AS unique_categories,
        AVG(EXTRACT(DAY FROM (o.shipped_date - o.order_date))) AS avg_shipping_time
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    JOIN order_details od ON o.order_id = od.order_id
    JOIN products p ON od.product_id = p.product_id
    GROUP BY c.country
    """
    
    return pd.read_sql(query, engine)

def find_optimal_eps(data):
    distances = []
    for i in range(len(data)):
        dist = np.sqrt(np.sum((data - data[i])**2, axis=1))
        distances.append(np.sort(dist)[1])
    
    distances = np.sort(distances)
    kneedle = KneeLocator(range(len(distances)), distances, curve='convex', direction='increasing')
    return distances[kneedle.knee]

def optimize_min_samples(data, eps):
    best_score = -1
    best_min_samples = 2
    
    for min_samples in range(2, 11):
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        labels = dbscan.fit_predict(data)
        
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        if n_clusters > 1:
            score = len(labels[labels != -1]) / len(labels)
            if score > best_score:
                best_score = score
                best_min_samples = min_samples
    
    return best_min_samples

def perform_clustering():
    df = get_country_data()
    features = ['total_orders', 'total_revenue', 'avg_order_value', 'unique_customers', 'unique_categories', 'avg_shipping_time']
    
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df[features])
    
    eps = find_optimal_eps(scaled_data)
    min_samples = optimize_min_samples(scaled_data, eps)
    
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    df['cluster'] = dbscan.fit_predict(scaled_data)
    
    return df, eps, min_samples

def plot_results(df):
    plt.figure(figsize=(15, 5))
    
    plt.subplot(1, 3, 1)
    sns.scatterplot(data=df, x='total_orders', y='total_revenue', hue='cluster', palette='viridis')
    plt.title('Toplam Sipariş vs Toplam Gelir')
    
    plt.subplot(1, 3, 2)
    sns.scatterplot(data=df, x='unique_customers', y='avg_order_value', hue='cluster', palette='viridis')
    plt.title('Benzersiz Müşteriler vs Ortalama Sipariş Değeri')
    
    plt.subplot(1, 3, 3)
    sns.scatterplot(data=df, x='avg_shipping_time', y='total_revenue', hue='cluster', palette='viridis')
    plt.title('Ortalama Kargo Süresi vs Toplam Gelir')
    
    plt.tight_layout()
    plt.savefig('country_clusters.png')
    plt.close()

@app.get("/")
async def root():
    return {"message": "Ülke Satış Desenleri API'sine Hoş Geldiniz"}

@app.get("/clusters")
async def get_clusters():
    try:
        df, eps, min_samples = perform_clustering()
        plot_results(df)
        
        outliers = df[df['cluster'] == -1]
        clusters = df[df['cluster'] != -1]['cluster'].nunique()
        
        return {
            "optimal_eps": eps,
            "optimal_min_samples": min_samples,
            "number_of_clusters": clusters,
            "outliers_count": len(outliers),
            "outliers": outliers.to_dict('records')
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8004)
