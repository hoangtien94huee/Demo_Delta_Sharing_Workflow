"""
Test Delta Sharing - Đọc data từ Delta Sharing Server
"""
import delta_sharing

# ==========================================================
# 1️⃣ Tạo Delta Sharing Client từ profile file
# ==========================================================
profile_file = "config.share"
client = delta_sharing.SharingClient(profile_file)

# ==========================================================
# 2️⃣ List các shares có sẵn
# ==========================================================
print("📦 Danh sách Shares:")
shares = client.list_shares()
for share in shares:
    print(f"  - {share.name}")

# ==========================================================
# 3️⃣ List các schemas trong share
# ==========================================================
print("\n📁 Danh sách Schemas trong 'sales_share':")
schemas = client.list_schemas(delta_sharing.Share(name="sales_share"))
for schema in schemas:
    print(f"  - {schema.name}")

# ==========================================================
# 4️⃣ List các tables trong schema
# ==========================================================
print("\n📊 Danh sách Tables trong 'sales_share.gold':")
tables = client.list_tables(delta_sharing.Schema(name="gold", share="sales_share"))
for table in tables:
    print(f"  - {table.name} ({table.share}.{table.schema}.{table.name})")

# ==========================================================
# 5️⃣ Đọc data từ table
# ==========================================================
print("\n📖 Đọc data từ table 'sales_gold':")
table_url = f"{profile_file}#sales_share.gold.sales_gold"
df = delta_sharing.load_as_pandas(table_url)

print(f"\n✅ Đã đọc được {len(df)} records:")
print(df)

# ==========================================================
# 6️⃣ Xem schema của table
# ==========================================================
print("\n🔍 Schema của table:")
print(df.dtypes)
