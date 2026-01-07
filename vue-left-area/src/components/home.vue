<template>
  <!-- @mouseenter="console.log('Mouse Entered')" @mouseleave="console.log('Mouse Left')" -->
  <div class="content" @mouseup="handelSelectedHighlight">
    <div class="sliderbox">

      <!-- 顶部栏 -->
      <div
        style="display: flex; width: 100%; background-color: #F9F9FA; min-height: 32px; border-bottom: 1px solid #B8B8B8;">
        <div style="display: flex; height: 100%; align-items: center; margin-left: 10px; gap: 10px;">
          <label class="btn-show-ori" @click="showOrigin=!showOrigin"
            :style="{color:showOrigin?'#4e7bbf':''}">ORIGIN</label>
          <label class="btn-adding" @click="chosen_add_text.length=0; chosen_text=''"
            :style="{width:chosen_add_text.length===0?0:'52px', opacity:chosen_add_text.length===0?0:1}">+{{
            chosen_add_text.length }} MORE</label>
          <div style="
            display: flex;
            position: absolute;
            font-size: 10px;
            right: 2px;
            column-gap: 10px;
            align-items: center;
            transform: scaleX(0.95);
            transform-origin: right;
          ">
            <label style="color: black;">Input:<span
                style="color: #4870AC;">{{classifyRateArr[0].toFixed(1)}}%</span></label>
            <label style="color: black;">Feedback:<span
                style="color: #82AD75;">{{classifyRateArr[1].toFixed(1)}}%</span></label>
            <label style="color: black;">Output:<span
                style="color: #AC4848;">{{classifyRateArr[2].toFixed(1)}}%</span></label>
          </div>
        </div>

      </div>

      <!-- 左侧功能区 -->
      <div style="
        display: flex;
        flex-flow: column;
        overflow: hidden;
        width: 100%;
        height: 100%;
        align-items: center;
      ">

        <!-- 原文 -->
        <div style="transition: all 0.2s ease; display: flex; flex-flow: column; width: 100%; height: 500px;"
          :style="{height: showOrigin? '500px':'0'}">
          <textarea class="textarea-ori"
            :style="{height: showOrigin? '100%':'0', opacity:showOrigin?'1':'0', pointerEvents:showOrigin?'all':'none'}">{{ shown_text }}</textarea>
        </div>

        <!-- GPT显示区域 -->
        <div style="display: flex; width: 100%; height: 100%; overflow: hidden; position: relative;">

          <!-- 索引部分 -->
          <div style="display: flex; flex-flow: column; height: 100%; width: 7px; background-color: white;">
            <div v-for="(item, index) in childrenHeightArr"
              :class="current_index===index && !can_current_index_change?'div-index-block-active':'div-index-block'"
              :style="{
              height:`${item.hrate}%`, 
              backgroundColor:MapHeadBarBackgroundColor(item.htype),
            }" @click="adjustScroll(item.hindex); highlightScroll(item.hindex);">
            </div>

            <!-- 位置指针 -->
            <div v-if="ai_res.length!==0" style="
                left: 7px;
                background-color: transparent;
                position: absolute;
                display: flex;
                align-items: start;
                justify-content: start;
                height: 0;
                margin-top: -7.5px;
                font-size: 10px;
                color: black;
                font-family: cursive;
                scale: 0.8;
                text-shadow: 2px 2px 2px rgba(0,0,0,0.3);
                transition: all 0.15s ease;
              " :style="{top: scrollTopRate}">◀</div>

            <!-- 高亮位置指针 -->
            <div v-for="(item, key, index) in hl_arr" :key="key" style="
                left: 5px;
                background-color: transparent;
                position: absolute;
                display: flex;
                align-items: start;
                justify-content: start;
                height: 0;
                margin-top: -7.5px;
                font-size: 10px;
                color: #B05151;
                font-family: cursive;
                scale: 0.5;
                text-shadow: 2px 2px 2px rgba(0,0,0,0.3);
              " :style="{top: item.position}">◀</div>

          </div>

          <!-- GPT显示内容 -->
          <div ref="render_container" class="gpt-render" @scroll="UpdatePointerPosition"
            @auxclick="handleMouseSideButton">
            <div v-for="(item, index) in ai_res" ref="render" :key="index"
              style="display: block; background-color: transparent; transition: all 0.2s ease;">
              <gptRenderUnit style="width: 100%;" :content="item.text" :datetime="item.dt" :hldata="item.hl"
                :headtype="item.type" :gid="index" :vid="vid" :img_name="item.img"
                :editting="index === annotation_edit_index" :key="`${refreshKey}-${index}`" @onQuote="handleQuote"
                @onClose="handleAiChange('DEL', index, null)" @onHlClick="handleHlClick(item.hl, item.type, index)"
                @onANNOClick="handleANNOClick(item.hl, item.type)" />

            </div>

            <div ref="last_blank"
              style="min-height: 0; color: transparent; background-color: transparent; flex-shrink: 0;">占位标识</div>
          </div>

          <!-- 精灵图片 -->
          <img src="../assets/images/Cyrstal.png" style="
            width: 75%;
            position: absolute;
            bottom: 0;
            left: 0;
            object-fit: contain;
            -webkit-user-select:none;
            -moz-user-select:none;
            -ms-user-select:none;
            user-select:none;
            pointer-events: none;
            transition: all 0.2s ease;
          " :style="{
            opacity: `${imageShowFlag?0.25:0}`,
            filter: `blur(${lastBottomRate < 0.05? 0 : 4*lastBottomRate*lastBottomRate*100 }px)`
          }" />

        </div>


        <!-- 追问 -->
        <div ref="askMask"
          style="display: flex; position: relative; width: 100%; height: 30px; transition: all 0.2s ease;"
          :style="{height:askFocus?'80px':'30px', minHeight:'30px'}">
          <textarea :style="{border: askFocus?'1.5px solid #4870AC':'1.5px solid rgba(0,0,0,0.25)'}" ref="askTextrea"
            class="textarea-ask" @focus="askFocus=true; 
          showOrigin=false" @blur="handleAskAreaBlur()" @keydown.ctrl.enter="handleAsk(); ConfirmAnnotation();"
            @paste="handlePaste" v-model="askContent" placeholder="Ask me => Ctrl + Enter！"></textarea>

          <label class="lb-quote-num"
            :style="{opacity:askQuote.length===0?'0':'1', pointerEvents:askQuote.length===0?'none':'all', borderColor:askQuote.length>1?'darkred':'#4870AC', color:askQuote.length>1?'darkred':'#4870AC'}"
            @click="askQuote.length=0">quote +{{ askQuote.length }}</label>
          <label class="lb-quote-num"
            :style="{opacity:askImage.img===null?'0':'1', pointerEvents:askImage.img===null?'none':'all', borderColor:'#6812b0', color:'#6812b0'}"
            @mouseover="can_blur=false" @mouseleave="can_blur=true"
            @click="handleAnnoationImgDel();resetImgInfo();">image {{ askImage.size }} kB</label>
        </div>

        <!-- 等待中（非内容部分） -->
        <div class="wait-outer-continer"
          :style="{opacity:waiting||waiting_cancel?'1':'0', pointerEvents:waiting||waiting_cancel?'all':'none'}"
          @keydown.esc="handleForceStop" @click="handleForceStop" @mouseover="waiting_mouse=true"
          @mouseleave="waiting_mouse=false">
          <waiting :labelText="wait_text" :labelColor="wait_color" :mouseState="waiting_mouse" />
        </div>
      </div>

      <textarea ref="blurTextarea" style="position: absolute; opacity: 0; height: 0; width: 0;"></textarea>
    </div>


  </div>



