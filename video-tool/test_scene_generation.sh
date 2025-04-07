#!/bin/bash

# 創建測試目錄
mkdir -p test_output

# 設置測試環境
export PYTHONPATH=$PYTHONPATH:$(pwd)

# 測試內容分析功能
echo "測試內容分析功能..."
python3 -c "
from scene_generation_module import ContentAnalyzer
import json

# 初始化內容分析器
analyzer = ContentAnalyzer()

# 測試文本
test_text = '''
人工智能正在改變我們的世界。從自動駕駛汽車到智能助手，AI技術已經融入了我們日常生活的方方面面。

深度學習是AI的一個重要分支，它模仿人腦的神經網絡結構，能夠從大量數據中學習複雜的模式。這種技術在圖像識別、自然語言處理和遊戲等領域取得了突破性進展。

然而，AI的發展也帶來了一些挑戰，如隱私保護、算法偏見和就業變化等問題。我們需要負責任地發展AI技術，確保它造福全人類。
'''

# 分析文本
analysis_result = analyzer.analyze_content(test_text)

# 輸出結果
print('分析結果:')
print(json.dumps(analysis_result, ensure_ascii=False, indent=2))

# 測試英文文本
english_text = '''
Artificial Intelligence is transforming our world. From self-driving cars to smart assistants, AI technology has been integrated into every aspect of our daily lives.

Deep learning is an important branch of AI that mimics the neural network structure of the human brain and can learn complex patterns from large amounts of data. This technology has made breakthroughs in fields such as image recognition, natural language processing, and gaming.

However, the development of AI also brings some challenges, such as privacy protection, algorithmic bias, and employment changes. We need to develop AI technology responsibly to ensure it benefits all of humanity.
'''

# 分析英文文本
english_analysis = analyzer.analyze_content(english_text)

# 輸出結果
print('\n英文文本分析結果:')
print(json.dumps(english_analysis, ensure_ascii=False, indent=2))
"

# 測試場景生成功能
echo -e "\n測試場景生成功能..."
python3 -c "
from scene_generation_module import SceneGenerator, SceneGenerationProvider
import os

# 創建輸出目錄
os.makedirs('test_output', exist_ok=True)

# 初始化場景生成器
generator = SceneGenerator(provider=SceneGenerationProvider.MOCK)

# 測試場景生成
prompt = '展示與人工智能、深度學習相關的場景'
output_file = 'test_output/test_scene.mp4'

# 生成場景
result = generator.generate_scene(
    prompt=prompt,
    output_file=output_file,
    style='realistic',
    duration=5,
    resolution='720p'
)

print(f'生成的場景視頻: {result}')
print(f'文件存在: {os.path.exists(result)}')
"

# 創建測試視頻文件
echo -e "\n創建測試視頻文件..."
python3 -c "
import os
import numpy as np
import cv2
from moviepy.editor import VideoFileClip, ImageSequenceClip

# 創建輸出目錄
os.makedirs('test_output', exist_ok=True)

# 創建數字人視頻
def create_digital_human_video():
    width, height = 640, 480
    fps = 30
    duration = 10  # 10秒
    
    frames = []
    for t in range(int(duration * fps)):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # 繪製一個簡單的頭像
        center_x, center_y = width // 2, height // 3
        radius = height // 4
        
        # 繪製頭部
        cv2.circle(frame, (center_x, center_y), radius, (200, 200, 200), -1)
        
        # 繪製眼睛
        eye_radius = radius // 8
        left_eye_x = center_x - radius // 3
        right_eye_x = center_x + radius // 3
        eye_y = center_y - radius // 8
        
        cv2.circle(frame, (left_eye_x, eye_y), eye_radius, (50, 50, 50), -1)
        cv2.circle(frame, (right_eye_x, eye_y), eye_radius, (50, 50, 50), -1)
        
        # 繪製嘴巴（根據時間變化）
        mouth_y = center_y + radius // 3
        mouth_width = radius // 2
        mouth_height = int((np.sin(t * 0.2) + 1) * radius // 8) + radius // 16
        
        mouth_left = center_x - mouth_width // 2
        mouth_top = mouth_y - mouth_height // 2
        
        cv2.ellipse(frame, (center_x, mouth_y), (mouth_width, mouth_height), 
                   0, 0, 180, (80, 80, 80), -1)
        
        # 添加綠幕背景
        mask = np.zeros((height, width), dtype=np.uint8)
        cv2.circle(mask, (center_x, center_y), radius + 20, 255, -1)
        
        # 將背景設為綠色
        green_bg = np.zeros_like(frame)
        green_bg[:, :] = (0, 255, 0)  # 綠色背景
        
        # 合成
        mask_3ch = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR) / 255.0
        frame = frame * mask_3ch + green_bg * (1 - mask_3ch)
        
        frames.append(frame)
    
    # 創建視頻
    video_clip = ImageSequenceClip(frames, fps=fps)
    output_file = 'test_output/digital_human.mp4'
    video_clip.write_videofile(output_file, codec='libx264')
    
    return output_file

