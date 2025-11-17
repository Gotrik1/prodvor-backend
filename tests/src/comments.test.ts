
import fetch from 'node-fetch';
import { createUniqueUser, createPost, createComment, cleanup, CommentResponse } from './helpers';

describe('Comments API', () => {
  const API_BASE_URL = 'http://localhost:8080';
  let user: any, headers: any, post: any;

  beforeAll(async () => {
    const { user: testUser, headers: testHeaders } = await createUniqueUser('comments_test_user');
    user = testUser;
    headers = testHeaders;
    post = await createPost(headers, 'Test post for comments');
  });

  afterAll(async () => {
    await cleanup();
  });

  test('POST /api/v1/comments - should create a comment', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/comments`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ postId: post.id, text: 'First comment' }),
    });
    expect(response.status).toBe(200);
    const comment = await response.json() as CommentResponse;
    expect(comment.text).toBe('First comment');
    expect(comment.authorId).toBe(user.id);
  });

  test('GET /api/v1/comments/{comment_id} - should retrieve a comment', async () => {
    const newComment = await createComment(headers, post.id, 'A comment to be retrieved');
    const response = await fetch(`${API_BASE_URL}/api/v1/comments/${newComment.id}`, {
      headers,
    });
    expect(response.status).toBe(200);
    const comment = await response.json() as CommentResponse;
    expect(comment.id).toBe(newComment.id);
  });

  test('GET /api/v1/comments/post/{post_id} - should retrieve all comments for a post', async () => {
    const newPost = await createPost(headers, 'Post with multiple comments');
    await createComment(headers, newPost.id, 'Comment 1');
    await createComment(headers, newPost.id, 'Comment 2');

    const response = await fetch(`${API_BASE_URL}/api/v1/comments/post/${newPost.id}`, {
      headers,
    });
    expect(response.status).toBe(200);
    const comments = await response.json() as CommentResponse[];
    expect(comments.length).toBe(2);
  });

  test('PUT /api/v1/comments/{comment_id} - should update a comment', async () => {
    const newComment = await createComment(headers, post.id, 'Original comment');
    const response = await fetch(`${API_BASE_URL}/api/v1/comments/${newComment.id}`, {
      method: 'PUT',
      headers,
      body: JSON.stringify({ text: 'Updated comment', postId: post.id }),
    });
    expect(response.status).toBe(200);
    const updatedComment = await response.json() as CommentResponse;
    expect(updatedComment.text).toBe('Updated comment');
  });

  test('DELETE /api/v1/comments/{comment_id} - should delete a comment', async () => {
    const newComment = await createComment(headers, post.id, 'A comment to be deleted');
    const response = await fetch(`${API_BASE_URL}/api/v1/comments/${newComment.id}`, {
      method: 'DELETE',
      headers,
    });
    expect(response.status).toBe(200);

    const getResponse = await fetch(`${API_BASE_URL}/api/v1/comments/${newComment.id}`, {
      headers,
    });
    expect(getResponse.status).toBe(404);
  });
});
