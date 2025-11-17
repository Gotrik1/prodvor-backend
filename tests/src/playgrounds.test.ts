
import fetch from 'node-fetch';
import { createUniqueUser, cleanup, PlaygroundResponse } from './helpers';

describe('Playgrounds API', () => {
  const API_BASE_URL = 'http://localhost:8080';

  afterAll(async () => {
    await cleanup();
  });

  test('POST /api/v1/playgrounds - should create a new playground', async () => {
    const { headers } = await createUniqueUser('playgrounds_admin');
    const playgroundName = `Test Playground ${Math.random()}`;

    const response = await fetch(`${API_BASE_URL}/api/v1/playgrounds`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ name: playgroundName, location: '123 Test St' }),
    });

    expect(response.status).toBe(200);
    const playground = await response.json() as PlaygroundResponse;
    expect(playground.name).toBe(playgroundName);
  });

  test('GET /api/v1/playgrounds - should retrieve a list of playgrounds', async () => {
    const { headers } = await createUniqueUser('playgrounds_user');
    const playgroundName = `Another Playground ${Math.random()}`;

    await fetch(`${API_BASE_URL}/api/v1/playgrounds`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ name: playgroundName, location: '456 Test Ave' }),
    });

    const response = await fetch(`${API_BASE_URL}/api/v1/playgrounds`);
    expect(response.status).toBe(200);
    const playgrounds = await response.json() as PlaygroundResponse[];
    expect(Array.isArray(playgrounds)).toBe(true);
    expect(playgrounds.length).toBeGreaterThan(0);
    expect(playgrounds.some((p: any) => p.name === playgroundName)).toBe(true);
  });
});
