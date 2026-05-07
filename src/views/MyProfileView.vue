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
  <main class="dashboard pfp">
    <div class="dash">

      <div class="top">
        <h2>My Profile</h2>
      </div>

      <p v-if="message" class="success">{{ message }}</p>
      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
      <p v-if="loading">Loading...</p>

      <div v-if="!loading" class="profile-panel">

        <div
          class="upload-zone"
          :class="{ active: dragActive }"
          @dragover.prevent="dragActive = true"
          @dragleave.prevent="dragActive = false"
          @drop.prevent="handleDrop"
        >
          <p>Drag & drop photos</p>
          <label class="cta upload-button">
            Choose Photos
            <input type="file" multiple hidden @change="handleFileSelect" />
          </label>
        </div>

        <div class="form-grid">
          <input v-model="profile.display_name" placeholder="Display name" />
          <input v-model="profile.age" type="number" placeholder="Age" />

          <input v-model="profile.location" placeholder="Location" />
          <input v-model="profile.gender" placeholder="Gender" />

          <input v-model="profile.looking_for" placeholder="Looking for" />

          <select v-model="profile.visibility">
            <option value="public">Public</option>
            <option value="private">Private</option>
          </select>

          <input style="display: none" v-model="profile.min_preferred_age" type="number" placeholder="Min age" />
          <input style="display: none" v-model="profile.max_preferred_age" type="number" placeholder="Max age" />

          <input style="display: none" v-model="profile.preferred_radius_km" type="number" placeholder="Radius (km)" />
        </div>

        <textarea v-model="profile.bio" placeholder="Bio"></textarea>

        <div class="interests-box">
          <h3>Interests</h3>

          <div class="interests-grid">
            <button
              v-for="i in allInterests"
              :key="i"
              class="interest-pill"
              :class="{ selected: selectedInterests.includes(i) }"
              @click="toggleInterest(i)"
            >
              {{ formatInterestName(i) }}
            </button>
          </div>

          <div class="interest">
            <input v-model="newInterest" placeholder="Add interest" />
            <button class="cta" @click="addCustomInterest">
              Add
            </button>
          </div>
        </div>

        <button class="cta reset-button save-button" @click="handleSave">
          Save Profile
        </button>

      </div>
    </div>
  </main>
</template>

<style scoped src="../assets/css/dashboard.css"></style>

<style scoped src="../assets/css/profile.css"></style>
