import fetch from 'cross-fetch';
import dotenv from 'dotenv';

dotenv.config();

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8080';

// Helper functions
async function registerAndLogin(email: string, password = 'testpassword') {
  await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, nickname: email.split('@')[0], first_name: 'Social', last_name: 'User' }),
  });

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

async function createTeam(headers: { [key: string]: string }, name: string, game: string) {
  const response = await fetch(`${API_BASE_URL}/api/v1/teams`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ name, game }),
  });
  return response.json();
}

async function sendRequest(headers: { [key: string]: string }, toUserId: string) {
  const response = await fetch(`${API_BASE_URL}/api/v1/friend-requests`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ to_user_id: toUserId }),
  });
  return response.json();
}

async function acceptRequest(headers: { [key: string]: string }, requestId: string) {
  await fetch(`${API_BASE_URL}/api/v1/friend-requests/${requestId}/accept`, {
    method: 'PUT',
    headers,
  });
}

describe('Users API - Social Graph', () => {
  let userA_headers: { [key: string]: string };
  let userB_headers: { [key: string]: string };
  let userA_id: string;
  let userB_id: string;
  let teamId: number;

  beforeAll(async () => {
    const userA = await registerAndLogin('userA.social@example.com', 'password123');
    userA_headers = authHeaders(userA.accessToken);
    userA_id = userA.userId;

    const userB = await registerAndLogin('userB.social@example.com', 'password123');
    userB_headers = authHeaders(userB.accessToken);
    userB_id = userB.userId;

    const userC = await registerAndLogin('userC.social@example.com', 'password123');
    const userC_headers = authHeaders(userC.accessToken);

    const sport = await createSport(userA_headers, 'Social Graph Sport');
    const team = await createTeam(userA_headers, 'Social Graph Team', sport.name);
    teamId = team.id;

    const request = await sendRequest(userB_headers, userA_id);
    await acceptRequest(userA_headers, request.id);

    await fetch(`${API_BASE_URL}/api/v1/teams/${teamId}/follow`, { method: 'POST', headers: userC_headers }); // C follows the Team
    await fetch(`${API_BASE_URL}/api/v1/teams/${teamId}/follow`, { method: 'POST', headers: userA_headers }); // A follows the Team
  });

  test('GET /api/v1/users/{user_id}/friends - should list user friends', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/users/${userA_id}/friends`, {
      headers: userA_headers,
    });
    expect(response.status).toBe(200);
    const body = await response.json();
    expect(body.meta.total).toBe(1);
    expect(body.data[0].id).toBe(userB_id);
  });

  test('GET /api/v1/users/{user_id}/followers - should list user followers', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/users/${userA_id}/followers`, {
      headers: userA_headers,
    });
    expect(response.status).toBe(200);
    const body = await response.json();
    expect(body.meta.total).toBe(0); // Direct user-to-user following is not implemented
  });

  test('GET /api/v1/users/{user_id}/following - should list followed users and teams', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/users/${userA_id}/following`, {
      headers: userA_headers,
    });
    expect(response.status).toBe(200);
    const body = await response.json();
    
    expect(body.users.meta.total).toBe(0); // Direct user-to-user following is not implemented
    
    expect(body.teams.meta.total).toBe(1);
    expect(body.teams.data[0].id).toBe(teamId);
  });
});
