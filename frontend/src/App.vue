<template>
  <router-view v-slot="{ Component }">
    <component :is="Component" ref="currentComponent"/>
  </router-view>
</template>

<script setup>
import { ref } from 'vue';
const currentComponent = ref(null);
</script>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html, body, #app {
  height: 100%;
  width: 100vw;
  overflow-x: hidden;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial, sans-serif;
  font-size: 14px;
  line-height: 1.6;
  color: #333;
}
</style>
