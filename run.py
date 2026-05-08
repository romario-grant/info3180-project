from flask import request, jsonify, session, send_from_directory
from sqlalchemy import or_
from app import create_app, db, bcrypt
from app.models import (
    User,
    Profile,
    Like,
    Match,
    Message,
    ProfilePhoto,
    Interest,
    Favorite,
    Notification,
)
import os
import uuid

app = create_app()

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def serialize_interest(interest):
    return {
        "id": interest.id,
        "name": interest.name,
    }


def get_or_create_interests(interest_names):
    interests = []

    for raw_name in interest_names:
        name = str(raw_name).strip().lower()
        if not name:
            continue

        existing_interest = Interest.query.filter_by(name=name).first()

        if existing_interest:
            interests.append(existing_interest)
        else:
            new_interest = Interest(name=name)
            db.session.add(new_interest)
            db.session.flush()
            interests.append(new_interest)

    return interests


def create_notification(user_id, notification_type, message, related_user_id=None):
    notification = Notification(
        user_id=user_id,
        type=notification_type,
        message=message,
        related_user_id=related_user_id
    )
    db.session.add(notification)


def calculate_match_score(current_profile, other_profile):
    score = 0

    if not current_profile or not other_profile:
        return score

    if (
        current_profile.min_preferred_age is not None
        and current_profile.max_preferred_age is not None
        and other_profile.age is not None
        and current_profile.min_preferred_age <= other_profile.age <= current_profile.max_preferred_age
    ):
        score += 25

    if (
        other_profile.min_preferred_age is not None
        and other_profile.max_preferred_age is not None
        and current_profile.age is not None
        and other_profile.min_preferred_age <= current_profile.age <= other_profile.max_preferred_age
    ):
        score += 25

    if current_profile.looking_for and other_profile.gender:
        if current_profile.looking_for.strip().lower() == other_profile.gender.strip().lower():
            score += 15

    if other_profile.looking_for and current_profile.gender:
        if other_profile.looking_for.strip().lower() == current_profile.gender.strip().lower():
            score += 15

    if current_profile.location and other_profile.location:
        if current_profile.location.strip().lower() == other_profile.location.strip().lower():
            score += 10

    current_interest_names = {interest.name.lower() for interest in current_profile.interests}
    other_interest_names = {interest.name.lower() for interest in other_profile.interests}
    shared_interests = current_interest_names.intersection(other_interest_names)

    score += min(len(shared_interests) * 5, 20)

    return min(score, 100)


@app.route("/api", methods=["GET"])
def api_index():
    return jsonify({"message": "Drift Dating API running"}), 200


@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.get_json()

    email = (data.get("email") or "").strip().lower()
    phone_number = (data.get("phone_number") or "").strip()
    password = data.get("password") or ""

    if not email or not phone_number or not password:
        return jsonify({
            "error": "Email, phone number, and password are required."
        }), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({
            "error": "An account with that email already exists."
        }), 409

    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    user = User(
        email=email,
        phone_number=phone_number,
        password_hash=password_hash
    )
    db.session.add(user)
    db.session.flush()

    profile = Profile(
        user_id=user.id,
        display_name=email.split("@")[0]
    )
    db.session.add(profile)
    db.session.commit()

    return jsonify({
        "message": "User registered successfully.",
        "user": {
            "id": user.id,
            "email": user.email,
            "phone_number": user.phone_number
        }
    }), 201


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({
            "error": "Email and password are required."
        }), 400

    user = User.query.filter_by(email=email).first()

    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({
            "error": "Invalid email or password."
        }), 401

    session["user_id"] = user.id

    return jsonify({
        "message": "Login successful.",
        "user": {
            "id": user.id,
            "email": user.email
        }
    }), 200


@app.route("/api/me", methods=["GET"])
def get_current_user():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Not logged in."}), 401

    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"error": "User not found."}), 404

    return jsonify({
        "id": user.id,
        "email": user.email,
        "phone_number": user.phone_number
    }), 200


