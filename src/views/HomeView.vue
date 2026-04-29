<template>
  <section class="section-hero">
    <div class="wrapper">
      <div class="hero">
        <div class="lockup">
          <h1>Meet People Who Matter</h1>
          <p>
            Drift matches you based on vibe, timing, and real compatibility so
            every connection feels natural, not forced.
          </p>

          <div class="buttons">
            <RouterLink to="/login" class="cta"> Start Now </RouterLink>
          </div>
        </div>

        <div class="img-box">
          <img src="../assets/pics/frame.webp" class="frame" />
          <img class="h1" src="../assets/pics/h1.webp"/>
          <img class="h2" src="../assets/pics/h2.webp"/>
          <img class="h3" src="../assets/pics/h3.webp"/>
          <div class="slider" ref="sliderRef">
            <div
              class="list"
              :style="{ transform: `translateX(-${index * width}px)` }"
            >
              <img v-for="(img, i) in images" :key="i" class="pic" :src="img" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped src="../assets/css/index.css"></style>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from "vue";

import img1 from "@/assets/pics/1.webp";
import img2 from "@/assets/pics/2.webp";
import img3 from "@/assets/pics/3.webp";
import img4 from "@/assets/pics/4.webp";
import img5 from "@/assets/pics/5.webp";
import img6 from "@/assets/pics/6.webp";

const images = [img1, img2, img3, img4, img5, img6];

const index = ref(0);
const direction = ref(1);

const width = ref(0);
const sliderRef = ref(null);

let interval = null;
const isAnimating = ref(false);

onMounted(async () => {
  await nextTick();
  width.value = sliderRef.value.clientWidth;

  interval = setInterval(() => {
    if (!isAnimating.value) {
      nextSlide();
    }
  }, 3000);

  window.addEventListener("resize", updateWidth);
});

const nextSlide = () => {
  isAnimating.value = true;

  if (index.value === images.length - 1) {
    direction.value = -1;
  } else if (index.value === 0) {
    direction.value = 1;
  }

  index.value += direction.value;

  setTimeout(() => {
    isAnimating.value = false;
  }, 500);
};

const updateWidth = () => {
  width.value = sliderRef.value.clientWidth;
};

onUnmounted(() => {
  clearInterval(interval);
  window.removeEventListener("resize", updateWidth);
});
</script>
