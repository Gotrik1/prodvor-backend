
import fetch, { Response } from 'node-fetch';

const API_BASE_URL = 'http://localhost:8080';

// Типы для ответов API
export type TokenResponse = {
  access_token: string;
  refresh_token: string;
  token_type: string;
};

export type UserResponse = {
  id: string;
  email: string;
  nickname: string;
  first_name: string;
  last_name: string;
};

export type Member = {
    id: string;
    email: string;
    nickname: string;
    first_name: string;
    last_name: string;
  };

export type TeamResponse = {
  id: string;
  name: string;
  owner_id: string;
  members: Member[];
  logoUrl: string | null;
  description: string | null;
  game: string | null;
  city: string | null;
  rank: string | null;
  owner: UserResponse;
  created_at: string;
  updated_at: string;
};

export type PostResponse = {
  id: string;
  content: string;
  author_id: string;
}

export type CommentResponse = {
  id: string;
  text: string;
  authorId: string;
  postId: string;
}

export type LikeResponse = {
    id: string;
    user_id: string;
    post_id: string;
}

export type LikeCountResponse = {
    count: number;
}

export type FriendRequestResponse = {
  id: string;
  requester_id: string;
  receiver_id: string;
  status: 'pending' | 'accepted' | 'declined';
  created_at: string;
}

export type PaginatedUsersResponse = {
  meta: {
    total: number;
    limit: number;
    offset: number;
  };
  data: UserResponse[];
}

export type PaginatedTeamResponse = {
  meta: {
    total: number;
    limit: number;
    offset: number;
  };
  data: TeamResponse[];
}

export type ApplicationResponse = {
    id: string;
    user_id: string;
    team_id: string;
    status: string;
}

export type PaginatedApplicationResponse = {
  meta: {
    total: number;
    limit: number;
    offset: number;
  };
  data: ApplicationResponse[];
}

export type FollowingResponse = {
  users: PaginatedUsersResponse;
  teams: {
      meta: {
          total: number;
          limit: number;
          offset: number;
      };
      data: TeamResponse[];
  };
};

export type PlaygroundResponse = {
  id: string;
  name: string;
  location: string;
}

export type SportResponse = {
  id: string;
  name: string;
  description: string;
}

export type InvitationResponse = {
  id: string;
  user_id: string;
  team_id: string;
  status: string;
}

export type LfgResponse = {
  id: number;
  sport: string;
  description: string;
  required_players: number;
  creator_id: string;
  type: string | null;
  team_id: string | null;
}

export type SubscriptionStatusResponse = {
  is_following: boolean;
};

export type SubscriptionResponse = {
    id: number;
    user_id: string;
    team_id: string;
}

export type PaginatedSubscriptionResponse = {
    meta: {
        total: number;
        limit: number;
        offset: number;
    };
    data: SubscriptionResponse[];
}

export type NotificationResponse = {
  id: number;
  user_id: string;
  message: string;
  is_read: boolean;
  created_at: string;
  updated_at: string;
};


/**
 * Генерирует уникального пользователя и возвращает его данные и токен для авторизации.
 */
export async function createUniqueUser(baseNickname: string) {
  const uniqueId = Date.now() + Math.random();
  const email = `${baseNickname}_${uniqueId}@example.com`;
  const nickname = `${baseNickname}_${uniqueId}`;
  const password = 'strongpassword';

  const registerResponse = await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email,
      password,
      nickname,
      first_name: 'Test',
      last_name: 'User',
    }),
  });

  if (registerResponse.status !== 200) {
    const errorBody = await registerResponse.text();
    throw new Error(`Failed to register user ${nickname}. Status: ${registerResponse.status}, Body: ${errorBody}`);
  }
  const user = await registerResponse.json() as UserResponse;

  const loginResponse = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: `username=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`,
  });
  
  if (loginResponse.status !== 200) {
    const errorBody = await loginResponse.text();
    throw new Error(`Failed to login user ${nickname}. Status: ${loginResponse.status}, Body: ${errorBody}`);
  }

  const tokens = await loginResponse.json() as TokenResponse;

  return {
    user,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${tokens.access_token}`,
    },
    refreshToken: tokens.refresh_token,
  };
}

/**
 * Создает уникальное имя для команды.
 */
export function createUniqueName(baseName: string): string {
    return `${baseName} ${Date.now()}${Math.random()}`;
}

export async function createTeam(headers: any, name: string): Promise<TeamResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/teams`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ name }),
  });
  if (response.status !== 200) {
    const errorBody = await response.text();
    throw new Error(`Failed to create team. Status: ${response.status}, Body: ${errorBody}`);
  }
  return await response.json() as TeamResponse;
}

