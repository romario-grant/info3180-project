const API_BASE_URL = "/api";

async function apiRequest(endpoint, options = {}) {
  const config = {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

  let data = {};
  try {
    data = await response.json();
  } catch {
    data = {};
  }

  if (!response.ok) {
    throw new Error(data.error || "Request failed.");
  }

  return data;
}

export async function signup(payload) {
  return apiRequest("/signup", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function login(payload) {
  return apiRequest("/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function logout() {
  return apiRequest("/logout", {
    method: "POST",
  });
}

export async function getCurrentUser() {
  return apiRequest("/me", {
    method: "GET",
  });
}

export async function getProfile() {
  return apiRequest("/profile", {
    method: "GET",
  });
}

export async function updateProfile(payload) {
  return apiRequest("/profile", {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export async function getSingleProfile(userId) {
  return apiRequest(`/profiles/${userId}`, {
    method: "GET",
  });
}

export async function getProfiles(params = {}) {
  const searchParams = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value !== "" && value !== null && value !== undefined) {
      searchParams.append(key, value);
    }
  });

  const queryString = searchParams.toString();
  const endpoint = queryString ? `/profiles?${queryString}` : "/profiles";

  return apiRequest(endpoint, {
    method: "GET",
  });
}

export async function likeUser(targetUserId) {
  return apiRequest(`/like/${targetUserId}`, {
    method: "POST",
  });
}

export async function passUser(targetUserId) {
  return apiRequest(`/pass/${targetUserId}`, {
    method: "POST",
  });
}

export async function getMatches() {
  return apiRequest("/matches", {
    method: "GET",
  });
}

export async function getMessages(otherUserId) {
  return apiRequest(`/messages/${otherUserId}`, {
    method: "GET",
  });
}

export async function sendMessage(otherUserId, payload) {
  return apiRequest(`/messages/${otherUserId}`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getInterests() {
  return apiRequest("/interests", {
    method: "GET",
  });
}

export async function updateProfileInterests(interests) {
  return apiRequest("/profile/interests", {
    method: "PUT",
    body: JSON.stringify({ interests }),
  });
}

export async function uploadProfilePhoto(file) {
  const formData = new FormData();
  formData.append("photo", file);

  const response = await fetch(`${API_BASE_URL}/profile/photo`, {
    method: "POST",
    credentials: "include",
    body: formData,
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Photo upload failed.");
  }

  return data;
}

export async function getMyPhotos() {
  return apiRequest("/photos", {
    method: "GET",
  });
}

export async function uploadPhotos(files) {
  const formData = new FormData();

  for (const file of files) {
    formData.append("photos", file);
  }

  const response = await fetch(`${API_BASE_URL}/photos`, {
    method: "POST",
    credentials: "include",
    body: formData,
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Photo upload failed.");
  }

  return data;
}

export async function deletePhoto(photoId) {
  return apiRequest(`/photos/${photoId}`, {
    method: "DELETE",
  });
}

export async function setPrimaryPhoto(photoId) {
  return apiRequest(`/photos/${photoId}/primary`, {
    method: "PUT",
  });
}

export async function addFavorite(favoriteUserId) {
  return apiRequest("/favorites", {
    method: "POST",
    body: JSON.stringify({
      favorite_user_id: favoriteUserId,
    }),
  });
}

export async function removeFavorite(favoriteUserId) {
  return apiRequest(`/favorites/${favoriteUserId}`, {
    method: "DELETE",
  });
}

export async function getFavorites() {
  return apiRequest("/favorites", {
    method: "GET",
  });
}

export async function getNotifications() {
  return apiRequest("/notifications", {
    method: "GET",
  });
}

export async function markNotificationRead(notificationId) {
  return apiRequest(`/notifications/${notificationId}/read`, {
    method: "PUT",
  });
}
