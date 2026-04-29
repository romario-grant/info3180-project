<script setup>
import { ref, onMounted } from "vue";
import {
  getProfiles,
  likeUser,
  passUser,
  getSingleProfile,
  addFavorite
} from "../services/api";

const profiles = ref([]);
const errorMessage = ref("");
const loading = ref(false);

const selectedProfile = ref(null);
const modalLoading = ref(false);

const filters = ref({
  search: "",
  location: "",
  min_age: "",
  max_age: "",
  interest: "",
});

const formatName = (name) => {
  if (!name) return "Unknown";
  return name
    .split(" ")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(" ");
};

const imageUrl = (path) => {
  if (!path) return new URL("../assets/pics/default.webp", import.meta.url).href;
  return `http://localhost:5000${path}`;
};

const loadProfiles = async () => {
  errorMessage.value = "";
  loading.value = true;

  try {
    profiles.value = await getProfiles(filters.value);
  } catch (error) {
    errorMessage.value = error.message;
  } finally {
    loading.value = false;
  }
};

const resetFilters = async () => {
  filters.value = {
    search: "",
    location: "",
    min_age: "",
    max_age: "",
    interest: "",
  };
  await loadProfiles();
};

const handleLike = async (userId) => {
  try {
    const result = await likeUser(userId);
    profiles.value = profiles.value.filter((profile) => profile.user_id !== userId);

    if (result.match_created) {
      alert("It's a match!");
    }
  } catch (error) {
    errorMessage.value = error.message;
  }
};

const handlePass = async (userId) => {
  try {
    await passUser(userId);
    profiles.value = profiles.value.filter((profile) => profile.user_id !== userId);
  } catch (error) {
    errorMessage.value = error.message;
  }
};

const handleFavorite = async (userId) => {
  try {
    await addFavorite(userId);
    alert("Added to favorites.");
  } catch (error) {
    errorMessage.value = error.message;
  }
};

const openProfileModal = async (userId) => {
  modalLoading.value = true;
  selectedProfile.value = null;

  try {
    selectedProfile.value = await getSingleProfile(userId);
  } catch (error) {
    errorMessage.value = error.message;
  } finally {
    modalLoading.value = false;
  }
};

const closeProfileModal = () => {
  selectedProfile.value = null;
};

onMounted(() => {
  loadProfiles();
});
</script>

<template>
  <main class="dashboard">
    <aside class="sidebar">
      <nav>
        <RouterLink to="/dashboard">Browse</RouterLink>
        <RouterLink to="/me/profile">My Profile</RouterLink>
        <RouterLink to="/matches">Matches</RouterLink>
        <RouterLink to="/favorites">Favorites</RouterLink>
        <RouterLink to="/notifications">Notifications</RouterLink>
      </nav>
    </aside>

    <div class="dash">
      <div class="container">
        <h2>Browse Potential Matches</h2>

        <div class="filters">
          <input
            v-model="filters.search"
            type="text"
            placeholder="Search by name or bio..."
          />
          <input
            v-model="filters.location"
            type="text"
            placeholder="Filter by location..."
          />
          <input
            v-model="filters.min_age"
            type="number"
            placeholder="Min age"
          />
          <input
            v-model="filters.max_age"
            type="number"
            placeholder="Max age"
          />
          <input
            v-model="filters.interest"
            type="text"
            placeholder="Interest..."
          />
        </div>

        <div class="fil">
          <button class="cta" @click="loadProfiles" type="button">
            Apply Filters
          </button>
          <button class="cta" data-cta-style="line" @click="resetFilters" type="button">
            Reset Filters
          </button>
        </div>

        <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>
        <p v-if="loading" class="loading-text">Loading profiles...</p>
      </div>

      <section class="section-team">
        <div class="wrapper">
          <div class="team">
            <div class="profile-card" v-for="profile in profiles" :key="profile.id">
              <figure class="img-box clickable" @click="openProfileModal(profile.user_id)">
                <img :src="imageUrl(profile.profile_picture)" alt="profile picture" />
              </figure>

              <div class="info">
                <div class="left clickable" @click="openProfileModal(profile.user_id)">
                  <h3>
                    {{ formatName(profile.display_name) }}
                    <span v-if="profile.age">, {{ profile.age }}</span>
                  </h3>

                  <p v-if="profile.bio">{{ profile.bio }}</p>
                  <p v-if="profile.location">{{ profile.location }}</p>

                  <p
                    v-if="profile.interests && profile.interests.length"
                    class="interests-text"
                  >
                    Interests: {{ profile.interests.join(", ") }}
                  </p>

                  <p
                    v-if="profile.shared_interest_count > 0"
                    class="shared-interest"
                  >
                    Shared interests: {{ profile.shared_interest_count }}
                  </p>

                  <p v-if="profile.looking_for" class="txt-p-clr">
                    Looking for: {{ profile.looking_for }}
                  </p>

                  <p class="match-score">
                    Match Score: {{ profile.match_score }}%
                  </p>
                </div>

                <div class="rate-btns">
                  <button
                    class="reset-btn favorite cta"
                    type="button"
                    @click="handleFavorite(profile.user_id)"
                  >
                    Favorite
                  </button>
                  <button
                    class="reset-btn like cta"
                    type="button"
                    @click="handleLike(profile.user_id)"
                  >
                    Like
                  </button>
                  <button
                    class="reset-btn pass"
                    type="button"
                    @click="handlePass(profile.user_id)"
                  >
                    Pass
                  </button>
                </div>
              </div>
            </div>

            <p v-if="!loading && profiles.length === 0" class="empty-text">
              No profiles found.
            </p>
          </div>
        </div>
      </section>
    </div>

    <div
      v-if="selectedProfile || modalLoading"
      class="modal-overlay"
      @click.self="closeProfileModal"
    >
      <div class="modal-card">
        <button class="close-btn" @click="closeProfileModal">×</button>

        <p v-if="modalLoading">Loading profile...</p>

        <template v-if="selectedProfile">
          <img
            class="modal-image"
            :src="imageUrl(selectedProfile.profile_picture)"
            alt="profile picture"
          />
          <h2>
            {{ formatName(selectedProfile.display_name) }}
            <span v-if="selectedProfile.age">, {{ selectedProfile.age }}</span>
          </h2>

          <p v-if="selectedProfile.bio">{{ selectedProfile.bio }}</p>
          <p v-if="selectedProfile.location">Location: {{ selectedProfile.location }}</p>
          <p v-if="selectedProfile.gender">Gender: {{ selectedProfile.gender }}</p>
          <p v-if="selectedProfile.looking_for">Looking for: {{ selectedProfile.looking_for }}</p>

          <p
            v-if="selectedProfile.interests && selectedProfile.interests.length"
            class="interests-text"
          >
            Interests: {{ selectedProfile.interests.join(", ") }}
          </p>

          <p class="match-score">Match Score: {{ selectedProfile.match_score }}%</p>
        </template>
      </div>
    </div>
  </main>
</template>


<style scoped src="../assets/css/dashboard.css"></style>