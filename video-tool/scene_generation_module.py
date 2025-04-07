"""
場景生成和合成模塊 - 支持基於內容生成相關場景並與數字人視頻合成

此模塊提供以下功能：
1. 分析演講文本內容，識別關鍵主題和場景
2. 生成與內容相關的視覺場景
3. 將數字人視頻與場景視頻智能合成
4. 提供模擬模式用於開發和測試
"""

import os
import json
import time
import uuid
import requests
import re
import random
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from dotenv import load_dotenv

# 導入NLP工具
import nltk
import spacy
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer

# 導入視頻處理工具
import cv2
import numpy as np
from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips

# 加載環境變量
load_dotenv()

# 下載必要的NLTK數據
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

class SceneGenerationProvider(Enum):
    """場景生成服務提供商枚舉"""
    ZEBRACAT = "zebracat"
    RUNWAY = "runway"
    MOCK = "mock"  # 模擬模式

class ContentAnalyzer:
    """內容分析類，用於分析文本並提取關鍵主題和場景"""
    
    def __init__(self):
        """初始化內容分析類"""
        # 加載語言模型
        try:
            self.nlp_en = spacy.load("en_core_web_sm")
        except:
            # 如果模型不存在，下載並加載
            os.system("python3 -m spacy download en_core_web_sm")
            try:
                self.nlp_en = spacy.load("en_core_web_sm")
            except:
                # 如果仍然失敗，使用空白模型
                self.nlp_en = spacy.blank("en")
        
        try:
            self.nlp_zh = spacy.load("zh_core_web_sm")
        except:
            # 中文模型可能不存在，使用空白模型
            self.nlp_zh = spacy.blank("zh")
        
        # 初始化停用詞和詞形還原器
        self.stop_words_en = set(stopwords.words('english'))
        self.stop_words_zh = set(['的', '了', '和', '是', '在', '我', '有', '這', '個', '們', '中', '也', '為', '以', '到', '說', '著'])
        self.lemmatizer = WordNetLemmatizer()
        
        # 初始化TF-IDF向量化器
        self.vectorizer = TfidfVectorizer(max_features=100)
    
    def detect_language(self, text: str) -> str:
        """
        檢測文本語言
        
        Args:
            text: 輸入文本
            
        Returns:
            語言代碼 ('zh' 或 'en')
        """
        # 簡單的語言檢測：計算中文字符的比例
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        total_chars = len(text.strip())
        
        if total_chars == 0:
            return 'en'
        
        chinese_ratio = chinese_chars / total_chars
        
        if chinese_ratio > 0.1:  # 如果中文字符比例超過10%，認為是中文
            return 'zh'
        else:
            return 'en'
    
    def segment_text(self, text: str) -> List[str]:
        """
        將文本分割為段落
        
        Args:
            text: 輸入文本
            
        Returns:
            段落列表
        """
        # 按換行符分割
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        
        # 如果沒有段落或只有一個段落，嘗試按句子分割
        if len(paragraphs) <= 1 and len(text) > 200:
            language = self.detect_language(text)
            
            if language == 'zh':
                # 中文按標點符號分割
                sentences = re.split(r'[。！？]', text)
                paragraphs = [s.strip() + '。' for s in sentences if s.strip()]
            else:
                # 英文按句子分割
                sentences = sent_tokenize(text)
                
                # 將句子組合成適當大小的段落
                paragraphs = []
                current_paragraph = ""
                
                for sentence in sentences:
                    if len(current_paragraph) + len(sentence) < 200:
                        current_paragraph += " " + sentence if current_paragraph else sentence
                    else:
                        if current_paragraph:
                            paragraphs.append(current_paragraph)
                        current_paragraph = sentence
                
                if current_paragraph:
                    paragraphs.append(current_paragraph)
        
        return paragraphs
    
    def extract_keywords(self, text: str, top_n: int = 5) -> List[str]:
        """
        從文本中提取關鍵詞
        
        Args:
            text: 輸入文本
            top_n: 返回的關鍵詞數量
            
        Returns:
            關鍵詞列表
        """
        language = self.detect_language(text)
        
        if language == 'zh':
            # 中文文本處理
            doc = self.nlp_zh(text)
            # 過濾停用詞和標點符號
            tokens = [token.text for token in doc if not token.is_stop and not token.is_punct and len(token.text) > 1]
            # 計算詞頻
            word_freq = {}
            for token in tokens:
                if token in self.stop_words_zh:
                    continue
                word_freq[token] = word_freq.get(token, 0) + 1
        else:
            # 英文文本處理
            doc = self.nlp_en(text)
            # 過濾停用詞和標點符號，並進行詞形還原
            tokens = [self.lemmatizer.lemmatize(token.text.lower()) for token in doc 
                     if not token.is_stop and not token.is_punct and token.text.isalpha()]
            # 計算詞頻
            word_freq = {}
            for token in tokens:
                if token in self.stop_words_en:
                    continue
                word_freq[token] = word_freq.get(token, 0) + 1
        
        # 按詞頻排序並返回前N個關鍵詞
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        keywords = [word for word, freq in sorted_words[:top_n]]
        
        return keywords
    
    def extract_entities(self, text: str) -> List[str]:
        """
        從文本中提取命名實體
        
        Args:
            text: 輸入文本
            
        Returns:
            實體列表
        """
        language = self.detect_language(text)
        
        if language == 'zh':
            doc = self.nlp_zh(text)
        else:
            doc = self.nlp_en(text)
        
        # 提取命名實體
        entities = [ent.text for ent in doc.ents if ent.label_ in ['PERSON', 'ORG', 'GPE', 'LOC', 'PRODUCT']]
        
        return entities
    
    def analyze_content(self, text: str) -> List[Dict[str, Any]]:
        """
        分析文本內容，提取段落、關鍵詞和場景描述
        
        Args:
            text: 輸入文本
            
        Returns:
            分析結果列表，每個元素包含段落文本、關鍵詞和場景描述
        """
        # 分割文本為段落
        paragraphs = self.segment_text(text)
        
        # 分析每個段落
        results = []
        
        for paragraph in paragraphs:
            if not paragraph.strip():
                continue
            
            # 提取關鍵詞
            keywords = self.extract_keywords(paragraph, top_n=5)
            
            # 提取命名實體
            entities = self.extract_entities(paragraph)
            
            # 生成場景描述
            scene_description = self.generate_scene_description(paragraph, keywords, entities)
            
            # 添加到結果列表
            results.append({
                "paragraph": paragraph,
                "keywords": keywords,
                "entities": entities,
                "scene_description": scene_description
            })
        
        return results
    
    def generate_scene_description(self, text: str, keywords: List[str], entities: List[str]) -> str:
        """
        根據文本、關鍵詞和實體生成場景描述
        
        Args:
            text: 段落文本
            keywords: 關鍵詞列表
            entities: 實體列表
            
        Returns:
            場景描述
        """
        language = self.detect_language(text)
        
        # 組合關鍵詞和實體
        key_terms = list(set(keywords + entities))
        
        if language == 'zh':
            # 中文場景描述
            if key_terms:
                description = f"展示與{', '.join(key_terms[:3])}相關的場景"
            else:
                # 如果沒有關鍵詞和實體，使用文本的前20個字符
                preview = text[:20] + "..." if len(text) > 20 else text
                description = f"展示與「{preview}」相關的場景"
        else:
            # 英文場景描述
            if key_terms:
                description = f"Scene related to {', '.join(key_terms[:3])}"
            else:
                # 如果沒有關鍵詞和實體，使用文本的前30個字符
                preview = text[:30] + "..." if len(text) > 30 else text
                description = f"Scene related to \"{preview}\""
        
        return description

