
import fetch from 'node-fetch';
import {
  createUniqueUser,
  cleanup,
  createTeam,
  createUniqueName,
  createLFG,
  applyToTeam,
  TeamResponse,
  UserResponse,
  LfgResponse,
} from './helpers';

describe('Uncovered endpoints', () => {
  const API_BASE_URL = 'http://localhost:8080';

  afterAll(async () => {
    await cleanup();
  });

  test('GET /api/v1/teams - should retrieve all teams', async () => {
    const { headers } = await createUniqueUser('teams_uncovered_user1');
    const teamName = createUniqueName('Team for all teams');
    await createTeam(headers, teamName);

    const response = await fetch(`${API_BASE_URL}/api/v1/teams?limit=1000`, {
      headers,
    });
    expect(response.status).toBe(200);
    const teams = (await response.json()) as TeamResponse[];
    expect(teams.length).toBeGreaterThan(0);
    expect(teams.some((team) => team.name === teamName)).toBe(true);
  });

  test('GET /api/v1/teams/{team_id} - should retrieve a specific team', async () => {
    const { headers } = await createUniqueUser('teams_uncovered_user2');
    const teamName = createUniqueName('Team for specific team');
    const team = await createTeam(headers, teamName);

    const response = await fetch(`${API_BASE_URL}/api/v1/teams/${team.id}`, {
      headers,
    });
    expect(response.status).toBe(200);
    const foundTeam = (await response.json()) as TeamResponse;
    expect(foundTeam.id).toBe(team.id);
    expect(foundTeam.name).toBe(team.name);
  });

  test('GET /api/v1/teams/{team_id}/applications - should retrieve team applications', async () => {
    const { headers: captainHeaders } = await createUniqueUser('teams_uncovered_captain');
    const { user: applicant, headers: applicantHeaders } = await createUniqueUser('teams_uncovered_applicant');
    const team = await createTeam(captainHeaders, createUniqueName('Team with application'));

    await applyToTeam(applicantHeaders, team.id);

    const response = await fetch(`${API_BASE_URL}/api/v1/teams/${team.id}/applications`, {
      headers: captainHeaders,
    });

    expect(response.status).toBe(200);
    const applicants = (await response.json()) as UserResponse[];
    expect(applicants.length).toBe(1);
    expect(applicants[0].id).toBe(applicant.id);
  });

  test('GET /api/v1/lfg?creator_id={user_id} - should retrieve LFGs for a specific user', async () => {
    const { user, headers } = await createUniqueUser('lfg_uncovered_user');
    const lfg = await createLFG(headers, 'football', 'LFG for user', 1, user.id);

    const response = await fetch(`${API_BASE_URL}/api/v1/lfg?creator_id=${user.id}`, {
      headers,
    });

    expect(response.status).toBe(200);
    const lfgs = (await response.json()) as LfgResponse[];
    expect(lfgs.some((l) => l.id === lfg.id)).toBe(true);
  });
});
