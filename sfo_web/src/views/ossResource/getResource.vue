/**
* Create by wenboling on 2018/5/16
*/

<template>
  <div>
    <el-form ref="form" :model="form" label-width="120px" style="margin: 10px">
      <el-form-item label="项目名" required>
        <el-col :span="10">
          <el-input v-model="project_name"></el-input>
        </el-col>
      </el-form-item>
      <el-form-item label="用户名" required>
        <el-col :span="10">
          <el-input v-model="username"></el-input>
        </el-col>
      </el-form-item>
      <el-form-item label="项目描述">
        <el-col :span="10">
          <el-input v-model="description"></el-input>
        </el-col>
      </el-form-item>
      <el-form-item label="domain">
        <el-col :span="10">
          <el-input v-model="domain"></el-input>
        </el-col>
      </el-form-item>
      <el-form-item label="容器名">
        <el-col :span="10">
          <el-input v-model="containerName"></el-input>
        </el-col>
      </el-form-item>
      <el-form-item label="空间(GB)" required>
        <el-col :span="10">
          <el-input v-model="form.capacity"></el-input>
        </el-col>
      </el-form-item>
      <el-form-item label="选择集群" required>
        <el-select v-model="form.clusterName">
          <el-option v-for="cluster in clusterList"
                     :key="cluster.cluster_name"
                     :label="cluster.cluster_name"
                     :value="cluster.cluster_name">
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="onSubmit">提交申请</el-button>
        <el-button @click="resetData">重 置</el-button>
      </el-form-item>
    </el-form>

    <el-dialog title="提示"
               :visible.sync="dialogVisible"
               width="50%"
               :before-close="handleClose"
               :close-on-click-modal="false"
               :close-on-press-escape="false"
               :show-close="!isProcessing">
      <div>
        <el-row v-if="isProcessing" style="margin-bottom: 10px;font-size: large"><i class="el-icon-warning"
                                       style="color: #e23a1f;"></i>&nbsp;{{ tips }}</el-row>
        <el-row style="margin-bottom: 10px">
          <span v-if="isApplyingResource">
            <i class="el-icon-loading"></i> 正在申请资源
          </span>
          <div v-else>
            <span v-if="applyResourceStatus === 'success'">
              <i class="el-icon-success" style="color: #6ce26c"></i> 申请资源成功
            </span>
            <span v-else-if="applyResourceStatus === 'failed'">
              <i class="el-icon-error" style="color: #bf1406"></i> 申请资源失败：
              <span>{{ result }}</span>
            </span>
          </div>
        </el-row>
      </div>
      <div v-if="applyResourceStatus === 'success' && !isProcessing" style="margin-bottom: 10px">
        <span>申请资源结果：</span>
        <el-form :model="result" label-width="120px" label-position="right" style='width: 100%; margin-left:20px;'>
          <el-form-item prop="container" label="container信息">
            <span class="result">{{ result.container }}</span>
          </el-form-item>
          <el-form-item prop="user" label="user信息">
            <span class="result">{{ result.user }}</span>
          </el-form-item>
          <el-form-item prop="password" label="密　码">
            <span class="result">{{ result.passwd }}</span>
          </el-form-item>
          <el-form-item prop="url" label="url">
            <span class="result">{{ result.url }}</span>
          </el-form-item>
        </el-form>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button type="primary" @click="handleClose" :disabled="isProcessing">确 定</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
  import { createAccount, applyForDNS, addToCMDB } from '@/api/oss'
  import { getClusters } from '@/api/dashboard'
  import { getTaskLogs } from '@/api/log'
  import axios from 'axios'

  export default {
    data() {
      return {
        project_name: '',
        form: {
          username: '',
          domain: '',
          containerName: '',
          description: '',
          capacity: '',
          clusterName: '',
        },
        dialogVisible: false,
        isProcessing: false,
        isApplyingResource: false,
        applyResourceStatus: '',
        result: '',
        tips: '正在执行请求，请耐心等待且不要关闭此对话框或者页面',
        clusterList: [],

        isPRD: false,
      }
    },
    computed: {
      oss_account(){
        if(this.syscode !== '' && this.form.system_env !== ''){
          return `AUTH_${this.syscode}-${this.form.system_env}`
        }else {
          return ''
        }
      },
    },
    created() {
      this.getClusterList()
    },
    mounted() {
      this.getENV()
    },
    methods: {
      resetData(){
        this.project_name = ''
        this.form = {
          username: '',
          domain: '',
          containerName: '',
          description: '',
          capacity: '',
          clusterName: '',
        }
      },
      onSubmit() {
        let data = Object.assign({}, this.form)
        data.ossAccountName = this.project_name
        data.sysname = this.project_name
        this.dialogVisible = true
        this.isProcessing = true
        this.isApplyingResource = true
        this.applyResource(this.project_name, data)
      },
      applyResource(syscode, form_data){
        createAccount(syscode, form_data).then(res=>{
          this.isApplyingResource = false
          if(res.data.status === 200){
            this.result = res.data.data
            this.applyResourceStatus = 'success'
            this.isProcessing = false
            this.resetData()
          }else{
            this.result = `${res.data.message}`
            this.applyResourceStatus = 'failed'
            this.isProcessing = false
          }
        }).catch(err=>{
          this.result = err.message
          this.isApplyingResource = false
          this.applyResourceStatus = 'failed'
          this.isProcessing = false
        })
      },
      handleClose() {
        this.$confirm('确认关闭？')
          .then(_ => {
            this.dialogVisible = false
            this.applyResourceStatus = ''
            this.applyDNSStatus = ''
          })
          .catch(_ => {});
      },
      getClusterList(){
        getClusters().then(response => {
          if(response.data.status === 200 && response.status === 200){
            this.clusterList = response.data.data
          }
        }).catch(error => {
          console.log(error)
        })
      },
      getENV(){
        if(process.env.ENV_NAME === 'prd'){
          this.isPRD = true
        }
      }
    }
  }
</script>
<style rel="stylesheet/scss" lang="scss" scoped>
  .result {
    font-size: larger;
    color: #00a0e9;
  }
</style>
