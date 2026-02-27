import { createPinia } from 'pinia'
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './style.css'

import { vMaska } from 'maska/vue'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.directive('maska', vMaska)

app.mount('#app')
