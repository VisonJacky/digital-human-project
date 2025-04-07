"""
文本轉語音模塊 - 支持普通話、粵語和英語的文本轉語音功能

此模塊提供以下功能：
1. 使用Google Cloud Text-to-Speech API將文本轉換為語音
2. 支持普通話、粵語和英語
3. 提供男聲和女聲選項
4. 支持語音參數調整（速度、音調等）
5. 提供Azure Speech Service作為備選方案

使用方法：
1. 設置環境變量GOOGLE_APPLICATION_CREDENTIALS指向您的Google Cloud憑證JSON文件
2. 或者設置AZURE_SPEECH_KEY和AZURE_SPEECH_REGION環境變量以使用Azure
3. 調用synthesize_speech函數生成語音文件
"""

import os
import tempfile
from enum import Enum
from typing import Optional, Dict, Any, Tuple

# 導入Google Cloud Text-to-Speech
from google.cloud import texttospeech

# 導入Azure Speech Service
import azure.cognitiveservices.speech as speechsdk

# 導入環境變量處理
from dotenv import load_dotenv

# 導入音頻處理
from pydub import AudioSegment

# 加載環境變量
load_dotenv()

class Language(Enum):
    """支持的語言枚舉"""
    MANDARIN = "zh-CN"  # 普通話
    CANTONESE = "zh-HK"  # 粵語
    ENGLISH = "en-US"    # 英語

class Gender(Enum):
    """聲線性別枚舉"""
    MALE = "MALE"
    FEMALE = "FEMALE"

class TTSProvider(Enum):
    """TTS服務提供商枚舉"""
    GOOGLE = "google"
    AZURE = "azure"

