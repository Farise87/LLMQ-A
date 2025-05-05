// 性能监控
window.addEventListener('load', () => {
    const timing = performance.timing;
    const loadTime = timing.loadEventEnd - timing.navigationStart;
    console.log(`页面加载时间: ${loadTime}ms`);

    // 可以发送到分析服务
    if (loadTime > 3000) {
        fetch('/analytics', {
            method: 'POST',
            body: JSON.stringify({
                event: 'performance_metric',
                loadTime: loadTime
            })
        });
    }
});

// 防抖函数
function debounce(func, wait) {
    let timeout;
    return function () {
        const context = this, args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            func.apply(context, args);
        }, wait);
    };
}

document.addEventListener('DOMContentLoaded', function () {
    // 显示骨架屏
    document.getElementById('skeleton-loading').style.display = 'block';

    const chatMessages = document.getElementById('chat-messages');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    const modelStatus = document.getElementById('model-status');
    const typingIndicator = document.getElementById('typing-indicator');
    const knowledgePanel = document.getElementById('knowledge-panel');
    const knowledgeContent = document.getElementById('knowledge-content');
    const closePanel = document.getElementById('close-panel');
    const skeletonLoading = document.getElementById('skeleton-loading');
    const historySidebar = document.getElementById('history-sidebar');
    const toggleSidebar = document.getElementById('toggle-sidebar');

    let isProcessing = false;
    let currentSessionId = null;
    let statusCheckInterval = null;

    // 自动调整文本框高度 - 添加防抖
    messageInput.addEventListener('input', debounce(function () {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    }, 150));

    // 检查模型状态
    checkModelStatus();

    // 定期检查模型状态
    setInterval(checkModelStatus, 5000);

    // 发送按钮点击事件
    sendButton.addEventListener('click', sendMessage);

    // 输入框回车事件（按Shift+Enter换行）
    messageInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // 停止按钮点击事件
    const stopButton = document.getElementById('stop-button');
    stopButton.addEventListener('click', cancelGeneration);

    // 关闭知识面板事件
    closePanel.addEventListener('click', function () {
        knowledgePanel.classList.remove('active');
    });

    // 侧边栏切换事件
    toggleSidebar.addEventListener('click', function () {
        historySidebar.classList.toggle('active');
        this.classList.toggle('active');
        const icon = this.querySelector('i');
        if (historySidebar.classList.contains('active')) {
            icon.classList.remove('fa-chevron-right');
            icon.classList.add('fa-chevron-left');
        } else {
            icon.classList.remove('fa-chevron-left');
            icon.classList.add('fa-chevron-right');
        }
    });

    // 知识面板交互观察
    const panelObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && knowledgeContent.textContent === '') {
                // 可以在这里加载更多知识内容
            }
        });
    }, {threshold: 0.1});

    panelObserver.observe(knowledgePanel);

    // 检查模型状态函数
    function checkModelStatus() {
        fetch('/api/model_status')
            .then(response => response.json())
            .then(data => {
                if (data.loaded) {
                    modelStatus.textContent = '模型已就绪';
                    modelStatus.className = 'status-indicator status-ready';
                    messageInput.disabled = false;
                    sendButton.disabled = false;
                    // 隐藏骨架屏
                    skeletonLoading.style.display = 'none';
                } else {
                    modelStatus.textContent = '模型加载失败';
                    modelStatus.className = 'status-indicator status-error';
                }
            })
            .catch(error => {
                console.error('检查模型状态出错:', error);
                modelStatus.textContent = '服务器连接错误';
                modelStatus.className = 'status-indicator status-error';
            });
    }

    // 发送消息函数
    function sendMessage() {
        const message = messageInput.value.trim();

        if (message && !isProcessing) {
            // 禁用输入和按钮
            isProcessing = true;
            messageInput.disabled = true;
            sendButton.disabled = true;

            // 使用DocumentFragment添加用户消息
            const fragment = document.createDocumentFragment();
            const wrapperElement = document.createElement('div');
            wrapperElement.classList.add('message-wrapper', 'user-message-wrapper');

            const containerElement = document.createElement('div');
            containerElement.classList.add('message-container');

            const avatarElement = document.createElement('div');
            avatarElement.classList.add('avatar', 'user-avatar');
            avatarElement.textContent = '你';

            const messageElement = document.createElement('div');
            messageElement.classList.add('message', 'user-message');
            messageElement.textContent = message;

            containerElement.appendChild(avatarElement);
            containerElement.appendChild(messageElement);
            wrapperElement.appendChild(containerElement);
            fragment.appendChild(wrapperElement);

            chatMessages.appendChild(fragment);

            // 清空输入框并重置高度
            messageInput.value = '';
            messageInput.style.height = 'auto';

            // 显示正在输入指示器和停止按钮
            typingIndicator.style.display = 'block';
            stopButton.style.display = 'flex';
            chatMessages.scrollTop = chatMessages.scrollHeight;

            // 使用requestAnimationFrame优化滚动
            requestAnimationFrame(() => {
                chatMessages.scrollTop = chatMessages.scrollHeight;
            });

            // 发送请求到后端
            fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({message: message})
            })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        // 处理错误
                        typingIndicator.style.display = 'none';
                        stopButton.style.display = 'none';
                        addMessage('抱歉，发生了错误: ' + data.error, 'ai');
                        resetUI();
                    } else if (data.session_id) {
                        // 保存会话ID并开始轮询状态
                        currentSessionId = data.session_id;
                        // 开始轮询生成状态
                        statusCheckInterval = setInterval(checkGenerationStatus, 1000);
                    }
                })
                .catch(error => {
                    console.error('发送消息出错:', error);
                    typingIndicator.style.display = 'none';
                    stopButton.style.display = 'none';
                    addMessage('抱歉，连接服务器时出错，请稍后再试。', 'ai');
                    resetUI();
                });
        }
    }

    // 检查生成状态
    function checkGenerationStatus() {
        if (!currentSessionId) return;

        fetch(`/api/generation_status?session_id=${currentSessionId}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    clearInterval(statusCheckInterval);
                    typingIndicator.style.display = 'none';
                    stopButton.style.display = 'none';
                    addMessage('抱歉，发生了错误: ' + data.error, 'ai');
                    resetUI();
                } else if (data.status === 'completed') {
                    // 生成完成
                    clearInterval(statusCheckInterval);
                    typingIndicator.style.display = 'none';
                    stopButton.style.display = 'none';

                    // 添加AI回复
                    addMessage(data.response, 'ai', data.knowledge_info ? true : false);

                    // 保存知识库信息
                    if (data.knowledge_info) {
                        knowledgeContent.textContent = data.knowledge_info;
                    }

                    resetUI();
                } else if (data.status === 'error') {
                    // 生成出错
                    clearInterval(statusCheckInterval);
                    typingIndicator.style.display = 'none';
                    stopButton.style.display = 'none';
                    addMessage('抱歉，生成回复时出错: ' + data.error, 'ai');
                    resetUI();
                } else if (data.status === 'cancelled') {
                    // 生成被取消
                    clearInterval(statusCheckInterval);
                    typingIndicator.style.display = 'none';
                    stopButton.style.display = 'none';
                    addMessage('生成已被用户取消', 'ai');
                    resetUI();
                }
                // 如果状态是running，继续轮询
            })
            .catch(error => {
                console.error('检查生成状态出错:', error);
                clearInterval(statusCheckInterval);
                typingIndicator.style.display = 'none';
                stopButton.style.display = 'none';
                addMessage('抱歉，检查生成状态时出错，请稍后再试。', 'ai');
                resetUI();
            });
    }

    // 取消生成
    function cancelGeneration() {
        if (!currentSessionId) return;

        fetch('/api/cancel_generation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({session_id: currentSessionId})
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error('取消生成出错:', data.error);
                }
                // 状态检查会处理UI更新
            })
            .catch(error => {
                console.error('取消生成出错:', error);
            });
    }

    // 重置UI状态
    function resetUI() {
        currentSessionId = null;
        isProcessing = false;
        messageInput.disabled = false;
        sendButton.disabled = false;
        messageInput.focus();
    }

    // 添加消息到聊天区域 - 优化版本
    function addMessage(text, sender, hasReferences = false) {
        // 使用DocumentFragment
        const fragment = document.createDocumentFragment();

        // 创建消息包装器
        const wrapperElement = document.createElement('div');
        wrapperElement.classList.add('message-wrapper');
        wrapperElement.classList.add(sender + '-message-wrapper');

        // 创建消息容器
        const containerElement = document.createElement('div');
        containerElement.classList.add('message-container');

        // 创建头像
        const avatarElement = document.createElement('div');
        avatarElement.classList.add('avatar');
        avatarElement.classList.add(sender + '-avatar');
        avatarElement.textContent = sender === 'user' ? '你' : 'AI';

        // 创建消息内容区域
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', sender + '-message');
        if (sender === 'ai') {
            messageElement.classList.add('markdown-body');
            messageElement.innerHTML = marked.parse(text);
        } else {
            messageElement.textContent = text;
        }

        // 如果是AI消息且有引用，添加查看引用按钮
        if (sender === 'ai' && hasReferences) {
            const referenceButton = document.createElement('button');
            referenceButton.classList.add('show-references');
            referenceButton.innerHTML = `
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 11C12.5523 11 13 11.4477 13 12C13 12.5523 12.5523 13 12 13C11.4477 13 11 12.5523 11 12C11 11.4477 11.4477 11 12 11Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M19 11C19.5523 11 20 11.4477 20 12C20 12.5523 19.5523 13 19 13C18.4477 13 18 12.5523 18 12C18 11.4477 18.4477 11 19 11Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M5 11C5.55228 11 6 11.4477 6 12C6 12.5523 5.55228 13 5 13C4.44772 13 4 12.5523 4 12C4 11.4477 4.44772 11 5 11Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                查看知识库引用
            `;
            referenceButton.title = '查看知识库引用';
            referenceButton.addEventListener('click', function () {
                knowledgePanel.classList.add('active');
            });

            messageElement.appendChild(document.createElement('br'));
            messageElement.appendChild(referenceButton);
        }

        // 组装消息
        containerElement.appendChild(avatarElement);
        containerElement.appendChild(messageElement);
        wrapperElement.appendChild(containerElement);
        fragment.appendChild(wrapperElement);

        // 添加到聊天区域
        chatMessages.appendChild(fragment);

        // 使用requestAnimationFrame优化滚动
        requestAnimationFrame(() => {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        });
    }
});






    document.addEventListener('DOMContentLoaded', function() {

        // 获取DOM元素

        const messageInput = document.getElementById('message-input');

        const sendButton = document.getElementById('send-button');

        const chatMessages = document.getElementById('chat-messages');

        const historyList = document.getElementById('history-list');

        const clearHistoryButton = document.getElementById('clear-history');



        // 从本地存储加载历史记录

        loadHistory();



        // 监听回车键发送消息

        messageInput.addEventListener('keypress', function(e) {

            if (e.key === 'Enter' && !e.shiftKey && messageInput.value.trim() !== '') {

                e.preventDefault();

                sendMessage();

            }

        });



        // 发送按钮点击事件

        sendButton.addEventListener('click', sendMessage);



        // 清空历史记录

        clearHistoryButton.addEventListener('click', function() {

            localStorage.removeItem('chatHistory');

            historyList.innerHTML = '';

        });



        // 发送消息函数

        function sendMessage() {

            const messageText = messageInput.value.trim();

            if (messageText === '') return;



            // 添加用户消息到聊天界面

            addMessageToChat('user', messageText);



            // 保存到历史记录

            saveToHistory(messageText);



            // 清空输入框

            messageInput.value = '';



            // 这里可以添加AI回复的逻辑

            // simulateAiResponse(messageText);

        }



        // 保存消息到历史记录

        function saveToHistory(message) {

            const historyItem = document.createElement('div');

            historyItem.className = 'history-item';

            historyItem.textContent = message;

            historyItem.addEventListener('click', function() {

                messageInput.value = message;

                messageInput.focus();

            });



            // 添加到历史记录列表的开头（最新消息在最上面）

            historyList.insertBefore(historyItem, historyList.firstChild);



            // 保存到本地存储

            saveHistoryToLocalStorage();

        }



        // 保存历史记录到本地存储

        function saveHistoryToLocalStorage() {

            const historyItems = Array.from(historyList.children).map(item => item.textContent);

            localStorage.setItem('chatHistory', JSON.stringify(historyItems));

        }



        // 从本地存储加载历史记录

        function loadHistory() {

            const savedHistory = localStorage.getItem('chatHistory');

            if (savedHistory) {

                const historyItems = JSON.parse(savedHistory);

                historyItems.forEach(itemText => {

                    const historyItem = document.createElement('div');

                    historyItem.className = 'history-item';

                    historyItem.textContent = itemText;

                    historyItem.addEventListener('click', function() {

                        messageInput.value = itemText;

                        messageInput.focus();

                    });

                    historyList.appendChild(historyItem);

                });

            }

        }



        // 添加消息到聊天界面

        function addMessageToChat(sender, text) {

            const messageDiv = document.createElement('div');

            messageDiv.className = `message ${sender}-message`;



            const avatar = document.createElement('div');

            avatar.className = `avatar ${sender}-avatar`;

            avatar.textContent = sender === 'user' ? '我' : 'AI';



            const content = document.createElement('div');

            content.className = 'message-content';

            content.textContent = text;



            messageDiv.appendChild(avatar);

            messageDiv.appendChild(content);

            chatMessages.appendChild(messageDiv);



            // 滚动到底部

            chatMessages.scrollTop = chatMessages.scrollHeight;

        }



        // 模拟AI响应（仅用于演示）

        function simulateAiResponse(userMessage) {

            setTimeout(() => {

                const aiResponse = `这是对"${userMessage}"的模拟AI回复。`;

                addMessageToChat('ai', aiResponse);

            }, 1000);

        }

    });