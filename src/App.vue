<script setup>
import { RouterView, useRoute } from "vue-router";
import AppHeader from "@/components/AppHeader.vue";
import AppFooter from "@/components/AppFooter.vue";
import SideBar from "@/components/SideBar.vue";

const route = useRoute();
</script>

<template>
  <!-- Header -->
  <Transition name="fade-header">
    <AppHeader v-if="!route.meta.hideBar" />
  </Transition>

  <SideBar v-if="route.meta.sideBar" />

  <!-- Pages -->
  <main>
    
    <RouterView v-slot="{ Component }">
      <Transition
        :name="route.meta.hideBar ? 'dashboard-fade' : 'fade-slide'"
      >
        <component :is="Component" />
      </Transition>
    </RouterView>
  </main>

  <!-- Footer -->
  <AppFooter v-if="!route.meta.hideBar" />
</template>

<style>

/* ===== Public Pages ===== */

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.6s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* ===== Dashboard ===== */

.dashboard-fade-enter-active,
.dashboard-fade-leave-active {
  transition: opacity 0.6s easerr;
}

.dashboard-fade-enter-from,
.dashboard-fade-leave-to {
  opacity: 0;
}

/* ===== Header ===== */

.fade-header-enter-active,
.fade-header-leave-active {
  transition: all 0.25s ease;
}

.fade-header-enter-from,
.fade-header-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

</style>