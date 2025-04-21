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

app = FastAPI(title="Müşteri Segmentasyonu API")

def get_customer_data():
    engine = create_engine('postgresql://username:password@localhost:5432/database_name')
    
    query = """
    SELECT 
        c.customer_id,
        COUNT(DISTINCT o.order_id) AS total_orders,
        SUM(od.quantity * od.unit_price) AS total_spent,
        AVG(od.quantity * od.unit_price) AS avg_order_value,
        COUNT(DISTINCT p.category_id) AS unique_categories,
        EXTRACT(DAY FROM (MAX(o.order_date) - MIN(o.order_date))) AS customer_lifetime_days
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_details od ON o.order_id = od.order_id
    JOIN products p ON od.product_id = p.product_id
    GROUP BY c.customer_id
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
    df = get_customer_data()
    features = ['total_orders', 'total_spent', 'avg_order_value', 'unique_categories', 'customer_lifetime_days']
    
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
    sns.scatterplot(data=df, x='total_orders', y='total_spent', hue='cluster', palette='viridis')
    plt.title('Toplam Sipariş vs Toplam Harcama')
    
    plt.subplot(1, 3, 2)
    sns.scatterplot(data=df, x='avg_order_value', y='unique_categories', hue='cluster', palette='viridis')
    plt.title('Ortalama Sipariş Değeri vs Kategori Çeşitliliği')
    
    plt.subplot(1, 3, 3)
    sns.scatterplot(data=df, x='customer_lifetime_days', y='total_spent', hue='cluster', palette='viridis')
    plt.title('Müşteri Ömrü vs Toplam Harcama')
    
    plt.tight_layout()
    plt.savefig('customer_clusters.png')
    plt.close()

@app.get("/")
async def root():
    return {"message": "Müşteri Segmentasyonu API'sine Hoş Geldiniz"}

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
    uvicorn.run(app, host="0.0.0.0", port=8003)
