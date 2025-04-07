#!/bin/bash

# 創建測試目錄
mkdir -p test_output

# 設置測試環境
export PYTHONPATH=$PYTHONPATH:$(pwd)

# 測試文本
MANDARIN_TEXT="這是一個測試文本，用於驗證文本轉語音模塊的功能。我們希望確保它能夠正確處理普通話。"
CANTONESE_TEXT="呢個係一個測試文本，用嚟驗證文本轉語音模塊嘅功能。我哋希望確保佢能夠正確處理粵語。"
ENGLISH_TEXT="This is a test text to verify the functionality of the text-to-speech module. We hope to ensure it correctly processes English."

# 測試直接使用模塊
echo "測試 TTS 模塊..."
python3 -c "
from tts_module import TextToSpeech, Language, Gender, TTSProvider
import os

# 創建輸出目錄
os.makedirs('test_output', exist_ok=True)

# 初始化 TTS
tts = TextToSpeech(provider=TTSProvider.GOOGLE)

# 測試普通話
output_file = 'test_output/test_mandarin.mp3'
tts.synthesize_speech(
    text='$MANDARIN_TEXT',
    language=Language.MANDARIN,
    gender=Gender.FEMALE,
    output_file=output_file
)
print(f'生成普通話語音: {output_file}')
print(f'音頻時長: {tts.get_audio_duration(output_file):.2f} 秒')

# 測試粵語
output_file = 'test_output/test_cantonese.mp3'
tts.synthesize_speech(
    text='$CANTONESE_TEXT',
    language=Language.CANTONESE,
    gender=Gender.MALE,
    output_file=output_file
)
print(f'生成粵語語音: {output_file}')
print(f'音頻時長: {tts.get_audio_duration(output_file):.2f} 秒')

# 測試英語
output_file = 'test_output/test_english.mp3'
tts.synthesize_speech(
    text='$ENGLISH_TEXT',
    language=Language.ENGLISH,
    gender=Gender.MALE,
    output_file=output_file
)
print(f'生成英語語音: {output_file}')
print(f'音頻時長: {tts.get_audio_duration(output_file):.2f} 秒')
"

# 啟動 API 服務（後台運行）
echo "啟動 API 服務..."
python3 api.py > api.log 2>&1 &
API_PID=$!

# 等待 API 啟動
echo "等待 API 啟動..."
sleep 5

# 測試健康檢查端點
echo "測試健康檢查端點..."
curl -s http://localhost:5000/health | python3 -m json.tool

# 測試語音合成端點
echo "測試語音合成端點..."
curl -s -X POST http://localhost:5000/synthesize \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"$ENGLISH_TEXT\", \"language\": \"english\", \"gender\": \"female\"}" \
  | python3 -m json.tool > test_output/synthesis_response.json

# 獲取文件 ID
FILE_ID=$(grep -o '"file_id": "[^"]*' test_output/synthesis_response.json | cut -d'"' -f4)

# 測試獲取音頻端點
echo "測試獲取音頻端點..."
curl -s http://localhost:5000/audio/$FILE_ID -o test_output/api_generated.mp3

# 測試示例生成端點
echo "測試示例生成端點..."
curl -s http://localhost:5000/examples | python3 -m json.tool > test_output/examples_response.json

# 停止 API 服務
echo "停止 API 服務..."
kill $API_PID

echo "測試完成！結果保存在 test_output 目錄中。"
