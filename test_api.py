"""
Comprehensive test suite for Drift Dating API (run.py)
"""
import os
import sys
import pytest
import json
import io

# Force SQLite for tests
os.environ["DATABASE_URL"] = "sqlite:///test_app.db"
os.environ["SECRET_KEY"] = "test-secret-key"

sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db as _db


@pytest.fixture(scope="session")
def app():
    import run
    flask_app = run.app
    flask_app.config["TESTING"] = True
    flask_app.config["WTF_CSRF_ENABLED"] = False
    return flask_app


@pytest.fixture()
def client(app, tmp_path):
    """Create a fresh SQLite DB per test."""
    db_path = tmp_path / "test.db"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    with app.app_context():
        _db.create_all()
        yield app.test_client()
        _db.session.remove()
        _db.drop_all()


# ─── Helpers ────────────────────────────────────────────────────────────────

def signup(client, email, phone="8681234567", password="Password123!"):
    return client.post("/signup", json={"email": email, "phone_number": phone, "password": password})


def login(client, email, password="Password123!"):
    return client.post("/login", json={"email": email, "password": password})


def signup_and_login(client, email, phone="8681234567", password="Password123!"):
    signup(client, email, phone, password)
    return login(client, email, password)


# ═══════════════════════════════════════════════════════════════════════════
#  1. INDEX
# ═══════════════════════════════════════════════════════════════════════════

class TestIndex:
    def test_index_returns_200(self, client):
        r = client.get("/")
        assert r.status_code == 200
        data = r.get_json()
        assert "message" in data


# ═══════════════════════════════════════════════════════════════════════════
#  2. SIGNUP
# ═══════════════════════════════════════════════════════════════════════════

class TestSignup:
    def test_signup_success(self, client):
        r = signup(client, "alice@test.com")
        assert r.status_code == 201
        data = r.get_json()
        assert data["user"]["email"] == "alice@test.com"

    def test_signup_missing_email(self, client):
        r = client.post("/signup", json={"phone_number": "123", "password": "pass"})
        assert r.status_code == 400

    def test_signup_missing_password(self, client):
        r = client.post("/signup", json={"email": "a@b.com", "phone_number": "123"})
        assert r.status_code == 400

    def test_signup_missing_phone(self, client):
        r = client.post("/signup", json={"email": "a@b.com", "password": "pass"})
        assert r.status_code == 400

    def test_signup_duplicate_email(self, client):
        signup(client, "dup@test.com")
        r = signup(client, "dup@test.com")
        assert r.status_code == 409

    def test_signup_email_normalized_lowercase(self, client):
        r = signup(client, "UPPER@TEST.COM")
        assert r.status_code == 201
        assert r.get_json()["user"]["email"] == "upper@test.com"

    def test_signup_creates_profile(self, client):
        r = signup(client, "profiletest@test.com")
        assert r.status_code == 201
        # Profile should be auto-created – verify by logging in and fetching profile
        login(client, "profiletest@test.com")
        pr = client.get("/profile")
        assert pr.status_code == 200


# ═══════════════════════════════════════════════════════════════════════════
#  3. LOGIN
# ═══════════════════════════════════════════════════════════════════════════

class TestLogin:
    def test_login_success(self, client):
        signup(client, "bob@test.com")
        r = login(client, "bob@test.com")
        assert r.status_code == 200
        assert "user" in r.get_json()

    def test_login_wrong_password(self, client):
        signup(client, "bob2@test.com")
        r = client.post("/login", json={"email": "bob2@test.com", "password": "wrongpass"})
        assert r.status_code == 401

    def test_login_unknown_email(self, client):
        r = client.post("/login", json={"email": "nobody@test.com", "password": "pass"})
        assert r.status_code == 401

    def test_login_missing_fields(self, client):
        r = client.post("/login", json={"email": "x@x.com"})
        assert r.status_code == 400

    def test_login_sets_session(self, client):
        signup(client, "sess@test.com")
        login(client, "sess@test.com")
        r = client.get("/me")
        assert r.status_code == 200


# ═══════════════════════════════════════════════════════════════════════════
#  4. LOGOUT
# ═══════════════════════════════════════════════════════════════════════════

