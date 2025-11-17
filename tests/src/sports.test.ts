
import fetch from 'node-fetch';
import { createUniqueUser, cleanup, SportResponse } from './helpers';

describe('Sports API', () => {
  const API_BASE_URL = 'http://localhost:8080';

  afterAll(async () => {
    await cleanup();
  });

  test('POST /api/v1/sports - should create a new sport', async () => {
    const { headers } = await createUniqueUser('sports_admin');
    const sportName = `Test Sport ${Math.random()}`;

    const response = await fetch(`${API_BASE_URL}/api/v1/sports`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ name: sportName, description: 'A test sport' }),
    });

    expect(response.status).toBe(200);
    const sport = await response.json() as SportResponse;
    expect(sport.name).toBe(sportName);
  });

  test('GET /api/v1/sports - should retrieve a list of sports', async () => {
    const { headers } = await createUniqueUser('sports_user');
    const sportName = `Another Sport ${Math.random()}`;

    await fetch(`${API_BASE_URL}/api/v1/sports`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ name: sportName, description: 'Another test sport' }),
    });

    const response = await fetch(`${API_BASE_URL}/api/v1/sports`);
    expect(response.status).toBe(200);
    const sports = await response.json() as SportResponse[];
    expect(Array.isArray(sports)).toBe(true);
    expect(sports.length).toBeGreaterThan(0);
    expect(sports.some((sport: any) => sport.name === sportName)).toBe(true);
  });
});
