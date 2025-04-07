// 全局變量
let fileId = null;
let fileExt = null;
let selectedAvatarId = null;

// 頁面加載完成後執行
document.addEventListener('DOMContentLoaded', function() {
    // 檢查服務狀態
    checkServiceStatus();
    
    // 初始化事件監聽器
    initEventListeners();
    
    // 加載語音和頭像選項
    loadVoices();
    loadAvatars();
});

// 檢查服務狀態
function checkServiceStatus() {
    fetch('/api/health')
        .then(response => response.json())
        .then(data => {
            const statusAlert = document.getElementById('status-alert');
            
            if (data.status === 'ok') {
                statusAlert.className = 'alert alert-success';
                statusAlert.textContent = '所有服務正常運行';
                
                // 3秒後隱藏狀態提示
                setTimeout(() => {
                    statusAlert.style.display = 'none';
                }, 3000);
            } else {
                statusAlert.className = 'alert alert-warning';
                statusAlert.textContent = '部分服務可能不可用，請檢查服務狀態';
                
                // 顯示詳細服務狀態
                let serviceStatus = '';
                for (const [service, status] of Object.entries(data.services)) {
                    serviceStatus += `${service}: ${status === 'ok' ? '正常' : '異常'}\n`;
                }
                
                console.log('服務狀態詳情:', serviceStatus);
            }
        })
        .catch(error => {
            console.error('檢查服務狀態時出錯:', error);
            
            const statusAlert = document.getElementById('status-alert');
            statusAlert.className = 'alert alert-danger';
            statusAlert.textContent = '無法連接到服務，請確保服務已啟動';
            
            // 添加啟動服務按鈕
            statusAlert.innerHTML += '<br><button class="btn btn-primary btn-sm mt-2" id="start-services-btn">啟動服務</button>';
            
            document.getElementById('start-services-btn').addEventListener('click', function() {
                startServices();
            });
        });
}

// 啟動服務
function startServices() {
    const statusAlert = document.getElementById('status-alert');
    statusAlert.className = 'alert alert-info';
    statusAlert.textContent = '正在啟動服務，請稍候...';
    
    fetch('/api/start_services', {
        method: 'POST'
    })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                statusAlert.className = 'alert alert-success';
                statusAlert.textContent = data.message + '，正在檢查服務狀態...';
                
                // 等待服務啟動
                setTimeout(() => {
                    checkServiceStatus();
                }, 5000);
            } else {
                statusAlert.className = 'alert alert-danger';
                statusAlert.textContent = '啟動服務失敗: ' + (data.error || '未知錯誤');
            }
        })
        .catch(error => {
            console.error('啟動服務時出錯:', error);
            statusAlert.className = 'alert alert-danger';
            statusAlert.textContent = '啟動服務時出錯，請查看控制台獲取詳細信息';
        });
}

