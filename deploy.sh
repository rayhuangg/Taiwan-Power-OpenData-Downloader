#!/bin/bash

# Taiwan Power Data Downloader 一鍵部署腳本
# 適用於綠聯 NAS 和其他 Linux 系統

set -e  # 遇到錯誤立即停止

echo "=========================================="
echo "Taiwan Power Data Downloader 部署腳本"
echo "=========================================="

# 檢查參數
if [ "$1" = "--update" ] || [ "$1" = "-u" ]; then
    echo "🔄 更新模式：重新部署現有服務"
    UPDATE_MODE=true
else
    echo "🆕 初始部署模式"
    UPDATE_MODE=false
fi

# 檢查 Docker 是否安裝
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安裝，請先安裝 Docker"
    exit 1
fi

# 檢查 Docker Compose 是否安裝
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安裝，請先安裝 Docker Compose"
    exit 1
fi

echo "✅ Docker 和 Docker Compose 已安裝"

# 檢查是否在專案目錄中
if [ ! -f "TaiwanPowerOpenDataDownloader.py" ]; then
    echo "❌ 請在專案根目錄中執行此腳本"
    exit 1
fi

echo "✅ 在正確的專案目錄中"

# 創建必要的目錄
if [ "$UPDATE_MODE" = false ]; then
    echo "📁 創建必要的目錄..."
    mkdir -p "csv(big5)" "csv(utf-8)" json
    
    # 設定目錄權限
    echo "🔧 設定目錄權限..."
    chmod 755 "csv(big5)" "csv(utf-8)" json
fi

# 停止現有的容器（如果存在）
echo "🛑 停止現有的容器..."
docker-compose down 2>/dev/null || true

# 建立 Docker 映像
if [ "$UPDATE_MODE" = true ]; then
    echo "🔄 重新建立 Docker 映像（清除快取）..."
    docker-compose build --no-cache
else
    echo "🐳 建立 Docker 映像..."
    docker-compose build --no-cache
fi

# 啟動服務
echo "🚀 啟動服務..."
docker-compose up -d

# 等待容器啟動
echo "⏳ 等待容器啟動..."
sleep 5

# 檢查容器狀態
if docker ps | grep -q taipower; then
    echo "✅ 容器已成功啟動"
else
    echo "❌ 容器啟動失敗"
    docker-compose logs
    exit 1
fi

# 檢查時區設定
echo "🕐 檢查時區設定..."
CONTAINER_TIME=$(docker exec taipower date '+%Y-%m-%d %H:%M:%S %Z')
echo "容器時間: $CONTAINER_TIME"

# 檢查 Python 時區
echo "🐍 檢查 Python 時區..."
docker exec taipower python3 -c "
import pytz
from datetime import datetime
taiwan_tz = pytz.timezone('Asia/Taipei')
taiwan_time = datetime.now(taiwan_tz)
print(f'Python 台灣時間: {taiwan_time.strftime(\"%Y-%m-%d %H:%M:%S %Z\")}')
"

echo ""
echo "=========================================="
if [ "$UPDATE_MODE" = true ]; then
    echo "🔄 更新完成！"
else
    echo "🎉 部署完成！"
fi
echo "=========================================="
echo ""
echo "📊 監控指令："
echo "  查看日誌: docker-compose logs -f taipower"
echo "  查看狀態: docker-compose ps"
echo "  停止服務: docker-compose down"
echo "  重啟服務: docker-compose restart"
echo "  更新部署: ./deploy.sh --update"
echo ""
echo "📁 輸出檔案位置："
echo "  UTF-8 CSV: ./csv(utf-8)/"
echo "  Excel 檔案: ./csv(big5)/"
echo "  JSON 備份: ./json/"
echo ""
echo "⏰ 程式會在每小時的 07、17、27、37、47、57 分執行"
echo "📅 檔案會在台灣時間午夜 12:00 切換到新的日期"
echo ""
echo "如需查看即時日誌，請執行："
echo "docker-compose logs -f taipower"
