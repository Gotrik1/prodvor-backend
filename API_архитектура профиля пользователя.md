# ProDvor: API-архитектура страницы профиля пользователя

Этот документ описывает комплексную архитектуру API для страницы профиля пользователя, вдохновленную подходом крупных социальных платформ (например, ВКонтакте).

**Цель:** Создать гибкое, безопасное и масштабируемое API, которое сможет:
- Отдавать все необходимые данные для отображения публичной и приватной частей профиля.
- Поддерживать обновление настроек пользователя.
- Возвращать связанные сущности (команды, друзья, достижения) с учетом прав доступа.
- Работать через JWT-токен для аутентифицированных запросов.

---

## 1. Схема данных (ER-диаграмма)

В основе лежит принцип разделения данных на логические сущности, связанные между собой.

```mermaid
erDiagram
    User {
        string id PK
        string nickname
        string email
        string avatarUrl
        string coverImageUrl
        string bio
        -- и другие базовые поля --
    }

    UserSettings {
        string userId PK, FK
        string theme
        string language
        -- другие настройки интерфейса --
    }

    UserPrivacy {
        string userId PK, FK
        string profile_visibility
        string teams_visibility
        string friends_visibility
    }

    PlayerProfile {
        string userId PK, FK
        int elo
        int matchesPlayed
        int wins
    }

    Friendship {
        string userId1 PK, FK
        string userId2 PK, FK
        string status
    }

    TeamMembership {
        string userId PK, FK
        string teamId PK, FK
        string role
    }

    Team {
        string id PK
        string name
        string logoUrl
    }

    Achievement {
        string id PK
        string name
        string description
        string icon
    }

    UserAchievement {
        string userId PK, FK
        string achievementId PK, FK
        datetime unlockedAt
    }

    Media {
        string id PK
        string userId FK
        string type
        string url
    }

    User ||--o{ UserSettings : "has"
    User ||--o{ UserPrivacy : "has"
    User ||--o{ PlayerProfile : "has"
    User }o--o{ Friendship : "many-to-many"
    User }o--o{ TeamMembership : "many-to-many"
    Team }o--o{ TeamMembership : "many-to-many"
    User }o--o{ UserAchievement : "many-to-many"
    Achievement }o--o{ UserAchievement : "many-to-many"
    User ||--o{ Media : "has"

```

**Связи many-to-many:**
- **`User` <-> `User` (через `Friendship`):** Дружеские связи.
- **`User` <-> `Team` (через `TeamMembership`):** Членство в командах.
- **`User` <-> `Achievement` (через `UserAchievement`):** Полученные достижения.

---

## 2. Архитектура API

### 2.1. Основные эндпоинты

- **`GET /api/v1/users/:id`**: **[Публичный]** Получение публичной информации о пользователе.
  - **Ответ:** Базовые данные из `User`, `PlayerProfile`, счетчики (`counters`) и публичные связанные сущности.
- **`GET /api/v1/users/me`**: **[Приватный]** Получение полной информации о текущем аутентифицированном пользователе.
  - **Ответ:** Полный объект `User`, все связанные профили, настройки, счетчики и т.д.
- **`PATCH /api/v1/users/me`**: **[Приватный]** Частичное обновление основной информации о пользователе (имя, `bio` и т.д.).
- **`PATCH /api/v1/users/me/settings`**: **[Приватный]** Обновление настроек интерфейса.
- **`PATCH /api/v1/users/me/privacy`**: **[Приватный]** Обновление настроек приватности.

### 2.2. Вложенные ресурсы

Для получения списков используются отдельные эндпоинты с пагинацией (`limit`, `offset`).

- **`GET /api/v1/users/:id/friends`**: **[Приватность: `friends_visibility`]** Получить список друзей пользователя.
- **`GET /api/v1/users/:id/teams`**: **[Приватность: `teams_visibility`]** Получить список команд пользователя.
- **`GET /api/v1/users/:id/achievements`**: **[Публичный]** Получить список достижений.
- **`GET /api/v1/users/:id/photos`**: **[Приватность: `media_visibility`]** Получить список фотографий.
- **`GET /api/v1/users/:id/posts`**: **[Публичный/Приватный]** Получить посты со стены пользователя.

### 2.3. Фильтры и сортировки

- **`?section=`**: Позволяет запрашивать только определенные блоки данных для оптимизации.
  - Пример: `GET /api/v1/users/me?section=counters,friends` вернет только счетчики и краткий список друзей.
- **`?tab=`**: Используется для получения данных под конкретную вкладку на фронтенде.
  - Пример: `GET /api/v1/users/:id?tab=stats` вернет расширенную игровую статистику.

---

## 3. Архитектура бэкенда

