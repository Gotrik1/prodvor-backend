import fetch from 'cross-fetch';
import dotenv from 'dotenv';

dotenv.config();

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8080';

describe('Posts API', () => {
  let accessToken: string;
  let currentUserId: string;
  let createdPostId: any; // This will be set after a post is created

  beforeAll(async () => {
    // Create a dedicated user for this test suite to ensure isolation
    const email = `testuser_posts_${Date.now()}@example.com`;
    const password = 'testpassword';

    await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, nickname: 'poststester', first_name: 'Test', last_name: 'User' }),
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
    currentUserId = meData.id;
  }, 60000);

  test('POST /api/v1/posts - should create a post', async () => {
    const postData = {
      content: 'This is a test post for the posts API!',
    };

    const response = await fetch(`${API_BASE_URL}/api/v1/posts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`,
      },
      body: JSON.stringify(postData),
    });

    const body = await response.json();
    expect(response.status).toBe(200);
    expect(body.content).toBe(postData.content);
    expect(body.id).toBeDefined();
    createdPostId = body.id; // Save the ID for subsequent tests
  });
  
  test('GET /api/v1/posts/{post_id} - should read a single post', async () => {
    expect(createdPostId).toBeDefined(); // Ensure the previous test ran and set the ID
    const response = await fetch(`${API_BASE_URL}/api/v1/posts/${createdPostId}`, {
        headers: { 'Authorization': `Bearer ${accessToken}` }
    });
    const body = await response.json();
    expect(response.status).toBe(200);
    expect(body.id).toBe(createdPostId);
    expect(body.content).toContain('posts API');
  });

  test('GET /api/v1/posts - should read all posts', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/posts`, {
        headers: { 'Authorization': `Bearer ${accessToken}` }
    });
    const body = await response.json();
    expect(response.status).toBe(200);
    expect(Array.isArray(body)).toBe(true);
    // Check if our created post is in the list
    const foundPost = body.find((post: any) => post.id === createdPostId);
    expect(foundPost).toBeDefined();
  });

  test('PUT /api/v1/posts/{post_id} - should update a post', async () => {
    expect(createdPostId).toBeDefined();
    const updatedContent = 'This post has been updated.';
    const response = await fetch(`${API_BASE_URL}/api/v1/posts/${createdPostId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${accessToken}`,
        },
        body: JSON.stringify({ content: updatedContent })
    });
    const body = await response.json();
    expect(response.status).toBe(200);
    expect(body.content).toBe(updatedContent);

    // Verify the update by fetching the post again
    const verifyResponse = await fetch(`${API_BASE_URL}/api/v1/posts/${createdPostId}`, {
        headers: { 'Authorization': `Bearer ${accessToken}` }
    });
    const verifiedBody = await verifyResponse.json();
    expect(verifiedBody.content).toBe(updatedContent);
  });

  test('DELETE /api/v1/posts/{post_id} - should delete a post', async () => {
    expect(createdPostId).toBeDefined();
    const response = await fetch(`${API_BASE_URL}/api/v1/posts/${createdPostId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${accessToken}` }
    });
    expect(response.status).toBe(200);

    // Verify the post is deleted by trying to fetch it again
    const verifyResponse = await fetch(`${API_BASE_URL}/api/v1/posts/${createdPostId}`, {
        headers: { 'Authorization': `Bearer ${accessToken}` }
    });
    expect(verifyResponse.status).toBe(404); // Expect Not Found
  });
});