class TextToSpeech:
    """文本轉語音類，支持Google和Azure服務"""
    
    def __init__(self, provider: TTSProvider = TTSProvider.GOOGLE):
        """
        初始化文本轉語音類
        
        Args:
            provider: TTS服務提供商，默認為Google
        """
        self.provider = provider
        
        # 初始化Google客戶端
        if provider == TTSProvider.GOOGLE:
            self.google_client = texttospeech.TextToSpeechClient()
        
        # 初始化Azure配置
        elif provider == TTSProvider.AZURE:
            self.azure_speech_key = os.getenv("AZURE_SPEECH_KEY")
            self.azure_speech_region = os.getenv("AZURE_SPEECH_REGION")
            
            if not self.azure_speech_key or not self.azure_speech_region:
                raise ValueError("Azure Speech服務需要設置AZURE_SPEECH_KEY和AZURE_SPEECH_REGION環境變量")
    
    def get_voice_name(self, language: Language, gender: Gender) -> str:
        """
        根據語言和性別獲取語音名稱
        
        Args:
            language: 語言選擇
            gender: 性別選擇
            
        Returns:
            語音名稱
        """
        # Google語音映射
        if self.provider == TTSProvider.GOOGLE:
            voice_mapping = {
                (Language.MANDARIN, Gender.MALE): "zh-CN-Wavenet-B",
                (Language.MANDARIN, Gender.FEMALE): "zh-CN-Wavenet-A",
                (Language.CANTONESE, Gender.MALE): "yue-HK-Standard-B",
                (Language.CANTONESE, Gender.FEMALE): "yue-HK-Standard-A",
                (Language.ENGLISH, Gender.MALE): "en-US-Neural2-D",
                (Language.ENGLISH, Gender.FEMALE): "en-US-Neural2-F"
            }
            
            return voice_mapping.get((language, gender), "zh-CN-Wavenet-A")
        
        # Azure語音映射
        elif self.provider == TTSProvider.AZURE:
            voice_mapping = {
                (Language.MANDARIN, Gender.MALE): "zh-CN-YunxiNeural",
                (Language.MANDARIN, Gender.FEMALE): "zh-CN-XiaoxiaoNeural",
                (Language.CANTONESE, Gender.MALE): "zh-HK-WanLungNeural",
                (Language.CANTONESE, Gender.FEMALE): "zh-HK-HiuMaanNeural",
                (Language.ENGLISH, Gender.MALE): "en-US-GuyNeural",
                (Language.ENGLISH, Gender.FEMALE): "en-US-JennyNeural"
            }
            
            return voice_mapping.get((language, gender), "zh-CN-XiaoxiaoNeural")
    
    def synthesize_speech_google(
        self, 
        text: str, 
        language: Language, 
        gender: Gender,
        output_file: str,
        speaking_rate: float = 1.0,
        pitch: float = 0.0
    ) -> str:
        """
        使用Google Cloud Text-to-Speech API生成語音
        
        Args:
            text: 要轉換的文本
            language: 語言選擇
            gender: 性別選擇
            output_file: 輸出文件路徑
            speaking_rate: 語速，範圍0.25-4.0，默認1.0
            pitch: 音調，範圍-20.0-20.0，默認0.0
            
        Returns:
            輸出文件路徑
        """
        # 設置輸入文本
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        # 選擇語音
        voice_name = self.get_voice_name(language, gender)
        voice = texttospeech.VoiceSelectionParams(
            language_code=language.value,
            name=voice_name,
            ssml_gender=texttospeech.SsmlVoiceGender[gender.value]
        )
        
        # 設置音頻配置
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=speaking_rate,
            pitch=pitch
        )
        
        # 執行請求
        response = self.google_client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        
        # 寫入音頻文件
        with open(output_file, "wb") as out:
            out.write(response.audio_content)
        
        return output_file
    
    def synthesize_speech_azure(
        self, 
        text: str, 
        language: Language, 
        gender: Gender,
        output_file: str,
        speaking_rate: float = 1.0,
        pitch: float = 0.0
    ) -> str:
        """
        使用Azure Speech Service生成語音
        
        Args:
            text: 要轉換的文本
            language: 語言選擇
            gender: 性別選擇
            output_file: 輸出文件路徑
            speaking_rate: 語速，範圍0.5-2.0，默認1.0
            pitch: 音調，範圍-50-50，默認0
            
        Returns:
            輸出文件路徑
        """
        # 創建語音配置
        speech_config = speechsdk.SpeechConfig(
            subscription=self.azure_speech_key,
            region=self.azure_speech_region
        )
        
        # 選擇語音
        voice_name = self.get_voice_name(language, gender)
        speech_config.speech_synthesis_voice_name = voice_name
        
        # 創建音頻配置
        audio_config = speechsdk.audio.AudioOutputConfig(filename=output_file)
        
        # 創建語音合成器
        speech_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config, 
            audio_config=audio_config
        )
        
        # 調整語速和音調
        ssml_text = f"""
        <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="{language.value}">
            <voice name="{voice_name}">
                <prosody rate="{speaking_rate}" pitch="{pitch}%">
                    {text}
                </prosody>
            </voice>
        </speak>
        """
        
        # 執行語音合成
        result = speech_synthesizer.speak_ssml_async(ssml_text).get()
        
        # 檢查結果
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            return output_file
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            raise Exception(f"語音合成取消: {cancellation_details.reason}, {cancellation_details.error_details}")
        else:
            raise Exception(f"語音合成失敗: {result.reason}")
    
    def synthesize_speech(
        self, 
        text: str, 
        language: Language, 
        gender: Gender,
        output_file: str,
        speaking_rate: float = 1.0,
        pitch: float = 0.0
    ) -> str:
        """
        生成語音的統一接口
        
        Args:
            text: 要轉換的文本
            language: 語言選擇
            gender: 性別選擇
            output_file: 輸出文件路徑
            speaking_rate: 語速，默認1.0
            pitch: 音調，默認0.0
            
        Returns:
            輸出文件路徑
        """
        if self.provider == TTSProvider.GOOGLE:
            return self.synthesize_speech_google(
                text, language, gender, output_file, speaking_rate, pitch
            )
        elif self.provider == TTSProvider.AZURE:
            return self.synthesize_speech_azure(
                text, language, gender, output_file, speaking_rate, pitch
            )
        else:
            raise ValueError(f"不支持的TTS提供商: {self.provider}")
    
    def get_audio_duration(self, audio_file: str) -> float:
        """
        獲取音頻文件的持續時間（秒）
        
        Args:
            audio_file: 音頻文件路徑
            
        Returns:
            音頻持續時間（秒）
        """
        audio = AudioSegment.from_file(audio_file)
        return len(audio) / 1000.0  # 毫秒轉秒
    
    def get_timestamps(self, text: str, audio_file: str) -> Dict[str, Tuple[float, float]]:
        """
        估算文本中每個句子的時間戳
        
        Args:
            text: 原始文本
            audio_file: 生成的音頻文件
            
        Returns:
            句子到時間戳的映射，格式為 {句子: (開始時間, 結束時間)}
        """
        # 分割句子
        sentences = [s.strip() for s in text.replace('。', '.').replace('！', '!').replace('？', '?').split('.') if s.strip()]
        
        # 獲取總時長
        total_duration = self.get_audio_duration(audio_file)
        
        # 計算每個句子的字符數
        char_counts = [len(s) for s in sentences]
        total_chars = sum(char_counts)
        
        # 估算每個句子的時間戳
        timestamps = {}
        current_time = 0.0
        
        for i, sentence in enumerate(sentences):
            if not sentence:
                continue
                
            # 估算句子持續時間
            duration = (char_counts[i] / total_chars) * total_duration
            
            # 記錄時間戳
            timestamps[sentence] = (current_time, current_time + duration)
            
            # 更新當前時間
            current_time += duration
        
        return timestamps

