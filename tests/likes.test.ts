import fetch from 'cross-fetch';
import dotenv from 'dotenv';

dotenv.config();

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8080';

describe('Likes API', () => {
  let accessToken: string;
  let userId: string;
  let postId: string;

  beforeAll(async () => {
    // Create a user
    const email = `testuser_likes_${Date.now()}@example.com`;
    const password = 'testpassword';
    await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, nickname: 'likesuser', first_name: 'Test', last_name: 'User' }),
    });

    const loginResponse = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: `username=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`,
    });
    const tokenData = await loginResponse.json();
    accessToken = tokenData.access_token;

    const meResponse = await fetch(`${API_BASE_URL}/api/v1/users/me`, {
      headers: { 'Authorization': `Bearer ${accessToken}` },
    });
    const meData = await meResponse.json();
    userId = meData.id;

    // Create a post
    const postResponse = await fetch(`${API_BASE_URL}/api/v1/posts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`,
      },
      body: JSON.stringify({ content: 'A post to be liked', author_id: userId }),
    });
    const postData = await postResponse.json();
    postId = postData.id;
  }, 90000);

  test('POST /api/v1/likes - should create a like', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/likes`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`,
      },
      body: JSON.stringify({ post_id: postId }),
    });
    expect(response.status).toBe(200);
    const body = await response.json();
    expect(body.user_id).toBe(userId);
    expect(body.post_id).toBe(postId);
  });

  test('GET /api/v1/likes/post/{post_id}/count - should get like count for a post', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/likes/post/${postId}/count`);
    expect(response.status).toBe(200);
    const body = await response.json();
    expect(body.count).toBe(1);
  });

  test('GET /api/v1/likes/user/{user_id}/liked-posts - should get liked posts by user', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/likes/user/${userId}/liked-posts`, {
        headers: { 'Authorization': `Bearer ${accessToken}` },
    });
    expect(response.status).toBe(200);
    const body = await response.json();
    expect(Array.isArray(body)).toBe(true);
    expect(body.length).toBe(1);
    expect(body[0].id).toBe(postId);
  });

  test('DELETE /api/v1/likes/{post_id} - should delete a like', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/likes/${postId}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${accessToken}` },
    });
    expect(response.status).toBe(200);

    // Verify the like count is 0 after deletion
    const countResponse = await fetch(`${API_BASE_URL}/api/v1/likes/post/${postId}/count`);
    const countBody = await countResponse.json();
    expect(countBody.count).toBe(0);
  });
});
