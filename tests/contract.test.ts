import Enforcer from 'openapi-enforcer';
import path from 'path';
import fetch from 'cross-fetch';
import dotenv from 'dotenv';

dotenv.config();

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:5000';

describe('Contract Tests', () => {
  let enforcer: any; 

  beforeAll(async () => {
    const openapiPath = path.resolve(__dirname, '../openapi.yaml');
    enforcer = await Enforcer(openapiPath, {
      dereference: true,
    });
  });

  test('GET /api/v1/sports/sports - should return a valid list of sports', async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/sports/sports`);
    const body = await response.json();

    const { error: validationError } = enforcer.response({
        path: '/api/v1/sports/sports',
        method: 'get',
        statusCode: response.status,
        body: body
    });

    expect(validationError).toBeUndefined();

    expect(response.status).toBe(200);
    expect(Array.isArray(body.data)).toBe(true);
    expect(body.data.length).toBeGreaterThan(0);
    expect(body.data[0]).toHaveProperty('id');
    expect(body.data[0]).toHaveProperty('name');
  });

  // TODO: Добавить тесты для других эндпоинтов (POST, GET by ID, и т.д.)
  // Пример для POST-запроса с аутентификацией:
  /*
  test('POST /api/v1/posts/posts - should create a post', async () => {
    const accessToken = '...'; // Получить токен через /login
    const postData = {
      content: 'This is a test post from contract tests!',
    };

    const response = await fetch(`${API_BASE_URL}/api/v1/posts/posts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`
      },
      body: JSON.stringify(postData)
    });

    const body = await response.json();
    const { error } = enforcer.response({
        path: '/api/v1/posts/posts',
        method: 'post',
        statusCode: response.status,
        body: body
    });

    expect(error).toBeUndefined();
    expect(response.status).toBe(201);
    expect(body.content).toBe(postData.content);
  });
  */
});
