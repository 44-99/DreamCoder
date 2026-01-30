import { createRouter, createWebHistory } from 'vue-router'
import GameChatView from "@/views/GameChatView.vue";

const routes = [
  { path: '/', redirect: '/chat' },
  { path: '/chat', component: GameChatView }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL), routes
})

export default router