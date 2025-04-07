"""
文本轉語音模塊的簡單API接口

此模塊提供一個Flask API，用於將文本轉換為語音。
支持普通話、粵語和英語，以及男聲和女聲選項。
"""

from flask import Flask, request, jsonify, send_file
import os
import uuid
from tts_module import TextToSpeech, Language, Gender, TTSProvider

app = Flask(__name__)

# 創建輸出目錄
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 初始化TTS
tts = TextToSpeech(provider=TTSProvider.GOOGLE)

@app.route('/health', methods=['GET'])
def health_check():
    """健康檢查端點"""
    return jsonify({"status": "ok", "message": "TTS服務正常運行"})

@app.route('/synthesize', methods=['POST'])
def synthesize_speech():
    """
    將文本轉換為語音
    
    請求參數:
    - text: 要轉換的文本
    - language: 語言 (mandarin, cantonese, english)
    - gender: 性別 (male, female)
    - speaking_rate: 語速 (可選，默認1.0)
    - pitch: 音調 (可選，默認0.0)
    
    返回:
    - 音頻文件
    """
    try:
        # 獲取請求參數
        data = request.json
        text = data.get('text')
        language_str = data.get('language', 'mandarin').lower()
        gender_str = data.get('gender', 'female').lower()
        speaking_rate = float(data.get('speaking_rate', 1.0))
        pitch = float(data.get('pitch', 0.0))
        
        # 驗證必要參數
        if not text:
            return jsonify({"error": "缺少必要參數: text"}), 400
        
        # 映射語言
        language_map = {
            'mandarin': Language.MANDARIN,
            'cantonese': Language.CANTONESE,
            'english': Language.ENGLISH
        }
        language = language_map.get(language_str)
        if not language:
            return jsonify({"error": f"不支持的語言: {language_str}"}), 400
        
        # 映射性別
        gender_map = {
            'male': Gender.MALE,
            'female': Gender.FEMALE
        }
        gender = gender_map.get(gender_str)
        if not gender:
            return jsonify({"error": f"不支持的性別: {gender_str}"}), 400
        
        # 生成唯一文件名
        file_id = str(uuid.uuid4())
        output_file = os.path.join(OUTPUT_DIR, f"{file_id}.mp3")
        
        # 生成語音
        tts.synthesize_speech(
            text=text,
            language=language,
            gender=gender,
            output_file=output_file,
            speaking_rate=speaking_rate,
            pitch=pitch
        )
        
        # 獲取時間戳
        timestamps = tts.get_timestamps(text, output_file)
        
        # 返回結果
        return jsonify({
            "message": "語音生成成功",
            "file_id": file_id,
            "duration": tts.get_audio_duration(output_file),
            "timestamps": {k: {"start": v[0], "end": v[1]} for k, v in timestamps.items()}
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/audio/<file_id>', methods=['GET'])
def get_audio(file_id):
    """
    獲取生成的音頻文件
    
    路徑參數:
    - file_id: 文件ID
    
    返回:
    - 音頻文件
    """
    try:
        # 驗證文件ID
        if not file_id or '..' in file_id:
            return jsonify({"error": "無效的文件ID"}), 400
        
        # 構建文件路徑
        file_path = os.path.join(OUTPUT_DIR, f"{file_id}.mp3")
        
        # 檢查文件是否存在
        if not os.path.exists(file_path):
            return jsonify({"error": "文件不存在"}), 404
        
        # 返回文件
        return send_file(file_path, mimetype='audio/mpeg')
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/examples', methods=['GET'])
def generate_examples():
    """
    生成示例音頻
    
    返回:
    - 示例音頻文件的ID列表
    """
    try:
        examples = []
        
        # 示例文本
        mandarin_text = "大家好，這是一個文本轉語音的示例。我們正在測試普通話語音合成。"
        cantonese_text = "大家好，呢個係一個文本轉語音嘅示例。我哋而家測試緊粵語語音合成。"
        english_text = "Hello everyone, this is a text-to-speech example. We are testing English speech synthesis."
        
        # 生成普通話語音（男聲）
        mandarin_male_id = str(uuid.uuid4())
        mandarin_male_output = os.path.join(OUTPUT_DIR, f"{mandarin_male_id}.mp3")
        tts.synthesize_speech(
            text=mandarin_text,
            language=Language.MANDARIN,
            gender=Gender.MALE,
            output_file=mandarin_male_output
        )
        examples.append({
            "id": mandarin_male_id,
            "language": "mandarin",
            "gender": "male",
            "text": mandarin_text
        })
        
        # 生成普通話語音（女聲）
        mandarin_female_id = str(uuid.uuid4())
        mandarin_female_output = os.path.join(OUTPUT_DIR, f"{mandarin_female_id}.mp3")
        tts.synthesize_speech(
            text=mandarin_text,
            language=Language.MANDARIN,
            gender=Gender.FEMALE,
            output_file=mandarin_female_output
        )
        examples.append({
            "id": mandarin_female_id,
            "language": "mandarin",
            "gender": "female",
            "text": mandarin_text
        })
        
        # 生成粵語語音（男聲）
        cantonese_male_id = str(uuid.uuid4())
        cantonese_male_output = os.path.join(OUTPUT_DIR, f"{cantonese_male_id}.mp3")
        tts.synthesize_speech(
            text=cantonese_text,
            language=Language.CANTONESE,
            gender=Gender.MALE,
            output_file=cantonese_male_output
        )
        examples.append({
            "id": cantonese_male_id,
            "language": "cantonese",
            "gender": "male",
            "text": cantonese_text
        })
        
        # 生成粵語語音（女聲）
        cantonese_female_id = str(uuid.uuid4())
        cantonese_female_output = os.path.join(OUTPUT_DIR, f"{cantonese_female_id}.mp3")
        tts.synthesize_speech(
            text=cantonese_text,
            language=Language.CANTONESE,
            gender=Gender.FEMALE,
            output_file=cantonese_female_output
        )
        examples.append({
            "id": cantonese_female_id,
            "language": "cantonese",
            "gender": "female",
            "text": cantonese_text
        })
        
        # 生成英語語音（男聲）
        english_male_id = str(uuid.uuid4())
        english_male_output = os.path.join(OUTPUT_DIR, f"{english_male_id}.mp3")
        tts.synthesize_speech(
            text=english_text,
            language=Language.ENGLISH,
            gender=Gender.MALE,
            output_file=english_male_output
        )
        examples.append({
            "id": english_male_id,
            "language": "english",
            "gender": "male",
            "text": english_text
        })
        
        # 生成英語語音（女聲）
        english_female_id = str(uuid.uuid4())
        english_female_output = os.path.join(OUTPUT_DIR, f"{english_female_id}.mp3")
        tts.synthesize_speech(
            text=english_text,
            language=Language.ENGLISH,
            gender=Gender.FEMALE,
            output_file=english_female_output
        )
        examples.append({
            "id": english_female_id,
            "language": "english",
            "gender": "female",
            "text": english_text
        })
        
        return jsonify({
            "message": "示例生成成功",
            "examples": examples
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
