import fetch from 'cross-fetch';
import dotenv from 'dotenv';

dotenv.config();

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8080';

describe('LFG API', () => {
  let accessToken: string;
  let userId: string;

  beforeAll(async () => {
    // Create a user
    const email = `testuser_lfg_${Date.now()}@example.com`;
    const password = 'testpassword';
    await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, nickname: 'lfguser', first_name: 'Test', last_name: 'User' }),
    });

    const loginResponse = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: `username=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`,
    });
    const tokenData = await loginResponse.json();
    accessToken = tokenData.access_token;

    const meResponse = await fetch(`${API_BASE_URL}/api/v1/users/me`, {
      headers: { 'Authorization': `Bearer ${accessToken}` },
    });
    const meData = await meResponse.json();
    userId = meData.id;
  }, 90000);

  test('POST /api/v1/lfg - should create an LFG', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/lfg`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`,
      },
      body: JSON.stringify({ sport: 'Basketball', description: 'Looking for a 5v5 game', required_players: 10, creator_id: userId }),
    });
    expect(response.status).toBe(200);
    const body = await response.json();
    expect(body.sport).toBe('Basketball');
    expect(body.creator_id).toBe(userId);
  });

  test('GET /api/v1/lfg - should read LFGs', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/lfg`);
    expect(response.status).toBe(200);
    const body = await response.json();
    expect(Array.isArray(body)).toBe(true);
    expect(body.length).toBeGreaterThan(0);
  });
});
