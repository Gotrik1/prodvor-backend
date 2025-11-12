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

describe('Friend Requests API', () => {
  let user1: { accessToken: string; id: any; };
  let user2: { accessToken: string; id: any; };
  let friendRequestId: any;

  beforeAll(async () => {
    user1 = await createUser(`testuser_${Date.now()}@example.com`, 'user1');
    user2 = await createUser(`testuser_${Date.now() + 1}@example.com`, 'user2');
  }, 90000);

  test('POST /api/v1/friend-requests - should create a friend request', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/friend-requests`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${user1.accessToken}`,
      },
      body: JSON.stringify({ receiver_id: user2.id }),
    });
    const body = await response.json();
    expect(response.status).toBe(200);
    expect(body.requester_id).toBe(user1.id);
    expect(body.receiver_id).toBe(user2.id);
    expect(body.status).toBe('pending');
    friendRequestId = body.id;
  });

  test('GET /api/v1/friend-requests/received - should get received friend requests', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/friend-requests/received`, {
      headers: { 'Authorization': `Bearer ${user2.accessToken}` },
    });
    const body = await response.json();
    expect(response.status).toBe(200);
    expect(Array.isArray(body)).toBe(true);
    expect(body.length).toBeGreaterThan(0);
    expect(body[0].id).toBe(friendRequestId);
  });

  test('PUT /api/v1/friend-requests/{request_id}/accept - should accept a friend request', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/friend-requests/${friendRequestId}/accept`, {
      method: 'PUT',
      headers: { 'Authorization': `Bearer ${user2.accessToken}` },
    });
    const body = await response.json();
    expect(response.status).toBe(200);
    expect(body.status).toBe('accepted');
  });

  test('GET /api/v1/friend-requests/friends - should list friends for both users', async () => {
    // Check user1's friends
    const friends1_response = await fetch(`${API_BASE_URL}/api/v1/friend-requests/friends`, {
        headers: { 'Authorization': `Bearer ${user1.accessToken}` },
    });
    const friends1_body = await friends1_response.json();
    expect(friends1_response.status).toBe(200);
    expect(friends1_body.some((friend: any) => friend.id === user2.id)).toBe(true);

    // Check user2's friends
    const friends2_response = await fetch(`${API_BASE_URL}/api/v1/friend-requests/friends`, {
        headers: { 'Authorization': `Bearer ${user2.accessToken}` },
    });
    const friends2_body = await friends2_response.json();
    expect(friends2_response.status).toBe(200);
    expect(friends2_body.some((friend: any) => friend.id === user1.id)).toBe(true);
  });

  test('PUT /api/v1/friend-requests/{request_id}/decline - should decline a friend request', async () => {
    // First, create a new request to decline
    // For the sake of simplicity, we'll re-use user2 and expect the request to fail if already friends.
    // A better test would use a third user.
    // Let's create user3
    const user3 = await createUser(`testuser_${Date.now() + 2}@example.com`, 'user3');
    const declineRequestResponse = await fetch(`${API_BASE_URL}/api/v1/friend-requests`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${user1.accessToken}`},
        body: JSON.stringify({ receiver_id: user3.id })
    });
    const declineRequestBody = await declineRequestResponse.json();
    const declineRequestId = declineRequestBody.id;

    const response = await fetch(`${API_BASE_URL}/api/v1/friend-requests/${declineRequestId}/decline`, {
      method: 'PUT',
      headers: { 'Authorization': `Bearer ${user3.accessToken}` },
    });
    const body = await response.json();
    expect(response.status).toBe(200);
    expect(body.status).toBe('declined');
  });
});
