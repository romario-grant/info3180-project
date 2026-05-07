<script setup>
import { ref, onMounted } from "vue";
import {
  getProfiles,
  likeUser,
  passUser,
  getSingleProfile,
  addFavorite,
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
  if (!path)
    return new URL("../assets/pics/default.webp", import.meta.url).href;
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
    profiles.value = profiles.value.filter(
      (profile) => profile.user_id !== userId,
    );

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
    profiles.value = profiles.value.filter(
      (profile) => profile.user_id !== userId,
    );
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
    <div class="dash">
      <div class="container">
        <h1>Browse Potential Matches</h1>
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
            min="18"
            placeholder="Min age"
          />
          <input
            v-model="filters.max_age"
            type="number"
            min="18"
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
          <button
            class="cta"
            data-cta-style="line"
            @click="resetFilters"
            type="button"
          >
            Reset Filters
          </button>
        </div>
      </div>
      <section class="section-team">
        <div class="team">
          <article
            class="profile-card"
            v-for="profile in profiles"
            :key="profile.id"
          >
            <figure
              class="profile-card__media clickable"
              @click="openProfileModal(profile.user_id)"
            >
              <img
                :src="imageUrl(profile.profile_picture)"
                alt="profile picture"
                class="profile-card__img"
              />
            </figure>
            <div class="profile-card__body">
              <div
                class="profile-card__info clickable"
                @click="openProfileModal(profile.user_id)"
              >
                <h3 class="profile-card__name">
                  {{ formatName(profile.display_name) }}
                  <span v-if="profile.age">, {{ profile.age }}</span>
                </h3>
                <p v-if="profile.location" class="text-muted">
                  {{ profile.location }}
                </p>
                <p v-if="profile.bio" class="text-muted">{{ profile.bio }}</p>
              </div>

              <div class="profile-card__signals">
                <p class="match-score">🔥 {{ profile.match_score }}% Match</p>
                <p
                  v-if="profile.shared_interest_count > 0"
                  class="text-highlight"
                >
                  💙 {{ profile.shared_interest_count }} shared interests
                </p>
                <p v-if="profile.interests?.length" class="text-muted small">
                  {{ profile.interests.join(", ") }}
                </p>
                <p v-if="profile.looking_for" class="text-muted small">
                  Looking for: {{ profile.looking_for }}
                </p>
              </div>

              <div class="profile-card__actions">
                <div class="tp">
                  <button
                    class="reset-button cta btn--favorite"
                    @click="handleFavorite(profile.user_id)"
                  >
                    Favorite
                  </button>
                  <button
                    class="reset-button cta btn--like"
                    @click="handleLike(profile.user_id)"
                  >
                    Like
                  </button>
                </div>
                <button
                  class="reset-button cta btn--pass"
                  @click="handlePass(profile.user_id)"
                  data-cta-style="line"
                >
                  Pass
                </button>
              </div>
            </div>
          </article>
          <p v-if="!loading && profiles.length === 0" class="empty-text">
            No profiles found.
          </p>
        </div>
      </section>
    </div>
  </main>
</template>

<style scoped src="../assets/css/dashboard.css"></style>
<style scoped src="../assets/css/browse.css"></style>
