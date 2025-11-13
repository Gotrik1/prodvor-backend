import fetch from 'cross-fetch';
import dotenv from 'dotenv';

dotenv.config();

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8080';

// Helper functions
async function registerAndLogin(email: string, password = 'testpassword') {
  await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, nickname: email.split('@')[0], first_name: 'Team', last_name: 'User' }),
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

describe('Teams API', () => {
  let captainHeaders: { [key: string]: string };
  let playerHeaders: { [key: string]: string };
  let applicantHeaders: { [key: string]: string };
  let captainId: string;
  let applicantId: string;
  let teamId: number;

  beforeAll(async () => {
    const captain = await registerAndLogin('captain.teams@example.com', 'password123');
    captainHeaders = authHeaders(captain.accessToken);
    captainId = captain.userId;

    const player = await registerAndLogin('player.teams@example.com', 'password123');
    playerHeaders = authHeaders(player.accessToken);

    const applicant = await registerAndLogin('applicant.teams@example.com', 'password123');
    applicantHeaders = authHeaders(applicant.accessToken);
    applicantId = applicant.userId;

    const sport = await createSport(captainHeaders, 'Team Test Sport');
    const team = await createTeam(captainHeaders, 'Team Test', sport.name);
    teamId = team.id;
  });

  test('GET /api/v1/teams - should read teams', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/teams`);
    expect(response.status).toBe(200);
    const body = await response.json();
    expect(Array.isArray(body)).toBe(true);
  });

  test('GET /api/v1/teams/{team_id} - should read a single team', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/teams/${teamId}`);
    expect(response.status).toBe(200);
    const body = await response.json();
    expect(body.id).toBe(teamId);
  });

  test('POST /api/v1/teams/{team_id}/apply - applicant should apply to the team', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/teams/${teamId}/apply`, {
      method: 'POST',
      headers: applicantHeaders,
    });
    expect(response.status).toBe(200);
    const body = await response.json();
    expect(body.message).toBe('Application sent successfully');
  });

  test('GET /api/v1/teams/{team_id}/applications - captain should see the application', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/teams/${teamId}/applications`, {
      headers: captainHeaders,
    });
    expect(response.status).toBe(200);
    const body = await response.json();
    expect(Array.isArray(body)).toBe(true);
    expect(body.length).toBe(1);
    expect(body[0].id).toBe(applicantId);
  });

  test('POST /api/v1/teams/{team_id}/applications/{user_id}/respond - captain should accept the application', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/teams/${teamId}/applications/${applicantId}/respond?action=accept`, {
      method: 'POST',
      headers: captainHeaders,
    });
    expect(response.status).toBe(200);
    const body = await response.json();
    expect(body.message).toBe('Player accepted');
  });

  test('POST /api/v1/teams/{team_id}/logo - captain should update team logo', async () => {
    const newLogoUrl = 'https://example.com/new_logo.png';
    const response = await fetch(`${API_BASE_URL}/api/v1/teams/${teamId}/logo`, {
      method: 'POST',
      headers: { ...captainHeaders, 'Content-Type': 'application/json' },
      body: JSON.stringify({ logoUrl: newLogoUrl }),
    });
    expect(response.status).toBe(200);
    const body = await response.json();
    expect(body.logoUrl).toBe(newLogoUrl);
  });

  test('POST /api/v1/teams/{team_id}/follow - should toggle follow status', async () => {
    // 1. Follow the team
    const followResponse = await fetch(`${API_BASE_URL}/api/v1/teams/${teamId}/follow`, {
      method: 'POST',
      headers: playerHeaders,
    });
    expect(followResponse.status).toBe(200);
    const followBody = await followResponse.json();
    expect(followBody.isFollowing).toBe(true);

    // 2. Unfollow the team
    const unfollowResponse = await fetch(`${API_BASE_URL}/api/v1/teams/${teamId}/follow`, {
      method: 'POST',
      headers: playerHeaders,
    });
    expect(unfollowResponse.status).toBe(200);
    const unfollowBody = await unfollowResponse.json();
    expect(unfollowBody.isFollowing).toBe(false);
  });

  test('DELETE /api/v1/teams/{team_id}/members/{user_id} - captain should remove a member', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/teams/${teamId}/members/${applicantId}`, {
      method: 'DELETE',
      headers: captainHeaders,
    });
    expect(response.status).toBe(200);
    const body = await response.json();
    expect(body.message).toBe('Player removed successfully');
  });
});
