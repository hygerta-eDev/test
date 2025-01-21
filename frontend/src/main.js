import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import CanvasJSChart from '@canvasjs/vue-charts';
import 'tailwindcss/tailwind.css';
import '@fortawesome/fontawesome-free/css/all.css';
import App from './App.vue'
import router from './router'
import Vue3Toasity from 'vue3-toastify';
import 'vue3-toastify/dist/index.css';
// import store from './stores/Shipments';
import store from './stores/shipments';

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(Vue3Toasity, {
    autoClose: 3000,
});
app.use(CanvasJSChart)

app.use(store);

app.component('vue-multiselect')
app.mount('#app')
