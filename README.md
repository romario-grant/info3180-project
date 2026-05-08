# 🌊 Drift — Date Matching Application

> A full-stack dating web application built with Vue 3 and Flask for INFO3180 Group Project 2025/2026.

---

## Team Members & Roles

| Name | Role | Responsibilities |
|---|---|---|
| Romario Grant | Project Manager | Timeline oversight, coordination, GitHub management |
| Shaznay Walker | QA/Testing Lead | Validation, documentation |
| Christina Blye | Backend Lead | Flask API, database design, authentication, security |
| Joshua Henry | Frontend Lead | Vue 3 components, UI/UX, routing, state management |
| Kye Brathwaite | QA/Testing Lead | Test suite |



---

## Project Description

Drift is a dating application that allows registered users to create detailed profiles, discover compatible matches, and connect with other users. Users can browse potential matches sorted by a compatibility score, like or pass on profiles, message their mutual matches, and save favourite profiles.

### Key Features

- User registration and secure login with bcrypt password hashing
- Profile creation with photo upload, interests, location, and preferences
- Smart match scoring algorithm based on age compatibility, shared interests, location, and gender preference
- Like/Pass system with automatic mutual match detection
- Messaging restricted to matched users only
- Favorites/bookmarking system
- In-app notification system for match alerts
- Profile visibility controls (public/private)
- Browse with filtering by location, age range, gender, and interests

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Vue 3, Vite, Vue Router |
| Backend | Python 3, Flask |
| Database | SQLite (development) / PostgreSQL (production) |
| ORM | SQLAlchemy + Flask-Migrate |
| Auth | Flask Sessions + bcrypt |
| CORS | Flask-CORS |

---

## Setup Instructions

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm

---

### 1. Clone the Repository

```bash
git clone https://github.com/romario-grant/info3180-project.git
cd info3180-project
```

---

### 2. Backend Setup (Flask)

**Create and activate a virtual environment:**

```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
.\venv\Scripts\activate
```

**Install Python dependencies:**

```bash
pip install -r requirements.txt
```

**Create a `.env` file in the project root:**

```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///app.db
```

> For PostgreSQL in production, set `DATABASE_URL=postgresql://user:password@host/dbname`

**Initialize the database:**

```bash
flask --app app db upgrade
```

> If migrations folder is not present, run `flask --app app db init` then `flask --app app db migrate` first.

**Start the Flask server:**

```bash
python run.py
```

The API will be available at `http://localhost:5000`

---

### 3. Frontend Setup (Vue 3)

Open a **new terminal** in the project root:

```bash
npm install
npm run dev
```

The app will be available at `http://localhost:5173`

---

### 4. Running Tests

```bash
pip install pytest
pytest test_api.py -v
```

All 65 tests should pass.

---

## Database Schema

The application uses 9 normalized tables:

| Table | Description |
|---|---|
| `users` | Core account info — email, phone, hashed password |
| `profiles` | Extended profile data — name, age, bio, location, gender, preferences |
| `interests` | Unique interest tags (e.g. "hiking", "cooking") |
| `profile_interests` | Many-to-many join between profiles and interests |
| `likes` | Records of like/pass actions between users |
| `matches` | Created automatically when two users mutually like each other |
| `messages` | Chat messages between matched users |
| `favorites` | Bookmarked profiles |
| `notifications` | In-app alerts (e.g. match notifications) |

### Relationships

- A `User` has one `Profile` (one-to-one)
- A `Profile` has many `Interests` via `profile_interests` (many-to-many)
- A `User` can send many `Likes`; a mutual like creates a `Match`
- `Messages` belong to a `Match` and require a match to exist
- `Favorites` and `Notifications` belong to a `User`

---

## API Documentation

All endpoints are prefixed at `http://localhost:5000`. Authentication uses Flask sessions (cookie-based). Protected routes return `401` if not logged in.

---

### Authentication

#### `POST /signup`
Register a new user.

**Request body:**
```json
{
  "email": "user@example.com",
  "phone_number": "8681234567",
  "password": "securepassword"
}
```

**Success `201`:**
```json
{
  "message": "User registered successfully.",
  "user": { "id": 1, "email": "user@example.com", "phone_number": "8681234567" }
}
```

**Errors:** `400` missing fields, `409` email already exists

---

#### `POST /login`
Log in and start a session.

**Request body:**
```json
{ "email": "user@example.com", "password": "securepassword" }
```

**Success `200`:**
```json
{ "message": "Login successful.", "user": { "id": 1, "email": "user@example.com" } }
```

**Errors:** `400` missing fields, `401` invalid credentials

---

#### `POST /logout`
End the current session.

**Success `200`:**
```json
{ "message": "Logged out successfully." }
```

---

#### `GET /me`
Get the currently logged-in user.

**Success `200`:**
```json
{ "id": 1, "email": "user@example.com", "phone_number": "8681234567" }
```

---

### Profile

#### `GET /profile`
Get the logged-in user's full profile.

**Success `200`:**
```json
{
  "id": 1, "user_id": 1, "display_name": "Alice",
  "age": 25, "bio": "Hello!", "location": "Bridgetown",
  "gender": "female", "looking_for": "male",
  "visibility": "public", "profile_picture": "/uploads/abc123.jpg",
  "min_preferred_age": 22, "max_preferred_age": 35,
  "preferred_radius_km": 50,
  "interests": [{ "id": 1, "name": "hiking" }]
}
```