// 初始化事件監聽器
function initEventListeners() {
    // 輸入類型切換
    document.getElementById('input-type').addEventListener('change', function() {
        const textContainer = document.getElementById('text-input-container');
        const fileContainer = document.getElementById('file-input-container');
        
        if (this.value === 'text') {
            textContainer.classList.remove('d-none');
            fileContainer.classList.add('d-none');
        } else {
            textContainer.classList.add('d-none');
            fileContainer.classList.remove('d-none');
        }
    });
    
    // 文件上傳
    document.getElementById('file-input').addEventListener('change', function(e) {
        if (this.files.length > 0) {
            const file = this.files[0];
            const formData = new FormData();
            formData.append('file', file);
            
            // 顯示上傳中提示
            const fileContainer = document.getElementById('file-input-container');
            fileContainer.innerHTML += '<div class="mt-2" id="upload-status">正在上傳文件，請稍候...</div>';
            
            fetch('/api/upload', {
                method: 'POST',
                body: formData
            })
                .then(response => response.json())
                .then(data => {
                    if (data.file_id) {
                        fileId = data.file_id;
                        fileExt = data.file_ext;
                        
                        // 如果是文本文件，顯示提取的文本
                        if (data.text) {
                            document.getElementById('text-input').value = data.text;
                            document.getElementById('input-type').value = 'text';
                            document.getElementById('text-input-container').classList.remove('d-none');
                            document.getElementById('file-input-container').classList.add('d-none');
                        }
                        
                        // 更新上傳狀態
                        document.getElementById('upload-status').innerHTML = 
                            '<div class="alert alert-success">文件上傳成功</div>';
                    } else {
                        document.getElementById('upload-status').innerHTML = 
                            '<div class="alert alert-danger">文件上傳失敗: ' + (data.error || '未知錯誤') + '</div>';
                    }
                })
                .catch(error => {
                    console.error('上傳文件時出錯:', error);
                    document.getElementById('upload-status').innerHTML = 
                        '<div class="alert alert-danger">上傳文件時出錯，請查看控制台獲取詳細信息</div>';
                });
        }
    });
    
    // 語言和性別選擇變更時重新加載聲線和頭像
    document.getElementById('language-select').addEventListener('change', function() {
        loadVoices();
        loadAvatars();
    });
    
    document.getElementById('gender-select').addEventListener('change', function() {
        loadVoices();
        loadAvatars();
    });
    
    // 標籤頁導航按鈕
    document.getElementById('next-to-settings').addEventListener('click', function() {
        // 驗證輸入
        const inputType = document.getElementById('input-type').value;
        let isValid = true;
        
        if (inputType === 'text') {
            const text = document.getElementById('text-input').value.trim();
            if (!text) {
                alert('請輸入演講文本');
                isValid = false;
            }
        } else {
            if (!fileId) {
                alert('請上傳文件');
                isValid = false;
            }
        }
        
        if (isValid) {
            // 切換到設置標籤頁
            const settingsTab = new bootstrap.Tab(document.getElementById('settings-tab'));
            settingsTab.show();
        }
    });
    
    document.getElementById('back-to-input').addEventListener('click', function() {
        const inputTab = new bootstrap.Tab(document.getElementById('input-tab'));
        inputTab.show();
    });
    
    document.getElementById('back-to-settings').addEventListener('click', function() {
        const settingsTab = new bootstrap.Tab(document.getElementById('settings-tab'));
        settingsTab.show();
    });
    
    // 生成視頻按鈕
    document.getElementById('generate-button').addEventListener('click', function() {
        // 驗證設置
        const voiceId = document.getElementById('voice-select').value;
        
        if (!voiceId) {
            alert('請選擇聲線');
            return;
        }
        
        if (!selectedAvatarId) {
            alert('請選擇數字人頭像');
            return;
        }
        
        // 切換到預覽標籤頁
        const previewTab = new bootstrap.Tab(document.getElementById('preview-tab'));
        previewTab.show();
        
        // 顯示進度條
        const progressContainer = document.getElementById('generation-progress');
        progressContainer.classList.remove('d-none');
        
        // 隱藏視頻和下載容器
        document.getElementById('video-container').classList.add('d-none');
        document.getElementById('download-container').classList.add('d-none');
        
        // 準備請求數據
        const inputType = document.getElementById('input-type').value;
        const language = document.getElementById('language-select').value;
        const gender = document.getElementById('gender-select').value;
        const videoMode = document.getElementById('video-mode').value;
        
        let requestData = {
            language: language,
            gender: gender,
            voice_id: voiceId,
            avatar_id: selectedAvatarId,
            video_mode: videoMode
        };
        
        if (inputType === 'text') {
            requestData.text = document.getElementById('text-input').value.trim();
        } else {
            requestData.file_id = fileId;
            requestData.file_ext = fileExt;
        }
        
        // 更新進度
        updateProgress(10, '正在處理請求...');
        
        // 發送生成請求
        fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        })
            .then(response => response.json())
            .then(data => {
                if (data.final_video_id) {
                    // 更新進度
                    updateProgress(100, '視頻生成完成！');
                    
                    // 顯示視頻
                    const videoContainer = document.getElementById('video-container');
                    videoContainer.classList.remove('d-none');
                    
                    const previewVideo = document.getElementById('preview-video');
                    previewVideo.src = data.preview_url;
                    previewVideo.load();
                    
                    // 顯示下載按鈕
                    const downloadContainer = document.getElementById('download-container');
                    downloadContainer.classList.remove('d-none');
                    
                    const downloadLink = document.getElementById('download-link');
                    downloadLink.href = data.download_url;
                    
                    // 隱藏進度條
                    setTimeout(() => {
                        progressContainer.classList.add('d-none');
                    }, 1000);
                } else {
                    updateProgress(0, '視頻生成失敗: ' + (data.error || '未知錯誤'));
                }
            })
            .catch(error => {
                console.error('生成視頻時出錯:', error);
                updateProgress(0, '生成視頻時出錯，請查看控制台獲取詳細信息');
            });
    });
    
    // 創建新視頻按鈕
    document.getElementById('new-video').addEventListener('click', function() {
        // 重置表單
        document.getElementById('text-input').value = '';
        document.getElementById('file-input').value = '';
        fileId = null;
        fileExt = null;
        selectedAvatarId = null;
        
        // 重置頭像選擇
        const avatarCards = document.querySelectorAll('.avatar-card');
        avatarCards.forEach(card => {
            card.classList.remove('selected');
        });
        
        // 切換到輸入標籤頁
        const inputTab = new bootstrap.Tab(document.getElementById('input-tab'));
        inputTab.show();
    });
}

