
import fetch from 'node-fetch';
import { 
  createUniqueUser, 
  cleanup, 
  UserResponse, 
  sendFriendRequest, 
  acceptFriendRequest, 
  PaginatedUsersResponse, 
  createTeam, 
  createUniqueName, 
  subscribeToTeam, 
  FollowingResponse 
} from './helpers';

describe('Users API', () => {
  const API_BASE_URL = 'http://localhost:8080';

  afterAll(async () => {
    await cleanup();
  });

  test('GET /api/v1/users/me - should retrieve the current user details', async () => {
    const { user, headers } = await createUniqueUser('users_test_me');
    const response = await fetch(`${API_BASE_URL}/api/v1/users/me`, {
      headers,
    });
    expect(response.status).toBe(200);
    const me = await response.json() as UserResponse;
    expect(me.id).toBe(user.id);
    expect(me.email).toBe(user.email);
  });

  test('GET /api/v1/users/{user_id} - should retrieve a specific user details', async () => {
    const { user: user1, headers } = await createUniqueUser('users_test_1');
    const { user: user2 } = await createUniqueUser('users_test_2');
    
    const response = await fetch(`${API_BASE_URL}/api/v1/users/${user2.id}`, {
      headers,
    });
    expect(response.status).toBe(200);
    const foundUser = await response.json() as UserResponse;
    expect(foundUser.id).toBe(user2.id);
    expect(foundUser.nickname).toBe(user2.nickname);
  });

  test('GET /api/v1/users/{user_id}/friends - should list user friends', async () => {
      const { user: user1, headers: headers1 } = await createUniqueUser('users_test_friends1');
      const { user: user2, headers: headers2 } = await createUniqueUser('users_test_friends2');
      const { user: user3 } = await createUniqueUser('users_test_friends3');

      const fr1 = await sendFriendRequest(headers1, user2.id);
      await acceptFriendRequest(headers2, fr1.id);

      await sendFriendRequest(headers1, user3.id);
      
      const response = await fetch(`${API_BASE_URL}/api/v1/users/${user1.id}/friends`, {
        headers: headers1,
      });

      expect(response.status).toBe(200);
      const friendsResponse = await response.json() as PaginatedUsersResponse;
      const friends = friendsResponse.data;
      
      expect(Array.isArray(friends)).toBe(true);
      expect(friends.length).toBe(1);
      expect(friends[0].id).toBe(user2.id);
  });

  test('GET /api/v1/users/{user_id}/followers - should read user followers', async () => {
    const { user: user1, headers: headers1 } = await createUniqueUser('users_test_followers1');
    const { user: user2 } = await createUniqueUser('users_test_followers2');

    await sendFriendRequest(headers1, user2.id);

    const response = await fetch(`${API_BASE_URL}/api/v1/users/${user2.id}/followers`, {
      headers: headers1,
    });

    expect(response.status).toBe(200);
    const followersResponse = await response.json() as PaginatedUsersResponse;
    expect(followersResponse.data.length).toBe(1);
    expect(followersResponse.data[0].id).toBe(user1.id);
  });

  test('GET /api/v1/users/{user_id}/following - should read user following', async () => {
    const { user: user1, headers: headers1 } = await createUniqueUser('users_test_following1');
    const team = await createTeam(headers1, createUniqueName('following_team'));

    await subscribeToTeam(headers1, team.id);

    const response = await fetch(`${API_BASE_URL}/api/v1/users/${user1.id}/following`, {
      headers: headers1,
    });

    expect(response.status).toBe(200);
    const followingResponse = await response.json() as FollowingResponse;
    
    expect(followingResponse.users.data.length).toBe(0);
    expect(followingResponse.teams.data.length).toBe(1);
    expect(followingResponse.teams.data[0].id).toBe(team.id);
  });
});