</template>

<script >
import gptRenderUnit from './gptRenderUnit.vue'
import waiting from './waiting.vue'
import { serialize, deserialize } from './range-serializer.js';

function RulesOfMarkdown() {
  return `
无序列表及其嵌套:要创建无序列表，请在每个列表项前添加'-'并紧跟一个英文句点, 并键入一个空格后键入内容; 由于四空格缩进容易被识别为代码块, 请使用两个空格缩进
- First item
- Second item
- Third item
    - Indented item
    - Indented item
- Fourth item

有序列表及其嵌套:要创建有序列表，请在每个列表项前添加数字并紧跟一个英文句点, 并键入一个空格后键入内容; 由于四空格缩进容易被识别为代码块, 请使用两个空格缩进
有序列表和无序列表可以混合使用, 以实现更加易于理解的分条
1. First item
2. Second item
3. Third item
    1. Indented item
    2. Indented item
4. Fourth item

代码块及其嵌套:使用三个反引号以创建围栏式代码块, 用于键入伪代码或是用户要求的编程语言代码, 请不要在这里面使用任何markdown或是latex语法, 因为这样将无法渲染
\`\`\`
{
  "firstName": "John",
    "lastName": "Smith",
      "age": 25
}
\`\`\`

引用语法: 引用常常用于解释或者引用, 要创建块引用，请在段落前添加一个'>'符号, 并键入一个空格后键入内容, 可以多行, 也可以使用其他markdown愈发
请注意, 为了渲染易读性, 请仅仅在文段后的进一步解释或是通俗理解中使用引用语法, 而不要在正文中使用
> #### The quarterly results look great!
>
> - Revenue was off the chart.
> - Profits were higher than ever.
>
>  *Everything* is going according to **plan**.

内联语法: 加粗, 斜体, 强调是存在的三种markdown内联语法, 然而为了渲染便利, 请不要使用斜体
1. 要加粗文本，请在单词或短语的前后各添加两个星号（asterisks）。如需加粗一个单词或短语的中间部分用以表示强调的话，请在要加粗部分的两侧各添加两个星号（asterisks）
例如: I just love **bold text**
2. 要用斜体显示文本，请在单词或短语前后添加一个星号（asterisk）。要斜体突出单词的中间部分，请在字母前后各添加一个星号
但是, 由于斜体会引起渲染异常, 请永远不要使用斜体格式
例如: Italicized text is the *cat's meow*.
3. 要强调文本, 请在单词或短语前后添加一个反引号'\`'
为了易读性和统一性, 请不要将强调格式用于符号和变量, 符号和变量统一使用latex单美元符号格式, 请仅仅在函数命名上使用该格式
例如: Using the inner function \`Console.log\` to print the logs.

[以下为没有任何渲染异常且格式合理的模范示例, 请参考]
- Alice 初到新城市，球技不佳，与他人组队踢球，因队友 Megan 表现出色而获胜.
- 使用单步动作策略梯度估计时，Alice 的所有动作都会因胜利而得到正向加强，即使她的表现不佳，这是因为她的行为被错误地归功于胜利.
- 常规基线无法解决此问题，因为 Alice 事先不知道 Megan 的技能，假设 Megan 的实力一般，队伍获胜的概率为 50%.
- 可以通过事后诸葛亮的方式解决此问题：
    - 认识到 Megan 的出色表现并非 Alice 造成的.
    - 事后将 Megan 的技能水平纳入基线考虑.

> 简单来说，就是 Alice 赢了比赛，但实际上是靠队友带飞。如果 Alice 不知道队友很强，就会误以为自己也很厉害，从而错误地学习。

- 使用根据 Megan 技能水平调整的 **后见之明基线** (Hindsight Baseline)，将优势估计（advantage estimate）和相应的学习信号驱动到接近于 0.

> 后见之明基线会根据实际情况调整对 Alice 行为的评价，避免 Alice 盲目自信。

`

}

function RulesOfLatex() {
  return `
内联公式: 需要在一行内使用符号或是短公式, 则用单美元符号标记, 注意在美元符号两侧留有空格
例如: $E=mc^2$ , $T$

行间公式: 如需要单独一行展示公式, 用双美元符号标记在公式航上下行, 而公式单独占用一行, 因此一共占用三行
$$
\\nabla \\cdot \\mathbf{D} = \\rho
$$
`

}

