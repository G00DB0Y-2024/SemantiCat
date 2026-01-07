<template>
<div class="main-container">
    <div class="img-container" @click="handleImgClick">
        <img :src="loadImg" style="height: 100%; width: 100%; object-fit: contain;"/>
    </div>
    <input 
    v-model="img_desc" 
    style="
        border: none;
        text-align: center; 
        margin-top:2px; 
        font-size:13px; 
        color: rgba(0, 0, 0, 0.75); 
        outline: none;
        width: 100%;
    " 
    :placeholder="`Fig. ${img_name.split('.')[0].split('_')[1]}`"
    @change="handleNameChange"
    >

    
</div>


</template>

<script>

export default{
    props:['img_name'],
    data(){
        return{
            img_desc:'',
        }


    },
    mounted(){
        this.$axios.post("/reqImgInfoGet", {imgname:this.img_name, base64:"", mode:""}).then(res=>{
            if(res.data){
                this.img_desc = res.data
            }
        })

    },
    methods:{
        handleImgClick(){
            window.open('http://localhost:8225/static/'+this.img_name, "_blank");

        },
        handleNameChange(){
            this.$axios.post("/reqImgInfoSet", {imgname:this.img_name, base64:this.img_desc, mode:""})
        }


    },
    computed:{

        loadImg(){
            return 'http://localhost:8225/static/'+this.img_name+`?t=${Date.now()}`
        },

    }

}

</script>

<style scoped>
.img-container{
    border: 1px solid grey;
    border-radius: 5px;
    padding: 5px;
    display: block;
    width: 100%;
    height: 100%;
    cursor: pointer;

    transition: all 0.3s ease;
}
.img-container:hover{
    box-shadow: 2px 2px 2px rgba(0, 0, 0, 0.2);
}

.main-container{
    display:flex;
    flex-flow: column;
    align-items: center;
    justify-content: center;
    height:  150px;

    padding-inline: 15px;
    margin-bottom: 15px;

}

</style>