// Глобальная переменная для текущего пользователя
let currentUser = null;

// Функция для получения данных о текущем пользователе
async function fetchCurrentUser() {
    if (currentUser) {
        return currentUser; // Возвращаем уже загруженного пользователя
    }

    try {
        const response = await fetch('/users/me');
        if (!response.ok) {
            throw new Error('Failed to fetch current user');
        }
        currentUser = await response.json();
        console.log('Текущий пользователь:', currentUser);
        return currentUser;
    } catch (error) {
        console.error('Ошибка при получении данных текущего пользователя:', error);
        return null;
    }
}