@app.route("/api/profile", methods=["GET"])
def get_profile():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Not logged in."}), 401

    profile = Profile.query.filter_by(user_id=user_id).first()

    if not profile:
        return jsonify({"error": "Profile not found."}), 404

    return jsonify({
        "id": profile.id,
        "user_id": profile.user_id,
        "display_name": profile.display_name,
        "age": profile.age,
        "bio": profile.bio,
        "location": profile.location,
        "gender": profile.gender,
        "looking_for": profile.looking_for,
        "visibility": profile.visibility,
        "profile_picture": profile.profile_picture,
        "min_preferred_age": profile.min_preferred_age,
        "max_preferred_age": profile.max_preferred_age,
        "preferred_radius_km": profile.preferred_radius_km,
        "interests": [serialize_interest(interest) for interest in profile.interests]
    }), 200


@app.route("/api/profile", methods=["PUT"])
def update_profile():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Not logged in."}), 401

    profile = Profile.query.filter_by(user_id=user_id).first()

    if not profile:
        return jsonify({"error": "Profile not found."}), 404

    data = request.get_json()

    display_name = data.get("display_name")
    age = data.get("age")
    bio = data.get("bio")
    location = data.get("location")
    gender = data.get("gender")
    looking_for = data.get("looking_for")
    visibility = data.get("visibility")
    profile_picture = data.get("profile_picture")
    min_preferred_age = data.get("min_preferred_age")
    max_preferred_age = data.get("max_preferred_age")
    preferred_radius_km = data.get("preferred_radius_km")
    interest_names = data.get("interests")

    if display_name is not None:
        profile.display_name = str(display_name).strip()

    if age is not None:
        try:
            age = int(age)
            if age < 18:
                return jsonify({"error": "Age must be at least 18."}), 400
            profile.age = age
        except ValueError:
            return jsonify({"error": "Age must be a valid number."}), 400

    if bio is not None:
        profile.bio = str(bio).strip()

    if location is not None:
        profile.location = str(location).strip()

    if gender is not None:
        profile.gender = str(gender).strip()

    if looking_for is not None:
        profile.looking_for = str(looking_for).strip()

    if visibility is not None:
        visibility = str(visibility).strip().lower()
        if visibility not in ["public", "private"]:
            return jsonify({"error": "Visibility must be 'public' or 'private'."}), 400
        profile.visibility = visibility

    if profile_picture is not None:
        profile.profile_picture = str(profile_picture).strip()

    if min_preferred_age is not None:
        try:
            profile.min_preferred_age = int(min_preferred_age)
        except ValueError:
            return jsonify({"error": "Minimum preferred age must be a valid number."}), 400

    if max_preferred_age is not None:
        try:
            profile.max_preferred_age = int(max_preferred_age)
        except ValueError:
            return jsonify({"error": "Maximum preferred age must be a valid number."}), 400

    if preferred_radius_km is not None:
        try:
            profile.preferred_radius_km = int(preferred_radius_km)
        except ValueError:
            return jsonify({"error": "Preferred radius must be a valid number."}), 400

    if (
        profile.min_preferred_age is not None
        and profile.max_preferred_age is not None
        and profile.min_preferred_age > profile.max_preferred_age
    ):
        return jsonify({
            "error": "Minimum preferred age cannot be greater than maximum preferred age."
        }), 400

    if interest_names is not None:
        if not isinstance(interest_names, list):
            return jsonify({"error": "Interests must be provided as a list."}), 400

        cleaned_names = []
        seen = set()

        for item in interest_names:
            name = str(item).strip().lower()
            if name and name not in seen:
                cleaned_names.append(name)
                seen.add(name)

        if len(cleaned_names) < 3:
            return jsonify({"error": "Please provide at least 3 interests."}), 400

        profile.interests = get_or_create_interests(cleaned_names)

    db.session.commit()

    return jsonify({
        "message": "Profile updated successfully.",
        "profile": {
            "id": profile.id,
            "user_id": profile.user_id,
            "display_name": profile.display_name,
            "age": profile.age,
            "bio": profile.bio,
            "location": profile.location,
            "gender": profile.gender,
            "looking_for": profile.looking_for,
            "visibility": profile.visibility,
            "profile_picture": profile.profile_picture,
            "min_preferred_age": profile.min_preferred_age,
            "max_preferred_age": profile.max_preferred_age,
            "preferred_radius_km": profile.preferred_radius_km,
            "interests": [serialize_interest(interest) for interest in profile.interests]
        }
    }), 200


@app.route("/api/interests", methods=["GET"])
def get_interests():
    interests = Interest.query.order_by(Interest.name.asc()).all()
    return jsonify([serialize_interest(interest) for interest in interests]), 200