# 創建場景視頻
def create_scene_videos(count=3):
    scene_files = []
    
    for i in range(count):
        width, height = 640, 480
        fps = 30
        duration = 5  # 5秒
        
        frames = []
        for t in range(int(duration * fps)):
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            
            # 生成隨機顏色
            r = np.random.randint(50, 200)
            g = np.random.randint(50, 200)
            b = np.random.randint(50, 200)
            
            # 繪製漸變背景
            for y in range(height):
                color = (
                    int(b * (1 - y/height) + np.random.randint(0, 100) * (y/height)),
                    int(g * (1 - y/height) + np.random.randint(0, 100) * (y/height)),
                    int(r * (1 - y/height) + np.random.randint(0, 100) * (y/height))
                )
                cv2.line(frame, (0, y), (width, y), color, 1)
            
            # 添加動態元素
            time_factor = t / (duration * fps)
            
            # 繪製移動的圓形
            for j in range(5):
                center_x = int(width * (0.2 + 0.6 * ((time_factor * (j+1)) % 1.0)))
                center_y = int(height * (0.2 + 0.6 * np.sin(time_factor * np.pi * 2 * (j+1))))
                radius = int(min(width, height) * 0.05 * (1 + 0.5 * np.sin(time_factor * np.pi * 4)))
                color = (
                    np.random.randint(100, 255),
                    np.random.randint(100, 255),
                    np.random.randint(100, 255)
                )
                cv2.circle(frame, (center_x, center_y), radius, color, -1)
            
            # 添加場景編號
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(frame, f'Scene {i+1}', (50, 50), font, 1, (255, 255, 255), 2)
            
            frames.append(frame)
        
        # 創建視頻
        video_clip = ImageSequenceClip(frames, fps=fps)
        output_file = f'test_output/scene_{i+1}.mp4'
        video_clip.write_videofile(output_file, codec='libx264')
        
        scene_files.append(output_file)
    
    return scene_files

# 創建音頻文件
def create_audio_file():
    output_file = 'test_output/audio.mp3'
    with open(output_file, 'wb') as f:
        f.write(bytes.fromhex('FFFB9064000000000000000000000000'))
        f.write(os.urandom(1024))
    return output_file

# 創建測試文件
dh_video = create_digital_human_video()
scene_videos = create_scene_videos(3)
audio_file = create_audio_file()

print(f'創建的數字人視頻: {dh_video}')
print(f'創建的場景視頻: {scene_videos}')
print(f'創建的音頻文件: {audio_file}')
"

# 測試視頻合成功能
echo -e "\n測試視頻合成功能..."
python3 -c "
from scene_generation_module import VideoComposer
import os

# 初始化視頻合成器
composer = VideoComposer()

# 測試文件
digital_human_video = 'test_output/digital_human.mp4'
scene_videos = [
    'test_output/scene_1.mp4',
    'test_output/scene_2.mp4',
    'test_output/scene_3.mp4'
]
output_file = 'test_output/composed_video.mp4'
audio_file = 'test_output/audio.mp3'

# 合成視頻
result = composer.compose_video(
    digital_human_video=digital_human_video,
    scene_videos=scene_videos,
    output_file=output_file,
    audio_file=audio_file
)

print(f'合成的視頻: {result}')
print(f'文件存在: {os.path.exists(result)}')

# 測試畫中畫功能
pip_output = 'test_output/pip_video.mp4'
pip_result = composer.create_picture_in_picture(
    main_video=scene_videos[0],
    pip_video=digital_human_video,
    output_file=pip_output,
    position='bottom-right',
    size_ratio=0.3
)

print(f'畫中畫視頻: {pip_result}')
print(f'文件存在: {os.path.exists(pip_result)}')
"

# 測試完整處理流程
echo -e "\n測試完整處理流程..."
python3 -c "
from scene_generation_module import SceneGenerationAndComposition, SceneGenerationProvider
import os

# 初始化處理器
processor = SceneGenerationAndComposition(provider=SceneGenerationProvider.MOCK)

# 測試文本
text = '''
人工智能正在改變我們的世界。從自動駕駛汽車到智能助手，AI技術已經融入了我們日常生活的方方面面。

深度學習是AI的一個重要分支，它模仿人腦的神經網絡結構，能夠從大量數據中學習複雜的模式。
'''

# 測試文件
digital_human_video = 'test_output/digital_human.mp4'
output_file = 'test_output/final_video.mp4'
audio_file = 'test_output/audio.mp3'

# 處理文本並生成場景
result = processor.process(
    text=text,
    digital_human_video=digital_human_video,
    output_file=output_file,
    audio_file=audio_file,
    style='realistic',
    scene_duration=5,
    resolution='720p'
)

print(f'生成的最終視頻: {result}')
print(f'文件存在: {os.path.exists(result)}')

# 測試畫中畫模式
pip_output = 'test_output/final_pip_video.mp4'
pip_result = processor.create_picture_in_picture_mode(
    text=text,
    digital_human_video=digital_human_video,
    output_file=pip_output,
    audio_file=audio_file,
    style='realistic',
    scene_duration=5,
    resolution='720p',
    pip_position='bottom-right',
    pip_size_ratio=0.3
)

print(f'生成的畫中畫模式視頻: {pip_result}')
print(f'文件存在: {os.path.exists(pip_result)}')
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
curl -s http://localhost:5002/health | python3 -m json.tool

# 測試分析端點
echo -e "\n測試分析端點..."
curl -s -X POST http://localhost:5002/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "人工智能正在改變我們的世界。從自動駕駛汽車到智能助手，AI技術已經融入了我們日常生活的方方面面。"}' \
  | python3 -m json.tool > test_output/analyze_response.json

# 測試場景生成端點
echo -e "\n測試場景生成端點..."
curl -s -X POST http://localhost:5002/generate-scene \
  -H "Content-Type: application/json" \
  -d '{"prompt": "展示與人工智能相關的場景", "duration": 5, "resolution": "720p"}' \
  | python3 -m json.tool > test_output/generate_scene_response.json

# 停止 API 服務
echo -e "\n停止 API 服務..."
kill $API_PID

echo -e "\n測試完成！結果保存在 test_output 目錄中。"
