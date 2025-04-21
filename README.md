# DBSCAN Analiz Projeleri

Bu proje, dört farklı DBSCAN kümeleme analizini içermektedir. Her bir analiz, farklı bir iş problemi için geliştirilmiştir.

## 1. Müşteri Segmentasyonu (Customer Segmentation)

**Dosya:** `customer_segmentation.py`  
**Port:** 8003

Müşterileri davranışsal özelliklerine göre segmentlere ayırır.

### İş Değeri:
- Müşteri davranışlarının anlaşılması
- Hedefli pazarlama stratejileri geliştirme
- Müşteri sadakati programları oluşturma
- Gelir optimizasyonu

### Analiz Edilen Özellikler:
- Toplam sipariş sayısı
- Toplam harcama miktarı
- Ortalama sipariş değeri
- Kategori çeşitliliği
- Müşteri ömrü (gün cinsinden)

### Görselleştirmeler:
- Toplam Sipariş vs Toplam Harcama
- Ortalama Sipariş Değeri vs Kategori Çeşitliliği
- Müşteri Ömrü vs Toplam Harcama

### Performans Metrikleri:
- Küme içi mesafe
- Küme sayısı
- Aykırı değer oranı
- Küme stabilitesi

## 2. Ürün Kümeleme (Product Clustering)

**Dosya:** `product_clustering.py`  
**Port:** 8001

Ürünleri performans özelliklerine göre kümeler.

### İş Değeri:
- Ürün kategorizasyonu
- Stok yönetimi optimizasyonu
- Fiyatlandırma stratejileri
- Ürün portföyü analizi

### Analiz Edilen Özellikler:
- Ortalama fiyat
- Sipariş sıklığı
- Sipariş başına ortalama miktar
- Benzersiz müşteri sayısı

### Görselleştirmeler:
- Fiyat vs Sipariş Sıklığı
- Miktar vs Benzersiz Müşteriler

### Performans Metrikleri:
- Küme homojenliği
- Ürün dağılımı
- Küme boyutları
- Aykırı ürün tespiti

## 3. Tedarikçi Segmentasyonu (Supplier Segmentation)

**Dosya:** `supplier_segmentation.py`  
**Port:** 8002

Tedarikçileri performans ve ürün özelliklerine göre segmentlere ayırır.

### İş Değeri:
- Tedarikçi performans değerlendirmesi
- Tedarik zinciri optimizasyonu
- Risk yönetimi
- İlişki yönetimi

### Analiz Edilen Özellikler:
- Ürün sayısı
- Toplam satış miktarı
- Ortalama satış fiyatı
- Benzersiz müşteri sayısı

### Görselleştirmeler:
- Ürün Sayısı vs Toplam Satış Miktarı
- Ortalama Fiyat vs Benzersiz Müşteriler

### Performans Metrikleri:
- Tedarikçi yoğunluğu
- Küme kalitesi
- Risk skorları
- Performans indeksleri

## 4. Ülke Satış Desenleri (Country Sales Patterns)

**Dosya:** `country_sales_patterns.py`  
**Port:** 8004

Ülkeleri satış performanslarına göre kümeler.

### İş Değeri:
- Pazar segmentasyonu
- Bölgesel strateji geliştirme
- Lojistik optimizasyonu
- Kültürel tercih analizi

### Analiz Edilen Özellikler:
- Toplam sipariş sayısı
- Toplam gelir
- Ortalama sipariş değeri
- Benzersiz müşteri sayısı
- Kategori çeşitliliği
- Ortalama kargo süresi

### Görselleştirmeler:
- Toplam Sipariş vs Toplam Gelir
- Benzersiz Müşteriler vs Ortalama Sipariş Değeri
- Ortalama Kargo Süresi vs Toplam Gelir

### Performans Metrikleri:
- Pazar büyüklüğü
- Büyüme potansiyeli
- Lojistik verimliliği
- Müşteri memnuniyeti

## DBSCAN Algoritması

### Temel Özellikler:
- Gürültüye dayanıklı
- Küme sayısını otomatik belirleme
- Düzensiz şekilli kümeleri tespit edebilme
- Aykırı değer tespiti

### Parametreler:
- eps: Komşuluk yarıçapı
- min_samples: Minimum nokta sayısı
- metric: Uzaklık ölçümü (varsayılan: 'euclidean')

## Kurulum ve Çalıştırma

1. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

2. Her bir analizi çalıştırmak için:
```bash
python customer_segmentation.py
python product_clustering.py
python supplier_segmentation.py
python country_sales_patterns.py
```

3. API dokümantasyonuna erişmek için:
- Müşteri Segmentasyonu: http://localhost:8003/docs
- Ürün Kümeleme: http://localhost:8001/docs
- Tedarikçi Segmentasyonu: http://localhost:8002/docs
- Ülke Satış Desenleri: http://localhost:8004/docs

## Veritabanı Bağlantısı

Tüm analizler PostgreSQL veritabanı kullanmaktadır. Veritabanı bağlantı bilgilerini her bir dosyada güncellemeniz gerekmektedir:

```python
engine = create_engine('postgresql://username:password@localhost:5432/database_name')
```

## Veri Ön İşleme

1. Eksik değerlerin temizlenmesi
2. Aykırı değerlerin tespiti
3. Özellik ölçeklendirme (StandardScaler)
4. Kategorik değişkenlerin dönüştürülmesi

## Çıktılar

Her analiz sonucunda:
- Kümeleme sonuçları
- Optimal DBSCAN parametreleri
- Aykırı değerler
- Görselleştirme grafikleri (PNG formatında)
- Performans metrikleri
- İş önerileri

oluşturulmaktadır. 

Hilal AKBEN 
Esra ORUÇ --esraoruc2805@gmail.com
Elif Seda Demirhan
Seda Mürütsoy