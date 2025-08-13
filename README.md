# Taiwan-Power-OpenData-Downloader

每十分鐘定時自動下載台電各機組發電量Open Data, 以及台電今日電力資訊, 並轉為Excel可讀取之csv檔案儲存

## 功能特色

- ⏰ 每10分鐘自動下載最新台電發電資料
- 📊 同時輸出 UTF-8 CSV 和 Excel 格式
- 🌏 支援台灣時區，確保檔案在正確時間（午夜12點）切換
- 🐳 完整 Docker 支援，適合 NAS 系統部署
- 📈 包含即時供電能力和使用率統計

## 資料來源

* 官方可視化當下時刻發電量: https://www.taipower.com.tw/d006/loadGraph/loadGraph/genshx_.html
* open data平台(台電系統(含外購電力)各機組發電量即時資訊): https://data.gov.tw/dataset/8931

觀察公開資料平台JSON [網址](https://service.taipower.com.tw/data/opendata/apply/file/d006001/001.json) ，資料內的內容與台電即時更新的網頁相同，因此對此JSON檔案進行處理

## 快速開始

### 一鍵部署（推薦）

對於 Linux 系統和 NAS，我們提供了一鍵部署腳本：

```bash
# 下載專案
git clone <repository-url>
cd Taiwan-Power-OpenData-Downloader

# 執行一鍵部署腳本
./deploy.sh
```

腳本會自動：
- 檢查 Docker 環境
- 創建必要目錄
- 建立並啟動 Docker 容器
- 驗證時區設定
- 顯示監控指令

### 方法一：使用 Docker Compose

1. 確保您的系統已安裝 Docker 和 Docker Compose

2. 克隆專案到本地：
```bash
git clone <repository-url>
cd Taiwan-Power-OpenData-Downloader
```

3. 使用 Docker Compose 啟動：
```bash
docker-compose up -d
```

4. 查看運行狀態：
```bash
docker-compose logs -f taipower
```

5. 停止服務：
```bash
docker-compose down
```

### 方法二：使用 Docker 命令

1. 建立 Docker 映像：
```bash
docker build -t taipower:latest .
```

2. 運行容器：
```bash
docker run -d \
  --name taipower \
  --restart unless-stopped \
  -e TZ=Asia/Taipei \
  -v "$(pwd)/csv(big5):/code/xlsx(big-5)" \
  -v "$(pwd)/csv(utf-8):/code/csv(utf-8)" \
  -v "$(pwd)/json:/code/json" \
  taipower:latest
```

3. 查看運行日誌：
```bash
docker logs -f taipower
```

4. 停止容器：
```bash
docker stop taipower
docker rm taipower
```

### 方法三：本地 Python 環境運行

1. 安裝 Python 3.9 或更高版本

2. 安裝依賴套件：
```bash
pip install -r requirements.txt
```

3. 直接運行：
```bash
python TaiwanPowerOpenDataDownloader.py
```

## 輸出檔案說明

程式會在以下目錄產生檔案：

- `csv(utf-8)/`: UTF-8 編碼的 CSV 檔案，適合大部分現代軟體讀取
- `csv(big5)/`: Excel 格式檔案（.xlsx），便於直接在 Excel 中開啟
- `json/`: 原始 JSON 資料備份

檔案命名格式：`YYYY_MM_DD.csv` 或 `YYYY_MM_DD.xlsx`

## 資料更新頻率

程式設定每小時的以下時間點執行資料下載：
- XX:07
- XX:17
- XX:27
- XX:37
- XX:47
- XX:57

每次執行會檢查是否有新資料，避免重複下載相同時間點的資料。

## 時區處理

此版本已修正時區問題：
- 程式內部使用台灣時區（Asia/Taipei）處理所有日期時間
- Docker 容器也設定為台灣時區
- 確保在台灣時間午夜12點正確切換到新的日期檔案

## 在 NAS 系統上部署

### 群暉 Synology NAS

1. 安裝 Docker 套件
2. 上傳專案檔案到 NAS
3. 使用 SSH 連接到 NAS，執行 Docker Compose 命令

### 威聯通 QNAP NAS

1. 安裝 Container Station
2. 上傳專案檔案到 NAS
3. 在 Container Station 中建立應用程式或使用命令列

### 綠聯 NAS

綠聯 NAS 部署需要特別注意時區設定：

1. 確保 Docker 服務已啟用
2. 上傳專案檔案到 NAS
3. 使用終端機執行部署：

```bash
# SSH 連接到 NAS
ssh admin@your-nas-ip

# 切換到專案目錄
cd /volume1/docker/Taiwan-Power-OpenData-Downloader

# 設定檔案權限
chmod +x deploy.sh
chmod 755 csv\(big5\) csv\(utf-8\) json

# 執行一鍵部署
./deploy.sh
```

**時區修正說明：**
- 程式已修正使用台灣時區 (Asia/Taipei)
- Docker 容器內建時區設定
- 確保在台灣時間午夜 12:00 正確切換檔案

如果時區仍有問題，請參考 [DEPLOYMENT.md](DEPLOYMENT.md) 的詳細故障排除說明。

## 故障排除

### 常見問題

1. **時區顯示錯誤**
   - 確認 Docker 容器的 TZ 環境變數設定為 `Asia/Taipei`
   - 檢查主機系統時區設定

2. **檔案權限問題**
   - 確保掛載的目錄有寫入權限
   - 在 NAS 上可能需要調整資料夾權限

3. **網路連線問題**
   - 檢查防火牆設定
   - 確認可以訪問台電 API 網址

4. **記憶體不足**
   - 程式記憶體需求很低，如遇問題請檢查系統資源

### 查看詳細日誌

```bash
# Docker Compose
docker-compose logs -f taipower

# Docker 命令
docker logs -f taipower
```

## 開發與貢獻

歡迎提交 Issue 和 Pull Request 來改善此專案。

### 本地開發環境設定

```bash
git clone <repository-url>
cd Taiwan-Power-OpenData-Downloader
pip install -r requirements.txt
python TaiwanPowerOpenDataDownloader.py
```

## 授權條款

此專案使用開源授權，詳見 LICENSE 檔案。

## 更新日誌

### v1.1.0
- 修正時區問題，確保在台灣時間正確切換檔案
- 改善 Docker 配置
- 更新完整的使用說明文件

### v1.0.0
- 初始版本，基本功能實現