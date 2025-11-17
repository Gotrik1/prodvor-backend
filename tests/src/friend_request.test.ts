
import fetch from 'node-fetch';
import { createUniqueUser, cleanup, UserResponse, sendFriendRequest, getReceivedFriendRequests, acceptFriendRequest, getFriends, FriendRequestResponse } from './helpers';

describe('Friend Requests API', () => {
  const API_BASE_URL = 'http://localhost:8080';

  afterAll(async () => {
    await cleanup();
  });

  test('POST /api/v1/friend-requests - should send a friend request', async () => {
    const { user: user1, headers: headers1 } = await createUniqueUser('fr_test_user1');
    const { user: user2 } = await createUniqueUser('fr_test_user2');

    const friendRequest = await sendFriendRequest(headers1, user2.id);
    expect(friendRequest.requester_id).toBe(user1.id);
    expect(friendRequest.receiver_id).toBe(user2.id);
    expect(friendRequest.status).toBe('pending');
  });

  test('PUT /api/v1/friend-requests/{request_id}/accept - should accept a friend request', async () => {
    const { user: user1, headers: headers1 } = await createUniqueUser('fr_test_user3');
    const { user: user2, headers: headers2 } = await createUniqueUser('fr_test_user4');

    // user1 sends a friend request to user2
    await sendFriendRequest(headers1, user2.id);
    // user2 gets their received friend requests
    const receivedRequests = await getReceivedFriendRequests(headers2);
    const requestFromUser1 = receivedRequests.find(req => req.requester_id === user1.id);
    expect(requestFromUser1).toBeDefined();

    // user2 accepts the friend request from user1
    const acceptedRequest = await acceptFriendRequest(headers2, requestFromUser1!.id);
    expect(acceptedRequest.status).toBe('accepted');
  });

  test('PUT /api/v1/friend-requests/{request_id}/decline - should decline a friend request', async () => {
    const { user: user1, headers: headers1 } = await createUniqueUser('fr_test_user5');
    const { user: user3, headers: headers3 } = await createUniqueUser('fr_test_user6');

    // user1 sends a friend request to user3
    await sendFriendRequest(headers1, user3.id);
    // user3 gets their received friend requests
    const receivedRequests = await getReceivedFriendRequests(headers3);
    const requestFromUser1 = receivedRequests.find(req => req.requester_id === user1.id);
    expect(requestFromUser1).toBeDefined();

    // user3 declines the friend request from user1
    const response = await fetch(`${API_BASE_URL}/api/v1/friend-requests/${requestFromUser1!.id}/decline`, {
        method: 'PUT',
        headers: headers3,
    });
    expect(response.status).toBe(200);
    const declinedRequest = await response.json() as FriendRequestResponse;
    expect(declinedRequest.status).toBe('declined');
  });

  test('GET /api/v1/friend-requests/friends - should get a list of friends', async () => {
    const { user: user1, headers: headers1 } = await createUniqueUser('fr_test_user7');
    const { user: user4, headers: headers4 } = await createUniqueUser('fr_test_user8');

    // user1 sends a friend request to user4
    const fr = await sendFriendRequest(headers1, user4.id);
    // user4 accepts the friend request from user1
    await acceptFriendRequest(headers4, fr.id);

    // user1 should have user4 as a friend
    const friends = await getFriends(headers1);
    expect(friends.data.some(friend => friend.id === user4.id)).toBe(true);
  });

  test('POST /api/v1/friend-requests - should not send a friend request to oneself', async () => {
    const { user: user1, headers: headers1 } = await createUniqueUser('fr_test_user9');

    const response = await fetch(`${API_BASE_URL}/api/v1/friend-requests`, {
        method: 'POST',
        headers: headers1,
        body: JSON.stringify({ receiver_id: user1.id }),
    });
    expect(response.status).toBe(400);
  });

  test('POST /api/v1/friend-requests - should not send a duplicate friend request', async () => {
    const { user: user1, headers: headers1 } = await createUniqueUser('fr_test_user10');
    const { user: user5 } = await createUniqueUser('fr_test_user11');

    // user1 sends a friend request to user5
    await sendFriendRequest(headers1, user5.id);

    // user1 tries to send another friend request to user5
    const response = await fetch(`${API_BASE_URL}/api/v1/friend-requests`, {
        method: 'POST',
        headers: headers1,
        body: JSON.stringify({ receiver_id: user5.id }),
    });
    expect(response.status).toBe(400);
  });

  test('GET /api/v1/friend-requests/received - should get a list of received friend requests', async () => {
    const { user: user1, headers: headers1 } = await createUniqueUser('fr_test_user12');
    const { user: user2, headers: headers2 } = await createUniqueUser('fr_test_user13');

    // user1 sends a friend request to user2
    await sendFriendRequest(headers1, user2.id);

    // user2 gets their received friend requests
    const receivedRequests = await getReceivedFriendRequests(headers2);
    const requestFromUser1 = receivedRequests.find(req => req.requester_id === user1.id);
    expect(requestFromUser1).toBeDefined();
    expect(receivedRequests.length).toBe(1);
  });
});
