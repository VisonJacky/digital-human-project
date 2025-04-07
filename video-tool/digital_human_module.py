"""
數字人動畫模塊 - 支持生成與語音同步的數字人視頻

此模塊提供以下功能：
1. 使用DeepBrain AI API生成數字人視頻
2. 實現口型與語音的同步
3. 支持不同的表情和動作
4. 提供模擬模式用於開發和測試
"""

import os
import json
import time
import uuid
import requests
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from dotenv import load_dotenv

# 導入環境變量處理
load_dotenv()

class AvatarGender(Enum):
    """數字人性別枚舉"""
    MALE = "male"
    FEMALE = "female"

class AvatarLanguage(Enum):
    """數字人語言枚舉"""
    MANDARIN = "zh-CN"  # 普通話
    CANTONESE = "zh-HK"  # 粵語
    ENGLISH = "en-US"    # 英語

class DigitalHumanProvider(Enum):
    """數字人服務提供商枚舉"""
    DEEPBRAIN = "deepbrain"
    SYNTHESIA = "synthesia"
    MOCK = "mock"  # 模擬模式

class DigitalHumanGenerator:
    """數字人生成類，支持DeepBrain和模擬模式"""
    
    def __init__(self, provider: DigitalHumanProvider = DigitalHumanProvider.MOCK):
        """
        初始化數字人生成類
        
        Args:
            provider: 數字人服務提供商，默認為模擬模式
        """
        self.provider = provider
        
        # 初始化DeepBrain配置
        if provider == DigitalHumanProvider.DEEPBRAIN:
            self.api_key = os.getenv("DEEPBRAIN_API_KEY")
            
            if not self.api_key:
                print("警告: 未設置DEEPBRAIN_API_KEY環境變量，將使用模擬模式")
                self.provider = DigitalHumanProvider.MOCK
            
            self.api_base_url = "https://api.deepbrain.io/v1"
        
        # 初始化Synthesia配置
        elif provider == DigitalHumanProvider.SYNTHESIA:
            self.api_key = os.getenv("SYNTHESIA_API_KEY")
            
            if not self.api_key:
                print("警告: 未設置SYNTHESIA_API_KEY環境變量，將使用模擬模式")
                self.provider = DigitalHumanProvider.MOCK
            
            self.api_base_url = "https://api.synthesia.io/v2"
    
    def get_available_avatars(self, language: AvatarLanguage, gender: AvatarGender) -> List[Dict[str, Any]]:
        """
        獲取可用的數字人頭像列表
        
        Args:
            language: 語言選擇
            gender: 性別選擇
            
        Returns:
            數字人頭像列表
        """
        if self.provider == DigitalHumanProvider.DEEPBRAIN:
            return self._get_deepbrain_avatars(language, gender)
        elif self.provider == DigitalHumanProvider.SYNTHESIA:
            return self._get_synthesia_avatars(language, gender)
        else:
            return self._get_mock_avatars(language, gender)
    
    def _get_deepbrain_avatars(self, language: AvatarLanguage, gender: AvatarGender) -> List[Dict[str, Any]]:
        """
        獲取DeepBrain可用的數字人頭像列表
        
        Args:
            language: 語言選擇
            gender: 性別選擇
            
        Returns:
            數字人頭像列表
        """
        try:
            url = f"{self.api_base_url}/avatars"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            params = {
                "language": language.value,
                "gender": gender.value
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                avatars = response.json().get("avatars", [])
                return avatars
            else:
                print(f"獲取DeepBrain頭像失敗: {response.status_code}, {response.text}")
                return []
        except Exception as e:
            print(f"獲取DeepBrain頭像時發生錯誤: {str(e)}")
            return []
    
    def _get_synthesia_avatars(self, language: AvatarLanguage, gender: AvatarGender) -> List[Dict[str, Any]]:
        """
        獲取Synthesia可用的數字人頭像列表
        
        Args:
            language: 語言選擇
            gender: 性別選擇
            
        Returns:
            數字人頭像列表
        """
        try:
            url = f"{self.api_base_url}/avatars"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                all_avatars = response.json()
                
                # 過濾符合語言和性別的頭像
                filtered_avatars = []
                for avatar in all_avatars:
                    avatar_languages = avatar.get("languages", [])
                    avatar_gender = avatar.get("gender", "").lower()
                    
                    if language.value in avatar_languages and avatar_gender == gender.value:
                        filtered_avatars.append(avatar)
                
                return filtered_avatars
            else:
                print(f"獲取Synthesia頭像失敗: {response.status_code}, {response.text}")
                return []
        except Exception as e:
            print(f"獲取Synthesia頭像時發生錯誤: {str(e)}")
            return []
    
    def _get_mock_avatars(self, language: AvatarLanguage, gender: AvatarGender) -> List[Dict[str, Any]]:
        """
        獲取模擬的數字人頭像列表
        
        Args:
            language: 語言選擇
            gender: 性別選擇
            
        Returns:
            數字人頭像列表
        """
        # 模擬頭像數據
        mock_avatars = []
        
        if language == AvatarLanguage.MANDARIN:
            if gender == AvatarGender.MALE:
                mock_avatars = [
                    {"id": "zh-m-01", "name": "李明", "gender": "male", "language": "zh-CN", "preview_url": "https://example.com/avatars/zh-m-01.jpg"},
                    {"id": "zh-m-02", "name": "張偉", "gender": "male", "language": "zh-CN", "preview_url": "https://example.com/avatars/zh-m-02.jpg"},
                    {"id": "zh-m-03", "name": "王強", "gender": "male", "language": "zh-CN", "preview_url": "https://example.com/avatars/zh-m-03.jpg"}
                ]
            else:
                mock_avatars = [
                    {"id": "zh-f-01", "name": "劉芳", "gender": "female", "language": "zh-CN", "preview_url": "https://example.com/avatars/zh-f-01.jpg"},
                    {"id": "zh-f-02", "name": "陳婷", "gender": "female", "language": "zh-CN", "preview_url": "https://example.com/avatars/zh-f-02.jpg"},
                    {"id": "zh-f-03", "name": "楊麗", "gender": "female", "language": "zh-CN", "preview_url": "https://example.com/avatars/zh-f-03.jpg"}
                ]
        elif language == AvatarLanguage.CANTONESE:
            if gender == AvatarGender.MALE:
                mock_avatars = [
                    {"id": "hk-m-01", "name": "陳大文", "gender": "male", "language": "zh-HK", "preview_url": "https://example.com/avatars/hk-m-01.jpg"},
                    {"id": "hk-m-02", "name": "黃志明", "gender": "male", "language": "zh-HK", "preview_url": "https://example.com/avatars/hk-m-02.jpg"}
                ]
            else:
                mock_avatars = [
                    {"id": "hk-f-01", "name": "王美麗", "gender": "female", "language": "zh-HK", "preview_url": "https://example.com/avatars/hk-f-01.jpg"},
                    {"id": "hk-f-02", "name": "李詩詩", "gender": "female", "language": "zh-HK", "preview_url": "https://example.com/avatars/hk-f-02.jpg"}
                ]
        else:  # 英語
            if gender == AvatarGender.MALE:
                mock_avatars = [
                    {"id": "en-m-01", "name": "John", "gender": "male", "language": "en-US", "preview_url": "https://example.com/avatars/en-m-01.jpg"},
                    {"id": "en-m-02", "name": "Michael", "gender": "male", "language": "en-US", "preview_url": "https://example.com/avatars/en-m-02.jpg"},
                    {"id": "en-m-03", "name": "David", "gender": "male", "language": "en-US", "preview_url": "https://example.com/avatars/en-m-03.jpg"}
                ]
            else:
                mock_avatars = [
                    {"id": "en-f-01", "name": "Sarah", "gender": "female", "language": "en-US", "preview_url": "https://example.com/avatars/en-f-01.jpg"},
                    {"id": "en-f-02", "name": "Emily", "gender": "female", "language": "en-US", "preview_url": "https://example.com/avatars/en-f-02.jpg"},
                    {"id": "en-f-03", "name": "Jessica", "gender": "female", "language": "en-US", "preview_url": "https://example.com/avatars/en-f-03.jpg"}
                ]
        
        return mock_avatars
    
    def generate_video(
        self, 
        avatar_id: str, 
        audio_file: str, 
        output_file: str,
        background_color: str = "#00FF00",  # 綠幕背景
        resolution: str = "1080p",
        expressions: List[Dict[str, Any]] = None
    ) -> str:
        """
        生成數字人視頻
        
        Args:
            avatar_id: 數字人頭像ID
            audio_file: 音頻文件路徑
            output_file: 輸出視頻文件路徑
            background_color: 背景顏色，默認為綠幕
            resolution: 視頻分辨率，默認為1080p
            expressions: 表情和動作列表，格式為 [{"timestamp": 1.5, "expression": "smile"}]
            
        Returns:
            輸出視頻文件路徑
        """
        if self.provider == DigitalHumanProvider.DEEPBRAIN:
            return self._generate_deepbrain_video(avatar_id, audio_file, output_file, background_color, resolution, expressions)
        elif self.provider == DigitalHumanProvider.SYNTHESIA:
            return self._generate_synthesia_video(avatar_id, audio_file, output_file, background_color, resolution, expressions)
        else:
            return self._generate_mock_video(avatar_id, audio_file, output_file, background_color, resolution, expressions)
    
    def _generate_deepbrain_video(
        self, 
        avatar_id: str, 
        audio_file: str, 
        output_file: str,
        background_color: str = "#00FF00",
        resolution: str = "1080p",
        expressions: List[Dict[str, Any]] = None
    ) -> str:
        """
        使用DeepBrain AI生成數字人視頻
        
        Args:
            avatar_id: 數字人頭像ID
            audio_file: 音頻文件路徑
            output_file: 輸出視頻文件路徑
            background_color: 背景顏色，默認為綠幕
            resolution: 視頻分辨率，默認為1080p
            expressions: 表情和動作列表
            
        Returns:
            輸出視頻文件路徑
        """
        try:
            url = f"{self.api_base_url}/videos"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 上傳音頻文件
            audio_url = self._upload_audio_file(audio_file)
            
            # 準備表情數據
            expression_data = []
            if expressions:
                for expr in expressions:
                    expression_data.append({
                        "timestamp": expr.get("timestamp", 0),
                        "type": expr.get("expression", "neutral")
                    })
            
            # 準備請求數據
            data = {
                "avatar": {
                    "id": avatar_id
                },
                "audio": {
                    "url": audio_url
                },
                "background": {
                    "type": "chroma",
                    "color": background_color
                },
                "export": {
                    "format": "mp4",
                    "resolution": resolution
                }
            }
            
            if expression_data:
                data["expressions"] = expression_data
            
            # 發送請求
            response = requests.post(url, headers=headers, data=json.dumps(data))
            
            if response.status_code == 200:
                result = response.json()
                video_url = result.get("video_url")
                
                # 下載視頻
                self._download_file(video_url, output_file)
                
                return output_file
            else:
                print(f"生成DeepBrain視頻失敗: {response.status_code}, {response.text}")
                return self._generate_mock_video(avatar_id, audio_file, output_file, background_color, resolution, expressions)
        except Exception as e:
            print(f"生成DeepBrain視頻時發生錯誤: {str(e)}")
            return self._generate_mock_video(avatar_id, audio_file, output_file, background_color, resolution, expressions)
    
    def _generate_synthesia_video(
        self, 
        avatar_id: str, 
        audio_file: str, 
        output_file: str,
        background_color: str = "#00FF00",
        resolution: str = "1080p",
        expressions: List[Dict[str, Any]] = None
    ) -> str:
        """
        使用Synthesia生成數字人視頻
        
        Args:
            avatar_id: 數字人頭像ID
            audio_file: 音頻文件路徑
            output_file: 輸出視頻文件路徑
            background_color: 背景顏色，默認為綠幕
            resolution: 視頻分辨率，默認為1080p
            expressions: 表情和動作列表
            
        Returns:
            輸出視頻文件路徑
        """
        try:
            url = f"{self.api_base_url}/videos"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 上傳音頻文件
            audio_url = self._upload_audio_file(audio_file)
            
            # 準備請求數據
            data = {
                "test": True,  # 測試模式
                "input": [
                    {
                        "audioUrl": audio_url,
                        "avatar": avatar_id,
                        "background": {
                            "color": background_color
                        },
                        "avatarSettings": {
                            "horizontalAlignment": "center",
                            "scale": 1.0,
                            "verticalAlignment": "center"
                        }
                    }
                ],
                "title": f"Generated Video {uuid.uuid4()}"
            }
            
            # 發送請求
            response = requests.post(url, headers=headers, data=json.dumps(data))
            
            if response.status_code == 201:
                result = response.json()
                video_id = result.get("id")
                
                # 等待視頻生成完成
                video_url = self._wait_for_synthesia_video(video_id)
                
                if video_url:
                    # 下載視頻
                    self._download_file(video_url, output_file)
                    return output_file
                else:
                    print("等待Synthesia視頻生成超時")
                    return self._generate_mock_video(avatar_id, audio_file, output_file, background_color, resolution, expressions)
            else:
                print(f"生成Synthesia視頻失敗: {response.status_code}, {response.text}")
                return self._generate_mock_video(avatar_id, audio_file, output_file, background_color, resolution, expressions)
        except Exception as e:
            print(f"生成Synthesia視頻時發生錯誤: {str(e)}")
            return self._generate_mock_video(avatar_id, audio_file, output_file, background_color, resolution, expressions)
    
    def _wait_for_synthesia_video(self, video_id: str, max_attempts: int = 30, delay: int = 10) -> Optional[str]:
        """
        等待Synthesia視頻生成完成
        
        Args:
            video_id: 視頻ID
            max_attempts: 最大嘗試次數
            delay: 每次嘗試間隔（秒）
            
        Returns:
            視頻URL或None（如果生成失敗）
        """
        url = f"{self.api_base_url}/videos/{video_id}"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        for attempt in range(max_attempts):
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                status = result.get("status")
                
                if status == "complete":
                    return result.get("download")
                elif status == "failed":
                    print(f"Synthesia視頻生成失敗: {result.get('error')}")
                    r<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>