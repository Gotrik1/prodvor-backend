
import fetch from 'node-fetch';
import { createUniqueUser, createPost, cleanup, PostResponse, LikeResponse, LikeCountResponse } from './helpers';

describe('Likes API', () => {
  const API_BASE_URL = 'http://localhost:8080';
  let user: any, headers: any, post: any;

  beforeAll(async () => {
    const { user: testUser, headers: testHeaders } = await createUniqueUser('likes_test_user');
    user = testUser;
    headers = testHeaders;
    post = await createPost(headers, 'Test post for likes');
  });

  afterAll(async () => {
    await cleanup();
  });

  test('POST /api/v1/likes - should like a post', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/likes`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ post_id: post.id }),
    });
    expect(response.status).toBe(200);
    const like = await response.json() as LikeResponse;
    expect(like.user_id).toBe(user.id);
    expect(like.post_id).toBe(post.id);
  });

  test('DELETE /api/v1/likes/{post_id} - should unlike a post', async () => {
    // First, like the post
    await fetch(`${API_BASE_URL}/api/v1/likes`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ post_id: post.id }),
    });

    // Then, unlike it
    const response = await fetch(`${API_BASE_URL}/api/v1/likes/${post.id}`, {
      method: 'DELETE',
      headers,
    });
    expect(response.status).toBe(200);
  });

  test('GET /api/v1/likes/post/{post_id}/count - should get like count for a post', async () => {
    const newPost = await createPost(headers, 'Post for like count');
    // Like the post
    await fetch(`${API_BASE_URL}/api/v1/likes`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ post_id: newPost.id }),
    });

    const response = await fetch(`${API_BASE_URL}/api/v1/likes/post/${newPost.id}/count`, {
      headers,
    });
    expect(response.status).toBe(200);
    const likeCount = await response.json() as LikeCountResponse;
    expect(likeCount.count).toBe(1);
  });

  test('GET /api/v1/likes/user/{user_id}/liked-posts - should get liked posts by user', async () => {
    const newPost = await createPost(headers, 'Another post to be liked');
    // Like the post
    await fetch(`${API_BASE_URL}/api/v1/likes`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ post_id: newPost.id }),
    });

    const response = await fetch(`${API_BASE_URL}/api/v1/likes/user/${user.id}/liked-posts`, {
        headers,
    });
    expect(response.status).toBe(200);
    const likedPosts = await response.json() as PostResponse[];
    expect(likedPosts.some(p => p.id === newPost.id)).toBe(true);
  });
});
