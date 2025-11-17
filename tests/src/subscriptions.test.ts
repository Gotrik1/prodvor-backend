
import fetch from 'node-fetch';
import { createUniqueUser, createTeam, createUniqueName, cleanup, SubscriptionStatusResponse, NotificationResponse } from './helpers';

describe('Subscriptions API', () => {
  const API_BASE_URL = 'http://localhost:8080';
  let user: any, team: any, headers: any;

  beforeAll(async () => {
    const { user: testUser, headers: testHeaders } = await createUniqueUser('subscriptions_user');
    user = testUser;
    headers = testHeaders;

    const teamName = createUniqueName('Test Team For Subscriptions');
    team = await createTeam(headers, teamName);
  });

  afterAll(async () => {
    await cleanup();
  });

  test('POST /api/v1/subscriptions/subscribe - should subscribe a user to a team', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/subscriptions/subscribe`,
      {
        method: 'POST',
        headers,
        body: JSON.stringify({ team_id: team.id }),
      }
    );
    expect(response.status).toBe(204);
  });

  test('GET /api/v1/subscriptions/status - should get subscription status', async () => {
    // First, subscribe
    await fetch(`${API_BASE_URL}/api/v1/subscriptions/subscribe`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ team_id: team.id }),
    });

    const response = await fetch(`${API_BASE_URL}/api/v1/subscriptions/status?team_id=${team.id}`, {
      headers,
    });
    expect(response.status).toBe(200);
    const status = await response.json() as SubscriptionStatusResponse;
    expect(status.is_following).toBe(true);
  });

  test('POST /api/v1/subscriptions/unsubscribe - should unsubscribe a user from a team', async () => {
    // First, subscribe
    await fetch(`${API_BASE_URL}/api/v1/subscriptions/subscribe`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ team_id: team.id }),
    });

    const response = await fetch(
      `${API_BASE_URL}/api/v1/subscriptions/unsubscribe`,
      {
        method: 'POST',
        headers,
        body: JSON.stringify({ team_id: team.id }),
      }
    );
    expect(response.status).toBe(204);

    // Verify that the user is no longer subscribed
    const statusResponse = await fetch(`${API_BASE_URL}/api/v1/subscriptions/status?team_id=${team.id}`, {
      headers,
    });
    const status = await statusResponse.json() as SubscriptionStatusResponse;
    expect(status.is_following).toBe(false);
  });

  test('GET /api/v1/subscriptions/notifications - should get user notifications', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/subscriptions/notifications`, {
      headers,
    });
    expect(response.status).toBe(200);
    const notifications = await response.json() as NotificationResponse[];
    // Since we just subscribed and unsubscribed, we should have notifications
    // In a real scenario, we would mock a notification trigger event
    // For now, we just check that the response is an array
    expect(Array.isArray(notifications)).toBe(true);
  });
});
