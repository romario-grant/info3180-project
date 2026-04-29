<script setup>
import { ref, onMounted } from "vue";
import {
  getProfile,
  updateProfile,
  getMyPhotos,
  uploadPhotos,
  deletePhoto,
  setPrimaryPhoto,
  getInterests,
} from "../services/api";

const profile = ref({
  display_name: "",
  age: "",
  bio: "",
  location: "",
  gender: "",
  looking_for: "",
  visibility: "public",
  min_preferred_age: "",
  max_preferred_age: "",
  preferred_radius_km: "",
  profile_picture: "",
  interests: [],
});

const allInterests = ref([]);
const selectedInterests = ref([]);
const newInterest = ref("");
const photos = ref([]);
const message = ref("");
const errorMessage = ref("");
const loading = ref(false);
const dragActive = ref(false);

const imageUrl = (path) => {
  if (!path)
    return new URL("../assets/pics/default.webp", import.meta.url).href;
  return `http://localhost:5000${path}`;
};

const formatInterestName = (name) => {
  if (!name) return "";
  return name.charAt(0).toUpperCase() + name.slice(1).toLowerCase();
};

const loadProfile = async () => {
  loading.value = true;
  errorMessage.value = "";

  try {
    const [profileData, photosData, interestsData] = await Promise.all([
      getProfile(),
      getMyPhotos(),
      getInterests(),
    ]);

    profile.value = profileData;
    photos.value = photosData;
    allInterests.value = interestsData.map((item) => item.name);
    selectedInterests.value = (profileData.interests || []).map(
      (item) => item.name,
    );
  } catch (error) {
    errorMessage.value = error.message;
  } finally {
    loading.value = false;
  }
};

const handleSave = async () => {
  message.value = "";
  errorMessage.value = "";

  try {
    if (selectedInterests.value.length < 3) {
      errorMessage.value = "Please choose at least 3 interests.";
      return;
    }

    const payload = {
      display_name: profile.value.display_name,
      age: profile.value.age === "" ? null : Number(profile.value.age),
      bio: profile.value.bio,
      location: profile.value.location,
      gender: profile.value.gender,
      looking_for: profile.value.looking_for,
      visibility: profile.value.visibility,
      min_preferred_age:
        profile.value.min_preferred_age === ""
          ? null
          : Number(profile.value.min_preferred_age),
      max_preferred_age:
        profile.value.max_preferred_age === ""
          ? null
          : Number(profile.value.max_preferred_age),
      preferred_radius_km:
        profile.value.preferred_radius_km === ""
          ? null
          : Number(profile.value.preferred_radius_km),
      interests: selectedInterests.value,
    };

    const result = await updateProfile(payload);
    profile.value = result.profile;
    selectedInterests.value = (result.profile.interests || []).map(
      (item) => item.name,
    );
    message.value = "Profile updated successfully.";
  } catch (error) {
    errorMessage.value = error.message;
  }
};

const refreshPhotos = async () => {
  photos.value = await getMyPhotos();
};

const handleFileSelect = async (event) => {
  const files = Array.from(event.target.files || []);
  if (!files.length) return;
  await handlePhotoUpload(files);
  event.target.value = "";
};

const handlePhotoUpload = async (files) => {
  message.value = "";
  errorMessage.value = "";

  try {
    await uploadPhotos(files);
    await refreshPhotos();
    message.value = "Photos uploaded successfully.";
  } catch (error) {
    errorMessage.value = error.message;
  }
};

const handleDrop = async (event) => {
  dragActive.value = false;
  const files = Array.from(event.dataTransfer.files || []);
  if (!files.length) return;
  await handlePhotoUpload(files);
};

const handleDeletePhoto = async (photoId) => {
  message.value = "";
  errorMessage.value = "";

  try {
    await deletePhoto(photoId);
    await refreshPhotos();
    message.value = "Photo deleted successfully.";
  } catch (error) {
    errorMessage.value = error.message;
  }
};

const handleSetPrimary = async (photoId) => {
  message.value = "";
  errorMessage.value = "";

  try {
    await setPrimaryPhoto(photoId);
    await refreshPhotos();
    message.value = "Primary photo updated.";
  } catch (error) {
    errorMessage.value = error.message;
  }
};

