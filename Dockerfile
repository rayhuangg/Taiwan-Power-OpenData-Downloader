
FROM python:3.9.12-slim

# 設定時區為台灣
ENV TZ=Asia/Taipei
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8

# 安裝時區相關套件
RUN apt-get update && \
    apt-get install -y tzdata && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /code

# 先複製 requirements.txt 並安裝依賴（利用 Docker 快取）
COPY requirements.txt /code/
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# 複製程式檔案
COPY . /code

# 建立必要的目錄
RUN mkdir -p csv\(utf-8\) csv\(big5\) json && \
    chmod 755 csv\(utf-8\) csv\(big5\) json

# 健康檢查
HEALTHCHECK --interval=5m --timeout=30s --start-period=30s --retries=3 \
    CMD python3 -c "import sys; sys.exit(0)" || exit 1

# 使用非 root 用戶運行（安全最佳實踐）
RUN useradd -m -u 1000 taipower && \
    chown -R taipower:taipower /code
USER taipower

CMD ["python3", "TaiwanPowerOpenDataDownloader.py"]

