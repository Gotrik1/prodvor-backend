
import fetch from 'node-fetch';
import { createUniqueUser, TokenResponse } from './helpers';

describe('Auth API', () => {
  const API_BASE_URL = 'http://localhost:8080';
  let accessToken: string;
  let refreshToken: string;
  let userEmail: string;
  let userNickname: string;

  jest.setTimeout(30000);

  beforeAll(async () => {
    const { user, headers, refreshToken: newRefreshToken } = await createUniqueUser('auth_test_user');
    accessToken = headers.Authorization.split(' ')[1];
    refreshToken = newRefreshToken;
    userEmail = user.email;
    userNickname = user.nickname;
  });

  test('POST /api/v1/auth/register - should fail on duplicate email', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        email: userEmail, 
        password: 'anotherpassword', 
        nickname: `another_${userNickname}` 
      }),
    });
    expect(response.status).toBe(400);
  });

  test('POST /api/v1/auth/refresh - should refresh the access token', async () => {
    expect(refreshToken).toBeDefined();

    const response = await fetch(`${API_BASE_URL}/api/v1/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    const body = await response.json() as TokenResponse;
    expect(response.status).toBe(200);
    expect(body.access_token).toBeDefined();
    expect(body.refresh_token).toBeDefined();
    expect(body.access_token).not.toBe(accessToken);
    
    accessToken = body.access_token;
    refreshToken = body.refresh_token;
  });

  test('POST /api/v1/auth/logout - should log out the user', async () => {
    expect(refreshToken).toBeDefined();

    const response = await fetch(`${API_BASE_URL}/api/v1/auth/logout`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }), 
    });
    
    expect(response.status).toBe(200);

    const refreshResponse = await fetch(`${API_BASE_URL}/api/v1/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
    });
    expect(refreshResponse.status).toBe(401);
  });
});