@app.route("/api/profile/interests", methods=["PUT"])
def update_profile_interests():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Not logged in."}), 401

    profile = Profile.query.filter_by(user_id=user_id).first()

    if not profile:
        return jsonify({"error": "Profile not found."}), 404

    data = request.get_json()
    interest_names = data.get("interests", [])

    if not isinstance(interest_names, list):
        return jsonify({"error": "Interests must be provided as a list."}), 400

    cleaned_names = []
    seen = set()

    for item in interest_names:
        name = str(item).strip().lower()
        if name and name not in seen:
            cleaned_names.append(name)
            seen.add(name)

    if len(cleaned_names) < 3:
        return jsonify({"error": "Please provide at least 3 interests."}), 400

    profile.interests = get_or_create_interests(cleaned_names)
    db.session.commit()

    return jsonify({
        "message": "Interests updated successfully.",
        "interests": [serialize_interest(interest) for interest in profile.interests]
    }), 200


@app.route("/api/profiles", methods=["GET"])
def get_profiles():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Not logged in."}), 401

    current_profile = Profile.query.filter_by(user_id=user_id).first()
    include_self = request.args.get("include_self") == "true"

    interacted_user_ids = db.session.query(Like.to_user_id).filter(
        Like.from_user_id == user_id
    )

    query = Profile.query.filter(Profile.visibility == "public")

    if not include_self:
        query = query.filter(Profile.user_id != user_id)

    query = query.filter(~Profile.user_id.in_(interacted_user_ids))

    search = request.args.get("search")
    location = request.args.get("location")
    min_age = request.args.get("min_age")
    max_age = request.args.get("max_age")
    gender = request.args.get("gender")
    looking_for = request.args.get("looking_for")
    interest = request.args.get("interest")
    sort = (request.args.get("sort") or "match_score").strip().lower()

    if search:
        search = search.strip()
        query = query.filter(
            or_(
                Profile.display_name.ilike(f"%{search}%"),
                Profile.bio.ilike(f"%{search}%")
            )
        )

    if location:
        query = query.filter(Profile.location.ilike(f"%{location.strip()}%"))

    if min_age:
        try:
            query = query.filter(Profile.age >= int(min_age))
        except ValueError:
            return jsonify({"error": "min_age must be a valid number."}), 400

    if max_age:
        try:
            query = query.filter(Profile.age <= int(max_age))
        except ValueError:
            return jsonify({"error": "max_age must be a valid number."}), 400

    if gender:
        query = query.filter(Profile.gender.ilike(gender.strip()))

    if looking_for:
        query = query.filter(Profile.looking_for.ilike(looking_for.strip()))

    if interest:
        interest = interest.strip().lower()
        query = query.join(Profile.interests).filter(Interest.name.ilike(interest))

    profiles = query.distinct().all()

    results = []
    current_interest_names = (
        {item.name.lower() for item in current_profile.interests}
        if current_profile else set()
    )

    for profile in profiles:
        score = calculate_match_score(current_profile, profile)
        profile_interest_names = [item.name for item in profile.interests]
        shared_interest_count = len(
            current_interest_names.intersection({item.name.lower() for item in profile.interests})
        )

        results.append({
            "id": profile.id,
            "user_id": profile.user_id,
            "display_name": profile.display_name,
            "age": profile.age,
            "bio": profile.bio,
            "location": profile.location,
            "gender": profile.gender,
            "looking_for": profile.looking_for,
            "visibility": profile.visibility,
            "profile_picture": profile.profile_picture,
            "min_preferred_age": profile.min_preferred_age,
            "max_preferred_age": profile.max_preferred_age,
            "preferred_radius_km": profile.preferred_radius_km,
            "match_score": score,
            "interests": profile_interest_names,
            "shared_interest_count": shared_interest_count,
            "created_at": profile.user.created_at.isoformat() if profile.user and profile.user.created_at else None
        })

    if sort == "newest":
        results.sort(
            key=lambda item: item["created_at"] or "",
            reverse=True
        )
    elif sort == "age_asc":
        results.sort(
            key=lambda item: (item["age"] is None, item["age"] if item["age"] is not None else 999)
        )
    elif sort == "age_desc":
        results.sort(
            key=lambda item: (item["age"] is None, -(item["age"] if item["age"] is not None else 0))
        )
    else:
        results.sort(key=lambda item: item["match_score"], reverse=True)

    return jsonify(results), 200


