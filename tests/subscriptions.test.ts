import fetch from 'cross-fetch';
import dotenv from 'dotenv';

dotenv.config();

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8080';

// Helper functions (previously in helpers.ts)
async function registerAndLogin(email: string, password = 'testpassword') {
  const registerResponse = await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, nickname: email.split('@')[0], first_name: 'Sub', last_name: 'User' }),
  });
  if (registerResponse.status !== 200) {
    console.error('Failed to register user:', await registerResponse.text());
  }

  const loginResponse = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: `username=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`,
  });
  const loginBody = await loginResponse.json();
  
  const meResponse = await fetch(`${API_BASE_URL}/api/v1/users/me`, {
      headers: { 'Authorization': `Bearer ${loginBody.access_token}` }
  });
  const meBody = await meResponse.json();

  return { accessToken: loginBody.access_token, userId: meBody.id };
}

function authHeaders(accessToken: string) {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${accessToken}`
  };
}

async function createSport(headers: { [key: string]: string }, name: string) {
    const response = await fetch(`${API_BASE_URL}/api/v1/sports`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ name }),
    });
    return response.json();
}

async function createTeam(headers: { [key: string]: string }, name: string, sportId: string) {
  const response = await fetch(`${API_BASE_URL}/api/v1/teams`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ name, sport_id: sportId }), 
  });
  return response.json();
}

describe('Subscriptions API', () => {
  let user1Headers: { [key: string]: string };
  let user2Headers: { [key: string]: string };
  let teamId: string;

  beforeAll(async () => {
    const user1 = await registerAndLogin('user1.sub@example.com', 'password123');
    user1Headers = authHeaders(user1.accessToken);

    const user2 = await registerAndLogin('user2.sub@example.com', 'password123');
    user2Headers = authHeaders(user2.accessToken);

    const sport = await createSport(user1Headers, 'Subscription Sport');
    const team = await createTeam(user1Headers, 'Subscription Test Team', sport.id);
    teamId = team.id;
  });

  test('POST /api/v1/subscriptions/subscribe - user2 should subscribe to user1s team', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/subscriptions/subscribe`, {
      method: 'POST',
      headers: user2Headers,
      body: JSON.stringify({ team_id: teamId }),
    });
    expect(response.status).toBe(204);
  });

  test('GET /api/v1/subscriptions/status - should confirm user2 is subscribed', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/subscriptions/status?team_id=${teamId}`, {
      headers: user2Headers,
    });
    expect(response.status).toBe(200);
    const body = await response.json();
    expect(body.is_following).toBe(true);
  });

  test('GET /api/v1/subscriptions/notifications - should get notification history', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/subscriptions/notifications`, {
      headers: user1Headers, 
    });
    expect(response.status).toBe(200);
    const body = await response.json();
    expect(Array.isArray(body)).toBe(true);
  });

  test('POST /api/v1/subscriptions/unsubscribe - user2 should unsubscribe from user1s team', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/subscriptions/unsubscribe`, {
      method: 'POST',
      headers: user2Headers,
      body: JSON.stringify({ team_id: teamId }),
    });
    expect(response.status).toBe(204);
  });

  test('GET /api/v1/subscriptions/status - should confirm user2 is no longer subscribed', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/subscriptions/status?team_id=${teamId}`, {
      headers: user2Headers,
    });
    expect(response.status).toBe(200);
    const body = await response.json();
    expect(body.is_following).toBe(false);
  });
});
