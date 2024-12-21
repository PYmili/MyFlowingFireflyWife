import { createApp } from 'vue'
import './assets/style.css'
import App from './App.vue'

// vue-router
import { createRouter, createWebHistory } from 'vue-router'
import Firefly from './components/model/Firefly.vue'
import Chun from './components/model/Chun.vue'

const routes = [
    {
        path: '/firefly',
        name: 'Firfly',
        component: Firefly
    },
    {
        path: '/chun',
        name: 'Chun',
        component: Chun
    }
]
const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes
})

const app = createApp(App)
app.use(router)
app.mount('#app')