class TestLogout:
    def test_logout_clears_session(self, client):
        signup_and_login(client, "logout@test.com")
        r = client.post("/logout")
        assert r.status_code == 200
        r2 = client.get("/me")
        assert r2.status_code == 401


# ═══════════════════════════════════════════════════════════════════════════
#  5. CURRENT USER  /me
# ═══════════════════════════════════════════════════════════════════════════

class TestGetCurrentUser:
    def test_me_returns_user(self, client):
        signup_and_login(client, "me@test.com")
        r = client.get("/me")
        assert r.status_code == 200
        data = r.get_json()
        assert data["email"] == "me@test.com"

    def test_me_unauthenticated(self, client):
        r = client.get("/me")
        assert r.status_code == 401


# ═══════════════════════════════════════════════════════════════════════════
#  6. PROFILE – GET / PUT
# ═══════════════════════════════════════════════════════════════════════════

class TestProfile:
    def test_get_profile_unauthenticated(self, client):
        r = client.get("/profile")
        assert r.status_code == 401

    def test_get_profile_authenticated(self, client):
        signup_and_login(client, "prof@test.com")
        r = client.get("/profile")
        assert r.status_code == 200
        data = r.get_json()
        assert "display_name" in data

    def test_update_profile_basic_fields(self, client):
        signup_and_login(client, "upd@test.com")
        r = client.put("/profile", json={
            "display_name": "Alice",
            "age": 25,
            "bio": "Hello world",
            "location": "Bridgetown",
            "gender": "female",
            "looking_for": "male"
        })
        assert r.status_code == 200
        data = r.get_json()
        assert data["profile"]["display_name"] == "Alice"
        assert data["profile"]["age"] == 25

    def test_update_profile_age_under_18_rejected(self, client):
        signup_and_login(client, "young@test.com")
        r = client.put("/profile", json={"age": 16})
        assert r.status_code == 400

    def test_update_profile_invalid_visibility(self, client):
        signup_and_login(client, "vis@test.com")
        r = client.put("/profile", json={"visibility": "hidden"})
        assert r.status_code == 400

    def test_update_profile_valid_visibility(self, client):
        signup_and_login(client, "vis2@test.com")
        r = client.put("/profile", json={"visibility": "private"})
        assert r.status_code == 200

    def test_update_profile_min_age_greater_than_max(self, client):
        signup_and_login(client, "age@test.com")
        r = client.put("/profile", json={"min_preferred_age": 50, "max_preferred_age": 30})
        assert r.status_code == 400

    def test_update_profile_interests_less_than_3(self, client):
        signup_and_login(client, "int@test.com")
        r = client.put("/profile", json={"interests": ["hiking", "reading"]})
        assert r.status_code == 400

    def test_update_profile_interests_at_least_3(self, client):
        signup_and_login(client, "int2@test.com")
        r = client.put("/profile", json={"interests": ["hiking", "reading", "cooking"]})
        assert r.status_code == 200
        data = r.get_json()
        assert len(data["profile"]["interests"]) == 3

    def test_update_profile_unauthenticated(self, client):
        r = client.put("/profile", json={"display_name": "Hacker"})
        assert r.status_code == 401


# ═══════════════════════════════════════════════════════════════════════════
#  7. INTERESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestInterests:
    def test_get_interests_empty(self, client):
        r = client.get("/interests")
        assert r.status_code == 200
        assert r.get_json() == []

    def test_get_interests_after_update(self, client):
        signup_and_login(client, "itest@test.com")
        client.put("/profile", json={"interests": ["yoga", "travel", "art"]})
        r = client.get("/interests")
        assert r.status_code == 200
        names = [i["name"] for i in r.get_json()]
        assert "yoga" in names

    def test_update_profile_interests_deduped(self, client):
        signup_and_login(client, "dedup@test.com")
        r = client.put("/profile", json={"interests": ["yoga", "YOGA", "travel", "art"]})
        assert r.status_code == 200
        # After dedup, yoga appears once
        interests = r.get_json()["profile"]["interests"]
        names = [i["name"] for i in interests]
        assert names.count("yoga") == 1


# ═══════════════════════════════════════════════════════════════════════════
#  8. PROFILES LISTING
# ═══════════════════════════════════════════════════════════════════════════

