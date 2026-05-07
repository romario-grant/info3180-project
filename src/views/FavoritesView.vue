<script setup>
import { ref, onMounted } from "vue";
import { getFavorites, removeFavorite, getSingleProfile } from "../services/api";

const favorites = ref([]);
const loading = ref(false);
const errorMessage = ref("");

const selectedProfile = ref(null);
const modalLoading = ref(false);

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

const loadFavorites = async () => {
  loading.value = true;
  errorMessage.value = "";

  try {
    favorites.value = await getFavorites();
  } catch (error) {
    errorMessage.value = error.message;
  } finally {
    loading.value = false;
  }
};

const handleRemove = async (userId) => {
  try {
    await removeFavorite(userId);
    favorites.value = favorites.value.filter((item) => item.user_id !== userId);
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
  loadFavorites();
});
</script>


<template>
  <main class="dashboard">
    <div class="dash">
      <h2>My favorites</h2>

      <p v-if="errorMessage" class="alert-error">{{ errorMessage }}</p>
      <p v-if="loading" class="loading-state">Loading favorites...</p>

      <section class="favorites-section">
        <div class="favorites-wrapper">
          <div class="favorites-grid">
            <div
              class="favorite-card"
              v-for="favorite in favorites"
              :key="favorite.id"
            >
              <figure
                class="favorite-image-box clickable"
                @click="openProfileModal(favorite.user_id)"
              >
                <img
                  :src="imageUrl(favorite.profile_picture)"
                  alt="profile picture"
                />
              </figure>

              <div class="favorite-content">
                <div
                  class="favorite-details clickable"
                  @click="openProfileModal(favorite.user_id)"
                >
                  <h3>
                    {{ formatName(favorite.display_name) }}
                    <span v-if="favorite.age">, {{ favorite.age }}</span>
                  </h3>

                  <p v-if="favorite.bio">{{ favorite.bio }}</p>

                  <p v-if="favorite.location">
                    {{ favorite.location }}
                  </p>
                </div>

                <div class="favorite-actions">
                  <RouterLink :to="`/message/${favorite.user_id}`" class="cta">
                    Message
                  </RouterLink>

                  <button
                    class="cta"
                    data-cta-style="outline"
                    @click="handleRemove(favorite.user_id)"
                  >
                    Remove
                  </button>
                </div>
              </div>
            </div>

            <p v-if="!loading && favorites.length === 0" class="empty-state">
              No favorites yet.
            </p>
          </div>
        </div>
      </section>
    </div>
  </main>
</template>

<style scoped src="../assets/css/dashboard.css"></style>
<style scoped src="../assets/css/favorites.css"></style>