---

#### `PUT /profile`
Update the logged-in user's profile. All fields optional.

**Request body (any subset):**
```json
{
  "display_name": "Alice", "age": 25, "bio": "Hello!",
  "location": "Bridgetown", "gender": "female", "looking_for": "male",
  "visibility": "public", "min_preferred_age": 22, "max_preferred_age": 35,
  "preferred_radius_km": 50, "interests": ["hiking", "cooking", "reading"]
}
```

**Validation rules:**
- `age` must be 18 or older
- `visibility` must be `"public"` or `"private"`
- `min_preferred_age` cannot exceed `max_preferred_age`
- `interests` must contain at least 3 items

---

#### `POST /profile/photo`
Upload a profile picture. Accepts multipart form data with field `photo`.

**Accepted formats:** png, jpg, jpeg, webp (max 5MB)

**Success `200`:**
```json
{ "message": "Profile photo uploaded successfully.", "profile_picture": "/uploads/abc.jpg" }
```

---

### Browse & Discovery

#### `GET /profiles`
Browse public profiles (excludes yourself and anyone already liked/passed).

**Query parameters (all optional):**

| Parameter | Type | Description |
|---|---|---|
| `search` | string | Search by display name or bio |
| `location` | string | Filter by location |
| `min_age` | integer | Minimum age filter |
| `max_age` | integer | Maximum age filter |
| `gender` | string | Filter by gender |
| `looking_for` | string | Filter by what they're looking for |
| `interest` | string | Filter by a specific interest |
| `sort` | string | `match_score` (default), `newest`, `age_asc`, `age_desc` |
| `include_self` | boolean | Include own profile (`true`/`false`) |

**Success `200`:** Array of profile objects, each including `match_score` and `shared_interest_count`.

---

#### `GET /profiles/<user_id>`
Get a single user's profile. Returns `403` if profile is private and you are not the owner.

---

### Matching

#### `POST /like/<user_id>`
Like a user. If they already liked you, a match is automatically created.

**Success `200`:**
```json
{ "message": "User liked successfully.", "match_created": true }
```

---

#### `POST /pass/<user_id>`
Pass on a user.

**Success `200`:**
```json
{ "message": "User passed successfully." }
```

---

#### `GET /matches`
Get all mutual matches for the logged-in user.

**Success `200`:** Array of matched user profiles including `match_id`.

---

### Messaging

#### `GET /messages/<user_id>`
Get message history with a matched user. Returns `403` if no match exists.

**Success `200`:** Array of message objects with `id`, `sender_id`, `receiver_id`, `content`, `created_at`.

---

#### `POST /messages/<user_id>`
Send a message to a matched user.

**Request body:**
```json
{ "content": "Hey, how are you?" }
```

**Success `201`:**
```json
{ "message": "Message sent successfully." }
```

**Errors:** `400` empty content, `403` no match exists

---

### Favorites

#### `POST /favorites`
Add a user to favorites.

**Request body:**
```json
{ "favorite_user_id": 5 }
```

#### `GET /favorites`
Get all favorited profiles.

#### `DELETE /favorites/<user_id>`
Remove a user from favorites.

---

### Notifications

#### `GET /notifications`
Get all notifications for the logged-in user, newest first.

**Success `200`:** Array of notification objects with `id`, `type`, `message`, `is_read`, `related_user_id`, `created_at`.

#### `PUT /notifications/<notification_id>/read`
Mark a notification as read.

---

### Interests

#### `GET /interests`
Get all available interests in the system (alphabetical order).

#### `PUT /profile/interests`
Update only the logged-in user's interests (minimum 3 required).

**Request body:**
```json
{ "interests": ["hiking", "cooking", "reading"] }
```

---

### Photos

#### `POST /photos`
Upload multiple additional profile photos (multipart, field `photos`).

#### `GET /photos`
Get all photos uploaded by the logged-in user.

#### `DELETE /photos/<photo_id>`
Delete a specific photo.

#### `PUT /photos/<photo_id>/primary`
Set a photo as the primary profile photo.

---

## Match Score Algorithm

Each profile is given a compatibility score from 0–100:

| Criteria | Points |
|---|---|
| Other user's age within your preferred range | +25 |
| Your age within their preferred range | +25 |
| Your `looking_for` matches their `gender` | +15 |
| Their `looking_for` matches your `gender` | +15 |
| Same location | +10 |
| Shared interests (5pts each, max 4) | up to +20 |

Profiles on the Browse page are sorted by this score by default.

---

## Known Issues / Limitations

- Messaging is not real-time (WebSocket). Messages update when the page is refreshed or navigated to.
- Location matching is exact string comparison, not GPS-based radius.
- Password reset is not implemented.
- No admin dashboard.

---

## Deployed Application

https://drift-dating-app.onrender.com

---

## Running Tests

```bash
pytest test_api.py -v
```

65 tests covering: authentication, profile management, browse/filtering, like/pass, match creation, messaging, favorites, notifications, match scoring, and privacy controls.