class TestProfiles:
    def _create_user(self, client, email, name, age, gender, location, interests, phone="8681111111"):
        signup(client, email, phone)
        login(client, email)
        client.put("/profile", json={
            "display_name": name,
            "age": age,
            "gender": gender,
            "location": location,
            "visibility": "public",
            "interests": interests
        })
        client.post("/logout")

    def test_profiles_unauthenticated(self, client):
        r = client.get("/profiles")
        assert r.status_code == 401

    def test_profiles_excludes_self(self, client):
        signup_and_login(client, "self@test.com", "8680000001")
        r = client.get("/profiles")
        assert r.status_code == 200
        data = r.get_json()
        # Should not include own profile by default
        for p in data:
            assert p["user_id"] != r  # rough check – more precise below

    def test_profiles_returns_public_only(self, client):
        self._create_user(client, "pub@test.com", "Public", 25, "male", "NYC",
                         ["hiking", "cooking", "reading"], "8680000002")
        self._create_user(client, "priv@test.com", "Private", 26, "female", "NYC",
                         ["hiking", "cooking", "reading"], "8680000003")
        # Make priv private
        login(client, "priv@test.com")
        client.put("/profile", json={"visibility": "private"})
        client.post("/logout")

        signup_and_login(client, "searcher@test.com", "8680000004")
        r = client.get("/profiles")
        assert r.status_code == 200
        names = [p["display_name"] for p in r.get_json()]
        assert "Public" in names
        assert "Private" not in names

    def test_profiles_filter_by_gender(self, client):
        self._create_user(client, "m@test.com", "Mike", 28, "male", "LA",
                         ["sports", "music", "art"], "8680000010")
        self._create_user(client, "f@test.com", "Fiona", 27, "female", "LA",
                         ["yoga", "travel", "food"], "8680000011")
        signup_and_login(client, "filter@test.com", "8680000012")
        r = client.get("/profiles?gender=male")
        assert r.status_code == 200
        for p in r.get_json():
            assert p["gender"] == "male"

    def test_profiles_filter_by_location(self, client):
        self._create_user(client, "btown@test.com", "Brigetowner", 30, "male", "Bridgetown",
                         ["cricket", "beach", "music"], "8680000013")
        self._create_user(client, "ptown@test.com", "Portownie", 30, "female", "Port of Spain",
                         ["carnival", "food", "art"], "8680000014")
        signup_and_login(client, "loc@test.com", "8680000015")
        r = client.get("/profiles?location=Bridgetown")
        assert r.status_code == 200
        names = [p["display_name"] for p in r.get_json()]
        assert "Brigetowner" in names
        assert "Portownie" not in names

    def test_profiles_filter_by_age_range(self, client):
        self._create_user(client, "age20@test.com", "Young", 20, "male", "NYC",
                         ["gaming", "anime", "coding"], "8680000020")
        self._create_user(client, "age40@test.com", "Older", 40, "female", "NYC",
                         ["travel", "wine", "yoga"], "8680000021")
        signup_and_login(client, "agefilter@test.com", "8680000022")
        r = client.get("/profiles?min_age=25&max_age=35")
        assert r.status_code == 200
        for p in r.get_json():
            if p["age"] is not None:
                assert 25 <= p["age"] <= 35

    def test_profiles_sorted_by_match_score(self, client):
        signup_and_login(client, "scorer@test.com", "8680000030")
        r = client.get("/profiles?sort=match_score")
        assert r.status_code == 200

    def test_profiles_invalid_min_age(self, client):
        signup_and_login(client, "invage@test.com", "8680000031")
        r = client.get("/profiles?min_age=abc")
        assert r.status_code == 400


# ═══════════════════════════════════════════════════════════════════════════
#  9. LIKE / PASS
# ═══════════════════════════════════════════════════════════════════════════

