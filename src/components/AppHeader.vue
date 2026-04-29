<template>
  <header class="main-header" id="nav-bar" v-if="!$route.meta.hideBar">
    <div class="wrapper" data-width="wide">
      <RouterLink
        to="/"
        class="logo"
        id="logo-box"
        v-if="!$route.meta.hideAuthButtons"
      >
        <img src="@/assets/icons/m-logo.svg" alt="logo" />
      </RouterLink>

      <RouterLink
        to="/dashboard"
        class="logo"
        id="logo-box"
        v-if="$route.meta.hideLogo"
      >
        <img src="@/assets/icons/m-logo.svg" alt="logo" />
      </RouterLink>

      <nav class="main-navigation" :class="{ active: menuOpen }">
        <ul class="nav-list left" v-if="!$route.meta.hideAuthButtons">
          <li>
            <RouterLink to="/about" class="nav-link">About</RouterLink>
          </li>
        </ul>

        <ul class="nav-list right" v-if="!$route.meta.hideAuthButtons">
          <li>
            <RouterLink to="/login" class="nav-link log" data-cta-style="line">
              Log in
            </RouterLink>
          </li>
          <li>
            <RouterLink to="/signup" class="nav-link sign">
              Sign up
            </RouterLink>
          </li>
        </ul>
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
    </div>
  </header>
  <div class="black" :class="{ active: menuOpen }" @click="closeMenu"></div>
</template>

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
