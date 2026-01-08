<template>
  <div class="content">
    <div class="sliderbox">
      <!-- barholder -->
      <div style="min-height: 32px; width: 100%; background-color: rgb(249, 249, 250); border-bottom: 1px solid rgb(184, 184, 184);"></div>

      <!-- barholder-little -->
      <div style="min-height: 12.5px; width: 100%; background-color: rgb(249, 249, 250);"></div>

      <!-- opacity block -->
      <div style="min-height: 0; flex: 1; width: 100%; transition: all 0.2s ease;"  v-for="(opa, index) in opacity_arr" :style="{backgroundColor:`rgba(72,112,172,${opa})`}"></div>

      <!-- barholder-little -->
      <div style="min-height: 12.5px; width: 100%; background-color: rgb(249, 249, 250);"></div>

    </div>

    
  </div>



</template>

<script >


export default{

  created(){
    this.opacity_arr = new Array(100).fill(0)
    const urlParams = new URLSearchParams(window.location.search);
    const ts = urlParams.get('ts');
    console.log(`VUE BAR Confirm VID: ${ts}`)
    this.vid = ts

    chrome.runtime.onMessage.addListener((message, sender, senderResponse) => {
      if(message.vid === this.vid || message.vid === ''){

        if(message.type === 'PDF_FP'){
          //获得PDF_FP以请求AI储存资料
          console.log("VUE BAR Get FP:"+message.fp)
          this.pdf_fp = message.fp
          this.$axios.post("/loadOps", { fp:this.pdf_fp}).then(res=>{
            this.opacity_arr.splice(0,100, ...res.data)
          })

        }
        if(message.type === 'UPDATE_PROGRESS'){
          //更新指定索引的透明度值
          var temp_ops = [...this.opacity_arr]
          var needNormalize = temp_ops.some(num => num > 1);
          temp_ops[message.index] += 0.01;  //透明度步进

          if(needNormalize){
            const max = Math.max(...temp_ops);
            const min = Math.min(...temp_ops);
            const range = max - min;
            
            temp_ops = range === 0 
              ? temp_ops.map(() => 0.5)
              : temp_ops.map(op => (op - min) / range);
            
          }
          // 更新原始数组为归一化后的值（可选）
          this.opacity_arr.splice(0, 100, ...temp_ops);

          //保存
          this.$axios.post("/saveOps", {ops:this.opacity_arr, fp:this.pdf_fp})
        }
      }

    });

  },
  data(){
    return{
      opacity_arr:[],
      vid:"",
      pdf_fp:"",

    }

  },
  methods:{


  }

}


</script>
<style scoped>

.content{
  display: flex; 
  flex-flow: row;  
  height: 100vh;
  overflow: hidden;
  background-color: white;

}
.iframebox {
  flex: 1;
}

.sliderbox{
  display: flex;
  flex-flow: column;
  overflow: hidden;
  width: 100%;
  align-items: center;
  position: relative;
}

</style>
