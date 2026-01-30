import './assets/main.css'
import './assets/shared-form-styles.css'
import { library } from '@fortawesome/fontawesome-svg-core';
import { faHome, faBell, faCog, faUser, faSignOutAlt, faSlidersH } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'


const app = createApp(App)

// 注册 FontAwesome
library.add(faHome, faBell, faCog, faUser, faSignOutAlt, faSlidersH);
app.component('font-awesome-icon', FontAwesomeIcon);

// 安装 Pinia
export const pinia = createPinia()
app.use(pinia)

// 启用路由
app.use(router)

app.mount('#app')