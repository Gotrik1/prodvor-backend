import fetch from 'cross-fetch';
import dotenv from 'dotenv';

dotenv.config();

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8080';

describe('Playgrounds API', () => {
  let accessToken: string;

  beforeAll(async () => {
    // Create a user
    const email = `testuser_playgrounds_${Date.now()}@example.com`;
    const password = 'testpassword';
    await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, nickname: 'playgrounduser', first_name: 'Test', last_name: 'User' }),
    });

    const loginResponse = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: `username=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`,
    });
    const tokenData = await loginResponse.json();
    accessToken = tokenData.access_token;
  }, 90000);

  test('POST /api/v1/playgrounds - should create a playground', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/playgrounds`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`,
      },
      body: JSON.stringify({ name: 'Central Park Courts', location: 'New York, NY', sports: 'Basketball, Tennis' }),
    });
    expect(response.status).toBe(200);
    const body = await response.json();
    expect(body.name).toBe('Central Park Courts');
  });

  test('GET /api/v1/playgrounds - should read playgrounds', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/playgrounds`);
    expect(response.status).toBe(200);
    const body = await response.json();
    expect(Array.isArray(body)).toBe(true);
    expect(body.length).toBeGreaterThan(0);
  });
});
