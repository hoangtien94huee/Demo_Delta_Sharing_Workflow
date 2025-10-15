from pyspark.sql import SparkSession

# ==========================================================
# Tạo SparkSession có hỗ trợ Delta Lake
# ==========================================================
spark = SparkSession.builder \
    .appName("CreateDeltaTable") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "admin") \
    .config("spark.hadoop.fs.s3a.secret.key", "password123") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .config("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider") \
    .getOrCreate()

# ==========================================================
# Tạo DataFrame mẫu
# ==========================================================
data = [
    ("VN", 2025, 100000),
    ("TH", 2025, 80000),
    ("SG", 2025, 95000)
]
cols = ["country", "year", "revenue"]

df = spark.createDataFrame(data, cols)

# ==========================================================
# Ghi Delta Table vào MinIO (OneLake giả lập)
# ==========================================================
df.write.format("delta").mode("overwrite").save("s3a://onelake/gold/sales_gold")

print("Đã ghi Delta Table ra MinIO (OneLake giả lập) thành công!")
spark.stop()