export async function applyToTeam(headers: any, team_id: string): Promise<ApplicationResponse> {
    const response = await fetch(`${API_BASE_URL}/api/v1/teams/${team_id}/apply`, {
        method: 'POST',
        headers,
    });
    if (response.status !== 200) {
        const errorBody = await response.text();
        throw new Error(`Failed to apply to team. Status: ${response.status}, Body: ${errorBody}`);
    }
    return await response.json() as ApplicationResponse;
}

export async function createLFG(headers: any, sport: string, description: string, required_players: number, creator_id: string): Promise<LfgResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/lfg`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ sport, description, required_players, creator_id }),
  });
  if (response.status !== 200) {
    const errorBody = await response.text();
    throw new Error(`Failed to create LFG. Status: ${response.status}, Body: ${errorBody}`);
  }
  return await response.json() as LfgResponse;
}

export async function createPost(headers: any, content: string): Promise<PostResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/posts`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ content }),
  });
  if (response.status !== 200) {
    const errorBody = await response.text();
    throw new Error(`Failed to create post. Status: ${response.status}, Body: ${errorBody}`);
  }
  return await response.json() as PostResponse;
}

export async function createComment(headers: any, postId: string, text: string): Promise<CommentResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/comments`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ postId, text }),
  });
  if (response.status !== 200) {
    const errorBody = await response.text();
    throw new Error(`Failed to create comment. Status: ${response.status}, Body: ${errorBody}`);
  }
  return await response.json() as CommentResponse;
}

export async function sendFriendRequest(headers: any, to_user_id: string): Promise<FriendRequestResponse> {
    const response = await fetch(`${API_BASE_URL}/api/v1/friend-requests`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ to_user_id }),
    });
    if (response.status !== 200) {
        const errorBody = await response.text();
        throw new Error(`Failed to send friend request. Status: ${response.status}, Body: ${errorBody}`);
    }
    return await response.json() as FriendRequestResponse;
}

export async function getReceivedFriendRequests(headers: any): Promise<FriendRequestResponse[]> {
    const response = await fetch(`${API_BASE_URL}/api/v1/friend-requests/received`, {
        headers,
    });
    if (response.status !== 200) {
        const errorBody = await response.text();
        throw new Error(`Failed to get received friend requests. Status: ${response.status}, Body: ${errorBody}`);
    }
    return await response.json() as FriendRequestResponse[];
}

export async function acceptFriendRequest(headers: any, request_id: string): Promise<FriendRequestResponse> {
    const response = await fetch(`${API_BASE_URL}/api/v1/friend-requests/${request_id}/accept`, {
        method: 'PUT',
        headers,
    });
    if (response.status !== 200) {
        const errorBody = await response.text();
        throw new Error(`Failed to accept friend request. Status: ${response.status}, Body: ${errorBody}`);
    }
    return await response.json() as FriendRequestResponse;
}

export async function getFriends(headers: any): Promise<PaginatedUsersResponse> {
    const response = await fetch(`${API_BASE_URL}/api/v1/friend-requests/friends`, {
        headers,
    });
    if (response.status !== 200) {
        const errorBody = await response.text();
        throw new Error(`Failed to get friends. Status: ${response.status}, Body: ${errorBody}`);
    }
    return await response.json() as PaginatedUsersResponse;
}

export async function subscribeToTeam(headers: any, team_id: string): Promise<Response> {
  const response = await fetch(`${API_BASE_URL}/api/v1/subscriptions/subscribe`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ team_id }),
  });
  if (response.status !== 204) {
    const errorBody = await response.text();
    throw new Error(`Failed to subscribe. Status: ${response.status}, Body: ${errorBody}`);
  }
  return response;
}

export async function cleanup() {
  // TODO: Implement cleanup logic
}
