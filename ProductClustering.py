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

app = FastAPI(title="Ürün Kümeleme API")

def get_product_data():
    engine = create_engine('postgresql://username:password@localhost:5432/Gyk1')
    
    query = """
    SELECT 
        p.product_id,
        AVG(od.unit_price) AS avg_price,
        COUNT(DISTINCT o.order_id) AS order_frequency,
        AVG(od.quantity) AS avg_quantity_per_order,
        COUNT(DISTINCT o.customer_id) AS unique_customers
    FROM products p
    JOIN order_details od ON p.product_id = od.product_id
    JOIN orders o ON od.order_id = o.order_id
    GROUP BY p.product_id
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
    df = get_product_data()
    features = ['avg_price', 'order_frequency', 'avg_quantity_per_order', 'unique_customers']
    
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df[features])
    
    eps = find_optimal_eps(scaled_data)
    min_samples = optimize_min_samples(scaled_data, eps)
    
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    df['cluster'] = dbscan.fit_predict(scaled_data)
    
    return df, eps, min_samples

def plot_results(df):
    plt.figure(figsize=(12, 6))
    
    plt.subplot(1, 2, 1)
    sns.scatterplot(data=df, x='avg_price', y='order_frequency', hue='cluster', palette='viridis')
    plt.title('Fiyat vs Sipariş Sıklığı')
    
    plt.subplot(1, 2, 2)
    sns.scatterplot(data=df, x='avg_quantity_per_order', y='unique_customers', hue='cluster', palette='viridis')
    plt.title('Miktar vs Benzersiz Müşteriler')
    
    plt.tight_layout()
    plt.savefig('product_clusters.png')
    plt.close()

@app.get("/")
async def root():
    return {"message": "Ürün Kümeleme API'sine Hoş Geldiniz"}

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
    uvicorn.run(app, host="0.0.0.0", port=8001)
