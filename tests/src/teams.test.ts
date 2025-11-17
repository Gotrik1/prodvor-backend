
import fetch from 'node-fetch';
import { FormData, File } from 'node-fetch';
import {
  createUniqueUser,
  createTeam,
  createUniqueName,
  applyToTeam,
  cleanup,
  TeamResponse,
} from './helpers';

describe('Teams endpoints', () => {
  const API_BASE_URL = 'http://localhost:8080';

  afterAll(async () => {
    await cleanup();
  });

  async function toggleTeamFollow(headers: any, team_id: string): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/v1/teams/${team_id}/follow`, {
        method: 'POST',
        headers,
    });
    if (response.status !== 200) {
        const errorBody = await response.text();
        throw new Error(`Failed to toggle team follow. Status: ${response.status}, Body: ${errorBody}`);
    }
    return await response.json();
  }

  async function respondToApplication(headers: any, team_id: string, user_id: string, accept: boolean): Promise<any> {
    const action = accept ? 'accept' : 'decline';
    const response = await fetch(`${API_BASE_URL}/api/v1/teams/${team_id}/applications/${user_id}/respond?action=${action}`, {
        method: 'POST',
        headers,
    });
    if (response.status !== 200) {
        const errorBody = await response.text();
        throw new Error(`Failed to respond to application. Status: ${response.status}, Body: ${errorBody}`);
    }
    return response.json();
  }

  test('POST /api/v1/teams/{team_id}/follow - should follow and unfollow a team', async () => {
    const { headers: userHeaders, user } = await createUniqueUser('follow_user');
    const { headers: captainHeaders } = await createUniqueUser('follow_captain');
    const team = await createTeam(captainHeaders, createUniqueName('Team to be followed'));

    await toggleTeamFollow(userHeaders, team.id);

    const followingResponse = await fetch(`${API_BASE_URL}/api/v1/users/${user.id}/following`, {
        headers: userHeaders,
    });
    const following = (await followingResponse.json()) as { teams: { data: TeamResponse[] } };
    expect(following.teams.data.some((t) => t.id === team.id)).toBe(true);

    await toggleTeamFollow(userHeaders, team.id);

    const notFollowingResponse = await fetch(`${API_BASE_URL}/api/v1/users/${user.id}/following`, {
        headers: userHeaders,
    });
    const notFollowing = (await notFollowingResponse.json()) as { teams: { data: TeamResponse[] } };
    expect(notFollowing.teams.data.some((t) => t.id === team.id)).toBe(false);
  });

  test('POST /api/v1/teams/{team_id}/applications/{user_id}/respond - accept', async () => {
    const { headers: captainHeaders } = await createUniqueUser('application_captain');
    const { headers: applicantHeaders, user: applicant } = await createUniqueUser('application_applicant');
    const team = await createTeam(captainHeaders, createUniqueName('Team for application response'));

    await applyToTeam(applicantHeaders, team.id);
    await respondToApplication(captainHeaders, team.id, applicant.id, true);

    const response = await fetch(`${API_BASE_URL}/api/v1/teams/${team.id}`, {
      headers: captainHeaders,
    });
    const updatedTeam = (await response.json()) as TeamResponse;

    expect(updatedTeam.members.some((m) => m.id === applicant.id)).toBe(true);
  });

  test('POST /api/v1/teams/{team_id}/applications/{user_id}/respond - decline', async () => {
    const { headers: captainHeaders } = await createUniqueUser('application_captain_decline');
    const { headers: applicantHeaders, user: applicant } = await createUniqueUser('application_applicant_decline');
    const team = await createTeam(captainHeaders, createUniqueName('Team for application decline'));

    await applyToTeam(applicantHeaders, team.id);
    await respondToApplication(captainHeaders, team.id, applicant.id, false);

    const response = await fetch(`${API_BASE_URL}/api/v1/teams/${team.id}`, {
      headers: captainHeaders,
    });
    const updatedTeam = (await response.json()) as TeamResponse;

    expect(updatedTeam.members.some((m) => m.id === applicant.id)).toBe(false);
  });

  test('POST /api/v1/teams/{team_id}/logo - should return null for logoUrl', async () => {
    const { headers: captainHeaders } = await createUniqueUser('logo_captain');
    const team = await createTeam(captainHeaders, createUniqueName('Team for logo upload'));
    const fileName = 'logo.png';

    const response = await fetch(`${API_BASE_URL}/api/v1/teams/${team.id}/logo`, {
        method: 'POST',
        headers: captainHeaders,
        body: JSON.stringify({ file_name: fileName }),
    });

    expect(response.status).toBe(200);

    const updatedTeam = (await response.json()) as TeamResponse;

    expect(updatedTeam.logoUrl).toBeNull();
  });

  test('DELETE /api/v1/teams/{team_id}/members/{user_id} - should remove a team member', async () => {
    const { headers: captainHeaders } = await createUniqueUser('member_removal_captain');
    const { headers: memberHeaders, user: member } = await createUniqueUser('member_to_be_removed');
    const team = await createTeam(captainHeaders, createUniqueName('Team for member removal'));

    await applyToTeam(memberHeaders, team.id);
    await respondToApplication(captainHeaders, team.id, member.id, true);

    const deleteResponse = await fetch(`${API_BASE_URL}/api/v1/teams/${team.id}/members/${member.id}`, {
      method: 'DELETE',
      headers: captainHeaders,
    });

    expect(deleteResponse.status).toBe(200);

    const getTeamResponse = await fetch(`${API_BASE_URL}/api/v1/teams/${team.id}`, {
      headers: captainHeaders,
    });
    const updatedTeam = (await getTeamResponse.json()) as TeamResponse;

    expect(updatedTeam.members.some(m => m.id === member.id)).toBe(false);
  });

});
