# 程式修改後重新部署指南

當您修改了 `TaiwanPowerOpenDataDownloader.py` 或其他檔案後，需要重新建立 Docker 映像並重啟容器才能使修改生效。

## 快速更新指令

### 方法一：使用部署腳本（推薦）

```bash
# 程式修改後重新部署
./deploy.sh --update
# 或
./deploy.sh -u
```

### 方法二：使用 Docker Compose

#### 1. 快速重新部署
```bash
# 停止現有容器
docker-compose down

# 重新建立映像並啟動（會自動檢測檔案變更）
docker-compose up --build -d

# 查看啟動狀態
docker-compose logs -f taipower
```

#### 2. 強制重新建立（清除快取）
如果修改沒有生效，可以強制重新建立：
```bash
# 停止並刪除現有容器
docker-compose down

# 強制重新建立映像（清除 Docker 快取）
docker-compose build --no-cache

# 啟動服務
docker-compose up -d

# 查看日誌
docker-compose logs -f taipower
```

### 方法三：手動 Docker 命令

如果不使用 Docker Compose：

```bash
# 停止並刪除現有容器
docker stop taipower
docker rm taipower

# 刪除舊的映像
docker rmi taipower:latest

# 重新建立映像
docker build -t taipower:latest .

# 重新運行容器
docker run -d \
  --name taipower \
  --restart unless-stopped \
  -e TZ=Asia/Taipei \
  -v "$(pwd)/csv(big5):/code/xlsx(big-5)" \
  -v "$(pwd)/csv(utf-8):/code/csv(utf-8)" \
  -v "$(pwd)/json:/code/json" \
  taipower:latest
```

## 常用監控指令

```bash
# 查看容器狀態
docker-compose ps

# 查看即時日誌
docker-compose logs -f taipower

# 查看最近 50 行日誌
docker-compose logs --tail 50 taipower

# 進入容器內部（除錯用）
docker exec -it taipower bash

# 檢查容器內的檔案
docker exec taipower ls -la /code

# 檢查容器內的時間
docker exec taipower date

# 檢查容器資源使用
docker stats taipower
```

## 開發工作流程

1. **修改程式碼**
   - 編輯 `TaiwanPowerOpenDataDownloader.py` 或其他檔案

2. **本地測試（可選）**
   ```bash
   python TaiwanPowerOpenDataDownloader.py
   ```

3. **重新部署**
   ```bash
   ./deploy.sh --update
   ```

4. **驗證部署**
   ```bash
   # 查看日誌確認程式正常運行
   docker-compose logs -f taipower
   ```

5. **監控運行**
   ```bash
   # 檢查檔案是否正常產生
   ls -la csv\(utf-8\)/
   ls -la csv\(big5\)/
   ```

## 故障排除

### 修改沒有生效
```bash
# 確保完全重新建立
docker-compose down
docker system prune -f  # 清理 Docker 快取
docker-compose build --no-cache
docker-compose up -d
```

### 檢查檔案是否正確複製到容器
```bash
# 進入容器檢查檔案
docker exec -it taipower bash
ls -la /code/
cat /code/TaiwanPowerOpenDataDownloader.py | head -20
```

### 檢查程式運行狀態
```bash
# 查看詳細日誌
docker-compose logs --tail 100 taipower

# 檢查容器是否正在運行
docker ps | grep taipower

# 檢查容器重啟次數
docker inspect taipower | grep RestartCount
```

### 日誌問題解決

如果看不到程式輸出：

```bash
# 檢查容器是否在運行
docker ps

# 查看容器啟動日誌
docker logs taipower

# 進入容器手動執行程式檢查
docker exec -it taipower python3 TaiwanPowerOpenDataDownloader.py

# 檢查程式是否有語法錯誤
docker exec taipower python3 -m py_compile TaiwanPowerOpenDataDownloader.py
```

## 部署參數說明

### deploy.sh 參數

- `./deploy.sh` - 初始部署模式
- `./deploy.sh --update` 或 `./deploy.sh -u` - 更新模式（適合程式修改後重新部署）

### 更新模式與初始部署的差異

- **初始部署**：會創建所有必要目錄和設定權限
- **更新模式**：只重新建立映像和容器，不會重複創建目錄

這樣可以避免不必要的檔案操作，加快更新速度。