const toggleInterest = (interestName) => {
  const normalized = interestName.trim().toLowerCase();

  if (selectedInterests.value.includes(normalized)) {
    selectedInterests.value = selectedInterests.value.filter(
      (item) => item !== normalized,
    );
  } else {
    selectedInterests.value.push(normalized);
  }
};

const addCustomInterest = () => {
  const normalized = newInterest.value.trim().toLowerCase();

  if (!normalized) return;

  if (!allInterests.value.includes(normalized)) {
    allInterests.value.push(normalized);
  }

  if (!selectedInterests.value.includes(normalized)) {
    selectedInterests.value.push(normalized);
  }

  newInterest.value = "";
};

onMounted(() => {
  loadProfile();
});
</script>

<template>
  <main class="profile-page">
    <aside class="sidebar">
      <nav>
        <RouterLink to="/dashboard">Browse</RouterLink>
        <RouterLink to="/me/profile">My Profile</RouterLink>
        <RouterLink to="/matches">Matches</RouterLink>
      </nav>
    </aside>

    <div class="content">
      <h2>My Profile</h2>

      <p v-if="message" class="success">{{ message }}</p>
      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
      <p v-if="loading">Loading profile...</p>

      <div v-if="!loading" class="profile-card">
        <img
          class="profile-image"
          :src="imageUrl(profile.profile_picture)"
          alt="profile picture"
        />

        <div
          class="drop-zone"
          :class="{ active: dragActive }"
          @dragover.prevent="dragActive = true"
          @dragleave.prevent="dragActive = false"
          @drop.prevent="handleDrop"
        >
          <p>Drag and drop photos here</p>
          <p>or</p>
          <label for="photoUpload" class="upload-btn">Choose Photos</label>
          <input
            id="photoUpload"
            type="file"
            accept=".png,.jpg,.jpeg,.webp"
            multiple
            @change="handleFileSelect"
            hidden
          />
        </div>

        <div class="photo-gallery">
          <div class="photo-card" v-for="photo in photos" :key="photo.id">
            <img :src="imageUrl(photo.image_url)" alt="uploaded photo" />
            <p v-if="photo.is_primary" class="primary-badge">Primary</p>

            <div class="photo-actions">
              <button
                type="button"
                class="small-btn"
                @click="handleSetPrimary(photo.id)"
              >
                Set Primary
              </button>
              <button
                type="button"
                class="small-btn delete"
                @click="handleDeletePhoto(photo.id)"
              >
                Delete
              </button>
            </div>
          </div>
        </div>

        <input
          v-model="profile.display_name"
          type="text"
          placeholder="Display name"
        />
        <input v-model="profile.age" type="number" placeholder="Age" />
        <textarea v-model="profile.bio" placeholder="Bio"></textarea>
        <input v-model="profile.location" type="text" placeholder="Location" />
        <input v-model="profile.gender" type="text" placeholder="Gender" />
        <input
          v-model="profile.looking_for"
          type="text"
          placeholder="Looking for"
        />

        <select v-model="profile.visibility">
          <option value="public">Public</option>
          <option value="private">Private</option>
        </select>

        <input
          v-model="profile.min_preferred_age"
          type="number"
          placeholder="Minimum preferred age"
        />
        <input
          v-model="profile.max_preferred_age"
          type="number"
          placeholder="Maximum preferred age"
        />
        <input
          v-model="profile.preferred_radius_km"
          type="number"
          placeholder="Preferred radius (km)"
        />

        <div class="interests-section">
          <h3>Choose Your Interests</h3>
          <p class="interest-note">Select at least 3 interests.</p>

          <div class="interest-list">
            <button
              v-for="interest in allInterests"
              :key="interest"
              type="button"
              class="interest-chip"
              :class="{ selected: selectedInterests.includes(interest) }"
              @click="toggleInterest(interest)"
            >
              {{ formatInterestName(interest) }}
            </button>
          </div>

          <div class="custom-interest-row">
            <input
              v-model="newInterest"
              type="text"
              placeholder="Add custom interest"
            />
            <button type="button" class="small-btn" @click="addCustomInterest">
              Add
            </button>
          </div>

          <p class="selected-count">Selected: {{ selectedInterests.length }}</p>
        </div>

        <button class="save-btn" @click="handleSave" type="button">
          Save Profile
        </button>
      </div>
    </div>
  </main>
</template>

<style scoped src="../assets/css/dashboard.css"></style>