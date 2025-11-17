
import fetch from 'node-fetch';
import { createUniqueUser, createPost, cleanup, PostResponse } from './helpers';

describe('Posts API', () => {
  const API_BASE_URL = 'http://localhost:8080';
  let user: any, headers: any;

  beforeAll(async () => {
    const { user: testUser, headers: testHeaders } = await createUniqueUser('posts_test_user');
    user = testUser;
    headers = testHeaders;
  });

  afterAll(async () => {
    await cleanup();
  });

  test('POST /api/v1/posts - should create a post', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/posts`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ content: 'This is a test post' }),
    });
    expect(response.status).toBe(200);
    const post = await response.json() as PostResponse;
    expect(post.content).toBe('This is a test post');
    expect(post.author_id).toBe(user.id);
  });

  test('GET /api/v1/posts/{post_id} - should retrieve a post', async () => {
    const newPost = await createPost(headers, 'A post to be retrieved');
    const response = await fetch(`${API_BASE_URL}/api/v1/posts/${newPost.id}`, {
      headers,
    });
    expect(response.status).toBe(200);
    const post = await response.json() as PostResponse;
    expect(post.id).toBe(newPost.id);
  });

  test('GET /api/v1/posts - should retrieve all posts', async () => {
    await createPost(headers, 'Post 1');
    await createPost(headers, 'Post 2');

    const response = await fetch(`${API_BASE_URL}/api/v1/posts`, {
      headers,
    });
    expect(response.status).toBe(200);
    const posts = await response.json() as PostResponse[];
    expect(posts.length).toBeGreaterThanOrEqual(2);
  });

  test('PUT /api/v1/posts/{post_id} - should update a post', async () => {
    const newPost = await createPost(headers, 'Original post');
    const response = await fetch(`${API_BASE_URL}/api/v1/posts/${newPost.id}`, {
      method: 'PUT',
      headers,
      body: JSON.stringify({ content: 'Updated post' }),
    });
    expect(response.status).toBe(200);
    const updatedPost = await response.json() as PostResponse;
    expect(updatedPost.content).toBe('Updated post');
  });

  test('DELETE /api/v1/posts/{post_id} - should delete a post', async () => {
    const newPost = await createPost(headers, 'A post to be deleted');
    const response = await fetch(`${API_BASE_URL}/api/v1/posts/${newPost.id}`, {
      method: 'DELETE',
      headers,
    });
    expect(response.status).toBe(200);

    const getResponse = await fetch(`${API_BASE_URL}/api/v1/posts/${newPost.id}`, {
      headers,
    });
    expect(getResponse.status).toBe(404);
  });
});