- **Контроллеры (`Controllers`):** Принимают HTTP-запросы, валидируют входные данные и вызывают соответствующие сервисы.
- **Сервисы (`Services`):** Содержат основную бизнес-логику. Например, `UserService` будет содержать метод `getUserProfile(userId, requestingUserId)`, который агрегирует данные из разных репозиториев.
- **Репозитории/Модели (`Repositories/Models`):** Отвечают за прямое взаимодействие с базой данных (SQLAlchemy модели).
- **DTO (Data Transfer Objects):** Объекты для передачи данных между слоями и для формирования ответа API. Это позволяет отделить внутреннюю структуру моделей от того, что видит клиент.
- **Middleware:** Прослойки для обработки каждого запроса.
  - **`AuthMiddleware`**: Проверяет JWT-токен и добавляет информацию о пользователе в контекст запроса.
  - **`PrivacyMiddleware`**: (В перспективе) Может проверять права доступа к запрашиваемому ресурсу на уровне роутинга.

---

## 4. Пример ответа `GET /api/v1/users/:id`

Это пример того, что бэкенд должен вернуть по запросу для построения страницы профиля.

```json
{
  "profile": {
    "id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
    "firstName": "Иван",
    "lastName": "Иванов",
    "nickname": "IvanTheGreat",
    "avatarUrl": "https://...",
    "coverImageUrl": "https://...",
    "role": "Игрок",
    "city": "Москва",
    "bio": "Люблю футбол и свою команду!",
    "elo": 1550,
    "onlineInfo": {
      "isOnline": true,
      "lastSeen": "2025-10-27T10:00:00Z"
    }
  },
  "stats": {
    "player_profile": {
      "matchesPlayed": 120,
      "wins": 79,
      "goals": 76,
      "assists": 37,
      "mvpAwards": 30
    },
    "progress": {
      "points": 8500,
      "level": 9
    }
  },
  "counters": {
    "friends": 54,
    "followers": 128,
    "teams": 1,
    "photos": 23,
    "posts": 42,
    "achievements": 5
  },
  "friends": {
    "count": 54,
    "items": [
      { "id": "user2", "nickname": "PlayerTwo", "avatarUrl": "..." },
      { "id": "user3", "nickname": "PlayerThree", "avatarUrl": "..." }
    ]
  },
  "teams": {
    "count": 1,
    "items": [
      { "id": "team1", "name": "Ночные Снайперы", "logoUrl": "..." }
    ]
  },
  "achievements": {
    "count": 5,
    "items": [
      { "id": "ach-fb-1", "name": "Первый гол", "icon": "Star" },
      { "id": "ach-fb-2", "name": "Хет-трик", "icon": "Target" }
    ]
  },
  "privacy": {
    "can_post": true,
    "can_write_private_message": true,
    "can_send_friend_request": false
  },
  "profile_buttons": [
    { "action": { "type": "friend_request", "status": "already_friend" }, "text": "Вы друзья" },
    { "action": { "type": "write_message" }, "text": "Сообщение" },
    { "action": { "type": "more_options" }, "text": "..." }
  ]
}
```

---

## 5. Спецификация безопасности

- **Аутентификация:** Все приватные маршруты (`/me`, `PATCH`-запросы) должны быть защищены с помощью **JWT Bearer** токена.
- **Публичные маршруты:** `GET /users/:id`, `GET /teams/:id` и другие роуты для получения публичной информации. Бэкенд должен проверять права доступа к полям на основе настроек приватности пользователя, чей профиль запрашивается.
- **CORS:** Настроить на уровне бэкенда, чтобы разрешать запросы с домена фронтенда.
- **Rate Limiting:** Применить ограничение на количество запросов к API (например, 100 запросов в минуту на IP) для защиты от DDoS-атак.
- **Хранение медиа:** Все приватные медиафайлы (например, фото из закрытого профиля) должны храниться в приватном S3-бакете. Доступ к ним должен предоставляться через **краткосрочные presigned URLs**, которые бэкенд генерирует только для авторизованных пользователей.

---

## 6. Интеграция с фронтендом (Next.js)

1.  **API-клиент:** Фронтенд использует `axios` и автоматически сгенерированный клиент (через `openapi-generator-cli`) для типобезопасных запросов к API.
2.  **Загрузка данных:** Для получения данных профиля используется хук (например, `useSWR` или `react-query`) или `getServerSideProps`/`React Server Components`.
    ```typescript
    // Пример хука для загрузки данных
    function useUserProfile(userId) {
      const { data, error } = useSWR(`/api/v1/users/${userId}`, fetcher);
      return { userProfile: data, isLoading: !error && !data, isError: error };
    }
    ```
3.  **Рендеринг:**
    - Компонент страницы `[id].tsx` вызывает хук `useUserProfile`.
    - Пока данные загружаются, отображается скелетон (заглушка).
    - После загрузки данные из объекта `userProfile` распределяются по виджетам: `ProfileHeader`, `StatsWidget`, `FriendsWidget` и т.д.
    - Массивы (`friends`, `teams`) используются для рендеринга первых нескольких элементов, а для просмотра полного списка делается отдельный запрос на соответствующий вложенный ресурс.

Этот подход обеспечивает быстрый первый рендер страницы и позволяет догружать "тяжелые" данные по мере необходимости.
