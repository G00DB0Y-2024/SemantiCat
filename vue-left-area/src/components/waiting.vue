<template>
    <div class="loading-container">

      <!-- 请求显示文字 注意hover颜色要和取消颜色差一个-->
      <label style="
        font-size: 20px;
        background-color: transparent;
        caret-color: transparent;
        user-select: none;
        font-weight: bold;

        transition: all 0.5s ease;
      "
      :style="{color:showColor}"
      >{{ labelText }}</label>

      <!-- 请求特效 -->
      <div 
        v-if="labelColor !== '#AC4848'"
        v-for="(ball, index) in balls" 
        :key="index" 
        class="loading-ball" 
        :style="{backgroundColor:showColor}"
      ></div>

      <!-- 取消请求特效 -->
      <label v-if="labelColor === '#AC4848'" style="width: 100%; text-align: center; color: darkred; font-size: 30px; font-weight: bold;">×</label>

    </div>
</template>

<script>

export default{
  props:['labelText', 'labelColor', 'mouseState'],
  data(){
    return{
      colors:['#4e7bbf', '#4e7bbf', '#4e7bbf'],
      balls:[1,2,3]
    }
    
  },
  computed:{
    showColor(){
      if(this.labelText === 'LOAD')
        return '#4e7bbf'
      return this.mouseState?'#AC4849':this.labelColor

    }

  }

}

</script>

<style scoped>
.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  pointer-events: none;
}

.loading-ball {
  margin-bottom: -5px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  animation: bounce 0.6s infinite alternate;
  
  transition: all 0.5s ease;
}

@keyframes bounce {
  0% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(-5px);
  }
}
</style>