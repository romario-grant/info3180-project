import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "home",
      component: HomeView,
    },
    {
      path: "/about",
      name: "about",
      component: () => import("../views/AboutView.vue"),
    },
    {
      path: "/login",
      name: "login",
      component: () => import("../views/AuthView.vue"),
      meta: { hideBar: true },
    },
    {
      path: "/signup",
      name: "signup",
      component: () => import("../views/AuthView.vue"),
      meta: { hideBar: true },
    },
    {
      path: "/dashboard",
      name: "dashboard",
      component: () => import("../views/DashboardView.vue"),
      meta: { hideBar: true, sideBar: true },
    },
    {
      path: "/matches",
      name: "matches",
      component: () => import("../views/MatchesView.vue"),
      meta: { hideBar: true, sideBar: true },
    },
    {
      path: "/favorites",
      name: "favorites",
      component: () => import("../views/FavoritesView.vue"),
      meta: { hideBar: true, sideBar: true },
    },
    {
      path: "/notifications",
      name: "notifications",
      component: () => import("../views/NotificationsView.vue"),
      meta: { hideBar: true, sideBar: true },
    },
    {
      path: "/message",
      redirect: "/matches",
      meta: { hideBar: true, sideBar: true },
    },
    {
      path: "/message/:userId",
      name: "message",
      component: () => import("../views/MessageView.vue"),
      props: true,
      meta: { hideBar: true, sideBar: true },
    },
    {
      path: "/me/profile",
      name: "my-profile",
      component: () => import("../views/MyProfileView.vue"),
      meta: { hideBar: true, sideBar: true },
    },
  ],
});

export default router;