@app.route("/api/like/<int:target_user_id>", methods=["POST"])
def like_user(target_user_id):
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Not logged in."}), 401

    if user_id == target_user_id:
        return jsonify({"error": "You cannot like your own profile."}), 400

    target_profile = Profile.query.filter_by(user_id=target_user_id).first()
    if not target_profile:
        return jsonify({"error": "Target user not found."}), 404

    existing_like = Like.query.filter_by(
        from_user_id=user_id,
        to_user_id=target_user_id
    ).first()

    if existing_like:
        existing_like.status = "like"
    else:
        new_like = Like(
            from_user_id=user_id,
            to_user_id=target_user_id,
            status="like"
        )
        db.session.add(new_like)

    reverse_like = Like.query.filter_by(
        from_user_id=target_user_id,
        to_user_id=user_id,
        status="like"
    ).first()

    match_created = False

    if reverse_like:
        existing_match = Match.query.filter(
            or_(
                (Match.user1_id == user_id) & (Match.user2_id == target_user_id),
                (Match.user1_id == target_user_id) & (Match.user2_id == user_id)
            )
        ).first()

        if not existing_match:
            user1_id = min(user_id, target_user_id)
            user2_id = max(user_id, target_user_id)
            match = Match(user1_id=user1_id, user2_id=user2_id)
            db.session.add(match)
            match_created = True

            liker_profile = Profile.query.filter_by(user_id=user_id).first()
            target_display_name = target_profile.display_name or f"User {target_user_id}"
            liker_display_name = liker_profile.display_name if liker_profile else f"User {user_id}"

            create_notification(
                user_id=target_user_id,
                notification_type="match",
                message=f"It's a match with {liker_display_name}!",
                related_user_id=user_id
            )
            create_notification(
                user_id=user_id,
                notification_type="match",
                message=f"It's a match with {target_display_name}!",
                related_user_id=target_user_id
            )

    db.session.commit()

    return jsonify({
        "message": "User liked successfully.",
        "match_created": match_created
    }), 200


@app.route("/api/pass/<int:target_user_id>", methods=["POST"])
def pass_user(target_user_id):
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Not logged in."}), 401

    if user_id == target_user_id:
        return jsonify({"error": "You cannot pass your own profile."}), 400

    target_profile = Profile.query.filter_by(user_id=target_user_id).first()
    if not target_profile:
        return jsonify({"error": "Target user not found."}), 404

    existing_like = Like.query.filter_by(
        from_user_id=user_id,
        to_user_id=target_user_id
    ).first()

    if existing_like:
        existing_like.status = "pass"
    else:
        new_pass = Like(
            from_user_id=user_id,
            to_user_id=target_user_id,
            status="pass"
        )
        db.session.add(new_pass)

    db.session.commit()

    return jsonify({
        "message": "User passed successfully."
    }), 200


@app.route("/api/matches", methods=["GET"])
def get_matches():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Not logged in."}), 401

    matches = Match.query.filter(
        or_(Match.user1_id == user_id, Match.user2_id == user_id)
    ).all()

    results = []

    for match in matches:
        other_user_id = match.user2_id if match.user1_id == user_id else match.user1_id
        other_profile = Profile.query.filter_by(user_id=other_user_id).first()

        if other_profile:
            results.append({
                "match_id": match.id,
                "user_id": other_profile.user_id,
                "display_name": other_profile.display_name,
                "age": other_profile.age,
                "bio": other_profile.bio,
                "location": other_profile.location,
                "gender": other_profile.gender,
                "looking_for": other_profile.looking_for,
                "profile_picture": other_profile.profile_picture
            })

    return jsonify(results), 200


@app.route("/api/messages/<int:other_user_id>", methods=["GET"])
def get_messages(other_user_id):
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Not logged in."}), 401

    match = Match.query.filter(
        or_(
            (Match.user1_id == user_id) & (Match.user2_id == other_user_id),
            (Match.user1_id == other_user_id) & (Match.user2_id == user_id)
        )
    ).first()

    if not match:
        return jsonify({"error": "You can only message matched users."}), 403

    messages = Message.query.filter_by(match_id=match.id).order_by(Message.created_at.asc()).all()

    results = []
    for msg in messages:
        results.append({
            "id": msg.id,
            "match_id": msg.match_id,
            "sender_id": msg.sender_id,
            "receiver_id": msg.receiver_id,
            "content": msg.content,
            "created_at": msg.created_at.isoformat()
        })

    return jsonify(results), 200


