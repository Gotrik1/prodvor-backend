import fetch from 'cross-fetch';
import dotenv from 'dotenv';

dotenv.config();

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8080';

// Helper to create a user and get token
const createUser = async (email: string, nickname: string) => {
  const password = 'testpassword';
  await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, nickname, first_name: 'Test', last_name: 'User' }),
  });
  const loginResponse = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: `username=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`,
  });
  const tokenData = await loginResponse.json();
  const meResponse = await fetch(`${API_BASE_URL}/api/v1/users/me`, {
    headers: { 'Authorization': `Bearer ${tokenData.access_token}` },
  });
  const meData = await meResponse.json();
  return { accessToken: tokenData.access_token, id: meData.id };
};

describe('Invitations API', () => {
  let captain: { accessToken: string; id: any; };
  let player: { accessToken: string; id: any; };
  let teamId: any;
  let invitationId: any;
  let sportName: any;

  beforeAll(async () => {
    captain = await createUser(`captain_${Date.now()}@example.com`, 'captain');
    player = await createUser(`player_${Date.now()}@example.com`, 'player');

    // Get a sport to create a team
    const sportsResponse = await fetch(`${API_BASE_URL}/api/v1/sports`);
    const sports = await sportsResponse.json();
    if (sports.length === 0) {
        // Create a sport if none exist
        const sportCreation = await fetch(`${API_BASE_URL}/api/v1/sports`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${captain.accessToken}` },
            body: JSON.stringify({ name: 'Test Sport', description: 'A sport for testing' })
        });
        const newSport = await sportCreation.json();
        sportName = newSport.name;
    } else {
        sportName = sports[0].name;
    }

    // Captain creates a team
    const teamResponse = await fetch(`${API_BASE_URL}/api/v1/teams`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${captain.accessToken}`,
      },
      body: JSON.stringify({ name: 'The Winners', game: sportName, description: 'A winning team' }),
    });
    const teamData = await teamResponse.json();
    teamId = teamData.id;
  }, 90000);

  test('POST /api/v1/invitations - should create an invitation', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/invitations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${captain.accessToken}`,
      },
      body: JSON.stringify({ user_id: player.id, team_id: teamId, status: 'pending' }),
    });
    const body = await response.json();
    expect(response.status).toBe(200);
    expect(body.user_id).toBe(player.id);
    expect(body.team_id).toBe(teamId);
    expect(body.status).toBe('pending');
    invitationId = body.id;
  });

  test('GET /api/v1/invitations/user/{user_id} - should get user invitations', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/invitations/user/${player.id}`, {
      headers: { 'Authorization': `Bearer ${player.accessToken}` },
    });
    const body = await response.json();
    expect(response.status).toBe(200);
    expect(Array.isArray(body)).toBe(true);
    expect(body.length).toBeGreaterThan(0);
    expect(body[0].id).toBe(invitationId);
  });

  test('PUT /api/v1/invitations/{invitation_id}/accept - should accept an invitation', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/invitations/${invitationId}/accept`, {
      method: 'PUT',
      headers: { 'Authorization': `Bearer ${player.accessToken}` },
    });
    const body = await response.json();
    expect(response.status).toBe(200);
    expect(body.status).toBe('accepted');
  });
  
  test('PUT /api/v1/invitations/{invitation_id}/decline - should decline an invitation', async () => {
    // Create a new invitation to decline
    const newInvitationResponse = await fetch(`${API_BASE_URL}/api/v1/invitations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${captain.accessToken}`,
        },
        body: JSON.stringify({ user_id: player.id, team_id: teamId, status: 'pending' }),
      });
      const newInvitationBody = await newInvitationResponse.json();
      const newInvitationId = newInvitationBody.id;

    const response = await fetch(`${API_BASE_URL}/api/v1/invitations/${newInvitationId}/decline`, {
      method: 'PUT',
      headers: { 'Authorization': `Bearer ${player.accessToken}` },
    });
    const body = await response.json();
    expect(response.status).toBe(200);
    expect(body.status).toBe('declined');
  });
});
