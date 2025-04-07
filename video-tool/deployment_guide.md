# 數字人演講視頻生成工具 - 部署和使用指南

## 系統概述

數字人演講視頻生成工具是一個能夠通過輸入演講稿或語音文件，生成數字人演講視頻的應用程序。該工具支持以下功能：

- 支持多種語言：普通話、粵語和英語
- 提供男聲/女聲選擇
- 根據演講內容智能生成相關場景
- 支持場景切換和畫中畫兩種視頻模式
- 提供簡潔易用的Web界面

## 系統架構

該工具由以下幾個核心模塊組成：

1. **文本轉語音模塊**：將文本轉換為高質量的語音
2. **數字人動畫模塊**：生成數字人頭像並實現口型同步
3. **場景生成和合成模塊**：分析內容、生成場景並合成最終視頻
4. **Web界面**：提供用戶交互界面

## 部署指南

### 系統要求

- Python 3.8+
- Node.js 14+（如果需要前端開發）
- 足夠的磁盤空間（建議至少10GB）
- 建議使用GPU進行視頻生成（可選但推薦）

### 部署步驟

#### 1. 克隆代碼庫

```bash
git clone https://github.com/your-username/digital-human-project.git
cd digital-human-project
```

#### 2. 安裝依賴

```bash
# 安裝文本轉語音模塊依賴
cd modules/text_to_speech
pip install -r requirements.txt
cd ../..

# 安裝數字人動畫模塊依賴
cd modules/digital_human
pip install -r requirements.txt
cd ../..

# 安裝場景生成和合成模塊依賴
cd modules/scene_generation
pip install -r requirements.txt
python -m spacy download en_core_web_sm
cd ../..

# 安裝Web界面依賴
cd web_interface
pip install -r requirements.txt
cd ..
```

#### 3. 配置環境變量

創建一個`.env`文件在項目根目錄，並添加以下配置：

```
# API密鑰（如果使用真實API服務）
GOOGLE_CLOUD_API_KEY=your_google_cloud_api_key
AZURE_SPEECH_KEY=your_azure_speech_key
AZURE_SPEECH_REGION=eastus
DEEPBRAIN_API_KEY=your_deepbrain_api_key
RUNWAY_API_KEY=your_runway_api_key

# 服務端口
TTS_SERVICE_PORT=5000
DIGITAL_HUMAN_SERVICE_PORT=5001
SCENE_SERVICE_PORT=5002
WEB_INTERFACE_PORT=8080

# 模式設置
USE_MOCK_MODE=true  # 設置為false以使用真實API
```

#### 4. 啟動服務

```bash
# 啟動文本轉語音服務
cd modules/text_to_speech
python api.py &
cd ../..

# 啟動數字人動畫服務
cd modules/digital_human
python api.py &
cd ../..

# 啟動場景生成和合成服務
cd modules/scene_generation
python api.py &
cd ../..

# 啟動Web界面
cd web_interface
python app.py &
cd ..
```

或者，您可以使用提供的啟動腳本：

```bash
./start_services.sh
```

#### 5. 訪問Web界面

打開瀏覽器，訪問：

```
http://localhost:8080
```

## 使用指南

### 基本使用流程

1. **輸入演講內容**
   - 選擇"文本"模式並輸入演講稿
   - 或選擇"文件"模式並上傳文本文件（支持TXT、DOCX、PDF）或音頻文件（支持MP3、WAV）

2. **設置參數**
   - 選擇語言（普通話、粵語或英語）
   - 選擇性別（男聲或女聲）
   - 選擇具體的聲線
   - 選擇數字人頭像
   - 選擇視頻模式（場景切換或畫中畫）

3. **生成視頻**
   - 點擊"生成視頻"按鈕
   - 等待處理完成（處理時間取決於演講稿長度和選擇的視頻模式）

4. **預覽和下載**
   - 在預覽頁面查看生成的視頻
   - 點擊"下載視頻"按鈕保存視頻文件

### 高級功能

- **場景切換模式**：根據演講內容自動切換相關場景，數字人和場景交替出現
- **畫中畫模式**：數字人顯示在場景的一角，適合需要同時展示數字人和視覺內容的場合

## 故障排除

### 常見問題

1. **服務無法啟動**
   - 檢查端口是否被占用
   - 確保已安裝所有依賴
   - 查看日誌文件獲取詳細錯誤信息

2. **視頻生成失敗**
   - 檢查API密鑰是否正確（如果使用真實API）
   - 確保輸入的文本不為空
   - 檢查磁盤空間是否充足

3. **視頻質量問題**
   - 調整視頻分辨率設置
   - 如果使用模擬模式，考慮切換到真實API以獲得更好的質量

## 自定義和擴展

### 添加新語言

修改`web_interface/app.py`中的`get_languages`函數：

```python
@app.route('/api/languages', methods=['GET'])
def get_languages():
    """獲取支持的語言列表"""
    languages = [
        {"code": "zh-CN", "name": "普通話（中文簡體）"},
        {"code": "zh-HK", "name": "粵語（香港中文）"},
        {"code": "en-US", "name": "英語（美式）"},
        {"code": "ja-JP", "name": "日語"}  # 添加新語言
    ]
    return jsonify({"languages": languages})
```

### 添加新的數字人頭像

在相應的服務中添加新頭像，並確保在`static/images/avatars`目錄中添加預覽圖片。

## 聯繫與支持

如有任何問題或需要支持，請聯繫：

- 電子郵件：support@example.com
- 項目主頁：https://github.com/your-username/digital-human-project

---

感謝您使用數字人演講視頻生成工具！