@app.route("/api/messages/<int:other_user_id>", methods=["POST"])
def send_message(other_user_id):
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Not logged in."}), 401

    match = Match.query.filter(
        or_(
            (Match.user1_id == user_id) & (Match.user2_id == other_user_id),
            (Match.user1_id == other_user_id) & (Match.user2_id == user_id)
        )
    ).first()

    if not match:
        return jsonify({"error": "You can only message matched users."}), 403

    data = request.get_json()
    content = (data.get("content") or "").strip()

    if not content:
        return jsonify({"error": "Message content is required."}), 400

    message = Message(
        match_id=match.id,
        sender_id=user_id,
        receiver_id=other_user_id,
        content=content
    )

    db.session.add(message)
    db.session.commit()

    return jsonify({
        "message": "Message sent successfully."
    }), 201


@app.route("/api/uploads/<path:filename>", methods=["GET"])
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/api/profiles/<int:user_id>", methods=["GET"])
def get_single_profile(user_id):
    current_user_id = session.get("user_id")

    if not current_user_id:
        return jsonify({"error": "Not logged in."}), 401

    profile = Profile.query.filter_by(user_id=user_id).first()

    if not profile:
        return jsonify({"error": "Profile not found."}), 404

    if profile.visibility != "public" and current_user_id != user_id:
        return jsonify({"error": "Profile is private."}), 403

    current_profile = Profile.query.filter_by(user_id=current_user_id).first()
    score = calculate_match_score(current_profile, profile)

    return jsonify({
        "id": profile.id,
        "user_id": profile.user_id,
        "display_name": profile.display_name,
        "age": profile.age,
        "bio": profile.bio,
        "location": profile.location,
        "gender": profile.gender,
        "looking_for": profile.looking_for,
        "visibility": profile.visibility,
        "profile_picture": profile.profile_picture,
        "min_preferred_age": profile.min_preferred_age,
        "max_preferred_age": profile.max_preferred_age,
        "preferred_radius_km": profile.preferred_radius_km,
        "match_score": score,
        "interests": [interest.name for interest in profile.interests]
    }), 200


