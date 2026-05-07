<script setup>
import { ref, onMounted } from "vue";
import { getNotifications, markNotificationRead } from "../services/api";

const notifications = ref([]);
const loading = ref(false);
const errorMessage = ref("");

const loadNotifications = async () => {
  loading.value = true;
  errorMessage.value = "";

  try {
    notifications.value = await getNotifications();
  } catch (error) {
    errorMessage.value = error.message;
  } finally {
    loading.value = false;
  }
};

const handleMarkRead = async (notificationId) => {
  try {
    await markNotificationRead(notificationId);
    notifications.value = notifications.value.map((item) =>
      item.id === notificationId ? { ...item, is_read: true } : item,
    );
  } catch (error) {
    errorMessage.value = error.message;
  }
};

const formatDate = (dateString) => {
  if (!dateString) return "";
  return new Date(dateString).toLocaleString();
};

onMounted(() => {
  loadNotifications();
});
</script>

<template>
  <main class="dashboard">

    <div class="dash">
      <h2>Notifications</h2>

      <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>
      <p v-if="loading" class="loading-text">Loading notifications...</p>

      <div v-if="!loading" class="notifications-list">
        <div
          v-for="notification in notifications"
          :key="notification.id"
          class="notification-card"
          :class="{ unread: !notification.is_read }"
        >
          <div class="notification-body">
            <h3>{{ notification.type }}</h3>
            <p>{{ notification.message }}</p>
            <small>{{ formatDate(notification.created_at) }}</small>
          </div>

          <div class="notification-actions">
            <button
              v-if="!notification.is_read"
              class="cta"
              @click="handleMarkRead(notification.id)"
            >
              Mark as Read
            </button>

            <RouterLink
              v-if="notification.related_user_id"
              :to="`/message/${notification.related_user_id}`"
              class="cta"
              data-cta-style="outline"
            >
              Open
            </RouterLink>
          </div>
        </div>

        <p v-if="notifications.length === 0" class="empty-text">
          No notifications yet.
        </p>
      </div>
    </div>
  </main>
</template>

<style scoped src="../assets/css/dashboard.css"></style>
<style scoped src="../assets/css/notification.css"></style>

