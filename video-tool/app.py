"""
數字人演講視頻生成工具 - Web界面

此模塊提供一個Web界面，用於生成數字人演講視頻。
支持上傳演講稿或語音文件，選擇語言和聲線，並生成包含相關場景的視頻。
"""

from flask import Flask, request, jsonify, render_template, send_file, url_for
from flask_cors import CORS
import os
import sys
import uuid
import json
import requests
import time
from werkzeug.utils import secure_filename

# 添加模塊路徑
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "modules"))

# 創建應用
app = Flask(__name__)
CORS(app)  # 啟用跨域請求

# 配置
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
app.config['OUTPUT_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB最大上傳大小
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'docx', 'pdf', 'mp3', 'wav'}

# 確保目錄存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# 服務配置
TTS_SERVICE_URL = "http://localhost:5000"
DIGITAL_HUMAN_SERVICE_URL = "http://localhost:5001"
SCENE_SERVICE_URL = "http://localhost:5002"

# 工具函數
def allowed_file(filename):
    """檢查文件是否允許上傳"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def extract_text_from_file(file_path):
    """從文件中提取文本"""
    file_ext = file_path.rsplit('.', 1)[1].lower()
    
    if file_ext == 'txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    elif file_ext == 'docx':
        try:
            import docx
            doc = docx.Document(file_path)
            return '\n'.join([para.text for para in doc.paragraphs])
        except Exception as e:
            print(f"提取DOCX文本時出錯: {str(e)}")
            return ""
    elif file_ext == 'pdf':
        try:
            import PyPDF2
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                text = ""
                for page_num in range(len(pdf_reader.pages)):
                    text += pdf_reader.pages[page_num].extract_text()
                return text
        except Exception as e:
            print(f"提取PDF文本時出錯: {str(e)}")
            return ""
    else:
        return ""

# 路由
@app.route('/')
def index():
    """主頁"""
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康檢查端點"""
    # 檢查各個服務的健康狀態
    services_status = {
        "web_interface": "ok"
    }
    
    try:
        tts_response = requests.get(f"{TTS_SERVICE_URL}/health", timeout=5)
        services_status["tts_service"] = "ok" if tts_response.status_code == 200 else "error"
    except:
        services_status["tts_service"] = "unavailable"
    
    try:
        dh_response = requests.get(f"{DIGITAL_HUMAN_SERVICE_URL}/health", timeout=5)
        services_status["digital_human_service"] = "ok" if dh_response.status_code == 200 else "error"
    except:
        services_status["digital_human_service"] = "unavailable"
    
    try:
        scene_response = requests.get(f"{SCENE_SERVICE_URL}/health", timeout=5)
        services_status["scene_service"] = "ok" if scene_response.status_code == 200 else "error"
    except:
        services_status["scene_service"] = "unavailable"
    
    return jsonify({
        "status": "ok",
        "message": "數字人演講視頻生成工具正常運行",
        "services": services_status
    })

@app.route('/api/languages', methods=['GET'])
def get_languages():
    """獲取支持的語言列表"""
    languages = [
        {"code": "zh-CN", "name": "普通話（中文簡體）"},
        {"code": "zh-HK", "name": "粵語（香港中文）"},
        {"code": "en-US", "name": "英語（美式）"}
    ]
    return jsonify({"languages": languages})

@app.route('/api/voices', methods=['GET'])
def get_voices():
    """獲取支持的聲線列表"""
    language = request.args.get('language', 'zh-CN')
    gender = request.args.get('gender', 'female')
    
    try:
        # 從TTS服務獲取聲線列表
        response = requests.get(
            f"{TTS_SERVICE_URL}/voices",
            params={"language": language, "gender": gender},
            timeout=5
        )
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            # 如果服務不可用，返回模擬數據
            voices = []
            if language == "zh-CN":
                if gender == "female":
                    voices = [
                        {"id": "zh-CN-XiaoxiaoNeural", "name": "曉曉（女聲）"},
                        {"id": "zh-CN-YunxiNeural", "name": "雲希（女聲）"}
                    ]
                else:
                    voices = [
                        {"id": "zh-CN-YunxiNeural", "name": "雲希（男聲）"},
                        {"id": "zh-CN-YunjianNeural", "name": "雲健（男聲）"}
                    ]
            elif language == "zh-HK":
                if gender == "female":
                    voices = [
                        {"id": "zh-HK-HiuMaanNeural", "name": "曉敏（女聲）"},
                        {"id": "zh-HK-HiuGaaiNeural", "name": "曉佳（女聲）"}
                    ]
                else:
                    voices = [
                        {"id": "zh-HK-WanLungNeural", "name": "雲龍（男聲）"},
                        {"id": "zh-HK-SamNeural", "name": "山姆（男聲）"}
                    ]
            else:  # en-US
                if gender == "female":
                    voices = [
                        {"id": "en-US-JennyNeural", "name": "Jenny（女聲）"},
                        {"id": "en-US-AriaNeural", "name": "Aria（女聲）"}
                    ]
                else:
                    voices = [
                        {"id": "en-US-GuyNeural", "name": "Guy（男聲）"},
                        {"id": "en-US-DavisNeural", "name": "Davis（男聲）"}
                    ]
            
            return jsonify({"voices": voices})
    except:
        # 如果服務不可用，返回空列表
        return jsonify({"voices": [], "error": "無法連接到TTS服務"})

