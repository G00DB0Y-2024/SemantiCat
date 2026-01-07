var vid = ''
var pdf_fp = ''
var loc = 0

function updateModelParameters(){
	chrome.storage.local.get(["model", "apiKey", "apiUrl", "prompt"]).then((result) => {
    chrome.runtime.sendMessage({
      type:'SET_MODEL',
      vid:'',  //不需要vid，因为参数更新是所有组件的
      model:result.model || 'gemini-2.0-flash-lite',
      apiKey:result.apiKey || '',
      apiUrl:result.apiUrl || '',
      prompt:result.prompt || '',
	  });

	});
}


chrome.storage.onChanged.addListener((changes, namespace) => {
  let param_flag = false
  for (let [key, { oldValue, newValue }] of Object.entries(changes)) {
    param_flag = (key === 'model' || key === 'apiKey' || key == 'apiUrl')
  }
  if(param_flag){
    updateModelParameters()
  }
});

// 监听来自页面的消息
window.addEventListener('message', (event)=>{

    if(event.data.type === 'VUE_INIT'){
      vid = event.data.vid
      updateModelParameters()
      console.log(`ROUTER Confirm VID: ${vid}`)

    }//end if
    if(event.data.type === 'PDF_FP'){
      pdf_fp =  event.data.fp
      console.log("Chrome Get FP:"+pdf_fp)

      //通知各个iframe准备从服务器请求
      chrome.runtime.sendMessage(
      { 
        type:"PDF_FP",
        fp:pdf_fp,
        vid:vid,
      })

    }
    if(event.data.type==='PDF_LOC_UPDATE'){
      // console.log(`PDF loc changed: ${event.data.loc}`)
      loc = Math.ceil(event.data.loc[1]*100)
    }



});

setInterval(() => {
  if(document.visibilityState === 'visible'){
      chrome.runtime.sendMessage({type:'UPDATE_PROGRESS', index:Math.max(0, Math.min(99, loc)), fp:pdf_fp, vid:vid});
    
  }
}, 1500);
