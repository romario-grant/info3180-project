<template>
  <footer id="footer" v-if="!$route.meta.hideBar">
    <div class="footer-cnt">
      <div class="top">
        <div class="wrapper top-cnt">
          <div class="company-info">
            <RouterLink to="/" v-if="!$route.meta.hideAuthButtons">
              <img src="@/assets/icons/w-logo.svg" alt="logo" />
            </RouterLink>

            <RouterLink to="/dashboard" v-if="$route.meta.hideLogo">
              <img src="@/assets/icons/w-logo.svg" alt="logo" />
            </RouterLink>
            <p>
              Help people connect without pressure, without pretending, and
              without the noise.
            </p>
          </div>
        </div>
      </div>

      <div class="btm">
        <p>&copy;2026 Drift Dating all rights reserved.</p>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { ref } from "vue";

const year = new Date().getFullYear();
</script>
