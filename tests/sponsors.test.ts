import fetch from 'cross-fetch';
import dotenv from 'dotenv';

dotenv.config();

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8080';

// Helper functions (previously in helpers.ts)
async function registerAndLogin(email = `testuser_sponsors_${Date.now()}@example.com`, password = 'testpassword') {
  await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, nickname: 'sponsorstester', first_name: 'Sponsor', last_name: 'Tester' }),
  });

  const loginResponse = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: `username=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`,
  });
  const loginBody = await loginResponse.json();
  return { accessToken: loginBody.access_token };
}

function authHeaders(accessToken: string) {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${accessToken}`
  };
}

describe('Sponsors API', () => {
  let headers: { [key: string]: string };

  beforeAll(async () => {
    const user = await registerAndLogin();
    headers = authHeaders(user.accessToken);
  });

  test('GET /api/v1/sponsors - should read sponsors', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/sponsors`, {
      headers, // endpoint doesn't require auth, but sending it doesn't hurt
    });
    expect(response.status).toBe(200);
    const body = await response.json();
    expect(Array.isArray(body)).toBe(true);
  });
});
