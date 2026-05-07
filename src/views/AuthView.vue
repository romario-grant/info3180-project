<script setup>
import { useRoute } from "vue-router";
import { computed } from "vue";
import AuthForm from "@/components/AuthForm.vue";

const route = useRoute();

const mode = computed(() =>
  route.name === "signup" ? "signup" : "login"
);
</script>

<template>
  <AuthForm :mode="mode" />
</template>