# 示例用法
def example_usage():
    """示例用法函數"""
    # 創建輸出目錄
    os.makedirs("output", exist_ok=True)
    
    # 初始化TTS
    tts = TextToSpeech(provider=TTSProvider.GOOGLE)
    
    # 示例文本
    mandarin_text = "大家好，這是一個文本轉語音的示例。我們正在測試普通話語音合成。"
    cantonese_text = "大家好，呢個係一個文本轉語音嘅示例。我哋而家測試緊粵語語音合成。"
    english_text = "Hello everyone, this is a text-to-speech example. We are testing English speech synthesis."
    
    # 生成普通話語音（男聲）
    mandarin_male_output = "output/mandarin_male.mp3"
    tts.synthesize_speech(
        text=mandarin_text,
        language=Language.MANDARIN,
        gender=Gender.MALE,
        output_file=mandarin_male_output
    )
    print(f"已生成普通話男聲語音: {mandarin_male_output}")
    
    # 生成普通話語音（女聲）
    mandarin_female_output = "output/mandarin_female.mp3"
    tts.synthesize_speech(
        text=mandarin_text,
        language=Language.MANDARIN,
        gender=Gender.FEMALE,
        output_file=mandarin_female_output
    )
    print(f"已生成普通話女聲語音: {mandarin_female_output}")
    
    # 生成粵語語音（男聲）
    cantonese_male_output = "output/cantonese_male.mp3"
    tts.synthesize_speech(
        text=cantonese_text,
        language=Language.CANTONESE,
        gender=Gender.MALE,
        output_file=cantonese_male_output
    )
    print(f"已生成粵語男聲語音: {cantonese_male_output}")
    
    # 生成粵語語音（女聲）
    cantonese_female_output = "output/cantonese_female.mp3"
    tts.synthesize_speech(
        text=cantonese_text,
        language=Language.CANTONESE,
        gender=Gender.FEMALE,
        output_file=cantonese_female_output
    )
    print(f"已生成粵語女聲語音: {cantonese_female_output}")
    
    # 生成英語語音（男聲）
    english_male_output = "output/english_male.mp3"
    tts.synthesize_speech(
        text=english_text,
        language=Language.ENGLISH,
        gender=Gender.MALE,
        output_file=english_male_output
    )
    print(f"已生成英語男聲語音: {english_male_output}")
    
    # 生成英語語音（女聲）
    english_female_output = "output/english_female.mp3"
    tts.synthesize_speech(
        text=english_text,
        language=Language.ENGLISH,
        gender=Gender.FEMALE,
        output_file=english_female_output
    )
    print(f"已生成英語女聲語音: {english_female_output}")
    
    # 獲取時間戳示例
    timestamps = tts.get_timestamps(english_text, english_male_output)
    print("時間戳示例:")
    for sentence, (start, end) in timestamps.items():
        print(f"'{sentence}': {start:.2f}s - {end:.2f}s")

if __name__ == "__main__":
    example_usage()
