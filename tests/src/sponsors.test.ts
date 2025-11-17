
import fetch from 'node-fetch';
import { createUniqueUser, cleanup } from './helpers';

describe('Sponsors API', () => {
  const API_BASE_URL = 'http://localhost:8080';

  afterAll(async () => {
    await cleanup();
  });

  test('GET /api/v1/sponsors - should retrieve a list of sponsors', async () => {
    const { headers } = await createUniqueUser('sponsors_user');
    const response = await fetch(`${API_BASE_URL}/api/v1/sponsors`, { headers });
    expect(response.status).toBe(200);
    const sponsors = await response.json();
    expect(Array.isArray(sponsors)).toBe(true);
  });
});
