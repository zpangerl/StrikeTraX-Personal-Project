import { createRouter, createWebHistory } from 'vue-router'
import ScoringView from "../views/Scoring.vue"
import Home from '../views/Home.vue'
import History from '../views/History.vue'

// Define the required routes needed for the application
const routes = [
  {
    path: '/',
    name: 'home',
    component: Home
  },
  {
    path: "/scoring",
    name: "scoring",
    component: ScoringView
  },
  {
    path: "/history",
    name: "history",
    component: History
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router
