<template>
  <div style="display: flex; flex-flow: column; transition: all 0.2s ease" :style="{opacity:editting?0.5:1}">
    
    <!-- div :class="hldata?'div-header-hl':'div-header-norm'" -->
    <div :class="(headtype==='LIST_TYPE_AI'||headtype.includes('LIST_TYPE_ANNO'))?'div-header-hl':'div-header-norm'" :style="{borderLeft:`4px solid ${MapHeadBarColor}`, backgroundColor:MapHeadBarBackgroundColor}" @click="$emit('onHlClick')"  @mousedown="handleHeaderMidClick">
      <label ref="lb_head" :style="{'color':MapHeadBarColor}" style=" font-size: 12px; font-family: 'Franklin Gothic Medium', 'Arial Narrow', Arial, sans-serif;">{{ datetime }} {{ editting?'(Editing)':'' }}</label>
      <label class="lb-close" :style="{color:MapCloseColor}" @click="$emit('onClose')" style="margin-block:-5px">×</label>
    </div>

    <p v-if="headtype.includes('LIST_TYPE_ANNO')" class="selected-container" @click="$emit('onANNOClick')"><span style="color: rgba(0,0,0,0.75); font-size: 25; font-weight:bold">“ </span>{{ parseMessage(content)[1] }}</p>
    <p class="markdown-container" v-highlight ref="container" @mousedown="handleMiddleClick" @dblclick="handleDoubleClick($event)" @copy="handleCopy($event)" v-html="renderedContent"></p>
    <image-render style="margin-top: 15px;" v-if="img_name" :img_name="img_name"/>

  
  </div>
  
</template>

<script>
import MarkdownIt from 'markdown-it'
import markdownItKatexGpt from 'markdown-it-katex-gpt'
import '../assets/github.css'
import imageRender from './imageRender.vue'


