<script setup>
import { ref, onMounted, watch, onBeforeUnmount } from "vue";
import {
  getMessages,
  sendMessage,
  getMatches,
  getCurrentUser,
} from "../services/api";

const props = defineProps({
  userId: {
    type: [String, Number],
    required: true,
  },
});

const messages = ref([]);
const matches = ref([]);
const currentUser = ref(null);
const newMessage = ref("");
const loading = ref(false);
const errorMessage = ref("");
const selectedMatch = ref(null);

let refreshInterval = null;

const formatName = (name) => {
  if (!name) return "Unknown";

  return name
    .split(" ")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(" ");
};

const loadMessagesOnly = async () => {
  try {
    const numericUserId = Number(props.userId);
    messages.value = await getMessages(numericUserId);
  } catch (error) {
    errorMessage.value = error.message;
  }
};

const loadPageData = async () => {
  loading.value = true;
  errorMessage.value = "";
  selectedMatch.value = null;
  messages.value = [];

  try {
    const numericUserId = Number(props.userId);

    const [matchesData, userData] = await Promise.all([
      getMatches(),
      getCurrentUser(),
    ]);

    matches.value = matchesData;
    currentUser.value = userData;
    selectedMatch.value =
      matchesData.find((match) => match.user_id === numericUserId) || null;

    if (!selectedMatch.value) {
      errorMessage.value = "Match not found.";
      return;
    }

    await loadMessagesOnly();
  } catch (error) {
    errorMessage.value = error.message;
  } finally {
    loading.value = false;
  }
};

const handleSend = async () => {
  if (!newMessage.value.trim()) return;

  try {
    const numericUserId = Number(props.userId);
    await sendMessage(numericUserId, { content: newMessage.value });
    newMessage.value = "";
    await loadMessagesOnly();
  } catch (error) {
    errorMessage.value = error.message;
  }
};

const startAutoRefresh = () => {
  clearInterval(refreshInterval);
  refreshInterval = setInterval(() => {
    if (selectedMatch.value) {
      loadMessagesOnly();
    }
  }, 3000);
};

onMounted(async () => {
  await loadPageData();
  startAutoRefresh();
});

watch(
  () => props.userId,
  async () => {
    await loadPageData();
    startAutoRefresh();
  },
);

onBeforeUnmount(() => {
  clearInterval(refreshInterval);
});
</script>

<template>
  <main class="dashboard">
    <div class="dash">
      <RouterLink to="/matches" class="cta" data-cta-style="line"
        >← Back to Matches</RouterLink
      >

      <div class="message-layout">


        <section class="chat-panel">
          <p v-if="errorMessage" class="error-text">
            {{ errorMessage }}
          </p>
          <p v-if="loading" class="loading-text">Loading conversation...</p>

          <section v-if="selectedMatch && !loading" class="chat-section">
            <div class="chat-header">
              <figure class="img-box">
                <img src="../assets/pics/default.webp" alt="profile picture" />
              </figure>

              <div class="match-info">
                <h3>
                  {{ formatName(selectedMatch.display_name) }}
                  <span v-if="selectedMatch.age"
                    >, {{ selectedMatch.age }}</span
                  >
                </h3>
                <p v-if="selectedMatch.location">
                  {{ selectedMatch.location }}
                </p>
              </div>
            </div>

            <div class="messages-box">
              <div
                v-for="message in messages"
                :key="message.id"
                :class="[
                  'message-bubble',
                  message.sender_id === currentUser?.id
                    ? 'my-message'
                    : 'their-message',
                ]"
              >
                {{ message.content }}
              </div>

              <p v-if="messages.length === 0" class="empty-text">
                No messages yet. Start the conversation.
              </p>
            </div>

            <form class="message-form" @submit.prevent="handleSend">
              <input
                v-model="newMessage"
                type="text"
                placeholder="Type your message..."
              />
              <button class="cta reset-btn" type="submit">Send</button>
             
          </section>
        </section>
      </div>
    </div>
  </main>
</template>

<style scoped src="../assets/css/dashboard.css"></style>
<style scoped src="../assets/css/message.css"></style>
