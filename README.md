# Delta Sharing với Power BI - Local Development Setup

Dự án này triển khai Delta Sharing protocol để chia sẻ Delta Lake tables từ MinIO (S3-compatible storage) đến Power BI Desktop.

## 📋 Kiến trúc hệ thống

```
┌─────────────────┐
│   Power BI      │ ← Client (Windows Host)
└────────┬────────┘
         │ HTTP (port 8080)
         ↓
┌─────────────────────────────┐
│ Delta Sharing Server        │ ← Container
│ (deltaio/delta-sharing)     │
└────────┬────────────────────┘
         │ S3 API (port 9000)
         ↓
┌─────────────────────────────┐
│ MinIO (S3-compatible)       │ ← Container
│ Bucket: onelake             │
│ Path: gold/sales_gold       │
└────────┬────────────────────┘
         │
         ↓
┌─────────────────────────────┐
│ Spark Container             │ ← Container
│ (Apache Spark + Delta Lake) │
└─────────────────────────────┘
```

## 🛠️ Tech Stack

- **Apache Spark 3.5.4** - Data processing engine
- **Delta Lake 3.2.0** - Storage layer with ACID transactions
- **MinIO** - S3-compatible object storage
- **Delta Sharing Server 0.7.8** - Data sharing protocol server
- **Docker Compose** - Container orchestration

## 📦 Cấu trúc thư mục

```
delta-sharing/
├── docker-compose.yml          # Container orchestration
├── Dockerfile                  # Spark container image
├── share.yaml                  # Delta Sharing configuration
├── core-site.xml              # Hadoop S3 configuration
├── config.share               # Power BI connection profile
├── spark-app/
│   └── create_delta_table.py  # Script tạo Delta table
├── minio_data/                # MinIO data persistence
└── README.md                  # This file
```

## 🚀 Quick Start

### Bước 1: Khởi động Docker Containers

```powershell
docker-compose up -d
```

Chờ tất cả containers khởi động (khoảng 30 giây).

### Bước 2: Tạo MinIO Bucket

```powershell
# Setup MinIO client alias
docker exec delta-minio mc alias set local http://localhost:9000 admin password123

# Tạo bucket
docker exec delta-minio mc mb local/onelake

# Set public read access
docker exec delta-minio mc anonymous set download local/onelake
```

### Bước 3: Tạo Delta Table

```powershell
# Copy script vào Spark container
docker cp ./spark-app/create_delta_table.py spark:/opt/spark-app/

# Chạy Spark job để tạo Delta table
docker exec -it spark spark-submit `
  --packages io.delta:delta-spark_2.12:3.2.0 `
  /opt/spark-app/create_delta_table.py
```

### Bước 4: Cấu hình Windows Hosts File

**QUAN TRỌNG:** Thêm dòng này vào `C:\Windows\System32\drivers\etc\hosts`:

```
127.0.0.1 delta-minio
```

**Cách thêm:**
1. Mở **Notepad as Administrator**
2. File → Open → `C:\Windows\System32\drivers\etc\hosts`
3. Thêm dòng trên vào cuối file
4. Save

**Hoặc dùng PowerShell (as Admin):**
```powershell
Add-Content -Path "C:\Windows\System32\drivers\etc\hosts" -Value "`n127.0.0.1 delta-minio"
```

### Bước 5: Kết nối Power BI

#### Cách 1: Sử dụng Web Data Source

1. Mở **Power BI Desktop**
2. **Get Data** → **Web** → **Advanced**
3. **URL**: 
   ```
   http://localhost:8080/delta-sharing/shares/sales_share/schemas/gold/tables/sales_gold/query
   ```
4. **HTTP Request Headers**:
   - Header name: `Authorization`
   - Header value: `Bearer powerbi_token_123`
   - Header name: `Content-Type`
   - Header value: `application/json`
5. **Request body** (nếu dùng POST):
   ```json
   {"predicateHints":[],"limitHint":null,"version":null}
   ```

#### Cách 2: Sử dụng Delta Sharing Profile File

1. File profile: `config.share` (đã có sẵn trong project)
2. Trong Power BI, dùng Python script:
   ```python
   import delta_sharing
   profile = "C:\\inter-k\\delta-sharing\\config.share"
   table_url = f"{profile}#sales_share.gold.sales_gold"
   df = delta_sharing.load_as_pandas(table_url)
   ```

## 🔧 Cấu hình

### Delta Sharing Server (`share.yaml`)

```yaml
version: 1.0

authorization:
  bearerToken: "powerbi_token_123"

preSignedUrlTimeoutSeconds: 3600

