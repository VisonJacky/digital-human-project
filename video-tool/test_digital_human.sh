#!/bin/bash

# 創建測試目錄
mkdir -p test_output

# 設置測試環境
export PYTHONPATH=$PYTHONPATH:$(pwd)

# 測試數字人模塊
echo "測試數字人模塊..."
python3 -c "
from digital_human_module import DigitalHumanGenerator, DigitalHumanProvider, AvatarLanguage, AvatarGender
import os

# 創建輸出目錄
os.makedirs('test_output', exist_ok=True)

# 初始化數字人生成器
dh_generator = DigitalHumanGenerator(provider=DigitalHumanProvider.MOCK)

# 測試獲取頭像
print('測試獲取頭像...')
for language in [AvatarLanguage.MANDARIN, AvatarLanguage.CANTONESE, AvatarLanguage.ENGLISH]:
    for gender in [AvatarGender.MALE, AvatarGender.FEMALE]:
        avatars = dh_generator.get_available_avatars(language, gender)
        print(f'{language.value} {gender.value}: {len(avatars)} 個頭像')
        if avatars:
            print(f'  示例: {avatars[0][\"id\"]} - {avatars[0][\"name\"]}')

# 創建測試音頻文件
test_audio = 'test_output/test_audio.mp3'
with open(test_audio, 'wb') as f:
    f.write(bytes.fromhex('FFFB9064000000000000000000000000'))
    f.write(os.urandom(1024))

# 測試生成視頻
print('\\n測試生成視頻...')
avatar_id = 'zh-m-01'  # 使用模擬頭像ID
output_file = 'test_output/test_video.mp4'

# 定義表情
expressions = [
    {'timestamp': 1.0, 'expression': 'smile'},
    {'timestamp': 3.0, 'expression': 'surprise'},
    {'timestamp': 5.0, 'expression': 'neutral'}
]

# 生成視頻
video_file = dh_generator.generate_video(
    avatar_id=avatar_id,
    audio_file=test_audio,
    output_file=output_file,
    expressions=expressions
)

print(f'生成的視頻文件: {video_file}')
print(f'文件存在: {os.path.exists(video_file)}')
"

# 啟動 API 服務（後台運行）
echo -e "\n啟動 API 服務..."
python3 api.py > api.log 2>&1 &
API_PID=$!

# 等待 API 啟動
echo "等待 API 啟動..."
sleep 5

# 測試健康檢查端點
echo -e "\n測試健康檢查端點..."
curl -s http://localhost:5001/health | python3 -m json.tool

# 測試獲取頭像端點
echo -e "\n測試獲取頭像端點..."
curl -s "http://localhost:5001/avatars?language=mandarin&gender=female" | python3 -m json.tool > test_output/avatars_response.json

# 準備測試生成視頻
# 首先創建一個測試音頻文件
echo -e "\n創建測試音頻文件..."
AUDIO_ID=$(uuidgen)
cp test_output/test_audio.mp3 output/${AUDIO_ID}.mp3
echo "音頻文件ID: ${AUDIO_ID}"

# 獲取頭像ID
AVATAR_ID=$(grep -o '"id": "[^"]*' test_output/avatars_response.json | head -1 | cut -d'"' -f4)
if [ -z "$AVATAR_ID" ]; then
    AVATAR_ID="zh-f-01"  # 使用默認頭像ID
fi
echo "頭像ID: ${AVATAR_ID}"

# 測試生成視頻端點
echo -e "\n測試生成視頻端點..."
curl -s -X POST http://localhost:5001/generate \
  -H "Content-Type: application/json" \
  -d "{\"avatar_id\": \"${AVATAR_ID}\", \"audio_file_id\": \"${AUDIO_ID}\", \"background_color\": \"#00FF00\", \"resolution\": \"720p\"}" \
  | python3 -m json.tool > test_output/generate_response.json

# 獲取視頻ID
VIDEO_ID=$(grep -o '"video_id": "[^"]*' test_output/generate_response.json | cut -d'"' -f4)
echo "視頻ID: ${VIDEO_ID}"

# 測試獲取視頻端點
if [ ! -z "$VIDEO_ID" ]; then
    echo -e "\n測試獲取視頻端點..."
    curl -s http://localhost:5001/video/${VIDEO_ID} -o test_output/api_generated_video.mp4
    echo "視頻已保存到: test_output/api_generated_video.mp4"
fi

# 測試示例生成端點
echo -e "\n測試示例生成端點..."
curl -s "http://localhost:5001/examples?audio_file_id=${AUDIO_ID}" | python3 -m json.tool > test_output/examples_response.json

# 停止 API 服務
echo -e "\n停止 API 服務..."
kill $API_PID

echo -e "\n測試完成！結果保存在 test_output 目錄中。"
