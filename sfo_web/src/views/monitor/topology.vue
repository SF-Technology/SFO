/**
* Create by wenboling on 2018/5/2
*/

<template>
  <div>
    <el-row v-if="this.role.length !==0 && this.role.indexOf('superadmin') > -1" class="btnRow">
      <el-button type="primary" size="medium" @click="UploadDialogVisible = true">上传拓扑图</el-button>
    </el-row>
    <!--<img src="../../assets/images/swift.png" ondragstart="return false;"/>-->
    <el-row style="text-align: center; max-width: 95%; max-height: 95%; margin: 10px auto">
      <img :src="img_src" style="max-width: 100%; max-height: 100%" ondragstart="return false;" :onerror="errorImg"/>
    </el-row>
    <el-dialog title="上传拓扑图"
               :visible.sync="UploadDialogVisible"
               :before-close="beforeClose"
               width="60%">
      <input type="file" id="upload" name="file" @change="uploadChange"  accept="image/png,image/jpg,image/jpeg" />
      <el-button type="success" size="small" @click="uploadImg" :disabled="!selectedFile">上传</el-button>
      <div style="margin: 10px">
        <p>拓扑图预览:</p>
        <div style="text-align: center;margin: 10px">
          <img :src="imgDataUrl" >
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
  import { mapGetters } from 'vuex'
  import { getRole } from '@/utils/cookie-util'
  import { uploadTopologyImage, topologyImageAPI } from '@/api/monitor'

  export default {
    computed: {
      ...mapGetters([
        'selectedCluster'
      ]),
      errorImg(){
        return 'this.src="' + require('../../assets/images/errimg.png') + '"'
      }
    },
    data() {
      return {
        role: '',
        img_src: '',
        UploadDialogVisible: false,
        selectedFile: '',
        imgDataUrl: '',
      }
    },
    methods: {
      getImgSrc(){
        this.img_src = `${topologyImageAPI(this.selectedCluster)}?${Math.random()}`
      },
      getLoginUserRole(){
        this.role = JSON.parse(getRole())
      },
      getBase64(file,callback){
        let maxWidth = 640;
        if(file.files && file.files[0]){
          let thisFile = file.files[0];
          if(thisFile.size>2019200){
            // mualert.alertBox("图片不能超过800K");
            this.$message({
              message: '图片不能超过2M',
              type: 'error'
            });
            return
          };
          let reader = new FileReader();
          reader.onload = function(event){
            let imgUrl = event.target.result;
            let img = new Image();
            img.onload = function(){
              let canvasId = 'canvasBase64Imgid',
                canvas = document.getElementById(canvasId);
              if(canvas!=null){
                document.body.removeChild(canvas);
              }
              canvas = document.createElement("canvas");
              canvas.innerHTML = 'New Canvas';
              canvas.setAttribute("id", canvasId);
              canvas.style.display='none';
              document.body.appendChild(canvas);
              canvas.width = this.width;
              canvas.height = this.height;
              let imageWidth = this.width,
                imageHeight = this.height;
              if (this.width > maxWidth){
                imageWidth = maxWidth;
                imageHeight = this.height * maxWidth/this.width;
                canvas.width = imageWidth;
                canvas.height = imageHeight;
              }
              let context = canvas.getContext('2d');
              context.clearRect(0, 0, imageWidth, imageHeight);
              context.drawImage(this, 0, 0, imageWidth, imageHeight);
              let base64 = canvas.toDataURL('image/png',1);
              let imgbase = base64.substr(22);
              callback(imgbase)
              //this.imgUrl =
            }
            img.src = imgUrl;
          }
          reader.readAsDataURL(file.files[0]);
        }
      },
      uploadChange(event){
        if(event.target.files.length>0){
          this.selectedFile = event.target.files[0];  //提交的图片
          this.getBase64(event.target,(url)=>{
            this.imgDataUrl = 'data:image/png;base64,'+url;   //显示的图片
          });
        }
      },
      uploadImg(){
        let data = new FormData()
        if(this.selectedFile){
          data.append('file', this.selectedFile, this.selectedFile.name)
        }
        uploadTopologyImage(this.selectedCluster, data).then(res=>{
          if(res.status === 200 && res.data.status === 200){
            this.$message({
              message: "上传成功",
              type: "success"
            })
            this.UploadDialogVisible = false
            this.imgDataUrl = ''
            let input = document.getElementById("upload");
            input.value='';
            this.getImgSrc()
          }
        }).catch(err=>{
          console.log(err)
          this.$message({
            message: "上传失败",
            type: "error"
          })
        })
      },
      beforeClose(done){
        this.imgDataUrl = ''
        let input = document.getElementById("upload");
        input.value='';
        done()
      }
    },
    created() {

    },
    mounted() {
      this.getLoginUserRole()
      this.getImgSrc()
    },
  }
</script>
<style rel="stylesheet/scss" lang="scss" scoped>
  .btnRow {
    margin: 10px;
  }
</style>
