
import fetch from 'node-fetch';
import { createUniqueUser, createTeam, cleanup, InvitationResponse, createUniqueName } from './helpers';

describe('Invitations API', () => {
  const API_BASE_URL = 'http://localhost:8080';
  let captain: any, user: any, team: any, headers: any;

  beforeAll(async () => {
    const { user: testCaptain, headers: captainHeaders } = await createUniqueUser('invitations_captain');
    captain = testCaptain;
    headers = captainHeaders;

    const { user: testUser } = await createUniqueUser('invitations_user');
    user = testUser;

    const teamName = createUniqueName('Test Team For Invitations');
    team = await createTeam(headers, teamName);
  });

  afterAll(async () => {
    await cleanup();
  });

  test('POST /api/v1/invitations - should create an invitation', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/invitations`,
      {
        method: 'POST',
        headers,
        body: JSON.stringify({ user_id: user.id, team_id: team.id, status: 'pending' }),
      }
    );
    expect(response.status).toBe(200);
    const invitation = await response.json() as InvitationResponse;
    expect(invitation.user_id).toBe(user.id);
    expect(invitation.team_id).toBe(team.id);
    expect(invitation.status).toBe('pending');
  });

  test('GET /api/v1/invitations/user/{user_id} - should get user invitations', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/invitations/user/${user.id}`
    , {
        headers,
    });
    expect(response.status).toBe(200);
    const invitations = await response.json() as InvitationResponse[];
    expect(invitations.length).toBeGreaterThan(0);
    expect(invitations[0].user_id).toBe(user.id);
  });

  test('PUT /api/v1/invitations/{invitation_id}/accept - should accept an invitation', async () => {
    const inviteResponse = await fetch(`${API_BASE_URL}/api/v1/invitations`,
      {
        method: 'POST',
        headers,
        body: JSON.stringify({ user_id: user.id, team_id: team.id, status: 'pending' }),
      }
    );
    const invitation = await inviteResponse.json() as InvitationResponse;

    const acceptResponse = await fetch(
      `${API_BASE_URL}/api/v1/invitations/${invitation.id}/accept`,
      {
        method: 'PUT',
        headers,
      }
    );
    expect(acceptResponse.status).toBe(200);
    const acceptedInvitation = await acceptResponse.json() as InvitationResponse;
    expect(acceptedInvitation.status).toBe('accepted');
  });

  test('PUT /api/v1/invitations/{invitation_id}/decline - should decline an invitation', async () => {
    const inviteResponse = await fetch(`${API_BASE_URL}/api/v1/invitations`,
      {
        method: 'POST',
        headers,
        body: JSON.stringify({ user_id: user.id, team_id: team.id, status: 'pending' }),
      }
    );
    const invitation = await inviteResponse.json() as InvitationResponse;

    const declineResponse = await fetch(
      `${API_BASE_URL}/api/v1/invitations/${invitation.id}/decline`,
      {
        method: 'PUT',
        headers,
      }
    );
    expect(declineResponse.status).toBe(200);
    const declinedInvitation = await declineResponse.json() as InvitationResponse;
    expect(declinedInvitation.status).toBe('declined');
  });
});
