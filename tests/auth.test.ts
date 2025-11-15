// tests/auth.test.ts
import { test, expect, describe } from '@jest/globals'; // ИЗМЕНЕНО

const API_BASE_URL = process.env.API_BASE_URL || 'http://127.0.0.1:8080';

describe('Auth API - New Flow', () => {
    let accessToken = '';
    let refreshToken = '';
    const userEmail = `testuser_${Date.now()}@example.com`;
    const userPassword = 'strongpassword';

    test('POST /api/v1/auth/register - should register a new user successfully', async () => {
        const response = await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email: userEmail,
                password: userPassword,
                nickname: 'testuser',
            }),
        });
        expect(response.status).toBe(200);
        const body = await response.json();
        expect(body.email).toBe(userEmail);
    });

    test('POST /api/v1/auth/login - should log in and return access and refresh tokens', async () => {
        const formData = new URLSearchParams();
        formData.append('username', userEmail);
        formData.append('password', userPassword);

        const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData.toString(),
        });

        expect(response.status).toBe(200);
        const body = await response.json();
        expect(body.access_token).toBeDefined();
        expect(body.refresh_token).toBeDefined();
        expect(body.token_type).toBe('bearer');

        accessToken = body.access_token;
        refreshToken = body.refresh_token;
    });
    
    test('GET /api/v1/users/me - should be accessible with the new access token', async () => {
        const response = await fetch(`${API_BASE_URL}/api/v1/users/me`, {
            headers: { Authorization: `Bearer ${accessToken}` },
        });
        expect(response.status).toBe(200);
        const body = await response.json();
        expect(body.email).toBe(userEmail);
    });

    test('POST /api/v1/auth/refresh - should refresh the tokens using the refresh token', async () => {
        const oldRefreshToken = refreshToken;
        const response = await fetch(`${API_BASE_URL}/api/v1/auth/refresh`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: oldRefreshToken }),
        });

        expect(response.status).toBe(200);
        const body = await response.json();
        expect(body.access_token).toBeDefined();
        expect(body.refresh_token).toBeDefined();
        expect(body.access_token).not.toBe(accessToken); // Токены должны быть новыми
        expect(body.refresh_token).not.toBe(oldRefreshToken);

        // Сохраняем новые токены для следующих тестов
        accessToken = body.access_token;
        refreshToken = body.refresh_token;

        // Проверяем, что старый refresh-токен больше не работает (ротация)
        const secondRefreshResponse = await fetch(`${API_BASE_URL}/api/v1/auth/refresh`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: oldRefreshToken }),
        });
        expect(secondRefreshResponse.status).toBe(401);
    });
    
    test('POST /api/v1/auth/logout - should log out the user by revoking the refresh token', async () => {
        const response = await fetch(`${API_BASE_URL}/api/v1/auth/logout`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: refreshToken }),
        });
        expect(response.status).toBe(200);
        const body = await response.json();
        expect(body.msg).toBe('Successfully logged out');

        // Проверяем, что отозванный refresh-токен больше не работает
        const refreshAfterLogoutResponse = await fetch(`${API_BASE_URL}/api/v1/auth/refresh`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: refreshToken }),
        });
        expect(refreshAfterLogoutResponse.status).toBe(401);
        
        // При этом старый access-токен все еще может быть валидным до истечения своего срока
        // Это ожидаемое поведение для stateless-токенов
        const meResponse = await fetch(`${API_BASE_URL}/api/v1/users/me`, {
            headers: { Authorization: `Bearer ${accessToken}` },
        });
        expect(meResponse.status).toBe(200);
    });
});
