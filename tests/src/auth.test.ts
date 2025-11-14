
import fetch from 'node-fetch';

// --- Типы для ответов API ---
declare type TokenResponse = {
  access_token: string;
  refresh_token: string;
  token_type: string;
};

declare type UserResponse = {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
};


describe('Auth API', () => {
  const API_BASE_URL = 'http://localhost:8080';
  let accessToken: string;
  let refreshToken: string;

  // Увеличим тайм-аут для тестов, чтобы сервер успел запуститься
  jest.setTimeout(30000); 

  // --- 1. Регистрация --- 
  test('POST /api/v1/auth/register - should register a new user', async () => {
    const email = `testuser_${Date.now()}@example.com`;
    const password = 'strongpassword';

    const response = await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, first_name: 'Test', last_name: 'User' }),
    });

    const body = await response.json() as UserResponse;
    expect(response.status).toBe(200);
    expect(body.email).toBe(email);
  });

  // --- 2. Логин --- 
  test('POST /api/v1/auth/login - should log in and return tokens', async () => {
    const email = `testuser_${Date.now()}@example.com`;
    const password = 'strongpassword';

    // Сначала регистрируем пользователя
    await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, first_name: 'Test', last_name: 'User' }),
    });

    // Затем логинимся
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: `username=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`,
    });

    const body = await response.json() as TokenResponse;
    expect(response.status).toBe(200);
    expect(body.access_token).toBeDefined();
    expect(body.refresh_token).toBeDefined();

    // Сохраняем токены для следующих тестов
    accessToken = body.access_token;
    refreshToken = body.refresh_token;
  });

  // --- 3. Refresh --- 
  test('POST /api/v1/auth/refresh - should refresh the access token', async () => {
    expect(refreshToken).toBeDefined(); // Убедимся, что тест на логин выполнился

    const response = await fetch(`${API_BASE_URL}/api/v1/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    const body = await response.json() as TokenResponse;
    expect(response.status).toBe(200);
    expect(body.access_token).toBeDefined();
    expect(body.refresh_token).toBeDefined();
    expect(body.access_token).not.toBe(accessToken); // Токен должен быть новым
    expect(body.refresh_token).not.toBe(refreshToken); // Refresh-токен тоже должен быть новым

    // Обновляем токены для следующего теста
    accessToken = body.access_token;
    refreshToken = body.refresh_token;
  });

  // --- 4. Logout --- 
  test('POST /api/v1/auth/logout - should log out the user', async () => {
    expect(refreshToken).toBeDefined(); // Убедимся, что предыдущие тесты выполнились

    const response = await fetch(`${API_BASE_URL}/api/v1/auth/logout`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }), 
    });
    
    expect(response.status).toBe(200);

    // Проверяем, что сессия была удалена, пытаясь использовать старый refresh-токен
    const refreshResponse = await fetch(`${API_BASE_URL}/api/v1/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
    });
    expect(refreshResponse.status).toBe(404); // Ожидаем "Session not found"
  });
});
