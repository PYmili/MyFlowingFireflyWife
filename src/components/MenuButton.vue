<template>
    <div class="options-container" :class="{ 'show-options': isOptionsVisible }">
      <button class="options-button" @click="toggleMenu">
        ☰ 菜单
      </button>
      <div class="options-list" v-if="isOptionsVisible">
        <ul>
          <li @click="handleMenuAction('chat')">聊天</li>
          <li @click="handleMenuAction('settings')">设置</li>
          <!-- motion -->
          <li @click="selectMotion(motion.id)" v-for="motion in motionList" :key="motion.id">
            {{ motion.name }}
          </li>
        </ul>
      </div>
    </div>
</template>
  
<script>
  import { ref, inject } from 'vue';
  
  const isOptionsVisible = ref(false);
  
  function toggleMenu() {
    isOptionsVisible.value = !isOptionsVisible.value;
  }
  
  function handleMenuAction(action) {
    toggleMenu();
  }

  function selectMotion(id) {
    this.$emit('selectMotion', id);
  }
  
  export default {
    setup() {
      // 使用 inject 来接收父组件提供的 motionList
      const motionList = inject('motionList');
  
      // 其他逻辑...
  
      return {
        isOptionsVisible,
        motionList,
        toggleMenu,
        handleMenuAction
      };
    },
    methods: {
        selectMotion
    }
  }
</script>

<style scoped>
.options-container {
    position: absolute;
    top: 0;
    left: 0;
    display: flex;
    align-items: center;
}

.options-button {
    background-color: #f8f8f8;
    border: none;
    padding: 10px;
    cursor: pointer;
    border-radius: 5px;
}

.options-list {
    position: absolute;
    top: 100%;
    left: 0;
    background-color: #fff;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    border: 1px solid #ccc;
    display: none;
    z-index: 10;
    border-radius: 5px;
    padding: 5px 0;
    margin-top: 5px;
    width: 150px;
}

.options-list ul {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
}

.options-list li {
    padding: 8px 16px;
    cursor: pointer;
    color: #333;
}

.options-list li:hover {
    background-color: #f0f0f0;
}

.show-options .options-list {
    display: block;
}
</style>