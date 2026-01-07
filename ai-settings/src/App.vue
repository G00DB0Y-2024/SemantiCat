<template>
  <div
    style="display: flex; flex-flow: column; gap: 10px; width: 360px; justify-content: center; align-items: center; padding-right: 10px; padding-block: 10px; transition: height 0.2s ease  ;"
    :style="{height:isFocused?'400px':'200px'}">
    <div style="display: flex; align-items: center; gap: 10px;">
      <div style="height: 20px; width: 50px;text-align:end;">Model:</div>
      <input style="height: 20px; width: 250px; padding-left: 5px;" v-model="model" @input="handelSettingChange" />
    </div>

    <div style="display: flex; align-items: center; gap: 10px; ">
      <div style="height: 20px; width: 50px;text-align:end;">apiUrl:</div>
      <input style="height: 20px; width: 250px; padding-left: 5px;" v-model="apiUrl" @input="handelSettingChange" />
    </div>

    <div style="display: flex; align-items: center; gap: 10px;  ">
      <div style="height: 20px; width: 50px; text-align:end;">apiKey:</div>
      <input style="height: 20px; width: 250px; padding-left: 5px;" v-model="apiKey" @input="handelSettingChange" />
    </div>

    <div style="display: flex; width: 100%; align-items: center; justify-content: center; ">
      <button class="btn-save" :style="{ color: saved ? 'green' : 'black' }" @click="handleSave">{{ saved ? 'Success' : 'Save'
      }}</button>
    </div>
    
    <textarea
      style="resize: none; padding: 5px; width: 90%; align-items: center; gap: 10px; flex: 1;  transition: height 0.2s ease  ;"
      placeholder="自定义提示词: 针对划词内容, 此处将替换原提示词「用中文准确概括」, 留空则为默认提示词" @focus="handleTextareaFocus" @blur="handleTextareaBlur"
      v-model="prompt" @input="handelSettingChange"></textarea>



  </div>

</template>

<script>
export default{
  data(){
    return{
      model:"gemini-2.0-flash-lite",
      apiKey: "", 
      apiUrl: "",
      prompt:"",
      saved:false,
      
      isFocused:false,
    }
  },
  mounted(){
    console.log("获取参数...")
    //获取参数
    chrome.storage.local.get(["model", "apiKey", "apiUrl", "prompt"]).then((result) => {
      this.model = result.model || 'gemini-2.0-flash-lite'
      this.apiKey = result.apiKey || ''
      this.apiUrl = result.apiUrl || ''
      this.prompt = result.prompt || ''
    });

  },
  methods:{
    handleTextareaFocus() {
      this.isFocused = true;
    },

    handleTextareaBlur() {
      this.isFocused = false;
    },
    handelSettingChange(){
      this.saved = false
    },
    handleSave(){
      chrome.storage.local.set({
        model: this.model,
        apiKey: this.apiKey,
        apiUrl: this.apiUrl,
        prompt: this.prompt,
      })
      this.saved = true
    }
  }
  
}

</script>

<style scoped>
.btn-save{
  height: 30px; width: 150px;
  border: 1px solid lightgrey;
  box-shadow: 2px 2px 5px rgba(103, 103, 103, 0.438);
  border-radius: 3px;
  cursor: pointer;
  background-color: #efefef;
  transition: all 0.2s ease;
}
.btn-save:hover{
  border: 1px solid transparent;;
}
</style>