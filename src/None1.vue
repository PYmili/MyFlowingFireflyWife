<script setup>
import { onMounted } from 'vue';
import * as live2d from 'live2d-render';

onMounted(async () => {
    await live2d.initializeLive2D({
        // live2d 所在区域的背景颜色
        BackgroundRGBA: [0.0, 0.0, 0.0, 0.0],

        // live2d 的 model3.json 文件的相对路径
        ResourcesPath: 'src/assets/live2d-model/chun/椿.model3.json',

        // live2d 的大小
        CanvasSize: {
            height: window.innerHeight,
            width: window.innerWidth
        },
        
        // 展示工具箱（可以控制 live2d 的展出隐藏，使用特定表情）
        ShowToolBox: true,

        // 是否使用 indexDB 进行缓存优化，这样下一次载入就不会再发起网络请求了
        LoadFromCache: true
    });
    live2d.setExpression("Button1");
    live2d.setExpression("Button2");
    live2d.setExpression("Button3");
    live2d.setExpression("Button7");
    
    console.log('finish loading');
});

</script>

<template>
  <div>
    
  </div>
</template>

<style scoped>

</style>