export default {
  props: ['content', 'datetime', 'hldata', 'gid', 'headtype', 'vid', 'img_name', 'editting'],
  emits: ['onQuote', 'onClose', 'onHlClick', 'onANNOClick'],
  components:{
    imageRender,

  },
  data() {
    return {
      md: new MarkdownIt().use(markdownItKatexGpt, {
        delimiters: [
          { left: '\\[', right: '\\]', display: true },
          { left: '\\(', right: '\\)', display: false },
          { left: '$$', right: '$$', display: true },
          { left: '$', right: '$', display: false }
        ]
      })
    }
  },
  beforeMount(){
    window.addEventListener('resize', this.checkMathOverflow);
    this.checkMathOverflow()
  },
  mounted(){
    this.$nextTick(() => {
      this.updateMathSpan()
      this.checkMathOverflow();
      this.styleFigureText(); // 图xx 文本样式处理
      this.boldFirstStrongInContainer(); // 加粗每个段落的第一个strong元素
    });

    // 监听滚轮事件，横向滚动math元素
    document.addEventListener('wheel', function(event) {
        const katexBlock = event.target.closest('p.katex');
        if (!katexBlock) return;

        const mathElement = katexBlock.querySelector('math');
        if (!mathElement) return;

        event.preventDefault();
        mathElement.scrollLeft += event.deltaY * 0.01;

    }, { passive: false }); // 必须设置 passive: false 才能 preventDefault
    
    // 初始化状态变量
    this.highlightActive = false;
    this.changeAllowed = true;

    chrome.runtime.onMessage.addListener((message, sender, senderResponse) => {
      if (message.vid === '' || message.vid === this.vid) {
        if (message.type === 'ACTIVE_CLICK_ANNO' && this.headtype.includes('LIST_TYPE_ANNO')) {
          let self_flag = this.headtype.split('_').at(-1);
          
          // 使用明确的状态检查替代简单的布尔标志
          if (self_flag === message.flag && this.changeAllowed) {
            // 防止重复触发
            this.changeAllowed = false;
            this.highlightActive = true;
            
            // 应用高亮样式
            this.applyHighlightStyles();
            
            // 使用单一计时器确保样式恢复的完整性
            setTimeout(() => {
              this.resetHighlightStyles();
              this.highlightActive = false;
              
              // 增加额外延迟以确保用户可以感知到变化
              setTimeout(() => {
                this.changeAllowed = true;
              }, 150);
            }, 250);
          }
        }
      }
    });
  },
  methods: {
    boldFirstStrongInContainer() {
      // 使用ref直接获取容器元素
      const container = this.$refs.container;
      
      // 如果容器不存在，直接返回
      if (!container) return;
      
      // 创建一个临时div来安全地操作HTML内容
      const tempDiv = document.createElement('div');
      tempDiv.innerHTML = container.innerHTML;
      
      // 查找所有直接子段落
      const paragraphs = tempDiv.querySelectorAll('p');
      
      // 遍历每个段落
      paragraphs.forEach(p => {
        // 获取第一个子节点（包括文本节点）
        let firstNode = p.firstChild;
        
        // 检查第一个节点是否存在且是element节点，并且是strong标签
        if (firstNode && firstNode.nodeType === Node.ELEMENT_NODE && 
            firstNode.tagName.toLowerCase() === 'strong') {
          // 应用加粗样式
          // firstNode.style.fontWeight = 'bold';
          firstNode.textContent = `${firstNode.textContent.trim()}` // 去除多余空格
        }
      });
      
      // 更新容器内容
      container.innerHTML = tempDiv.innerHTML;
    },
    // 将样式操作封装为方法，提高代码可维护性
    applyHighlightStyles() {
      const container = this.$refs.container;
      container.style.borderColor = '#AC4848';
      container.style.scale = 1.005;
      container.style.marginTop = '2px';
    },

    resetHighlightStyles() {
      const container = this.$refs.container;
      container.style.borderColor = 'transparent';
      container.style.scale = '';
      container.style.marginTop = '';
    },
    normalizeLabels(text) {
      // 替换 fig/FIG/Figure/FIGURE 等为 "图 x"
      text = text.replace(/(?:fig|FIG|Figure|FIGURE)\s+(\d+)/gi, "图 $1");
      
      // 替换 table/Table/TABLE 等为 "表 x"
      text = text.replace(/(?:table|Table|TABLE)\s+(\d+)/gi, "表 $1");
      
      // 替换 algorithm/Algorithm/ALGORITHM 等为 "算法 x"
      text = text.replace(/(?:algorithm|Algorithm|ALGORITHM)\s+(\d+)/gi, "算法 $1");
      
      return text;
    },
    styleFigureText() {
      const container = this.$refs.container;
      if (!container) return;

      // 获取容器中的 HTML 内容
      let content = container.innerHTML;

      content = this.normalizeLabels(content); //预先替换

      // 使用正则表达式匹配 "图 x"、"算法 x" 和 "表 x"
      const regex = /图\s*(\d+)|算法\s*(\d+)|表\s*(\d+)|\[文献[^\]]*\]/g;

      // 替换为指定的 HTML 代码
      content = content.replace(regex, (match) => {
        if (match.startsWith('[文献')) {
          return `<span class="styled-reference" style="color: white; background-color: rgb(72, 112, 172); padding-inline: 3px; margin-inline: 2px; border-radius: 2px;">${match}</span>`;
        } else {
          return `<span class="styled-figure" style="color: white; background-color: rgb(72, 112, 172); padding-inline: 3px; margin-inline: 2px; border-radius: 2px;">${match.trim().replace(/(\S)\s*(\d+)/, '\$1 \$2')}</span>`;
        }
      });

      // 更新容器的内容
      container.innerHTML = content;
    },
    processDivText(fragment){
        // 创建临时容器
        const tempDiv = document.createElement('div');
        tempDiv.appendChild(fragment.cloneNode(true));
        
        // 处理所有katex元素
        const processedKatex = tempDiv.querySelectorAll('.katex');
        processedKatex.forEach(katex => {
            const annotation = katex.querySelector('annotation');
            if (annotation) {
                // 使用特殊标记代替换行符，稍后再恢复
                let katex_flag_l = katex.tagName==='P'?'[NEWLINE]$$[NEWLINE]':' $'
                let katex_flag_r = katex.tagName==='P'?'[NEWLINE]$$[NEWLINE]':'$ '
                katex.textContent = katex_flag_l + annotation.textContent + katex_flag_r;
            }
        });

        // 处理strong, code, em
        let mdIdentify = {
            'strong':'**',
            'em':'*',
            'code':'`'
        }
        for (const [key, value] of Object.entries(mdIdentify)) {
            const processed = tempDiv.querySelectorAll(key);
            processed.forEach(el => {
                if (key === 'code' && el.parentNode.tagName === 'PRE') {
                    return; // 跳过代码块
                }
                let text = document.createTextNode(` ${value}${el.textContent}${value} `)
                el.parentNode.replaceChild(text, el)
            });
        }

        // 处理选区中的一级元素
        const processTopLevelElements = (container) => {
            // 先处理独立的<li>元素
            Array.from(container.children).forEach(child => {
                if (child.tagName === 'LI') {
                    const listParent = child.parentNode;
                    const isOrdered = listParent.tagName === 'OL';
                    const index = isOrdered ? 
                        Array.from(listParent.children).indexOf(child) + 1 : null;
                    const prefix = isOrdered ? `${index}. ` : '- ';
                    
                    const textNode = document.createTextNode(`[NEWLINE]${prefix}${child.textContent.trim()}`);
                    container.replaceChild(textNode, child);
                }
            });
        }
        processTopLevelElements(tempDiv)

        // 处理ul和ol列表（递归处理嵌套）
        const processLists = (element, indentLevel = 0) => {
            const lists = element.querySelectorAll('ul, ol');
            
            lists.forEach(list => {
                const isOrdered = list.tagName === 'OL';
                const items = list.querySelectorAll('li');
                const listContainer = document.createElement('p');
                
                items.forEach((item, index) => {
                    
                    // 添加缩进空格
                    const indent = ' '.repeat(indentLevel * 2);
                    
                    // 处理列表标记
                    const prefix = isOrdered ? `[NEWLINE]${indent}${index + 1}. ` : `[NEWLINE]${indent}- `;
                    
                    // 处理子节点（可能包含嵌套列表）
                    const itemContent = document.createElement('span');
                    itemContent.innerHTML = item.innerHTML;
                    
                    // 递归处理嵌套列表
                    processLists(itemContent, indentLevel + 1);
                    
                    const itemPara = document.createTextNode(prefix + itemContent.textContent.trim())
                    listContainer.appendChild(itemPara);
                });
                
                // 替换原列表
                list.parentNode.replaceChild(listContainer, list);
            });
        };
        
        // 处理临时容器中的列表
        processLists(tempDiv);

        // 处理<p>标签：除了第一个p标签，其他p标签开头添加[NEWLINE]
        const paragraphs = tempDiv.querySelectorAll('p');
        if (paragraphs.length > 1) {
            paragraphs.forEach((p, index) => {
                if (index > 0) { // 跳过第一个p标签
                    const firstChild = p.firstChild;
                    if (firstChild && firstChild.nodeType === Node.TEXT_NODE) {
                        firstChild.textContent = '[NEWLINE]' + firstChild.textContent;
                    } else {
                        const textNode = document.createTextNode('[NEWLINE]');
                        p.insertBefore(textNode, p.firstChild);
                    }
                }
            });
        }
        
        // 获取处理后的文本内容
        let textToCopy = tempDiv.textContent;
        // 清理文本
        textToCopy = textToCopy
            .replace(/\s+/g, ' ')      // 合并多个空格
            .replace(/\$ /g, '$ ')      // 清理公式后的空格
            .replace(/ \$/g, ' $')      // 清理公式前的空格
            .replace(/\[NEWLINE\]/g, '\n')  // 恢复换行符
            .trim();
        
        return textToCopy

    },
    handleCopy(e) {
        // 获取选中的范围
        const selection = window.getSelection();
        if (!selection.rangeCount) return;
        
        // 创建一个文档片段用于处理
        const range = selection.getRangeAt(0);
        const fragment = range.cloneContents();
        
        // 检查是否有katex元素需要处理
        const katexElements = fragment.querySelectorAll('.katex');
        if (katexElements.length === 0) return;
        
        // 阻止默认复制行为
        e.preventDefault();
        let textToCopy = this.processDivText(fragment)

        this.copyToClipboard(textToCopy);
    },
    handleDoubleClick(event) {
      // 获取双击的元素
      const fragment = event.target;
      
      // 构建要复制的文本内容
      let textToCopy = this.processDivText(fragment)
      // 复制到剪贴板
      this.copyToClipboard(textToCopy);
    },
    updateMathSpan(){
      // 获取所有class为katex的span元素
      const katexSpans = document.querySelectorAll('span.katex');
      
      // 遍历每个span.katex元素
      katexSpans.forEach(span => {
        // 检查是否包含math子元素且该子元素有display="block"属性
        const mathElement = span.querySelector('math[display="block"]');
        
        if (mathElement) {
          // 创建新的p元素
          const pElement = document.createElement('p');
          
          // 将span的所有属性和子元素转移到p元素
          pElement.className = span.className;
          pElement.innerHTML = span.innerHTML;
          
          // 用p元素替换span元素
          span.parentNode.replaceChild(pElement, span);

        }

      });
      
    },
    checkMathOverflow() {
      //计算元素是否溢出，修改justify-content
      document.querySelectorAll('.markdown-container math[display="block"]').forEach(mathElement => {
        // 检测是否溢出
        const isOverflowing = mathElement.scrollWidth > mathElement.clientWidth;
        // 动态设置 justify-content
        mathElement.style.setProperty(
          '--justify-content', 
          isOverflowing ? 'flex-start' : 'center'
        );
        
      });
    },
    async handleHeaderMidClick(event){
      if (event.button === 1) {  // 1 表示鼠标中键
        event.preventDefault();  //这个会阻止左键选择事件，因此只放在这里
        // 检查点击的是p或ul元素
        this.$emit("onQuote", this.gid, this.content, 'add')
        event.stopPropagation();
      }
    },
    async handleMiddleClick(event) {
      
      window.focus()
      const katexElement = event.target.closest('.katex');
      if(event.button === 0){ //左键
        //监测数学公式
        // console.log("tagname: "+event.target.tagName)
        if (katexElement) {
          // 获取annotation内容
          const annotation = katexElement.querySelector('annotation');
          if (annotation) {
            // console.log("latex annotation: "+annotation.textContent)
            await navigator.clipboard.writeText(annotation.textContent);
          } 
        } 
        else if(event.target.tagName === 'CODE'){
            // console.log("code: "+event.target.textContent)
            await navigator.clipboard.writeText(event.target.textContent);
        }

      }
      else if (event.button === 1) {  // 1 表示鼠标中键
        event.preventDefault();  //这个会阻止左键选择事件，因此只放在这里
        // 检查点击的是p或ul元素
        if (event.target.tagName === 'P' || event.target.tagName === 'LI' || katexElement || event.target.tagName === 'PRE' || event.target.tagName === 'CODE') {
          this.$emit("onQuote", this.gid, event.target.textContent, 'add')
          
        }
        event.stopPropagation();
      }
      
    },
    // 辅助方法：复制到剪贴板
    copyToClipboard(text) {
      if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
          console.log('内容已复制:', text);
          this.$message.success('内容已复制');
        }).catch(err => {
          console.error('复制失败:', err);
        });
      }
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

  },
  computed:{
    renderedContent() {
      return this.md.render(this.parseMessage(this.content)[0])
    },
    MapHeadBarColor(){
      if(this.headtype.includes('LIST_TYPE_ASK')){
        return '#559145'
      }
      if(this.headtype.includes('LIST_TYPE_AI')){
        return '#4870AC'
      }
      if(this.headtype.includes('LIST_TYPE_ANNO')){
        return '#AC4848'
      }
    },
    MapHeadBarBackgroundColor(){
      if(this.headtype.includes('LIST_TYPE_ASK')){
        return 'rgba(203, 226, 201, 0.5)'
      }
      if(this.headtype.includes('LIST_TYPE_AI')){
        return 'rgba( 72,112,172, 0.15)'
      }
      if(this.headtype.includes('LIST_TYPE_ANNO')){
        return 'rgba(172, 72, 72, 0.15)'
      }
    },
    MapCloseColor(){
      if(this.headtype.includes('LIST_TYPE_ASK')){
        return 'rgba(86, 145, 69, 0.741)'
      }
      if(this.headtype.includes('LIST_TYPE_AI')){
        return 'rgb(122, 155, 205)'
      }
      if(this.headtype.includes('LIST_TYPE_ANNO')){
        return '#AC4848'
      }
    },
    

  }

}
</script>

