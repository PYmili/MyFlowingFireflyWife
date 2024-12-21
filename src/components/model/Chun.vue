<template>
  <div class="container">
    <!-- 画布元素 -->
    <canvas ref="canvas"></canvas>
    <!-- 导入并使用 MenuButton 组件 -->
    <MenuButton />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import * as PIXI from "pixi.js";
import { Live2DModel } from "pixi-live2d-display/cubism4";
import MenuButton from '@/components/MenuButton.vue'; // 导入MenuButton组件

// 将PIXI库挂载到window上，以便在Live2DModel中使用
window.PIXI = PIXI;
// 使用ref创建一个响应式变量来存储canvas元素
const canvas = ref(null);
// 音频文件路径
const audioFile = "public/audio/chun/test.mp3";
// 模型缩放值
const scaleValue = 0.09;

let app;
let model;
let audioContext;

// 生成随机数的函数
function random(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

// 显示/隐藏模型指针事件的函数
function ModelPointerdownEvent(model) {
  model.on('pointerdown', (hitAreas) => {
    const { x, y } = hitAreas.data.global;
    const header = ["爱心眼", "脸红", "眼高光消失", "哭"];
    const other = "黑脸";
    if (y <= 300) {
      model.expression(header[random(0, header.length - 1)]);
    } else {
      model.expression(other);
    }
    console.log("pointerdown event over.");
  })
}

// 调整画布大小的函数
function resizeCanvas() {
  if (!(app && model)) {
    return;
  }
  app.renderer.resize(model.width, model.height);
}

// 初始化Live2D模型和Pixi应用的异步函数
async function initLive2D() {
  // 创建音频上下文
  audioContext = new AudioContext();
  // 载入Live2D模型
  model = await Live2DModel.from("./live2d-model/chun/椿.model3.json");
  // 创建Pixi应用
  app = new PIXI.Application({
    view: canvas.value,
    resizeTo: window,
    width: model.width,
    height: model.height,
    autoDensity: true,
    antialias: true,
    resolution: window.devicePixelRatio,
    backgroundAlpha: 0,
  });
  
  // 初始化模型事件
  ModelPointerdownEvent(model);
  
  // 设置模型缩放
  model.scale.set(scaleValue);
  
  // 将模型添加到Pixi舞台
  app.stage.addChild(model);
  // 监听窗口大小变化事件
  window.addEventListener('resize', resizeCanvas);
  // 调整画布大小
  resizeCanvas();
}

// 在组件挂载后初始化Live2D
onMounted(async () => {
  await initLive2D();
});

// 在组件卸载前移除事件监听并销毁资源
onUnmounted(() => {
  window.removeEventListener('resize', resizeCanvas);
  model?.destroy();
  app?.destroy();
});
</script>

<style scoped>
/* 设置容器为 Flexbox 布局 */
.container {
  display: flex;
  flex-direction: column; /* 垂直排列子元素 */
  justify-content: center; /* 垂直居中 */
  align-items: center; /* 水平居中 */
  height: 100vh; /* 使容器高度占满视口 */
  background-color: transparent;
}
canvas {
  background-color: transparent;
}
</style>