@app.route("/api/profile/photo", methods=["POST"])
def upload_profile_photo():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Not logged in."}), 401

    profile = Profile.query.filter_by(user_id=user_id).first()

    if not profile:
        return jsonify({"error": "Profile not found."}), 404

    if "photo" not in request.files:
        return jsonify({"error": "No photo file provided."}), 400

    file = request.files["photo"]

    if file.filename == "":
        return jsonify({"error": "No file selected."}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Use png, jpg, jpeg, or webp."}), 400

    extension = file.filename.rsplit(".", 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{extension}"
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    file.save(filepath)

    profile.profile_picture = f"/uploads/{filename}"
    db.session.commit()

    return jsonify({
        "message": "Profile photo uploaded successfully.",
        "profile_picture": profile.profile_picture
    }), 200


@app.route("/api/photos", methods=["POST"])
def upload_photos():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    files = request.files.getlist("photos")

    if not files:
        return jsonify({"error": "No files uploaded"}), 400

    uploaded_photos = []

    for file in files:
        if file and allowed_file(file.filename):
            ext = file.filename.rsplit(".", 1)[1].lower()
            filename = f"{uuid.uuid4().hex}.{ext}"
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            photo = ProfilePhoto(
                user_id=user_id,
                image_url=f"/uploads/{filename}"
            )
            db.session.add(photo)
            uploaded_photos.append(photo)

    db.session.commit()

    return jsonify({
        "message": "Photos uploaded",
        "photos": [p.image_url for p in uploaded_photos]
    }), 201


@app.route("/api/photos", methods=["GET"])
def get_my_photos():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    photos = ProfilePhoto.query.filter_by(user_id=user_id).all()

    return jsonify([
        {
            "id": p.id,
            "image_url": p.image_url,
            "is_primary": p.is_primary
        }
        for p in photos
    ]), 200


@app.route("/api/photos/<int:photo_id>", methods=["DELETE"])
def delete_photo(photo_id):
    user_id = session.get("user_id")

    photo = ProfilePhoto.query.get(photo_id)

    if not photo or photo.user_id != user_id:
        return jsonify({"error": "Not found"}), 404

    db.session.delete(photo)
    db.session.commit()

    return jsonify({"message": "Deleted"}), 200


@app.route("/api/photos/<int:photo_id>/primary", methods=["PUT"])
def set_primary(photo_id):
    user_id = session.get("user_id")

    photos = ProfilePhoto.query.filter_by(user_id=user_id).all()

    for p in photos:
        p.is_primary = False

    photo = ProfilePhoto.query.get(photo_id)

    if not photo or photo.user_id != user_id:
        return jsonify({"error": "Not found"}), 404

    photo.is_primary = True
    db.session.commit()

    return jsonify({"message": "Primary photo updated"}), 200


@app.route("/api/favorites", methods=["POST"])
def add_favorite():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Not logged in."}), 401

    data = request.get_json()
    favorite_user_id = data.get("favorite_user_id")

    if not favorite_user_id:
        return jsonify({"error": "favorite_user_id is required."}), 400

    try:
        favorite_user_id = int(favorite_user_id)
    except ValueError:
        return jsonify({"error": "favorite_user_id must be a valid number."}), 400

    if favorite_user_id == user_id:
        return jsonify({"error": "You cannot favorite yourself."}), 400

    target_profile = Profile.query.filter_by(user_id=favorite_user_id).first()
    if not target_profile:
        return jsonify({"error": "Target user not found."}), 404

    existing_favorite = Favorite.query.filter_by(
        user_id=user_id,
        favorite_user_id=favorite_user_id
    ).first()

    if existing_favorite:
        return jsonify({"message": "User already in favorites."}), 200

    favorite = Favorite(
        user_id=user_id,
        favorite_user_id=favorite_user_id
    )
    db.session.add(favorite)
    db.session.commit()

    return jsonify({"message": "Favorite added successfully."}), 201


@app.route("/api/favorites/<int:favorite_user_id>", methods=["DELETE"])
def remove_favorite(favorite_user_id):
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Not logged in."}), 401

    favorite = Favorite.query.filter_by(
        user_id=user_id,
        favorite_user_id=favorite_user_id
    ).first()

    if not favorite:
        return jsonify({"error": "Favorite not found."}), 404

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"message": "Favorite removed successfully."}), 200


@app.route("/api/favorites", methods=["GET"])
def get_favorites():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Not logged in."}), 401

    favorites = Favorite.query.filter_by(user_id=user_id).order_by(Favorite.created_at.desc()).all()

    results = []

    for favorite in favorites:
        profile = Profile.query.filter_by(user_id=favorite.favorite_user_id).first()
        if profile:
            results.append({
                "id": favorite.id,
                "user_id": profile.user_id,
                "display_name": profile.display_name,
                "age": profile.age,
                "bio": profile.bio,
                "location": profile.location,
                "gender": profile.gender,
                "looking_for": profile.looking_for,
                "profile_picture": profile.profile_picture,
                "created_at": favorite.created_at.isoformat()
            })

    return jsonify(results), 200


@app.route("/api/notifications", methods=["GET"])
def get_notifications():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Not logged in."}), 401

    notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()

    return jsonify([
        {
            "id": notification.id,
            "type": notification.type,
            "message": notification.message,
            "is_read": notification.is_read,
            "related_user_id": notification.related_user_id,
            "created_at": notification.created_at.isoformat()
        }
        for notification in notifications
    ]), 200


@app.route("/api/notifications/<int:notification_id>/read", methods=["PUT"])
def mark_notification_read(notification_id):
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Not logged in."}), 401

    notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()

    if not notification:
        return jsonify({"error": "Notification not found."}), 404

    notification.is_read = True
    db.session.commit()

    return jsonify({"message": "Notification marked as read."}), 200


@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully."}), 200



# --- Serve Vue.js built frontend in production ---
dist_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")


@app.route("/assets/<path:filename>")
def serve_assets(filename):
    return send_from_directory(os.path.join(dist_dir, "assets"), filename)


@app.route("/")
@app.route("/<path:path>")
def catch_all(path=""):
    if path != "":
        file_path = os.path.join(dist_dir, path)
        if os.path.isfile(file_path):
            return send_from_directory(dist_dir, path)
    return send_from_directory(dist_dir, "index.html")


if __name__ == "__main__":
    app.run(debug=True)