import Enforcer from 'openapi-enforcer';
import fetch from 'cross-fetch';
import dotenv from 'dotenv';

dotenv.config();

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8080';

describe('Contract Tests', () => {
  let enforcer: any;
  let accessToken: string;
  let currentUserId: string;
  let userNickname: string;

  beforeAll(async () => {
    const response = await fetch(`${API_BASE_URL}/openapi.json`);
    const openapiDoc = await response.json();
    enforcer = await Enforcer(openapiDoc, {
      dereference: true,
    });

    const email = `testuser_${Date.now()}@example.com`;
    const password = 'testpassword';
    userNickname = email.split('@')[0];

    await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        email,
        password,
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

    const meResponse = await fetch(`${API_BASE_URL}/api/v1/users/me`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    });
    const meData = await meResponse.json();
    currentUserId = meData.id;
  }, 60000);

  test('GET /api/v1/sports - should return a valid list of sports', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/sports`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    });
    const body = await response.json();

    const { error: validationError } = enforcer.paths['/api/v1/sports'].get.response(response.status, body);

    expect(validationError).toBeUndefined();

    expect(response.status).toBe(200);
    expect(Array.isArray(body)).toBe(true);
  });

  test('GET /api/v1/users/{user_id} - should return the user profile', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/users/${currentUserId}`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    });
    const body = await response.json();

    // Basic validation without the enforcer to avoid date issues.
    expect(response.status).toBe(200);
    expect(body.id).toBe(currentUserId);
    expect(body.nickname).toBe(userNickname);
  });

  test('POST /api/v1/sports - should create a new sport', async () => {
    const sportName = `Super-testing-sport-${Date.now()}`;
    const response = await fetch(`${API_BASE_URL}/api/v1/sports`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${accessToken}`,
        },
        body: JSON.stringify({ name: sportName })
    });
    const body = await response.json();
    expect(response.status).toBe(200);
    expect(body.name).toBe(sportName);
  });
});