@app.route('/api/avatars', methods=['GET'])
def get_avatars():
    """獲取支持的數字人頭像列表"""
    language = request.args.get('language', 'zh-CN')
    gender = request.args.get('gender', 'female')
    
    try:
        # 從數字人服務獲取頭像列表
        response = requests.get(
            f"{DIGITAL_HUMAN_SERVICE_URL}/avatars",
            params={"language": language, "gender": gender},
            timeout=5
        )
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            # 如果服務不可用，返回模擬數據
            avatars = []
            if language == "zh-CN":
                if gender == "female":
                    avatars = [
                        {"id": "zh-f-01", "name": "劉芳", "preview_url": "/static/images/avatars/zh-f-01.jpg"},
                        {"id": "zh-f-02", "name": "王美", "preview_url": "/static/images/avatars/zh-f-02.jpg"}
                    ]
                else:
                    avatars = [
                        {"id": "zh-m-01", "name": "李明", "preview_url": "/static/images/avatars/zh-m-01.jpg"},
                        {"id": "zh-m-02", "name": "張偉", "preview_url": "/static/images/avatars/zh-m-02.jpg"}
                    ]
            elif language == "zh-HK":
                if gender == "female":
                    avatars = [
                        {"id": "hk-f-01", "name": "王美麗", "preview_url": "/static/images/avatars/hk-f-01.jpg"},
                        {"id": "hk-f-02", "name": "陳小姐", "preview_url": "/static/images/avatars/hk-f-02.jpg"}
                    ]
                else:
                    avatars = [
                        {"id": "hk-m-01", "name": "陳大文", "preview_url": "/static/images/avatars/hk-m-01.jpg"},
                        {"id": "hk-m-02", "name": "黃先生", "preview_url": "/static/images/avatars/hk-m-02.jpg"}
                    ]
            else:  # en-US
                if gender == "female":
                    avatars = [
                        {"id": "en-f-01", "name": "Sarah", "preview_url": "/static/images/avatars/en-f-01.jpg"},
                        {"id": "en-f-02", "name": "Emily", "preview_url": "/static/images/avatars/en-f-02.jpg"}
                    ]
                else:
                    avatars = [
                        {"id": "en-m-01", "name": "John", "preview_url": "/static/images/avatars/en-m-01.jpg"},
                        {"id": "en-m-02", "name": "Michael", "preview_url": "/static/images/avatars/en-m-02.jpg"}
                    ]
            
            return jsonify({"avatars": avatars})
    except:
        # 如果服務不可用，返回空列表
        return jsonify({"avatars": [], "error": "無法連接到數字人服務"})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """上傳文件"""
    # 檢查是否有文件
    if 'file' not in request.files:
        return jsonify({"error": "沒有文件"}), 400
    
    file = request.files['file']
    
    # 檢查文件名
    if file.filename == '':
        return jsonify({"error": "沒有選擇文件"}), 400
    
    # 檢查文件類型
    if not allowed_file(file.filename):
        return jsonify({"error": "不支持的文件類型"}), 400
    
    # 保存文件
    filename = secure_filename(file.filename)
    file_id = str(uuid.uuid4())
    file_ext = filename.rsplit('.', 1)[1].lower()
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}.{file_ext}")
    file.save(file_path)
    
    # 如果是文本文件，提取文本
    text = ""
    if file_ext in ['txt', 'docx', 'pdf']:
        text = extract_text_from_file(file_path)
    
    return jsonify({
        "message": "文件上傳成功",
        "file_id": file_id,
        "file_ext": file_ext,
        "text": text
    })

