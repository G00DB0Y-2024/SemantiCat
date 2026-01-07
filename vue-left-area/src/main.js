import { createApp } from 'vue'
import App from './App.vue'
import axios from 'axios'
import './assets/main.css'

import hljs from 'highlight.js'
import 'highlight.js/styles/atom-one-dark.css'

const app = createApp(App)

app.config.globalProperties.$axios = axios;
axios.defaults.withCredentials = false;
axios.defaults.baseURL = 'http://localhost:8225'

app.directive('highlight', {
    mounted(el) {
        // console.log('el', el)
        const blocks = el.querySelectorAll('pre code')
        for (let i = 0; i < blocks.length; i++) {
            hljs.highlightElement(blocks[i])
        }
    }
})

app.mount('#app')