# Taiwan-Power-OpenData-Downloader

每十分鐘定時自動下載台電各機組發電量Open Data, 以及台電今日電力資訊, 並轉為Excel可讀取之csv檔案儲存

## Method

* 官方可視化當下時刻發電量: https://www.taipower.com.tw/d006/loadGraph/loadGraph/genshx_.html
* open data平台(台電系統(含外購電力)各機組發電量即時資訊): https://data.gov.tw/dataset/8931

觀察公開資料平台JSON [網址](https://service.taipower.com.tw/data/opendata/apply/file/d006001/001.json) ，資料內的內容與台電即時更新的網頁相同，因此對此JSON檔案進行處理


### Docker

docker run

```bash
docker run -it --rm --name "taipower" -v /Users/huangtingray/MyData/code/Taiwan-Power-OpenData-Downloader:/Taiwan-Power-OpenData-Downloader  taipower:v0.1 bash
```

or 使用docker-compose

```bash
docker-compose up -d
```