class SceneGenerator:
    """場景生成類，用於生成與內容相關的視覺場景"""
    
    def __init__(self, provider: SceneGenerationProvider = SceneGenerationProvider.MOCK):
        """
        初始化場景生成類
        
        Args:
            provider: 場景生成服務提供商，默認為模擬模式
        """
        self.provider = provider
        
        # 初始化Zebracat配置
        if provider == SceneGenerationProvider.ZEBRACAT:
            self.api_key = os.getenv("ZEBRACAT_API_KEY")
            
            if not self.api_key:
                print("警告: 未設置ZEBRACAT_API_KEY環境變量，將使用模擬模式")
                self.provider = SceneGenerationProvider.MOCK
            
            self.api_base_url = "https://api.zebracat.ai/v1"
        
        # 初始化Runway配置
        elif provider == SceneGenerationProvider.RUNWAY:
            self.api_key = os.getenv("RUNWAY_API_KEY")
            
            if not self.api_key:
                print("警告: 未設置RUNWAY_API_KEY環境變量，將使用模擬模式")
                self.provider = SceneGenerationProvider.MOCK
            
            self.api_base_url = "https://api.runwayml.com/v1"
    
    def generate_scene(
        self, 
        prompt: str, 
        output_file: str,
        style: str = "realistic",
        duration: int = 5,
        resolution: str = "1080p"
    ) -> str:
        """
        生成場景視頻
        
        Args:
            prompt: 場景描述
            output_file: 輸出文件路徑
            style: 視覺風格
            duration: 視頻時長（秒）
            resolution: 視頻分辨率
            
        Returns:
            輸出文件路徑
        """
        if self.provider == SceneGenerationProvider.ZEBRACAT:
            return self._generate_zebracat_scene(prompt, output_file, style, duration, resolution)
        elif self.provider == SceneGenerationProvider.RUNWAY:
            return self._generate_runway_scene(prompt, output_file, style, duration, resolution)
        else:
            return self._generate_mock_scene(prompt, output_file, style, duration, resolution)
    
    def _generate_zebracat_scene(
        self, 
        prompt: str, 
        output_file: str,
        style: str = "realistic",
        duration: int = 5,
        resolution: str = "1080p"
    ) -> str:
        """
        使用Zebracat生成場景視頻
        
        Args:
            prompt: 場景描述
            output_file: 輸出文件路徑
            style: 視覺風格
            duration: 視頻時長（秒）
            resolution: 視頻分辨率
            
        Returns:
            輸出文件路徑
        """
        try:
            url = f"{self.api_base_url}/scenes"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 解析分辨率
            if resolution == "1080p":
                width, height = 1920, 1080
            elif resolution == "720p":
                width, height = 1280, 720
            else:
                width, height = 1280, 720
            
            # 準備請求數據
            data = {
                "prompt": prompt,
                "style": style,
                "duration": duration,
                "resolution": {
                    "width": width,
                    "height": height
                },
                "format": "mp4"
            }
            
            # 發送請求
            response = requests.post(url, headers=headers, data=json.dumps(data))
            
            if response.status_code == 200:
                result = response.json()
                scene_url = result.get("url")
                
                # 下載視頻
                self._download_file(scene_url, output_file)
                
                return output_file
            else:
                print(f"生成Zebracat場景失敗: {response.status_code}, {response.text}")
                return self._generate_mock_scene(prompt, output_file, style, duration, resolution)
        except Exception as e:
            print(f"生成Zebracat場景時發生錯誤: {str(e)}")
            return self._generate_mock_scene(prompt, output_file, style, duration, resolution)
    
    def _generate_runway_scene(
        self, 
        prompt: str, 
        output_file: str,
        style: str = "realistic",
        duration: int = 5,
        resolution: str = "1080p"
    ) -> str:
        """
        使用Runway生成場景視頻
        
        Args:
            prompt: 場景描述
            output_file: 輸出文件路徑
            style: 視覺風格
            duration: 視頻時長（秒）
            resolution: 視頻分辨率
            
        Returns:
            輸出文件路徑
        """
        try:
            url = f"{self.api_base_url}/text-to-video"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 準備請求數據
            data = {
                "prompt": prompt,
                "num_frames": duration * 30,  # 假設30fps
                "style_preset": style
            }
            
            # 發送請求
            response = requests.post(url, headers=headers, data=json.dumps(data))
            
            if response.status_code == 200:
                result = response.json()
                video_url = result.get("output")
                
                # 下載視頻
                self._download_file(video_url, output_file)
                
                return output_file
            else:
                print(f"生成Runway場景失敗: {response.status_code}, {response.text}")
                return self._generate_mock_scene(prompt, output_file, style, duration, resolution)
        except Exception as e:
            print(f"生成Runway場景時發生錯誤: {str(e)}")
            return self._generate_mock_scene(prompt, output_file, style, duration, resolution)
    
    def _download_file(self, url: str, output_file: str) -> None:
        """
        下載文件
        
        Args:
            url: 文件URL
            output_file: 輸出文件路徑
        """
        try:
            # 確保輸出目錄存在
            os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
            
            # 下載文件
            response = requests.get(url, stream=True)
            
            if response.status_code == 200:
                with open(output_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
            else:
                print(f"下載文件失敗: {response.status_code}")
                # 創建一個空文件
                with open(output_file, "wb") as f:
                    f.write(b"")
        except Exception as e:
            print(f"下載文件時發生錯誤: {str(e)}")
            # 創建一個空文件
            with open(output_file, "wb") as f:
                f.write(b"")
    
    def _generate_mock_scene(
        self, 
        prompt: str, 
        output_file: str,
        style: str = "realistic",
        duration: int = 5,
        resolution: str = "1080p"
    ) -> str:
        """
        生成模擬的場景視頻
        
        Args:
            prompt: 場景描述
            output_file: 輸出文件路徑
            style: 視覺風格
            duration: 視頻時長（秒）
            resolution: 視頻分辨率
            
        Returns:
            輸出文件路徑
        """
        try:
            print(f"生成模擬場景視頻: {prompt}")
            print(f"輸出文件: {output_file}")
            print(f"風格: {style}")
            print(f"時長: {duration}秒")
            print(f"分辨率: {resolution}")
            
            # 解析分辨率
            if resolution == "1080p":
                width, height = 1920, 1080
            elif resolution == "720p":
                width, height = 1280, 720
            elif resolution == "480p":
                width, height = 854, 480
            else:
                width, height = 1280, 720
            
            # 確保輸出<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>