<style scoped>
.lb-close{
  margin-left: auto; 
  margin-right:5px;  
  font-size: 16px; 
  font-family: 'Franklin Gothic Medium', 'Arial Narrow', Arial, sans-serif;
  cursor: pointer;
  
  transition: all 0.2s ease;
}
.lb-close:hover{
  filter: brightness(0.75);
  scale: 1.02;
}

.selected-container {
  line-height: 1.6em;
  font-size: 12.5px;
  margin-inline:10px; 
  margin-top:10px; 
  margin-bottom:2px; 
  padding:3px; 
  padding-inline:6px;

  display: flex;
  font-family: 'Times New Roman', Times, serif;
  background-color: rgba(0, 0, 0, 0.1);
  color: rgba(0, 0, 0, 0.75);
  border-radius: 5px;
  cursor: pointer;
  
  /* 最多显示两行 */
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;

  transition: all 0.2s ease;
}

.selected-container:hover{
  box-shadow: 2px 2px 2px rgba(0, 0, 0, 0.2);
  color: black;
}

.markdown-container {
  line-height: 1.6em;
  font-size: 12.5px;
  display: flex;
  flex-flow: column;
  margin-top: 0;
  font-family:'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;
  border: 2px dashed transparent;
  border-radius: 5px;
  
  transition: all 0.25s ease;
}