export default{
  components:{
    gptRenderUnit,
    waiting,

  },
  data(){
    return{
      chosen_text:"",
      chosen_text_history:"",
      chosen_add_text:[],
      chosen_hldata:null,
      shown_text:"",

      ai_res:[],  //控制侧边显示的内容viewmodel，由于早期开发的因素，此处命名为ai_res，其实包含ai、询问以及注释
      isDragOver: false,
      showOrigin: false, // 新增状态控制
      askFocus: false,
      askContent:"",
      askQuote:[],
      askImage:{img:null, size:0},
      

      memorylist:[],
      gptModel:"gemini-2.0-flash",
      gptModelVision:"gpt-4o-mini",
      apiKey: "", // 替换为你的 AiHubMix API 密钥
      apiUrl: "",
      addedPrompt:"",

      pdf_fp:"", //pdf指纹，用于访问AI的储存

      waiting:false,
      waiting_cancel:false,
      waiting_mouse:false,
      wait_text:'WAIT',
      wait_color:'#4e7bbf',  //#4e7bbf #AC4848
      cancelTokenSource:null,

      opacityArr:[],

      annotation_mode:false,
      annotation_flag:false, //判断是否确认注释
      annotation_hldata:null,
      annotaiton_selected:"",  //注释选中文本
      annotation_edit_index:-1, //准备修改的item
      annotation_edit_texts:[],
      can_blur:true,
      refreshKey:0,
      can_render_click:true,
      
      childrenHeightArr:[],  //索引显示model
      classifyRateArr:[0,0,0], //显示每一种卡片百分比
      scrollTopRate:"0%",  //指针位置
      scrollHeightSum:1,

      containerRect:null,
      current_index:0,  //追踪索引
      can_current_index_change:true, //是否允许当前索引改变
      lastBottomRate:1, //最后一个元素的底部距离容器底部占容器百分比
      imageShowFlag: false, //图片显示标志
    
      hl_arr:{},  //高亮位置
    }

    
  },
  setup(){
    return {
      RulesOfMarkdown,
      RulesOfLatex
    };
  },
  mounted() {
    const container = this.$refs.render_container;
    this.containerRect = container.getBoundingClientRect();
    
    window.addEventListener('resize', () => {
      const container = this.$refs.render_container;
      if (container) {
        this.containerRect = container.getBoundingClientRect();
        this.UpdateWindowUI().then(()=>{
          this.adjustScroll(this.current_index);
        });
      }
    });

    const urlParams = new URLSearchParams(window.location.search);
    const ts = urlParams.get('ts');
    console.log(`VUE Confirm VID: ${ts}`)
    this.vid = ts

    chrome.runtime.onMessage.addListener((message, sender, senderResponse) => {
      if(message.vid==='' ||  message.vid === this.vid){

        if(message.type === 'SET_TEXT'){
          console.log(`VUE[${this.vid}] SELECT TEXT: ${message.text.length} words`)
          this.onTextChange(message.text, message.add, message.hldata)
          window.focus()
          this.$refs.blurTextarea.focus()

        }
        if(message.type === 'SET_MODEL'){
          console.log("VUE PARAMETERS SET: "+`${JSON.stringify(message)}`)
          this.gptModel = message.model
          this.apiKey = message.apiKey
          this.apiUrl = message.apiUrl
          this.addedPrompt = message.prompt

        }
        if(message.type === 'RESET_MORE'){
          //MORE 清除请求
          if(this.chosen_add_text.length !== 0){
            this.chosen_add_text.length = 0
            this.chosen_text = ''
          }
        }
        if(message.type === 'PDF_FP'){
          //获得PDF_FP以请求AI储存资料
          console.log("VUE Get FP:"+message.fp)
          this.pdf_fp = message.fp
          this.$axios.post('/reqLoadAIPre', {fp:this.pdf_fp}).then(res=>{
            if(res.data){
              this.wait_text = 'LOAD'
              this.waiting = true
              this.handelAiLoad()

            }
          })

        }
        if(message.type === 'ADD_ANNOTATION'){
          //请求添加注释，此时输入框获得焦点
          this.annotation_flag = false 
          this.annotation_mode = true
          this.annotation_hldata = message.hldata
          this.askFocus = true
          this.$refs.askTextrea.focus()
          this.annotaiton_selected = message.text

        }
        if(message.type === 'ACTIVE_CANCEL_ANNOATION'){
          //pdf主动失去焦点
          if(this.annotation_mode){
            this.annotation_mode = false
            this.askContent = ""
            this.askQuote.length = 0
            this.askFocus = false
            this.$refs.blurTextarea.focus()
            this.resetImgInfo()
          }


        }
        if(message.type === 'ACTIVE_CLICK_ANNO'){
          //pdf主动点击注释，vue跳转
          let index = -1
          this.ai_res.forEach((item, i)=>{
            if(item.type==='LIST_TYPE_ANNO_'+message.flag){
              index = i
              return
            }
          })
          this.adjustScroll(index)
        }
        if(message.type === 'API_FORCE_STOP'){
          //主动请求取消
          this.handleForceStop()

        }
      }

    });

    window.top.postMessage({type:'VUE_INIT', vid:ts}, '*')

  },
  methods:{
    getHighlightPos(rangeRect){
      
      //控制计算
      const container = this.$refs.render_container;
      const targetElement = container.children[0];

      if (targetElement) {
        const targetRect = targetElement.getBoundingClientRect();
        const offsetTop = Math.abs(rangeRect.top - targetRect.top);
        const percentage = offsetTop/this.scrollHeightSum*100
        return `${percentage}%`;
      }

      return '0%';
    },
    setRangeHighlight(selectedRange, key) {
      // 检查选中范围是否包含数学公式节点
      // 查找所有包含 math 标签的 p.katex 元素
      const mathNodes = document.querySelectorAll('p.katex:has(math)');
      let containsMath = false;
      
      // 检查选中范围是否与任何数学公式节点重叠
      mathNodes.forEach(node => {
        if (selectedRange.intersectsNode(node)) {
          containsMath = true;
        }
      });
      
      // 如果包含数学公式节点，则不执行高亮
      if (containsMath) {
        console.log('选中范围包含数学公式，已跳过高亮');
        return;
      }

      // 创建高亮span
      const highlightSpan = document.createElement('span');
      highlightSpan.style.cssText = `
        background-color: transparent;
        color: inherit;
        font-style: inherit;
        font-weight: inherit;
        text-decoration: inherit;
        border-inline: 2px solid transparent;
        padding: 1px;
        margin-inline: 1px;
        transition: all 0.2s ease;
      `;

      // 添加鼠标悬停事件监听器来控制光标样式
      highlightSpan.addEventListener('mouseover', (event) => {
        if (event.altKey) {
          highlightSpan.style.cursor = 'pointer';
        } else {
          highlightSpan.style.cursor = '';
        }
      });

      // 添加鼠标移出事件监听器清除光标样式
      highlightSpan.addEventListener('mouseout', () => {
        highlightSpan.style.cursor = '';
      });

      // 注册按住 Alt 再左键删除高亮
      highlightSpan.addEventListener('click', (event) => {
        if (!(event.altKey && event.button === 0)) return;
        event.stopPropagation();
        const parent = highlightSpan.parentNode;
        // 提取高亮节点的所有子节点（支持非文本节点）
        const fragment = document.createDocumentFragment();
        while (highlightSpan.firstChild) {
          fragment.appendChild(highlightSpan.firstChild);
        }
        // 用子节点替换高亮span，恢复原始结构
        parent.replaceChild(fragment, highlightSpan);

        if (this.hl_arr.hasOwnProperty(key)) {
          delete this.hl_arr[key];
        }
        this.$axios.put('/reqHighlightSet', { fp: this.pdf_fp, key: key, hl: null });
      });

      // 提取选中范围的内容（支持非文本节点）
      const extractedContent = selectedRange.extractContents();
      // 将提取的内容放入高亮span
      highlightSpan.appendChild(extractedContent);
      // 将高亮span插入到原选中范围的位置
      selectedRange.insertNode(highlightSpan);

      // 延迟添加高亮样式，产生过渡效果
      setTimeout(() => {
        highlightSpan.style.backgroundColor = '#B0515135';
        highlightSpan.style.borderColor = '#B05151';
      }, 50);

    },
    loadRangeHighlight(){
      this.hl_arr = {};  // 清空高亮位置对象
      this.$axios.post('/reqHighlightGet', {fp:this.pdf_fp, key:'', hl:null}).then(res=>{
        if (res.data) {
          Object.entries(res.data).forEach(([key, hl]) => {
            if (hl) {
              const range = deserialize(hl);
              if(range){
                this.setRangeHighlight(range, key);
                this.hl_arr[key] = {
                  range: range,
                  position: this.getHighlightPos(range.getBoundingClientRect()),  // 获取高亮位置
                }
              }

            }
          });
        }

      })
    },
    handelSelectedHighlight(e) {
      if (e.button === 0) {
        const selection = window.getSelection();
        if (!selection.isCollapsed) {
          const selectedRange = selection.getRangeAt(0);
          const selectedText = selection.toString();

          if (e.altKey && selectedText) {
            const key = `HL_${Date.now()}_${this.generateRandomCode()}`
            const hl_range_sel = serialize(selectedRange);  //序列化range

            const hl_range_des = deserialize(hl_range_sel);  //反序列化range
            this.setRangeHighlight(hl_range_des, key);  // 设置高亮

            this.hl_arr[key] = {
              range: hl_range_des,
              position: this.getHighlightPos(hl_range_des.getBoundingClientRect()),  // 获取高亮位置
            }
            this.$axios.put('/reqHighlightSet', {fp:this.pdf_fp, key:key, hl:hl_range_sel})  //发送高亮数据
            
            selection.removeAllRanges();
          }
        }
      }
    },
    handleMouseSideButton(event){
      if(!this.can_current_index_change)
        return
      if (event.button === 3) {  // 后退侧键
        this.current_index ++
      } else if (event.button === 4) {  // 前进侧键
        this.current_index --
      }
      else{
        return
      }
      this.current_index = this.current_index <0 ? 0: this.current_index>=this.ai_res.length? this.ai_res.length-1 :this.current_index  //边界修正
    
      this.adjustScroll(this.current_index); 
      this.highlightScroll(this.current_index);


    },
    UpdateWindowUI(){
      return new Promise((resolve, reject) => {
        //控制更新UI 
        this.$nextTick(()=>{
          this.UpdateChildrenHeightArr()
          this.UpdatePointerPosition()

          let container = this.$refs.render_container
          this.containerRect = container.getBoundingClientRect();

          let last_ai_el = container.children[this.ai_res.length-1]  //最后一个ai元素
          if(last_ai_el){
            this.$refs.last_blank.style.height = `${this.containerRect.height}px`
          } 
        
          this.$nextTick(resolve)
        })
      });


    },
    UpdatePointerPosition() {
      // 控制计算
      const container = this.$refs.render_container;
      const targetElement = container.children[0];

      if (targetElement) {
        const targetRect = targetElement.getBoundingClientRect();
        const offsetTop = Math.abs(targetRect.top - this.containerRect.top);
        const percentage = offsetTop / this.scrollHeightSum * 100;
        this.scrollTopRate = `${percentage}%`;
      }

      let last_ai_el = container.children[this.ai_res.length - 1]; // 最后一个ai元素
      if (last_ai_el) {
        let last_ai_el_rect = last_ai_el.getBoundingClientRect();
        this.imageShowFlag = true;
        this.lastBottomRate = Math.max(0, (last_ai_el_rect.bottom - this.containerRect.top) / (this.containerRect.height));
      }

      //更新高亮位置
      Object.entries(this.hl_arr).forEach(([key, hl]) => {
        if (hl.range) {
          const rangeRect = hl.range.getBoundingClientRect();
          if (rangeRect.top === 0 && rangeRect.left === 0)  //位置有效性判断
          {
            delete this.hl_arr[key];
            this.$axios.put('/reqHighlightSet', { fp: this.pdf_fp, key: key, hl: null }); 
          }
          else{
              hl.position = this.getHighlightPos(rangeRect);
          }
          
        }
      });

      this.$nextTick(()=>{
        // 判断滚动是否到底
        if (container.scrollTop + container.clientHeight >= container.scrollHeight - 2) {
          this.lastBottomRate = 0
        }
      })
    },
    UpdateChildrenHeightArr(){
      this.childrenHeightArr.length = 0
      const container = this.$refs.render_container;

      let height_arr = []
      let height_sum = 0

      this.ai_res.forEach((item, index)=>{
        // 确保索引有效
        if (index < -1 || index >= container.children.length) {
          console.error('Invalid index:', index);
          return;
        }
        const targetElement = container.children[index];
      
        if (targetElement) {
          // 获取目标元素的边界矩形
          const targetRect = targetElement.getBoundingClientRect();
          let h = targetRect.height
          height_arr.push(h)
          height_sum += h
        }
      })
      this.scrollHeightSum = height_sum  //更新求和高度
      this.classifyRateArr = [0,0,0]
      
      height_arr.forEach((h, index)=>{
        const ai_type = this.ai_res[index].type
        const ai_hrate = h/height_sum*100 
        this.childrenHeightArr.push({
          hindex:index,
          hrate:ai_hrate,
          htype:ai_type
        })
        //classifyRateArr [input  feedback   ouput]
        if(ai_type.includes('LIST_TYPE_AI')){
          this.classifyRateArr[0] += ai_hrate
        }
        if(ai_type.includes('LIST_TYPE_ASK')){
          this.classifyRateArr[1] += ai_hrate
        }
        if(ai_type.includes('LIST_TYPE_ANNO')){
          this.classifyRateArr[2] += ai_hrate
        }
      })

    },
    MapHeadBarBackgroundColor(headtype){
      if(headtype.includes('LIST_TYPE_ASK')){
        return 'rgba(86, 145, 69, 0.741)'
      }
      if(headtype.includes('LIST_TYPE_AI')){
        return 'rgb(122, 155, 205)'
      }
      if(headtype.includes('LIST_TYPE_ANNO')){
        return '#AC4848'
      }
    },
    handleForceStop(){
      if(this.wait_text === 'LOAD' || !this.waiting)  //加载操作不可取消
        return
      
      this.waiting = false //强制停止
      this.waiting_cancel = true //强制遮罩
      this.cancelTokenSource?this.cancelTokenSource.cancel('请求被用户取消'):null //强制停止请求
      this.wait_text = 'CANCEL'
      this.wait_color = '#AC4848'

      const delay_time = 500
      setTimeout(() => {
        this.waiting_cancel = false
      }, delay_time);
      setTimeout(() => {
        this.wait_text = 'WAIT'
        this.wait_color = '#4e7bbf'
      }, delay_time + 200);  //附加动画时间 0.2s

    },
    generateRandomCode() {
      // 生成0-999999的随机数，不足六位时前补0
      return Math.floor(Math.random() * 1000000).toString().padStart(6, '0');
    },
    ConfirmAnnotation(){
      if(!this.annotation_mode && this.annotation_edit_index===-1)
        return

      if(this.askContent.trim() !== ""){

        if(this.annotation_edit_index !== -1){
          //修改模式
          let history_res = {...this.ai_res[this.annotation_edit_index]}
          history_res.text = `${this.askContent}>>${this.annotation_edit_texts[1]}<<`
          
          if(this.askImage.img !== null){
            let img_name = `${this.pdf_fp}_${Date.now()}.png`
            //启动图片覆盖
            this.$axios.put('/reqImg', {
              imgname: history_res.img? history_res.img:img_name,
              base64:this.askImage.img,
              mode:'ADD'
            })
            history_res.img = history_res.img? history_res.img:img_name
            
          }
          this.handleAiChange('SET', this.annotation_edit_index, history_res)  //如果同时填写index和content，表示修改
          this.handleAskAreaBlur()
          this.refreshKey++

        }
        else{
          const timestamp = Date.now();  //确认标记
          let img_name = ""

          if(this.askImage.img !== null){
            img_name = `${this.pdf_fp}_${Date.now()}.png`
            //启动图片上传
            this.$axios.put('/reqImg', {
              imgname: img_name,
              base64:this.askImage.img,
              mode:'ADD'
            })
          }

          //确认注释储存内容
          this.handleAiChange('ADD', -1, {
            type:'LIST_TYPE_ANNO_'+timestamp,
            text:this.askContent + `>>${this.annotaiton_selected}<<`,
            dt:this.getFormattedDate(),
            hl:this.annotation_hldata,
            img:img_name,
          })
          
          this.annotation_flag = true  //确认注释，不再发送CANCEL消息
          chrome.runtime.sendMessage({  //发送确认消息
            type:'CONFIRM_ANNOATION', 
            vid:this.vid,
            flag:timestamp,
          })

        }
      }

      // 焦点失去
      this.askContent = ""
      this.askQuote.length = 0
      this.askFocus = false
      this.$refs.blurTextarea.focus()
      this.annotation_hldata = null
      this.resetImgInfo()

    },
    handleAskAreaBlur(clear=false){
      if(!this.can_blur)
        return

      //询问区域失去焦点
      this.annotation_mode = false
      this.annotation_edit_index = -1

      //判断是否确认注释
      if(!this.annotation_flag){
        chrome.runtime.sendMessage({
          type:'CANCEL_ANNOATION', 
          vid:this.vid,
        })
      }

      // 焦点失去
      if (clear){
        this.askContent = "" 
        this.askQuote.length = 0
        this.resetImgInfo()
      }

      this.askFocus = false
      this.$refs.blurTextarea.focus()

    },
    parseMessage(message) {
      const separatorIndex = message.indexOf(">>");
      
      if (separatorIndex === -1) {
        // 如果没有找到分隔符，返回原始消息和空字符串
        return [message, ""];
      }
      
      const firstPart = message.substring(0, separatorIndex);
      
      // 查找结束标记 << 的位置
      const endMarkerIndex = message.indexOf("<<", separatorIndex + 2);
      
      if (endMarkerIndex === -1) {
        // 如果没有找到结束标记，返回第一部分和剩余部分（不含开始标记）
        return [firstPart, message.substring(separatorIndex + 2)];
      }
      
      const secondPart = message.substring(separatorIndex + 2, endMarkerIndex);
      
      return [firstPart, secondPart];
    },
    handleHlClick(hl, htype, index){
      if(!this.can_render_click)
        return
      if(htype === 'LIST_TYPE_AI'){
        if(hl){
          chrome.runtime.sendMessage({
            type:'PDF_HIGHLIGHT', 
            vid:this.vid,
            hl:JSON.parse(JSON.stringify(hl)),
            hl_type:htype,
          })
        }
      }
      if(htype.includes('LIST_TYPE_ANNO')){
        if(this.annotation_edit_index!==index){
          this.annotation_edit_index = index
          //主动获得焦点，进入编辑模式
          this.askFocus = true
          this.$refs.askTextrea.focus()
          this.annotation_edit_texts = this.parseMessage(this.ai_res[index].text)
          this.askContent = this.annotation_edit_texts[0]
          if(this.ai_res[index].img!==''){
            this.readImageData('http://localhost:8225/static/'+this.ai_res[index].img)
          }

        }
        else{
          this.annotation_edit_index = -1
          this.handleAskAreaBlur()
        }


      }

    },
    handleANNOClick(hl, htype){
      chrome.runtime.sendMessage({
        type:'PDF_HIGHLIGHT', 
        vid:this.vid,
        hl:JSON.parse(JSON.stringify(hl)),
        hl_type:htype,
      })

    },
    handleAiChange(mode, index, content){
      if(mode==='ADD'){
        this.ai_res.push(content)
      }
      if(mode==='DEL'){
        this.can_render_click = false
        if(this.ai_res[index].type.includes("LIST_TYPE_ANNO")){
          let flag = this.ai_res[index].type.split('_').at(-1)
          chrome.runtime.sendMessage({
            type:'DEL_ANNOATION', 
            vid:this.vid,
            flag:flag,
          })
        }
        if(this.ai_res[index].img){
          //启动图片删除
          this.$axios.put('/reqImg', {
            imgname: this.ai_res[index].img,
            base64:"",
            mode:'DEL'
          })
        }
        this.ai_res.splice(index, 1)
        
      }
      if(mode === 'SET'){
        this.ai_res[index]=content

      }
      this.$axios.put('/reqSaveAI', {fp:this.pdf_fp, mode:mode, index:index, cont:content})
      
      let scrollToIndex;
      if (mode === 'ADD') {
        scrollToIndex = this.ai_res.length - 1;
      } else if (mode === 'DEL') {
        scrollToIndex = Math.max(index - 1, 0);
      } else if (mode === 'SET') {
        scrollToIndex = index;
      } else {
        scrollToIndex = this.ai_res.length - 1;
      }

      this.UpdateWindowUI().then(()=>{
        if (
          (mode === 'ADD' && content && !content.type.includes("LIST_TYPE_ANNO")) ||
          (mode === 'SET' && content && !content.type.includes("LIST_TYPE_ANNO")) ||
          (mode === 'DEL')
        ) {
          this.adjustScroll(scrollToIndex);  //跳转
        }

        setTimeout(() => {
          this.can_render_click = true
        }, 200);
      })

      
      
    },
    handelAiLoad(){
      this.$axios.post('/reqLoadAI', {fp:this.pdf_fp}).then(res=>{

          setTimeout(()=>{
            this.ai_res = res.data
            this.wait_text = 'WAIT'
            this.waiting = false
            
            //自动跳转
            if(this.ai_res){
              
              this.UpdateWindowUI().then(()=>{
                this.adjustScroll()
                this.loadRangeHighlight()
                this.current_index = this.ai_res.length-1
                this.$refs.blurTextarea.focus()
              })

            }

            //检出其中所有的ANNO，发送给pdfjs
            let anno_list = []
            this.ai_res.forEach(item=>{

              if(item.type.includes('LIST_TYPE_ANNO')){
                anno_list.push({
                  flag: item.type.split('_').at(-1),
                  hldata:item.hl,
                })                
                // console.log("VUE 已经读取flag= "+item.type.split('_').at(-1) +"的数据")
              }
            })
            chrome.runtime.sendMessage({
              type:'LOAD_ANNOATION', 
              vid:this.vid,
              notify_list:anno_list,
            })

          }, 1000)
      })

    },
    generateDateTimeString() {
      const now = new Date();

      // 获取年、月、日、小时、分钟、秒
      const year = now.getFullYear().toString().slice(-2); // 取后两位年份
      const month = String(now.getMonth() + 1).padStart(2, '0'); // 月份从0开始，补零
      const day = String(now.getDate()).padStart(2, '0'); // 补零
      const hours = String(now.getHours()).padStart(2, '0'); // 补零
      const minutes = String(now.getMinutes()).padStart(2, '0'); // 补零

      // 拼接字符串
      return `${year}${month}${day}-${hours}${minutes}`;
    },
    handleAnnoationImgDel(){
      if(this.annotation_edit_index !== -1 && this.ai_res[this.annotation_edit_index].img!==''){
        let history_res = this.ai_res[this.annotation_edit_index]
        //启动图片删除
        this.$axios.put('/reqImg', {
          imgname: history_res.img,
          base64:"",
          mode:'DEL'
        })
        history_res.img = ''
        this.handleAiChange('SET', this.annotation_edit_index, history_res)  //如果同时填写index和content，表示修改
      }
      //恢复blur操作
      this.can_blur = true
      this.handleAskAreaBlur()

    },
    resetImgInfo(){
      this.askImage.img = null
      this.askImage.size = 0
      
    },
    handlePaste(e) {
      e.preventDefault();
      
      // 1. 检查粘贴内容是否为图片
      const clipboardItems = e.clipboardData?.items || [];
      for (const item of clipboardItems) {
        if (item.type.startsWith('image/')) {
          this.handleAddImg();
          return;
        }
      }
      
      // 2. 获取粘贴文本
      const pastedText = e.clipboardData?.getData('text') || '';
      if (!pastedText) return;
      
      // 3. 获取当前光标位置
      const textarea = e.target;
      const startPos = textarea.selectionStart;
      const endPos = textarea.selectionEnd;
      
      // 4. 在光标位置插入文本
      const currentValue = textarea.value;
      textarea.value = 
        currentValue.substring(0, startPos) + 
        pastedText + 
        currentValue.substring(endPos);
      
      // 5. 更新Vue数据模型（如果用v-model）
      this.$emit('input', textarea.value); // 如果是自定义组件
      // 或者 this.textContent = textarea.value; // 如果是直接绑定的data
      
      // 6. 恢复光标位置（在粘贴文本之后）
      this.$nextTick(() => {
        textarea.selectionStart = textarea.selectionEnd = startPos + pastedText.length;
      });
    },
    async readImageData(url) {
      // 1. 获取图片为 ArrayBuffer
      const response = await fetch(url);
      const buffer = await response.arrayBuffer();

      // 2. 计算文件大小（字节）
      const fileSizeInBytes = buffer.byteLength;
      const fileSizeInKB = (fileSizeInBytes / 1024).toFixed(2);

      // 3. 转换为 Base64
      const base64 = btoa(
        new Uint8Array(buffer).reduce(
          (data, byte) => data + String.fromCharCode(byte),
          ''
        )
      );

      this.askImage.img = `data:${response.headers.get('content-type')};base64,${base64}`;
      this.askImage.size = fileSizeInKB;

    },
    async handleAddImg(){
      const clipboardItems = await navigator.clipboard.read();

      for (const clipboardItem of clipboardItems) {
        for (const type of clipboardItem.types) {
          if (type.startsWith('image/')) {
            const blob = await clipboardItem.getType(type);
            
            // 获取图片文件大小（字节）
            const fileSize = blob.size;
            const fileSizeKB = Math.round(fileSize / 1024 * 100) / 100; // 转换为KB
            
            // 创建临时URL来获取图片尺寸
            const img = new Image();
            img.onload = function() {
              // 转换为Base64
              const reader = new FileReader();
              reader.onload = function(e) {
                const base64data = e.target.result;
                // 这里的 this 现在指向外层 this
                this.askImage.img = base64data;
                this.askImage.size = fileSizeKB;
              }.bind(this); // 绑定外层 this 到 FileReader 的回调
              
              reader.readAsDataURL(blob);
            }.bind(this); // 绑定外层 this 到 Image 的 onload 回调
            
            img.src = URL.createObjectURL(blob);

            this.askQuote.length = 0
            return;
          }
        }
      }

    },
    getQuoteContent(){
      let res = ""
      let gid_set = new Set();
      this.askQuote.forEach(node=>{
        gid_set.add(node.gid)
      })
      gid_set.forEach(i=>{
        res += this.ai_res[i] + '\n\n'
      })
      return res
    },
    onTextChange(t, add, hl){
      let text = this.selectionProcess(t)
      text = this.AIinputProcess(text)
      if(text.length >=3500 || text.length <=50){
        const isConfirmed = confirm(`选中字数异常 ${text.length} words，确认吗？`);
        if (!isConfirmed) {
          return
        }

      }

      this.resetImgInfo()
      if(!this.showOrigin && !this.waiting && text != "" && text != this.chosen_text_history){
        this.chosen_hldata = hl
        if(add){
          this.chosen_text_history = this.chosen_text
          this.chosen_add_text.push(text)
          this.chosen_text = this.chosen_add_text.join('')

        }else{
          this.chosen_text_history = this.chosen_text
          this.chosen_text += text  //这一步是为了上面add
          this.addMemoryList(this.chosen_text)
          this.callAIResponse()
          this.chosen_text = ""
          this.chosen_add_text.length = 0
        }


      }
      this.shown_text = text

    },
    addMemoryList(text){
      const mem_len = 10  //记忆长度
      if(this.memorylist.length < mem_len){
        if(!this.memorylist.includes(text)){
          this.memorylist.push(text)
        }
      }else{
        let index = this.memorylist.indexOf(text)
        if(index === -1 || index === 0){
          this.memorylist.shift()
          this.memorylist.push(text)
        }
      }
    },
    handleQuote(gid, msg, method){
      let new_quote = {quote_gid:gid, quote_msg:msg}
      let index = this.askQuote.findIndex(item => item.quote_gid===new_quote.quote_gid && item.quote_msg===new_quote.quote_msg);

      if(method === 'set'){
        if (index !== -1) {
          // 如果存在则删除
          this.askQuote.length = 0
        } 
        else{
          this.askQuote.length = 0
          this.askQuote.push(new_quote);
        }
      }
      else if(method === 'add'){
        if (index !== -1) {
          // 如果存在则删除
          this.askQuote.splice(index, 1);
        } else {
          // 如果不存在则添加
          this.askQuote.push(new_quote);
        }
        
      }
      this.resetImgInfo()
      this.askFocus = false

    },
    checkAndRemoveTest(str) {
        if (str.includes("@Test")) {
            return {
                found: true,
                newString: str.replace("@Test", "")
            };
        } else {
            return {
                found: false,
                newString: str
            };
        }
    },
    handleAsk(){
      if(this.annotation_mode)
        return
      if(this.annotation_edit_index!==-1)
        return
      
      if(this.askContent.includes("@Clear")){
        const isConfirmed = confirm(`你确定要删除这 ${this.ai_res.length} 条记录吗？`);
        if (isConfirmed) {
          this.$axios.put('/clear_all', {
            fp: this.pdf_fp,
          })
          this.ai_res.length = 0
          this.hl_arr.length = 0
          this.UpdateWindowUI().then(() => {
            this.adjustScroll()
            this.loadRangeHighlight()
            this.current_index = this.ai_res.length - 1
            this.$refs.blurTextarea.focus()
          })

          chrome.runtime.sendMessage({  //发送确认消息
            type: 'CONFIRM_CLEARALL',
            vid: this.vid,
          })
        }
        
        // 焦点失去
        this.handleAskAreaBlur(true)

        return
      }

      let user_action = ""
      let user_prompt = '';
      let user_assisant = ''
      let model = this.gptModel
      let vision_model = false

      if(this.askImage.img !== null){
        //视觉提问
        user_prompt =  [
          { type: "text", text: '针对给定图片，结合原文'+ (this.askContent.trim()?('回答用户提问: '+this.askContent):'对图片进行解释')  },
          {
            type: "image_url",
            image_url: {
              url:this.askImage.img,
            }
          },
        ]
        model = this.gptModelVision
        vision_model = true
      }
      else{
        if(this.askQuote.length === 0){
          // user_action = `针对: ${ai_last_res}`
          user_action = '根据用户阅读过的文段'
        }
        else{
          user_action = `针对用户提到的点：\n`
          let t=1
          this.askQuote.forEach(node=>{
            user_action += `${t}.${node.quote_msg}\n`
          })

          user_assisant = "\n\n用户提到的解释: " + this.getQuoteContent()
        }
        //设定非视觉提示词
        user_prompt = `${user_action}, 解决询问【 ${this.askContent}】`
        
      }

      if(!vision_model && this.askContent===''){
        return
      }

      //启动流程
      this.waiting = true
      this.cancelTokenSource?this.cancelTokenSource.cancel('请求被用户取消'):null //强制停止请求
      this.cancelTokenSource = this.$axios.CancelToken.source();
      this.controller = new AbortController();

      this.$axios.post(this.apiUrl, {
        model: model,
        messages: [
          {
            role:"developer",
            content: "你是一名学术专家秘书，请解决用户询问, 这是一些语法规范:" + "\n\n"+RulesOfMarkdown()+"\n\n"+RulesOfLatex()+"\n\n",
          },
          {
            role:"assistant",
            content:"之前用户查看过的论文内容: " + this.memorylist.join("\n\n") + user_assisant
          },
          {
            role: "user",
            content: user_prompt,
          }
        ]
      }, 
      {
        headers: {"Authorization": `Bearer ${this.apiKey}`},
        cancelToken: this.cancelTokenSource.token, // 绑定CancelToken

      }).then(res=>{
        const aiResponse = res.data.choices?.[0]?.message?.content || 
                          res.data.choices?.[0]?.text || 
                          JSON.stringify(res.data);

        let final_text = this.AIoutputProcess(aiResponse)

        this.handleAiChange('ADD', -1, {
          type:'LIST_TYPE_ASK',
          text:final_text,
          dt:this.getFormattedDate(),
          hl:null,
        })

        this.waiting = false
        window.focus()

      })
      
      // 焦点失去
      this.handleAskAreaBlur(true)
      
    },
    callAIResponse() {
      //请求控制
      this.waiting = true
      this.cancelTokenSource?this.cancelTokenSource.cancel('请求被用户取消'):null //强制停止请求
      this.cancelTokenSource = this.$axios.CancelToken.source();
      this.controller = new AbortController();
      
      this.$axios.post(this.apiUrl, {
        model: this.gptModel,
        messages: [
          {
            role:"developer",
            content: "你是一名学术论文解释和翻译专家，直接输出总结内容，不要任何引导句(如'好的','以下是'), 请遵守这些语法规范: " + "\n\n" + RulesOfMarkdown() + "\n\n" + RulesOfLatex() + "\n\n",
          },
          {
            role:"assistant",
            content:"之前的论文内容: " + this.memorylist.join("\n\n")
          },
          {
            role: "user",
            content: `
请结合上下文和之前的论文内容，将学术内容【${this.chosen_text}】${this.addedPrompt === '' ? '用中文准确概括' : this.addedPrompt}，要求如下：
- 概括内容简短、简洁明了，突出重点，合理分段或者分点，无需额外说明，不要输出其它内容
- 文中出现对于图片(fig x/figure x/Fig x/Figure x/...)、表格(table x...)、算法(algorithm x....)的引用, 输出结果中请替换为“如图x所示、如表x所示、如算法x所示” (x表示具体引用数字)
- 仅在确有必要时进行分条列点，避免分条过细；
- 可以在较难或是较长的描述输出后, 利用markdown引用格式进行进一步的通俗理解或是解释
- 对于重要的专业术语，中文翻译后markdown加粗并附全称, 例如：中文(缩写, 英文全称), 但此后再出现相同的专业术语就不要再附加全称了, 避免过长影响阅读
- 对于公式, 请在公式后利用markdown引用格式解释公式含义或是文中提到的变量解释, 除此以外, 请不要在此块以外再重复进行公式解释了
- 如果是伪代码或是用户要求输出的代码，要用markdown代码块(\`\`\`)格式
- 直接输出总结内容，不要任何引导句(如"好的""以下是")
`
          }
        ]
      }, 
      {
        headers: {"Authorization": `Bearer ${this.apiKey}`},
        cancelToken: this.cancelTokenSource.token, // 绑定CancelToken

      }).then(res=>{
        const aiResponse = res.data.choices?.[0]?.message?.content || 
                          res.data.choices?.[0]?.text || 
                          JSON.stringify(res.data);
        
        let final_text = this.AIoutputProcess(aiResponse)
        console.log(final_text)

        this.handleAiChange('ADD', -1, {
          type:'LIST_TYPE_AI',
          text:final_text,
          dt:this.getFormattedDate(),
          hl:this.chosen_hldata,
        })

        this.waiting = false
        this.cancelTokenSource = null; // 重置

        window.focus()

      })

      // 焦点失去
      this.handleAskAreaBlur(true)

    },
    getFormattedDate() {
      const now = new Date();
      
      const year = now.getFullYear(); // 2025
      const month = now.getMonth() + 1; // 月份从0开始，所以要加1
      const day = now.getDate(); // 30
      const hours = now.getHours(); // 14
      const minutes = now.getMinutes(); // 52
      
      return `${year}/${month}/${day} ${hours}:${minutes.toString().padStart(2, '0')}`;
    },
    adjustScroll(index=this.ai_res.length -1) {
      const container = this.$refs.render_container;
      const targetElement = container.children[index];
      
      if (targetElement) {
        this.current_index = index
        const targetRect = targetElement.getBoundingClientRect();
        const offsetTop = targetRect.top - this.containerRect.top;
        this.can_current_index_change = false
        this.smoothScrollBy(container, offsetTop, 150)
        setTimeout(() => {
          this.can_current_index_change=true
        }, 200);
      }
      
    },
    smoothScrollBy(container, offsetTop, duration = 500) {
      const start = container.scrollTop;
      const startTime = performance.now();
      const easeOutQuad = (t) => t * (2 - t);

      function scrollStep(timestamp) {
        const elapsed = timestamp - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const currentOffset = start + offsetTop *easeOutQuad(progress) ;
        container.scrollTop = currentOffset;

        if (progress < 1) {
          requestAnimationFrame(scrollStep);
        }
      }

      requestAnimationFrame(scrollStep);
    },
    highlightScroll(index) {
      const container = this.$refs.render_container;
      // 确保索引有效
      if (index < 0 || index >= container.children.length) {
        console.error('Invalid index:', index);
        return;
      }
      const targetElement = container.children[index];
      if (targetElement) {
        targetElement.style.scale = '1.01'
        setTimeout(() => {
          targetElement.style.scale = ''
        }, 200);
      }
    },
    selectionProcess(text){
      // 第一步：处理英文换行连字符（"-"后跟换行符的情况）
      let processedText = text.replace(/-\r?\n|\r/g, '');
      // 第二步：将所有换行符替换为空格
      processedText = processedText.replace(/\r?\n|\r/g, ' ');
      // 第三步：将双斜杠 // 替换为空格
      processedText = processedText.replace(/\/\//g, ' ');
      // 第四步：删除文献标识符，如[1]、[2,3]、[4-6]等
      processedText = processedText.replace(/\[\d+(?:,\s?\d+|-\d+)*\]/g, '');
      // 可选：将多个连续空格替换为单个空格
      processedText = processedText.replace(/\s+/g, ' ').trim();
      return processedText;
    },
    AIinputProcess(text) {
      return text
        // 替换A*和A\*为A-star
        .replace(/A\*/g, 'A-star')
        .replace(/A\\\*/g, 'A-star')

    },
    AIoutputProcess(text) {
      return text
        // // 处理加粗格式，确保前后有空格
        .replace(/\*\*([^*]+)\*\*/g, function (match, p1) {
          return ' **' + p1.trim() + '** ';
        })
        // // 处理缩进，将4个空格替换为2个空格
        // .replace(/^ {4}/gm, '  ');
    },


  },


}

</script>
<style scoped>
.search-input{
  width: 100%;
  height: 100%;
  padding-left: 20px;
  padding-right: 75px;
  font-size: 15px;
  outline: none;
  box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.25);
  border-radius: 25px;
  border: 1px solid lightgray;
  transition: all 0.2s ease;
}
.search-input:hover{
  border: 1px solid transparent;
}
.search-btn{
  right: 15px;
  
  font-size: 18px; 
  font-family:'Gill Sans', 'Gill Sans MT', Calibri, 'Trebuchet MS', sans-serif; 
  color: #4870AC; 
  border: none; 
  background-color: transparent;
  cursor: pointer;
  position: absolute;

  transition: all 0.2s ease;
}
.search-btn:hover{
  color: #554acc;

}
.wait-outer-continer{
  display: flex; 
  flex-flow: column; 
  align-items: center; 
  justify-content: center; 
  background-color: transparent;
  cursor: pointer;

  position: absolute;
  width: 100%;
  height: 100%;
  
  background: rgba(255, 255, 255, 0.0.25);
  backdrop-filter: blur(8px);

  transition: all 0.2s ease;
}

