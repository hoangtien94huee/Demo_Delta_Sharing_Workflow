# ======================================================
# Spark Container (Delta Lake + MinIO)
# ======================================================

FROM bitnamilegacy/spark:3.5.4

USER root

# Cài thêm các tiện ích cơ bản
RUN apt-get update && apt-get install -y curl wget && rm -rf /var/lib/apt/lists/*

# Giữ tương thích đường dẫn /opt/spark
RUN ln -sf /opt/bitnami/spark /opt/spark

# === Thêm Hadoop AWS và AWS SDK để kết nối MinIO ===
RUN wget -q https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar \
    -O /opt/spark/jars/hadoop-aws-3.3.4.jar && \
    wget -q https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.565/aws-java-sdk-bundle-1.12.565.jar \
    -O /opt/spark/jars/aws-java-sdk-bundle-1.12.565.jar

# (Tùy chọn) Copy script xử lý
# COPY spark/ /opt/spark/

USER 1001
