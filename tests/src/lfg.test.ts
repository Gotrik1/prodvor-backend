
import fetch from 'node-fetch';
import { createUniqueUser, cleanup, LfgResponse } from './helpers';

describe('LFG API', () => {
  const API_BASE_URL = 'http://localhost:8080';
  let user: any, headers: any;

  beforeAll(async () => {
    const { user: testUser, headers: testHeaders } = await createUniqueUser('lfg_user');
    user = testUser;
    headers = testHeaders;
  });

  afterAll(async () => {
    await cleanup();
  });

  test('POST /api/v1/lfg - should create an LFG', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/lfg`,
      {
        method: 'POST',
        headers,
        body: JSON.stringify({ sport: 'football', description: 'Looking for players', required_players: 5, creator_id: user.id }),
      }
    );
    expect(response.status).toBe(200);
    const lfg = await response.json() as LfgResponse;
    expect(lfg.sport).toBe('football');
    expect(lfg.description).toBe('Looking for players');
    expect(lfg.required_players).toBe(5);
    expect(lfg.creator_id).toBe(user.id);
  });

  test('GET /api/v1/lfg - should get all LFGs', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/lfg`, {
        headers,
    });
    expect(response.status).toBe(200);
    const lfgs = await response.json() as LfgResponse[];
    expect(lfgs.length).toBeGreaterThan(0);
  });
});