/* 内联公式 */
.markdown-container :deep(.katex) {
  margin: 0.3em 0;
  padding: 0.2em;
  cursor: pointer;
  overflow: auto;
  transition: all 0.3s ease;
}


/*行间公式*/
.markdown-container :deep(math[display="block"]) {
  display: flex;
  justify-content:  var(--justify-content, center);;
  align-items: center;
  
  overflow-x: auto;
  overflow-y: hidden;
  padding-inline: 10px ;
  cursor:auto !important;
  transition: all 0.3s ease;

  /* 隐藏滚动条（但仍可滚动） */
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE/Edge */
  
  /* WebKit浏览器滚动条样式（设为透明） */
  &::-webkit-scrollbar {
    display: none; /* Chrome/Safari */
  }
}


/* 公式鼠标悬浮效果 */
.markdown-container :deep(semantics) {
  padding-inline: 2px;
  cursor: pointer;
  transition: all 0.2s ease; /* 平滑过渡 */
}
.markdown-container :deep(semantics:hover) {
  text-shadow: 1px 1px 1.5px rgba(0, 89, 255, 0.534);
  /* text-shadow: 1px 1px 1.5px rgba(255, 136, 0, 0.8); */
}

.markdown-container :deep(katex)
.markdown-container :deep(ul li),
.markdown-container :deep(ol li),
.markdown-container :deep(p) {
  /* cursor: pointer; */
  transition: all 0.3s ease;
}

.markdown-container :deep(katex:hover),
.markdown-container :deep(ul li:hover),
.markdown-container :deep(ol li:hover),
.markdown-container :deep(p:hover) {
  background-color: rgb(232, 242, 255);
}

.markdown-container :deep(p) {
  /* cursor: pointer; */
  /* 允许长单词在边界处折断并换到下一行 */
  word-wrap: break-word;
  /* 现代浏览器兼容性更好的写法，功能相同 */
  overflow-wrap: break-word;
  transition: all 0.3s ease;
}

.div-header-norm{
  display: flex;  
  margin: 5px; 
  margin-bottom: -2px; 
  padding-left: 5px; 
  align-items: center; 
}

.div-header-hl{
  display: flex;  
  margin: 5px; 
  margin-bottom: -2px; 
  padding-left: 5px; 
  align-items: center; 

  cursor: pointer;
  transition: all 0.2s ease;
  
}
.div-header-hl:hover{
  scale: 1.005;
  box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.3);

}

</style>