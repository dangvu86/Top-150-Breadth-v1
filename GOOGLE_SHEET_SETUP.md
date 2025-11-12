# Google Sheet Auto-Upload Setup Guide

Hướng dẫn cấu hình tự động upload dữ liệu lên Google Sheet mỗi khi refresh app.

## Bước 1: Tạo Google Cloud Service Account

1. Truy cập [Google Cloud Console](https://console.cloud.google.com/)
2. Tạo project mới hoặc chọn project hiện có
3. Bật Google Sheets API:
   - Vào **APIs & Services** > **Library**
   - Tìm "Google Sheets API" và click **Enable**
   - Tìm "Google Drive API" và click **Enable**

4. Tạo Service Account:
   - Vào **APIs & Services** > **Credentials**
   - Click **Create Credentials** > **Service Account**
   - Nhập tên service account (ví dụ: "market-breadth-uploader")
   - Click **Create and Continue**
   - Skip role selection > Click **Done**

5. Tạo JSON Key:
   - Click vào service account vừa tạo
   - Vào tab **Keys**
   - Click **Add Key** > **Create new key**
   - Chọn **JSON** format
   - Click **Create** - file JSON sẽ tự động download

## Bước 2: Tạo Google Sheet

1. Tạo Google Sheet mới tại [Google Sheets](https://sheets.google.com)
2. Đặt tên sheet (ví dụ: "Market Breadth Analysis Data")
3. Copy **Sheet ID** từ URL:
   - URL format: `https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit`
   - Ví dụ: nếu URL là `https://docs.google.com/spreadsheets/d/1ABC...XYZ/edit`
   - Thì Sheet ID là: `1ABC...XYZ`

4. Chia sẻ Sheet với Service Account:
   - Click nút **Share** trong Google Sheet
   - Paste **service account email** (có dạng `xxx@xxx.iam.gserviceaccount.com`)
   - Email này có trong JSON key file ở field `client_email`
   - Chọn quyền **Editor**
   - Click **Share**

## Bước 3: Cấu hình Secrets (Local Development)

Tạo file `.streamlit/secrets.toml` với nội dung:

```toml
# Google Sheet ID
GOOGLE_SHEET_ID = "your-sheet-id-here"

# Dragon Capital Token (already configured)
DRAGON_CAPITAL_TOKEN = "your-token-here"

# Google Cloud Service Account Credentials
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYour-Private-Key-Here\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
```

**Lưu ý:**
- Copy toàn bộ nội dung từ JSON key file đã download
- `private_key` phải giữ nguyên format với `\n` (newline characters)
- Đảm bảo file `.streamlit/secrets.toml` đã được add vào `.gitignore`

## Bước 4: Cấu hình Streamlit Cloud

1. Vào App Settings trên Streamlit Cloud
2. Click vào **Secrets** tab
3. Paste nội dung của `.streamlit/secrets.toml`
4. Click **Save**

## Bước 5: Test

1. Chạy app: `streamlit run app.py`
2. Khi app load xong, check sidebar:
   - Nếu thấy "✅ Data uploaded to Google Sheet" → thành công
   - Nếu không thấy message → không có config hoặc silent fail
3. Mở Google Sheet để xem data đã upload

## Cách Hoạt Động

- Mỗi lần refresh app (F5 hoặc click Rerun), app sẽ tự động:
  1. Load và tính toán data
  2. Format data theo display format
  3. Upload lên Google Sheet (sắp xếp theo Date tăng dần - chronological order)
  4. Apply formatting (header bold, freeze row, auto-resize columns)
  5. Thêm timestamp "Last Updated" ở cuối sheet

- Nếu không config Google Sheet, app vẫn chạy bình thường (không bị lỗi)
- Upload process chạy trong sidebar với spinner indicator

## Troubleshooting

**Lỗi: "Cannot connect to Google Sheets"**
- Check service account credentials trong secrets.toml
- Đảm bảo đã enable Google Sheets API và Google Drive API
- Verify `private_key` format đúng với `\n` characters

**Lỗi: "Permission denied"**
- Đảm bảo đã share Google Sheet với service account email
- Service account cần quyền Editor

**Lỗi: "Worksheet not found"**
- App sẽ tự động tạo worksheet mới tên "Market Breadth Data"
- Nếu vẫn lỗi, check quyền Editor của service account

## Tắt Auto-Upload

Để tắt tính năng auto-upload:
- Xóa dòng `GOOGLE_SHEET_ID` trong secrets.toml
- Hoặc comment out dòng đó: `# GOOGLE_SHEET_ID = "..."`

App sẽ tự động skip upload nếu không tìm thấy config.
