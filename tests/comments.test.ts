import fetch from 'cross-fetch';
import dotenv from 'dotenv';

dotenv.config();

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8080';

describe('Comments API', () => {
  let accessToken: string;
  let currentUserId: any;
  let testPostId: any;
  let testCommentId: any;

  // Setup: Create a user and a post before any comment tests run
  beforeAll(async () => {
    const email = `testuser_comments_${Date.now()}@example.com`;
    const password = 'testpassword';

    await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, nickname: 'commentstester', first_name: 'Test', last_name: 'User' }),
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

    // Create a post to comment on
    const postResponse = await fetch(`${API_BASE_URL}/api/v1/posts`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${accessToken}`,
        },
        body: JSON.stringify({ content: 'A post to be commented on'})
    });
    const postData = await postResponse.json();
    testPostId = postData.id;
  }, 90000);

  test('POST /api/v1/comments - should create a comment', async () => {
    const commentData = {
        text: 'This is a test comment.',
        postId: testPostId
    };
    const response = await fetch(`${API_BASE_URL}/api/v1/comments`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${accessToken}`,
        },
        body: JSON.stringify(commentData)
    });
    const body = await response.json();
    expect(response.status).toBe(200);
    expect(body.text).toBe(commentData.text);
    expect(body.id).toBeDefined();
    testCommentId = body.id;
  });

  test('GET /api/v1/comments/{comment_id} - should read a single comment', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/comments/${testCommentId}`, {
        headers: { 'Authorization': `Bearer ${accessToken}` }
    });
    const body = await response.json();
    expect(response.status).toBe(200);
    expect(body.id).toBe(testCommentId);
  });

  test('GET /api/v1/comments/post/{post_id} - should read all comments for a post', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/comments/post/${testPostId}`, {
        headers: { 'Authorization': `Bearer ${accessToken}` }
    });
    const body = await response.json();
    expect(response.status).toBe(200);
    expect(Array.isArray(body)).toBe(true);
    expect(body.length).toBeGreaterThan(0);
    expect(body.some((comment:any) => comment.id === testCommentId)).toBe(true);
  });

  test('PUT /api/v1/comments/{comment_id} - should update the comment', async () => {
    const updatedText = 'This comment has been updated.';
    const response = await fetch(`${API_BASE_URL}/api/v1/comments/${testCommentId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${accessToken}`,
        },
        body: JSON.stringify({ text: updatedText, postId: testPostId })
    });
    const body = await response.json();
    expect(response.status).toBe(200);
    expect(body.text).toBe(updatedText);
  });

  test('DELETE /api/v1/comments/{comment_id} - should delete the comment', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/comments/${testCommentId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${accessToken}` }
    });
    expect(response.status).toBe(200);

    // Verify deletion
    const verifyResponse = await fetch(`${API_BASE_URL}/api/v1/comments/${testCommentId}`);
    expect(verifyResponse.status).not.toBe(200); // Should be 404 or other error
  });
});