@app.route('/api/generate', methods=['POST'])
def generate_video():
    """生成視頻"""
    data = request.json
    
    # 驗證必要參數
    if not data:
        return jsonify({"error": "缺少請求數據"}), 400
    
    # 獲取參數
    text = data.get('text', '')
    file_id = data.get('file_id', '')
    file_ext = data.get('file_ext', '')
    language = data.get('language', 'zh-CN')
    gender = data.get('gender', 'female')
    voice_id = data.get('voice_id', '')
    avatar_id = data.get('avatar_id', '')
    video_mode = data.get('video_mode', 'scene_switching')  # scene_switching 或 picture_in_picture
    
    # 檢查必要參數
    if not text and not (file_id and file_ext in ['mp3', 'wav']):
        return jsonify({"error": "缺少文本或音頻文件"}), 400
    
    if not voice_id:
        return jsonify({"error": "缺少聲線選擇"}), 400
    
    if not avatar_id:
        return jsonify({"error": "缺少數字人頭像選擇"}), 400
    
    try:
        # 步驟1：生成語音
        audio_file_id = None
        if text:
            # 如果有文本，使用TTS服務生成語音
            tts_response = requests.post(
                f"{TTS_SERVICE_URL}/synthesize",
                json={
                    "text": text,
                    "voice_id": voice_id,
                    "language": language
                },
                timeout=30
            )
            
            if tts_response.status_code != 200:
                return jsonify({"error": f"TTS服務錯誤: {tts_response.text}"}), 500
            
            audio_file_id = tts_response.json().get("audio_id")
        else:
            # 如果沒有文本，使用上傳的音頻文件
            audio_file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}.{file_ext}")
            
            # 上傳音頻文件到TTS服務
            with open(audio_file_path, 'rb') as f:
                files = {'file': f}
                tts_response = requests.post(
                    f"{TTS_SERVICE_URL}/upload_audio",
                    files=files,
                    timeout=30
                )
            
            if tts_response.status_code != 200:
                return jsonify({"error": f"音頻上傳錯誤: {tts_response.text}"}), 500
            
            audio_file_id = tts_response.json().get("audio_id")
        
        # 步驟2：生成數字人視頻
        dh_response = requests.post(
            f"{DIGITAL_HUMAN_SERVICE_URL}/generate",
            json={
                "avatar_id": avatar_id,
                "audio_file_id": audio_file_id,
                "background_color": "#00FF00",  # 綠幕背景
                "resolution": "1080p"
            },
            timeout=120
        )
        
        if dh_response.status_code != 200:
            return jsonify({"error": f"數字人生成錯誤: {dh_response.text}"}), 500
        
        digital_human_video_id = dh_response.json().get("video_id")
        
        # 步驟3：生成場景並合成最終視頻
        final_video_id = None
        
        if video_mode == "scene_switching":
            # 場景切換模式
            scene_response = requests.post(
                f"{SCENE_SERVICE_URL}/process",
                json={
                    "text": text,
                    "digital_human_video_id": digital_human_video_id,
                    "audio_file_id": audio_file_id,
                    "style": "realistic",
                    "scene_duration": 5,
                    "resolution": "1080p"
                },
                timeout=300
            )
        else:
            # 畫中畫模式
            scene_response = requests.post(
                f"{SCENE_SERVICE_URL}/picture-in-picture",
                json={
                    "text": text,
                    "digital_human_video_id": digital_human_video_id,
                    "audio_file_id": audio_file_id,
                    "style": "realistic",
                    "scene_duration": 5,
                    "resolution": "1080p",
                    "pip_position": "bottom-right",
                    "pip_size_ratio": 0.3
                },
                timeout=300
            )
        
        if scene_response.status_code != 200:
            return jsonify({"error": f"場景生成錯誤: {scene_response.text}"}), 500
        
        final_video_id = scene_response.json().get("video_id")
        
        # 返回結果
        return jsonify({
            "message": "視頻生成成功",
            "audio_id": audio_file_id,
            "digital_human_video_id": digital_human_video_id,
            "final_video_id": final_video_id,
            "preview_url": url_for('get_video', video_id=final_video_id),
            "download_url": url_for('download_video', video_id=final_video_id)
        })
    
    except Exception as e:
        return jsonify({"error": f"處理請求時發生錯誤: {str(e)}"}), 500

@app.route('/api/video/<video_id>', methods=['GET'])
def get_video(video_id):
    """獲取視頻"""
    # 首先檢查本地是否有視頻
    local_video_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{video_id}.mp4")
    
    if os.path.exists(local_video_path):
        return send_file(local_video_path, mimetype='video/mp4')
    
    # 如果本地沒有，嘗試從場景服務獲取
    try:
        response = requests.get(f"{SCENE_SERVICE_URL}/video/{video_id}", stream=True)
        
        if response.status_code == 200:
            # 保存到本地
            with open(local_video_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return send_file(local_video_path, mimetype='video/mp4')
        else:
            # 如果場景服務沒有，嘗試從數字人服務獲取
            response = requests.get(f"{DIGITAL_HUMAN_SERVICE_URL}/video/{video_id}", stream=True)
            
            if response.status_code == 200:
                # 保存到本地
                with open(local_video_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                return send_file(local_video_path, mimetype='video/mp4')
            else:
                return jsonify({"error": "視頻不存在"}), 404
    except:
        return jsonify({"error": "獲取視頻時發生錯誤"}), 500

@app.route('/api/download/<video_id>', methods=['GET'])
def download_video(video_id):
    """下載視頻"""
    # 首先檢查本地是否有視頻
    local_video_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{video_id}.mp4")
    
    if os.path.exists(local_video_path):
        return send_file(
            local_video_path,
            mimetype='video/mp4',
            as_attachment=True,
            download_name=f"digital_human_video_{video_id}.mp4"
        )
    
    # 如果本地沒有，嘗試從場景服務獲取
    try:
        response = requests.get(f"{SCENE_SERVICE_URL}/video/{vi<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>