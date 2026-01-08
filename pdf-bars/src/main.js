import { createApp } from 'vue'
import App from './App.vue'
import axios from 'axios'
import './assets/main.css'

const app = createApp(App)

app.config.globalProperties.$axios = axios;
axios.defaults.withCredentials = false;
axios.defaults.baseURL = 'http://localhost:8225'

app.mount('#app')