shares:
  - name: sales_share
    schemas:
      - name: gold
        tables:
          - name: sales_gold
            location: s3a://onelake/gold/sales_gold
            id: sales_gold_table_001
```

### MinIO Credentials

- **Endpoint**: http://localhost:9000
- **Console**: http://localhost:9001
- **Access Key**: `admin`
- **Secret Key**: `password123`

### Delta Sharing API

- **Base URL**: http://localhost:8080/delta-sharing
- **Bearer Token**: `powerbi_token_123`

## 📊 API Endpoints

### List Shares
```powershell
Invoke-WebRequest -Uri "http://localhost:8080/delta-sharing/shares" `
  -Headers @{Authorization="Bearer powerbi_token_123"}
```

### List Schemas
```powershell
Invoke-WebRequest -Uri "http://localhost:8080/delta-sharing/shares/sales_share/schemas" `
  -Headers @{Authorization="Bearer powerbi_token_123"}
```

### List Tables
```powershell
Invoke-WebRequest -Uri "http://localhost:8080/delta-sharing/shares/sales_share/schemas/gold/tables" `
  -Headers @{Authorization="Bearer powerbi_token_123"}
```

### Get Table Metadata
```powershell
Invoke-WebRequest -Uri "http://localhost:8080/delta-sharing/shares/sales_share/schemas/gold/tables/sales_gold/metadata" `
  -Headers @{Authorization="Bearer powerbi_token_123"}
```

## 🐛 Troubleshooting

### Lỗi: "The remote name could not be resolved: 'delta-minio'"

**Nguyên nhân:** Chưa thêm `delta-minio` vào Windows hosts file.

**Giải pháp:** Xem [Bước 4](#bước-4-cấu-hình-windows-hosts-file)

### Lỗi: "INTERNAL_ERROR" khi query table

**Nguyên nhân:** Delta Sharing Server không thể kết nối MinIO.

**Giải pháp:**
```powershell
# Kiểm tra logs
docker logs delta-sharing-server --tail 50

# Restart container
docker restart delta-sharing-server
```

### Lỗi: "NoSuchBucket"

**Nguyên nhân:** Bucket `onelake` chưa được tạo.

**Giải pháp:** Chạy lại [Bước 2](#bước-2-tạo-minio-bucket)

### Lỗi: "403 Forbidden" khi đọc Delta table

**Nguyên nhân:** MinIO không cho phép anonymous access.

**Giải pháp:**
```powershell
docker exec delta-minio mc anonymous set download local/onelake
```

### Docker Desktop không hoạt động

**Giải pháp:**
1. Restart Docker Desktop
2. Hoặc dùng Docker CLI trực tiếp:
   ```powershell
   docker-compose down
   docker-compose up -d
   ```

## 🔄 Cập nhật Delta Table

Để thêm data mới vào Delta table:

```powershell
# Sửa file create_delta_table.py với data mới
# Sau đó chạy lại:
docker exec -it spark spark-submit `
  --packages io.delta:delta-spark_2.12:3.2.0 `
  /opt/spark-app/create_delta_table.py
```

## 🧹 Dọn dẹp

### Xóa tất cả containers và data

```powershell
docker-compose down -v
Remove-Item -Recurse -Force ./minio_data
```

### Chỉ restart containers

```powershell
docker-compose restart
```

## 📚 Tài liệu tham khảo

- [Delta Sharing Protocol](https://github.com/delta-io/delta-sharing)
- [Delta Lake Documentation](https://docs.delta.io/)
- [MinIO Documentation](https://min.io/docs/minio/linux/index.html)
- [Apache Spark Documentation](https://spark.apache.org/docs/latest/)

## 🔐 Security Notes

**⚠️ Cảnh báo:** Setup này chỉ dành cho development/demo!

Trong production, cần:
- [ ] Sử dụng HTTPS/TLS
- [ ] Implement proper authentication (OAuth, SAML, etc.)
- [ ] Sử dụng secrets management (Azure Key Vault, AWS Secrets Manager)
- [ ] Enable MinIO encryption at rest
- [ ] Configure network security groups/firewalls
- [ ] Sử dụng real domain names (không dùng localhost)
- [ ] Implement rate limiting và monitoring

## 📝 License

This project is for demonstration purposes.

## 👥 Contributors

- Initial setup: Nguyen Nhu Hoang Tien
- Date: October 15, 2025

## 📧 Support

Nếu gặp vấn đề, hãy:
1. Kiểm tra [Troubleshooting](#-troubleshooting)
2. Xem logs: `docker-compose logs -f`
3. Verify containers đang chạy: `docker ps`

---

**Happy Data Sharing! 🎉**
