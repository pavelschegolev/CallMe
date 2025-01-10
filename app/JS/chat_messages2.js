let chatWebSocket; // Переменная для WebSocket соединения
let lastDate = null; // Глобальная переменная для отслеживания последней даты
let isManualDisconnect = false; // Флаг для отслеживания принудительного отключения
// Загрузка сообщений для выбранного чата
async function loadMessages(chatId) {
    try {
        await fetchCurrentUser(); // Загружаем данные текущего пользователя из current_user.js

        const response = await fetch(`/messages/chats/${chatId}/`);

        if (!response.ok) {
            throw new Error(`Failed to load messages: ${response.status}`);
        }

        const messages = await response.json();
        console.log('Полученные сообщения:', messages);

        const chatMessagesContainer = document.getElementById('chat-messages');

        if (!chatMessagesContainer) {
            console.error('Элемент с id "chat-messages" не найден.');
            return;
        }

        chatMessagesContainer.innerHTML = ''; // Очищаем контейнер сообщений

        lastDate = null; // Сбрасываем lastDate при загрузке сообщений

        // Изменяем вызов appendMessage в loadMessages
        messages.forEach(message => {
            lastDate = appendMessage(message, chatMessagesContainer, lastDate);
        });
    } catch (error) {
        console.error('Ошибка при загрузке сообщений:', error);
    }
}

// Функция для добавления сообщения в DOM
function appendMessage(message, container, lastDate) {
    const messageDate = new Date(message.created_at);
    const formattedDate = messageDate.toISOString().split('T')[0]; // Форматируем дату как YYYY-MM-DD

    // Если дата отличается от предыдущей, добавляем заголовок с датой
    if (formattedDate !== lastDate) {
        const dateElement = document.createElement('div');
        dateElement.className = 'message-date';
        dateElement.textContent = messageDate.toLocaleDateString(); // Отображаем в формате локали
        container.appendChild(dateElement);

        // Обновляем lastDate
        lastDate = formattedDate;
    }

    // Создание элемента сообщения
    const messageElement = document.createElement('div');
    messageElement.className = 'message-item';


    if (message.sender_id === currentUser.id) {
        // Сообщение отправлено текущим пользователем
        messageElement.classList.add('sent');
        messageElement.innerHTML = `
            <p>${message.content}</p>
            <span class="message-time">
                ${messageDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </span>
        `;
    } else {
        // Сообщение от другого пользователя
        messageElement.classList.add('received');
        messageElement.innerHTML = `
            <strong>${message.sender_username ?? 'Unknown'}</strong>
            <p>${message.content}</p>
            <span class="message-time">
                ${messageDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </span>
        `;
    }

    container.appendChild(messageElement);

    // Возвращаем обновлённое значение lastDate
    return lastDate;
}

// Установление WebSocket соединения
async function initializeWebSocket(chatId) {
    try {
        await fetchCurrentUser();

        if (!currentUser || !currentUser.id) {
            console.error("Текущий пользователь не найден.");
            return;
        }

        // Закрываем предыдущее соединение, если оно существует
        if (chatWebSocket) {
            if (chatWebSocket.readyState === WebSocket.OPEN || chatWebSocket.readyState === WebSocket.CONNECTING) {
                isManualDisconnect = true; // Устанавливаем флаг для ручного отключения
                chatWebSocket.onclose = null; // Удаляем предыдущий обработчик onclose
                chatWebSocket.close(); // Закрываем WebSocket
            }
        }

        // Создаём новое соединение
        chatWebSocket = new WebSocket(`ws://127.0.0.1:8000/messages/ws/${chatId}`);
        isManualDisconnect = false; // Сбрасываем флаг, так как соединение новое

        chatWebSocket.onopen = () => {
            console.log('WebSocket подключен.');

            // Отправляем событие "join_chat"
            const joinChatData = {
                event_type: "join_chat",
                chat_id: chatId,
            };
            chatWebSocket.send(JSON.stringify(joinChatData));
        };

        chatWebSocket.onmessage = (event) => {
            const receivedData = JSON.parse(event.data);
            console.log("Получено сообщение через WebSocket:", receivedData);

            const chatMessagesContainer = document.getElementById('chat-messages');
            if (receivedData.event_type === "chat_message" && chatMessagesContainer) {
                lastDate = appendMessage(receivedData, chatMessagesContainer, lastDate);
            } else if (receivedData.event_type === "chat_list") {
                console.log("Список чатов:", receivedData.chats);
            } else {
                console.error("Неизвестный тип события:", receivedData.event_type);
            }
        };

        chatWebSocket.onclose = () => {
            if (!isManualDisconnect) {
                console.log('WebSocket отключен. Пытаюсь переподключиться...');
                setTimeout(() => initializeWebSocket(chatId), 5000);
            } else {
                console.log('WebSocket отключен вручную.');
            }
        };

        chatWebSocket.onerror = (error) => {
            console.error('WebSocket ошибка:', error.message, error);
        };
    } catch (error) {
        console.error("Ошибка при инициализации WebSocket:", error);
    }
}

// Функция для отправки сообщения через WebSocket
function sendMessageWebSocket(chatId) {
    const inputField = document.querySelector(".chat-input input");
    const sendButton = document.querySelector(".send-btn");

    if (!inputField || !sendButton) {
        console.error("Элементы отправки сообщения не найдены.");
        return;
    }

    sendButton.addEventListener("click", () => {
        const messageContent = inputField.value.trim();

        if (!messageContent) return; // Не отправляем пустое сообщение

        const messageData = {
            event_type: "chat_message",
            chat_id: chatId,
            content: messageContent,
        };

        if (chatWebSocket && chatWebSocket.readyState === WebSocket.OPEN) {
            chatWebSocket.send(JSON.stringify(messageData));
            inputField.value = ""; // Очищаем поле ввода
        } else {
            console.error("WebSocket соединение недоступно для отправки сообщения.");
        }
    });
}

// Инициализация чата
async function initializeChat(chatId) {
    console.log(`Текущий пользователь:`, currentUser);
    console.log(`Выбран чат с ID: ${chatId}`);
    await loadMessages(chatId); // Загрузка сообщений
    await initializeWebSocket(chatId); // Установление WebSocket соединения
    sendMessageWebSocket(chatId); // Настройка отправки сообщений через WebSocket
}