.content{
  display: flex; 
  flex-flow: row;  
  height: 100vh;
  width: 100%;
  overflow: hidden;
  background-color: white;

}
.iframebox {
  flex: 1;
}

.div-index-block{
  display: block; 
  width: 100%;
  border-bottom: 1px solid white;
  cursor: pointer;
  transition: all 0.2s ease;

}
.div-index-block-active{
  display: block; 
  width: 100%;
  border-bottom: 1px solid white;
  cursor: pointer;
  transition: all 0.2s ease;
  scale: 1.05;
  box-shadow: 2px 2px 2px rgba(0, 0, 0, 0.5);
  border-color: transparent;

}
.div-index-block:hover{
  scale: 1.05;
  box-shadow: 2px 2px 2px rgba(0, 0, 0, 0.5);
  border-color: transparent;
}

.gpt-render{
  display: flex; 
  flex-flow: column; 
  overflow-y:scroll; 
  overflow-x: hidden; 
  height: 100%;
  flex: 1;  /*撑满右侧空间*/

  /* WebKit浏览器滚动条样式 */
  &::-webkit-scrollbar {
    height: 4px !important; /* 水平滚动条高度 */
    width: 4px !important;  /* 垂直滚动条宽度（虽然这里用不到） */
  }
  &::-webkit-scrollbar-thumb {
    background: #8a8a8a7b; 
    border-radius: 2px;
  }
  &::-webkit-scrollbar-track {
    background: #f1f1f1;
  }
}
.sliderbox{
  display: flex;
  flex-flow: column;
  overflow: hidden;
  width: 100%;
  align-items: center;
  position: relative;
}

