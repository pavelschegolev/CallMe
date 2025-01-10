// Функция для обновления шапки чата
async function updateChatHeader(chatId) {
    try {
        const response = await fetch(`/chats/${chatId}/`);
        if (!response.ok) {
            throw new Error(`Failed to fetch chat info: ${response.status}`);
        }

        const chatInfo = await response.json();

        // Обновляем название чата
        const chatTitleElement = document.getElementById('chat-title');
        if (chatTitleElement) {
            chatTitleElement.textContent = chatInfo._name || 'Unnamed Chat';
        }

        // Обновляем статус чата (например, Online/Offline или другая информация)
        const chatStatusElement = document.getElementById('chat-status');
        if (chatStatusElement) {
            chatStatusElement.textContent = chatInfo.status || 'Status Unknown';
        }

        console.log('Chat header updated successfully:', chatInfo);
    } catch (error) {
        console.error('Ошибка при обновлении шапки чата:', error);
    }
}

// Инициализация шапки чата
async function initializeChatHeader(chatId) {
    try {
        const response = await fetch(`/chats/${chatId}/`);
        if (!response.ok) {
            throw new Error(`Failed to fetch chat info: ${response.status}`);
        }

        const chatInfo = await response.json();

        document.getElementById('chat-title').textContent = chatInfo._name || 'Unnamed Chat';
        document.getElementById('chat-status').textContent = chatInfo.status || 'Offline';
    } catch (error) {
        console.error('Ошибка при обновлении шапки чата:', error);
    }
}