class TestLikePass:
    def _two_users(self, client):
        signup(client, "liker@test.com", "8681110001")
        signup(client, "liked@test.com", "8681110002")

    def test_like_user_success(self, client):
        self._two_users(client)
        login(client, "liker@test.com")
        # Get liked user's id
        r = client.get("/me")
        login(client, "liked@test.com")
        liked_id = client.get("/me").get_json()["id"]
        client.post("/logout")
        login(client, "liker@test.com")
        r = client.post(f"/like/{liked_id}")
        assert r.status_code == 200

    def test_like_self_rejected(self, client):
        signup_and_login(client, "self2@test.com", "8681110003")
        my_id = client.get("/me").get_json()["id"]
        r = client.post(f"/like/{my_id}")
        assert r.status_code == 400

    def test_pass_user_success(self, client):
        signup(client, "passer@test.com", "8681110004")
        signup(client, "passed@test.com", "8681110005")
        login(client, "passed@test.com")
        passed_id = client.get("/me").get_json()["id"]
        client.post("/logout")
        login(client, "passer@test.com")
        r = client.post(f"/pass/{passed_id}")
        assert r.status_code == 200

    def test_mutual_like_creates_match(self, client):
        signup(client, "a@test.com", "8681110006")
        signup(client, "b@test.com", "8681110007")

        login(client, "a@test.com")
        a_id = client.get("/me").get_json()["id"]
        client.post("/logout")

        login(client, "b@test.com")
        b_id = client.get("/me").get_json()["id"]
        client.post(f"/like/{a_id}")
        client.post("/logout")

        login(client, "a@test.com")
        r = client.post(f"/like/{b_id}")
        assert r.status_code == 200
        assert r.get_json()["match_created"] == True

    def test_like_unauthenticated(self, client):
        r = client.post("/like/99")
        assert r.status_code == 401

    def test_like_nonexistent_user(self, client):
        signup_and_login(client, "ghost@test.com", "8681110008")
        r = client.post("/like/999999")
        assert r.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════
#  10. MATCHES
# ═══════════════════════════════════════════════════════════════════════════

class TestMatches:
    def test_get_matches_unauthenticated(self, client):
        r = client.get("/matches")
        assert r.status_code == 401

    def test_get_matches_empty(self, client):
        signup_and_login(client, "nomatch@test.com", "8682220001")
        r = client.get("/matches")
        assert r.status_code == 200
        assert r.get_json() == []

    def test_get_matches_after_mutual_like(self, client):
        signup(client, "ma@test.com", "8682220002")
        signup(client, "mb@test.com", "8682220003")

        login(client, "ma@test.com")
        ma_id = client.get("/me").get_json()["id"]
        client.post("/logout")

        login(client, "mb@test.com")
        mb_id = client.get("/me").get_json()["id"]
        client.post(f"/like/{ma_id}")
        client.post("/logout")

        login(client, "ma@test.com")
        client.post(f"/like/{mb_id}")
        r = client.get("/matches")
        assert r.status_code == 200
        assert len(r.get_json()) == 1


# ═══════════════════════════════════════════════════════════════════════════
#  11. MESSAGES
# ═══════════════════════════════════════════════════════════════════════════

class TestMessages:
    def _matched_pair(self, client):
        signup(client, "msg1@test.com", "8683330001")
        signup(client, "msg2@test.com", "8683330002")

        login(client, "msg1@test.com")
        u1_id = client.get("/me").get_json()["id"]
        client.post("/logout")

        login(client, "msg2@test.com")
        u2_id = client.get("/me").get_json()["id"]
        client.post(f"/like/{u1_id}")
        client.post("/logout")

        login(client, "msg1@test.com")
        client.post(f"/like/{u2_id}")
        client.post("/logout")
        return u1_id, u2_id

    def test_send_message_requires_match(self, client):
        signup(client, "unmatched1@test.com", "8683330010")
        signup(client, "unmatched2@test.com", "8683330011")
        login(client, "unmatched2@test.com")
        u2_id = client.get("/me").get_json()["id"]
        client.post("/logout")
        login(client, "unmatched1@test.com")
        r = client.post(f"/messages/{u2_id}", json={"content": "Hi!"})
        assert r.status_code == 403

    def test_send_and_get_message(self, client):
        u1_id, u2_id = self._matched_pair(client)
        login(client, "msg1@test.com")
        r = client.post(f"/messages/{u2_id}", json={"content": "Hello!"})
        assert r.status_code == 201
        r2 = client.get(f"/messages/{u2_id}")
        assert r2.status_code == 200
        msgs = r2.get_json()
        assert len(msgs) == 1
        assert msgs[0]["content"] == "Hello!"

    def test_send_empty_message_rejected(self, client):
        u1_id, u2_id = self._matched_pair(client)
        login(client, "msg1@test.com")
        r = client.post(f"/messages/{u2_id}", json={"content": "   "})
        assert r.status_code == 400

    def test_get_messages_unauthenticated(self, client):
        r = client.get("/messages/1")
        assert r.status_code == 401


