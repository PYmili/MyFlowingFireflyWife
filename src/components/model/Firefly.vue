<template>
  <div class="container">
    <!-- 画布元素 -->
    <canvas ref="canvas"></canvas>
    <!-- 导入并使用 MenuButton 组件 -->
    <MenuButton @selectMotion="hanldeSelectMotion" />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, provide } from "vue";
import * as PIXI from "pixi.js";
import { Live2DModel } from "pixi-live2d-display/cubism4";
import MenuButton from "@/components/MenuButton.vue"; // 导入MenuButton组件

// 将PIXI库挂载到window上，以便在Live2DModel中使用
window.PIXI = PIXI;
// 使用ref创建一个响应式变量来存储canvas元素
const canvas = ref(null);

let app;
let model;

const motionList = ref([{ id: 9, name: "唱歌" }]);
provide("motionList", motionList);

function hanldeSelectMotion(id) {
  model.motion("动作组", id).then(() => {
    model.motion(null, null, -1);
  });
}

// 显示/隐藏模型指针事件的函数
function ModelPointerdownEvent(model) {
  model.on("pointerdown", (hitAreas) => {
    const { x, y } = hitAreas.data.global;
    console.log(`pointerdown event: x=${x}, y=${y}`);
    // 判断头部区域是否被点击
    if (x >= 100 && x <= 250 && y >= 30 && y <= 100) {
      console.log("头部区域被点击");
      model.expression("expression2.exp3");
      model.motion("表情组", 1).then(() => {
        model.motion(null, null, -1);
      });
      return;
    }
    // 判断眼睛区域是否被点击
    if (x >= 150 && x <= 240 && y >= 120 && y <= 135) {
      console.log("眼睛区域被点击");
      model.expression("expression1.exp3").then(() => {
        model.motion(null, null, -1);
      });
      model.motion("表情组", 0);
      return;
    }
    // 其他区域点击
    console.log("其他区域被点击");
    const randomMotion = {
      动作组: [4, 8],
    };
    const randomActionIndex = Math.floor(
      Math.random() * randomMotion["动作组"].length
    );
    model
      .motion("动作组", randomMotion["动作组"][randomActionIndex])
      .then(() => {
        model.motion(null, null, -1);
      });
  });
}

// 调整画布大小的函数
function resizeCanvas() {
  if (!(app && model)) {
    return;
  }
  const canvasElement = canvas.value;
  const maxWidth = canvasElement.clientWidth;
  const maxHeight = canvasElement.clientHeight;
  const scaleWidth = maxWidth / model.width;
  const scaleHeight = maxHeight / model.height;
  const scale = Math.min(scaleWidth, scaleHeight);
  // 设置一个缩放比例的范围，比如 0.05 到 0.09
  const minScale = 0.02;
  const maxScale = 0.09;
  const finalScale = Math.max(minScale, Math.min(scale, maxScale));
  model.scale.set(finalScale);

  // 设置模型的锚点为其中心点
  model.anchor.set(0.5, 0.5);

  // 计算模型的新位置，使其居中
  model.x = maxWidth / 2;
  model.y = maxHeight / 2;

  app.renderer.resize(maxWidth, maxHeight);
}

// 初始化Live2D模型和Pixi应用的异步函数
async function initLive2D() {
  model = await Live2DModel.from("./live2d-model/Firefly/Firefly.model3.json");
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

  ModelPointerdownEvent(model);
  model.scale.set(0.09); // 初始缩放值
  app.stage.addChild(model);
  window.addEventListener("resize", resizeCanvas);
  resizeCanvas();
}

onMounted(async () => {
  await initLive2D();
});

onUnmounted(() => {
  window.removeEventListener("resize", resizeCanvas);
  model?.destroy();
  app?.destroy();
});
</script>

<style scoped>
.container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: transparent;
}
canvas {
    background-color: transparent;
}
</style>