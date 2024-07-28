import "./tailwind.css";
import "element-plus/dist/index.css";

import { createApp } from 'vue'
import App from './App.vue'
import router from './router' // Import the router configuration

const app = createApp(App);

app.use(router); // Use the router

app.mount('#app');