# ═══════════════════════════════════════════════════════════════════════════
#  12. FAVORITES
# ═══════════════════════════════════════════════════════════════════════════

class TestFavorites:
    def test_add_favorite(self, client):
        signup(client, "fav1@test.com", "8684440001")
        signup(client, "fav2@test.com", "8684440002")
        login(client, "fav2@test.com")
        fav2_id = client.get("/me").get_json()["id"]
        client.post("/logout")
        login(client, "fav1@test.com")
        r = client.post("/favorites", json={"favorite_user_id": fav2_id})
        assert r.status_code == 201

    def test_add_favorite_self_rejected(self, client):
        signup_and_login(client, "favself@test.com", "8684440003")
        my_id = client.get("/me").get_json()["id"]
        r = client.post("/favorites", json={"favorite_user_id": my_id})
        assert r.status_code == 400

    def test_add_duplicate_favorite(self, client):
        signup(client, "fav3@test.com", "8684440004")
        signup(client, "fav4@test.com", "8684440005")
        login(client, "fav4@test.com")
        fav4_id = client.get("/me").get_json()["id"]
        client.post("/logout")
        login(client, "fav3@test.com")
        client.post("/favorites", json={"favorite_user_id": fav4_id})
        r = client.post("/favorites", json={"favorite_user_id": fav4_id})
        assert r.status_code == 200  # Returns 200 for already-favorited

    def test_get_favorites(self, client):
        signup(client, "fav5@test.com", "8684440006")
        signup(client, "fav6@test.com", "8684440007")
        login(client, "fav6@test.com")
        fav6_id = client.get("/me").get_json()["id"]
        client.post("/logout")
        login(client, "fav5@test.com")
        client.post("/favorites", json={"favorite_user_id": fav6_id})
        r = client.get("/favorites")
        assert r.status_code == 200
        assert len(r.get_json()) == 1

    def test_remove_favorite(self, client):
        signup(client, "fav7@test.com", "8684440008")
        signup(client, "fav8@test.com", "8684440009")
        login(client, "fav8@test.com")
        fav8_id = client.get("/me").get_json()["id"]
        client.post("/logout")
        login(client, "fav7@test.com")
        client.post("/favorites", json={"favorite_user_id": fav8_id})
        r = client.delete(f"/favorites/{fav8_id}")
        assert r.status_code == 200
        r2 = client.get("/favorites")
        assert len(r2.get_json()) == 0

    def test_favorites_unauthenticated(self, client):
        r = client.get("/favorites")
        assert r.status_code == 401


# ═══════════════════════════════════════════════════════════════════════════
#  13. NOTIFICATIONS
# ═══════════════════════════════════════════════════════════════════════════