.btn-show-ori{
  font-size: 12px;
  background-color: transparent;
  cursor: pointer;
  /* 不要被选中文字 */
  caret-color: transparent;
  user-select: none;
  transition: all 0.2s ease;
}
.btn-show-ori:hover{
  color: #4e7bbf;
  text-shadow: 0.5px 0.5px 1px rgba(0, 0, 0, 0.25);
}

.btn-adding{
  font-size: 12px;
  text-align: center;
  color: #4870AC;
  border: 1px solid #4870AC;
  font-weight: bold;
  cursor: pointer;
  /* 不要被选中文字 */
  caret-color: transparent;
  user-select: none;
  padding-inline: 10px;
  border-radius: 15px;
  overflow: hidden; /* 隐藏溢出内容 */
  white-space: nowrap; /* 防止文字换行 */
  min-width: 0;

  transition: all 0.2s ease;

}
.btn-adding:hover{
  border: 1px solid transparent;
  background-color: lightgray;
  color: rgb(71, 71, 71);

}

.btn-show-img{
  font-size: 12px;
  background-color: transparent;
  cursor: pointer;
  /* 不要被选中文字 */
  caret-color: transparent;
  user-select: none;
  transition: all 0.2s ease;
}
.btn-show-img:hover{
  color: #6812b0;
  text-shadow: 0.5px 0.5px 1px rgba(0, 0, 0, 0.25);
}


.textarea-ori{
  font-size: 13px;
  padding: 5px;
  margin-bottom: 5px;
  border: 2px dashed #4870acb2;
  width: 100%;
  height: 100%;
  box-sizing: border-box;
  font-family:'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  resize: none;
  transition: all 0.2s ease;
}
.textarea-ask{
  width: 100%; 
  margin: 2px; 
  resize: none;
  outline: none;
  border: 1.5px solid #4870AC;
  border-radius: 5px;
  transition: all 0.2s ease;

  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  padding-left: 5px;
  padding-right: 5px;
}
.textarea-ask:hover{
  background-color: #eff6ff;
}
.lb-quote-num{
  position: absolute;
  left: 4px;
  top: -22px;
  color: #4870AC;
  font-weight: bold;
  border-left: #4870AC solid 5px;
  
  padding-inline: 5px;
  padding-block: 1px;
  font-size: 10px;
  text-align: center;

  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(1px);

  cursor: pointer;
  transition: all 0.2s ease;
  
}
.lb-quote-num:hover{
  color: grey !important;
  border-color: grey !important;
}
</style>
