import Enforcer from 'openapi-enforcer';
import fetch from 'cross-fetch';
import dotenv from 'dotenv';

dotenv.config();

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8080';

describe('Contract Tests', () => {
  let enforcer: any;
  let accessToken: string;

  beforeAll(async () => {
    const response = await fetch(`${API_BASE_URL}/openapi.json`);
    const openapiDoc = await response.json();
    enforcer = await Enforcer(openapiDoc, {
      dereference: true,
    });

    const email = `testuser_${Date.now()}@example.com`;
    const password = 'testpassword';

    await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        email,
        password,
        nickname: 'testuser',
        first_name: 'Test',
        last_name: 'User',
       })
    });

    const loginResponse = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: `username=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`,
    });
    const tokenData = await loginResponse.json();
    accessToken = tokenData.access_token;
  }, 60000);

  test('GET /api/v1/sports - should return a valid list of sports', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/sports`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    });
    const body = await response.json();

    const { error: validationError } = enforcer.v2.response({
        path: '/api/v1/sports',
        method: 'get',
        statusCode: response.status,
        body: body
    });

    expect(validationError).toBeUndefined();

    expect(response.status).toBe(200);
    expect(Array.isArray(body.data)).toBe(true);
  });

  test('POST /api/v1/posts - should create a post', async () => {
    const postData = {
      content: 'This is a test post from contract tests!',
    };

    const response = await fetch(`${API_BASE_URL}/api/v1/posts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`
      },
      body: JSON.stringify(postData)
    });

    const body = await response.json();
    const { error } = enforcer.v2.response({
        path: '/api/v1/posts',
        method: 'post',
        statusCode: response.status,
        body: body
    });

    expect(error).toBeUndefined();
    expect(response.status).toBe(201);
    expect(body.content).toBe(postData.content);
  });
});
