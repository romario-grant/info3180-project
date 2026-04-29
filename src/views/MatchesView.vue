<script setup>
import { ref, onMounted } from "vue";
import { getMatches } from "../services/api";

const matches = ref([]);
const loading = ref(false);
const errorMessage = ref("");

const formatName = (name) => {
  if (!name) return "Unknown";

  return name
    .split(" ")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(" ");
};

const loadMatches = async () => {
  loading.value = true;
  errorMessage.value = "";

  try {
    const data = await getMatches();
    matches.value = data;
  } catch (error) {
    errorMessage.value = error.message;
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadMatches();
});
</script>

<template>
  <main class="dashboard">
    <aside class="sidebar">
      <nav>
        <RouterLink to="/dashboard">Browse</RouterLink>
        <RouterLink to="/matches">Matches</RouterLink>
      </nav>
    </aside>

    <div class="dash">
      <h2>Your Matches</h2>

      <p v-if="errorMessage" class="error-text">
        {{ errorMessage }}
      </p>
      <p v-if="loading" class="loading-text">Loading matches...</p>

      <section class="section-team">
        <div class="wrapper">
          <div class="team">
            <div
              class="profile-card"
              v-for="match in matches"
              :key="match.match_id"
            >
              <figure class="img-box">
                <img src="../assets/pics/default.webp" alt="profile picture" />
              </figure>

              <div class="info">
                <div class="left">
                  <h3>
                    {{ formatName(match.display_name) }}
                    <span v-if="match.age">, {{ match.age }}</span>
                  </h3>

                  <p v-if="match.bio">{{ match.bio }}</p>
                  <p v-if="match.location">{{ match.location }}</p>
                </div>

                <RouterLink
                  :to="`/message/${match.user_id}`"
                  class="reset-btn mess"
                >
                  Message
                </RouterLink>
              </div>
            </div>

            <p v-if="!loading && matches.length === 0" class="empty-text">
              No matches yet.
            </p>
          </div>
        </div>
      </section>
    </div>
  </main>
</template>

<style scoped src="../assets/css/dashboard.css"></style>
