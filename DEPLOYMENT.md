# 部署指南

## 綠聯 NAS 部署步驟（詳細版）

### 1. 準備工作

確保您的綠聯 NAS 已啟用 Docker 服務：
- 進入 NAS 管理界面
- 找到 Docker 或 Container Manager
- 確保服務已啟動

### 2. 上傳專案檔案

將整個專案資料夾上傳到 NAS 的共享目錄中，例如：
```
/volume1/docker/Taiwan-Power-OpenData-Downloader/
```

### 3. SSH 連接到 NAS

使用 SSH 工具連接到 NAS：
```bash
ssh admin@your-nas-ip
```

### 4. 切換到專案目錄

```bash
cd /volume1/docker/Taiwan-Power-OpenData-Downloader/
```

### 5. 確認檔案權限

```bash
# 設定適當的檔案權限
chmod 755 TaiwanPowerOpenDataDownloader.py
chmod 644 *.md *.txt *.yaml Dockerfile

# 確保資料夾存在且有寫入權限
mkdir -p csv\(big5\) csv\(utf-8\) json
chmod 755 csv\(big5\) csv\(utf-8\) json
```

## 部署方式選擇

### 方式一：Docker Compose（推薦）

#### 建立並啟動服務
```bash
# 建立映像檔並啟動容器
docker-compose up -d

# 查看服務狀態
docker-compose ps

# 查看即時日誌
docker-compose logs -f taipower
```

#### 管理服務
```bash
# 停止服務
docker-compose down

# 重新啟動服務
docker-compose restart

# 更新服務（當程式碼有變更時）
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 方式二：Docker 命令

#### 建立映像檔
```bash
docker build -t taipower:latest .
```

#### 運行容器
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

#### 管理容器
```bash
# 查看容器狀態
docker ps

# 查看日誌
docker logs -f taipower

# 停止容器
docker stop taipower

# 刪除容器
docker rm taipower

# 重新啟動容器
docker restart taipower
```

## 驗證部署

### 1. 檢查容器狀態
```bash
docker ps
```
應該看到 taipower 容器在運行中

### 2. 檢查日誌輸出
```bash
docker logs taipower
```
應該看到類似以下的輸出：
```
0813_14:07:23| status_code: 200 |  download 14:00 data .....done
```

### 3. 檢查檔案生成
```bash
ls -la csv\(utf-8\)/
ls -la csv\(big5\)/
ls -la json/
```
應該看到當天日期的檔案，例如：`2025_08_13.csv`

### 4. 驗證時區設定
檢查容器內的時間是否為台灣時間：
```bash
docker exec taipower date
```
應該顯示台灣時間（Asia/Taipei）

## 時區問題解決方案

如果仍遇到時區問題，可以嘗試以下解決方案：

### 1. 強制設定容器時區
在 docker-compose.yaml 中添加時區設定：
```yaml
services:
  taipower:
    build: .
    container_name: taipower
    environment:
      - TZ=Asia/Taipei
      - PYTHONIOENCODING=utf-8
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - /etc/timezone:/etc/timezone:ro
      - ./csv(big5):/code/xlsx(big-5)
      - ./csv(utf-8):/code/csv(utf-8)
      - ./json:/code/json
    restart: unless-stopped
```

### 2. 檢查 NAS 系統時區
確保 NAS 系統本身的時區設定正確：
```bash
# 檢查系統時區
timedatectl status

# 如果需要設定時區
sudo timedatectl set-timezone Asia/Taipei
```

## 監控與維護

### 1. 設定日誌輪轉
為了避免日誌檔案過大，可以設定日誌輪轉：
```bash
# 在 docker-compose.yaml 中添加日誌設定
services:
  taipower:
    # ... 其他設定
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 2. 定期備份資料
建議定期備份產生的 CSV 和 Excel 檔案：
```bash
# 創建備份腳本
#!/bin/bash
BACKUP_DIR="/volume1/backup/taipower/$(date +%Y%m)"
mkdir -p "$BACKUP_DIR"
cp -r csv\(utf-8\)/* "$BACKUP_DIR/"
cp -r csv\(big5\)/* "$BACKUP_DIR/"
```

### 3. 監控容器健康狀態
可以建立健康檢查腳本：
```bash
#!/bin/bash
# 檢查容器是否運行
if ! docker ps | grep -q taipower; then
    echo "Container not running, restarting..."
    docker-compose restart
fi

# 檢查今天是否有產生檔案
TODAY=$(date +%Y_%m_%d)
if [ ! -f "csv(utf-8)/${TODAY}.csv" ]; then
    echo "No data file for today, check logs"
    docker-compose logs --tail 50 taipower
fi
```

## 故障排除

### 常見錯誤及解決方案

#### 1. 權限錯誤
```
PermissionError: [Errno 13] Permission denied
```
解決方案：
```bash
# 設定正確的資料夾權限
chmod -R 755 csv\(big5\) csv\(utf-8\) json
```

#### 2. 網路連線錯誤
```
requests.exceptions.ConnectionError
```
解決方案：
- 檢查 NAS 的網路連線
- 確認防火牆設定
- 檢查 DNS 設定

#### 3. 時區仍然不正確
如果檔案仍在錯誤時間創建：
```bash
# 重新建立容器
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# 檢查容器時間
docker exec taipower python3 -c "
import pytz
from datetime import datetime
taiwan_tz = pytz.timezone('Asia/Taipei')
print('Taiwan time:', datetime.now(taiwan_tz))
print('UTC time:', datetime.now(pytz.UTC))
"
```

#### 4. 記憶體不足
```
MemoryError
```
解決方案：
- 檢查 NAS 可用記憶體
- 在 docker-compose.yaml 中限制記憶體使用：
```yaml
services:
  taipower:
    # ... 其他設定
    deploy:
      resources:
        limits:
          memory: 256M
        reservations:
          memory: 128M
```

## 效能最佳化

### 1. 減少資源使用
```yaml
# 在 docker-compose.yaml 中添加資源限制
services:
  taipower:
    # ... 其他設定
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M
```

### 2. 網路最佳化
如果網路較慢，可以調整請求超時設定，在程式中加入：
```python
# 在 requests.get() 中添加 timeout 參數
res = requests.get(opendata_url, headers=headers, timeout=30)
```

這樣就完成了綠聯 NAS 上的完整部署配置！
