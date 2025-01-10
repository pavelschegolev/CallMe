
// ✅ Загрузка списка чатов
async function loadChatList() {
    try {
        await fetchCurrentUser(); // Убедимся, что currentUser загружен

        const chatsResponse = await fetch('/chats/user_chats');
        if (!chatsResponse.ok) {
            throw new Error(`HTTP error! Status: ${chatsResponse.status}`);
        }

        const chatsData = await chatsResponse.json();
        const chatListContainer = document.getElementById('chat-list');

        if (!chatListContainer) {
            console.error('Элемент с id "chat-list" не найден.');
            return;
        }

        chatListContainer.innerHTML = ''; // Очищаем список чатов

        if (chatsData.chats.length === 0) {
            chatListContainer.innerHTML = '<p class="no-chats">No chats available</p>';
            return;
        }

        chatsData.chats.forEach(chatItemData => {
            const chatListItem = document.createElement('div');
            chatListItem.classList.add('chat-list-item'); // Используем твой стиль
            chatListItem.dataset.chatId = chatItemData.id;

            let chatFormattedTime = '';
            if (chatItemData.last_message_time) {
                const messageDateTime = new Date(chatItemData.last_message_time);
                const currentDate = new Date();

                if (messageDateTime.toDateString() === currentDate.toDateString()) {
                    chatFormattedTime = messageDateTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                } else {
                    chatFormattedTime = messageDateTime.toLocaleDateString('en-GB');
                }
            }

            chatListItem.innerHTML = `
                <div class="chat-item-header">
                    <h3 class="chat-item-title">${chatItemData.name}</h3>
                    <span class="chat-item-time">${chatFormattedTime}</span>
                </div>
                <p class="chat-item-last-message">
                    <strong>${chatItemData.last_sender || 'Unknown'}</strong>: ${chatItemData.last_message || 'No messages yet'}
                </p>
            `;

            chatListContainer.appendChild(chatListItem);
        });
    } catch (fetchChatsError) {
        console.error('Ошибка при получении чатов:', fetchChatsError);
    }
}

// ✅ Делегирование кликов на родительский элемент
function setupChatListEventHandlers() {
    const chatListContainer = document.getElementById('chat-list');
    if (!chatListContainer) {
        console.error('Элемент с id "chat-list" не найден.');
        return;
    }

    chatListContainer.addEventListener('click', (event) => {
        const chatItem = event.target.closest('.chat-list-item');
        if (chatItem) {
            const chatId = chatItem.dataset.chatId;
            if (chatId) {
                console.log(`Выбран чат с ID: ${chatId}`);
                window.currentChatId = chatId; // Сохраняем chatId в глобальную переменную
                initializeChat(chatId); // Загружаем сообщения
                initializeChatHeader(chatId); // Обновляем шапку чата
            }
        }
    });
}

// ✅ Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', async () => {
    await loadChatList(); // Загружаем список чатов
    setupChatListEventHandlers(); // Настраиваем делегирование событий
});
