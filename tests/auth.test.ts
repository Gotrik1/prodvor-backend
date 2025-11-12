import fetch from 'cross-fetch';
import dotenv from 'dotenv';

dotenv.config();

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8080';

describe('Auth API', () => {
  let accessToken: string;
  let refreshToken: string; 
  const email = `testuser_auth_${Date.now()}@example.com`;
  const password = 'testpassword';

  test('POST /api/v1/auth/register - should register a new user', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        email,
        password,
        nickname: 'authtester',
        first_name: 'Auth',
        last_name: 'Tester',
      }),
    });
    const body = await response.json();
    expect(response.status).toBe(200);
    expect(body.email).toBe(email);
  });

  test('POST /api/v1/auth/login - should log in and return tokens', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: `username=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`,
    });
    const body = await response.json();
    expect(response.status).toBe(200);
    expect(body.access_token).toBeDefined();
    expect(body.refresh_token).toBeDefined();
    accessToken = body.access_token;
    refreshToken = body.refresh_token;
  });

  test('POST /api/v1/auth/refresh - should refresh the access token', async () => {
    expect(refreshToken).toBeDefined(); // Ensure login test ran
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/refresh`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${refreshToken}`
      },
    });
    const body = await response.json();
    expect(response.status).toBe(200);
    expect(body.access_token).toBeDefined();
    expect(body.access_token).not.toBe(accessToken); // Should be a new token
    accessToken = body.access_token; // Update access token for next tests
  });

  test('POST /api/v1/auth/logout - should log out the user', async () => {
    expect(accessToken).toBeDefined();
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/logout`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`
      },
    });
    expect(response.status).toBe(200);

    // Verify logout by trying to access a protected route
    const meResponse = await fetch(`${API_BASE_URL}/api/v1/users/me`, {
      headers: { 'Authorization': `Bearer ${accessToken}` }
    });
    expect(meResponse.status).toBe(401); // Expect Unauthorized
  });
});
