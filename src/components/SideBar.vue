<template>
  <aside class="sidebar">
    <img class="lg" src="../assets/icons/m-logo.svg" />
    <nav :class="{ active: menuOpen }">
      <RouterLink to="/me/profile" class="pfp">
        <img
          class="profile-image"
          src="../assets/pics/default.webp"
          alt="profile picture"
        />
      </RouterLink>
      <RouterLink to="/dashboard"> <p>Browse</p> </RouterLink>
      <RouterLink to="/matches"><p>Matches</p></RouterLink>
      <RouterLink to="/favorites"><p>Favorites</p></RouterLink>
      <RouterLink to="/notifications"><p>Notifications</p></RouterLink>
      <RouterLink to="/" class="btm"
        ><i class="fa-solid fa-right-from-bracket"></i> Log out</RouterLink
      >
    </nav>
    <button
      class="mobile-navigation"
      :class="{ active: menuOpen }"
      @click="toggleMenu"
    >
      <div class="bar"></div>
      <div class="bar"></div>
      <div class="bar"></div>
    </button>
  </aside>
  <div class="black" :class="{ active: menuOpen }" @click="closeMenu"></div>
</template>

<style scoped src="../assets/css/sidebar.css"></style>

<script setup>
import { ref } from "vue";

const menuOpen = ref(false);

const toggleMenu = () => {
  menuOpen.value = !menuOpen.value;
};

const closeMenu = () => {
  menuOpen.value = false;
};
</script>