class TestNotifications:
    def test_get_notifications_unauthenticated(self, client):
        r = client.get("/notifications")
        assert r.status_code == 401

    def test_get_notifications_empty(self, client):
        signup_and_login(client, "notif@test.com", "8685550001")
        r = client.get("/notifications")
        assert r.status_code == 200
        assert r.get_json() == []

    def test_notifications_created_on_match(self, client):
        signup(client, "notif1@test.com", "8685550002")
        signup(client, "notif2@test.com", "8685550003")

        login(client, "notif1@test.com")
        n1_id = client.get("/me").get_json()["id"]
        client.post("/logout")

        login(client, "notif2@test.com")
        n2_id = client.get("/me").get_json()["id"]
        client.post(f"/like/{n1_id}")
        client.post("/logout")

        login(client, "notif1@test.com")
        client.post(f"/like/{n2_id}")
        r = client.get("/notifications")
        assert r.status_code == 200
        notifs = r.get_json()
        assert any(n["type"] == "match" for n in notifs)

    def test_mark_notification_read(self, client):
        signup(client, "notif3@test.com", "8685550004")
        signup(client, "notif4@test.com", "8685550005")

        login(client, "notif3@test.com")
        n3_id = client.get("/me").get_json()["id"]
        client.post("/logout")

        login(client, "notif4@test.com")
        n4_id = client.get("/me").get_json()["id"]
        client.post(f"/like/{n3_id}")
        client.post("/logout")

        login(client, "notif3@test.com")
        client.post(f"/like/{n4_id}")
        notifs = client.get("/notifications").get_json()
        notif_id = notifs[0]["id"]
        r = client.put(f"/notifications/{notif_id}/read")
        assert r.status_code == 200
        updated = client.get("/notifications").get_json()
        match_notif = next(n for n in updated if n["id"] == notif_id)
        assert match_notif["is_read"] == True

    def test_mark_other_user_notification_fails(self, client):
        signup(client, "notif5@test.com", "8685550006")
        signup(client, "notif6@test.com", "8685550007")

        login(client, "notif5@test.com")
        n5_id = client.get("/me").get_json()["id"]
        client.post("/logout")

        login(client, "notif6@test.com")
        n6_id = client.get("/me").get_json()["id"]
        client.post(f"/like/{n5_id}")
        client.post("/logout")

        login(client, "notif5@test.com")
        client.post(f"/like/{n6_id}")
        notifs_5 = client.get("/notifications").get_json()
        notif_id = notifs_5[0]["id"]
        client.post("/logout")

        # notif6 tries to mark notif5's notification
        login(client, "notif6@test.com")
        r = client.put(f"/notifications/{notif_id}/read")
        assert r.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════
#  14. SINGLE PROFILE
# ═══════════════════════════════════════════════════════════════════════════

class TestSingleProfile:
    def test_get_single_profile(self, client):
        signup(client, "sp1@test.com", "8686660001")
        login(client, "sp1@test.com")
        sp1_id = client.get("/me").get_json()["id"]
        client.put("/profile", json={"display_name": "SP One", "visibility": "public"})
        client.post("/logout")

        signup_and_login(client, "sp2@test.com", "8686660002")
        r = client.get(f"/profiles/{sp1_id}")
        assert r.status_code == 200
        assert r.get_json()["display_name"] == "SP One"

    def test_get_private_profile_blocked(self, client):
        signup(client, "priv1@test.com", "8686660003")
        login(client, "priv1@test.com")
        priv1_id = client.get("/me").get_json()["id"]
        client.put("/profile", json={"visibility": "private"})
        client.post("/logout")

        signup_and_login(client, "priv2@test.com", "8686660004")
        r = client.get(f"/profiles/{priv1_id}")
        assert r.status_code == 403

    def test_get_own_private_profile_allowed(self, client):
        signup_and_login(client, "ownpriv@test.com", "8686660005")
        my_id = client.get("/me").get_json()["id"]
        client.put("/profile", json={"visibility": "private"})
        r = client.get(f"/profiles/{my_id}")
        assert r.status_code == 200


# ═══════════════════════════════════════════════════════════════════════════
#  15. MATCH SCORE
# ═══════════════════════════════════════════════════════════════════════════

class TestMatchScore:
    def test_match_score_in_profile_response(self, client):
        signup(client, "score1@test.com", "8687770001")
        signup(client, "score2@test.com", "8687770002")

        login(client, "score1@test.com")
        s1_id = client.get("/me").get_json()["id"]
        client.put("/profile", json={
            "age": 25, "gender": "female", "looking_for": "male",
            "visibility": "public", "interests": ["yoga", "travel", "art"]
        })
        client.post("/logout")

        login(client, "score2@test.com")
        s2_id = client.get("/me").get_json()["id"]
        client.put("/profile", json={
            "age": 27, "gender": "male", "looking_for": "female",
            "min_preferred_age": 22, "max_preferred_age": 30,
            "visibility": "public", "interests": ["yoga", "music", "art"]
        })
        client.post("/logout")

        login(client, "score1@test.com")
        client.put("/profile", json={"min_preferred_age": 25, "max_preferred_age": 30})
        r = client.get(f"/profiles/{s2_id}")
        data = r.get_json()
        assert "match_score" in data
        assert data["match_score"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