// 加載聲線選項
function loadVoices() {
    const language = document.getElementById('language-select').value;
    const gender = document.getElementById('gender-select').value;
    const voiceSelect = document.getElementById('voice-select');
    
    // 清空現有選項
    voiceSelect.innerHTML = '<option value="" selected disabled>載入中...</option>';
    
    fetch(`/api/voices?language=${language}&gender=${gender}`)
        .then(response => response.json())
        .then(data => {
            voiceSelect.innerHTML = '';
            
            if (data.voices && data.voices.length > 0) {
                data.voices.forEach(voice => {
                    const option = document.createElement('option');
                    option.value = voice.id;
                    option.textContent = voice.name;
                    voiceSelect.appendChild(option);
                });
            } else {
                const option = document.createElement('option');
                option.value = '';
                option.textContent = '沒有可用的聲線';
                option.disabled = true;
                option.selected = true;
                voiceSelect.appendChild(option);
            }
        })
        .catch(error => {
            console.error('加載聲線時出錯:', error);
            voiceSelect.innerHTML = '<option value="" selected disabled>加載失敗</option>';
        });
}

// 加載頭像選項
function loadAvatars() {
    const language = document.getElementById('language-select').value;
    const gender = document.getElementById('gender-select').value;
    const avatarContainer = document.getElementById('avatar-container');
    
    // 清空現有選項
    avatarContainer.innerHTML = '<div class="text-center">載入中...</div>';
    
    fetch(`/api/avatars?language=${language}&gender=${gender}`)
        .then(response => response.json())
        .then(data => {
            avatarContainer.innerHTML = '';
            
            if (data.avatars && data.avatars.length > 0) {
                data.avatars.forEach(avatar => {
                    const col = document.createElement('div');
                    col.className = 'col-md-3 col-sm-6';
                    
                    const card = document.createElement('div');
                    card.className = 'avatar-card';
                    card.dataset.avatarId = avatar.id;
                    
                    // 頭像點擊事件
                    card.addEventListener('click', function() {
                        // 移除其他頭像的選中狀態
                        document.querySelectorAll('.avatar-card').forEach(c => {
                            c.classList.remove('selected');
                        });
                        
                        // 選中當前頭像
                        this.classList.add('selected');
                        selectedAvatarId = this.dataset.avatarId;
                    });
                    
                    // 頭像圖片
                    const img = document.createElement('img');
                    img.src = avatar.preview_url;
                    img.alt = avatar.name;
                    img.className = 'card-img-top';
                    
                    // 頭像名稱
                    const cardBody = document.createElement('div');
                    cardBody.className = 'card-body';
                    
                    const cardTitle = document.createElement('h5');
                    cardTitle.className = 'card-title';
                    cardTitle.textContent = avatar.name;
                    
                    cardBody.appendChild(cardTitle);
                    card.appendChild(img);
                    card.appendChild(cardBody);
                    col.appendChild(card);
                    avatarContainer.appendChild(col);
                });
            } else {
                avatarContainer.innerHTML = '<div class="text-center">沒有可用的頭像</div>';
            }
        })
        .catch(error => {
            console.error('加載頭像時出錯:', error);
            avatarContainer.innerHTML = '<div class="text-center text-danger">加載頭像失敗</div>';
        });
}

// 更新進度條
function updateProgress(percent, text) {
    const progressBar = document.querySelector('.progress-bar');
    const progressText = document.getElementById('progress-text');
    
    progressBar.style.width = percent + '%';
    progressText.textContent = text;
    
    if (percent === 0) {
        progressBar.className = 'progress-bar progress-bar-striped bg-danger';
    } else if (percent === 100) {
        progressBar.className = 'progress-bar progress-bar-striped bg-success';
    } else {
        progressBar.className = 'progress-bar progress-bar-striped progress-bar-animated';
    }
}
