import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { pinia } from "../main";
import LoginView from "@/views/LoginView.vue";
import ProfileView from "@/views/ProfileView.vue";
import GameGeneratorView from "@/views/GameGeneratorView.vue";

const routes = [
  { path: '/login', component: LoginView },
  { path: '/profile', component: ProfileView },
  { path: '/', component: GameGeneratorView },
  { path: '/generate', component: GameGeneratorView }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL), routes
})
const publicRoutes = ['/login', '/docs']


// 路由守卫 - 保护需要认证的路由
router.beforeEach((to, from, next) => {
  if (to.path === '' || publicRoutes.includes(to.path)) {
    return next();
  }
  const authStore = useAuthStore(pinia);
  if (!authStore.isAuthenticated) {
    return next('/login');
  }
  next();
})

export default router