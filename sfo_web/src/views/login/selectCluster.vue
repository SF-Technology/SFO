/**
* Create by wenboling on 2018/8/16
*/
<template>
  <div>
    <div class="login-container">
      <div class="select-div">
        <h3 class="title">选择集群</h3>
        <div class="tips">
          <span>请在此选择你想要监控的集群。在进入监控页面之后，你可以通过页面右上方的选择框切换监控集群。</span>
        </div>
        <el-table :data="clusterList" style="width: 100%" max-height="500">
          <el-table-column prop="cluster_name" min-width="120" label="集群名"></el-table-column>
          <el-table-column prop="alias" min-width="120" label="集群别名"></el-table-column>
          <el-table-column prop="description" min-width="120" label="描述"></el-table-column>
          <el-table-column label="操作">
            <template slot-scope="scope">
              <el-button type="primary" @click="selectCluster(scope.row.cluster_name)">选择该集群</el-button>
            </template>
          </el-table-column>
        </el-table>
        <div class="help_url">
          <a href="http://xxx.com/help/document.html" target="_blank">产品说明书</a>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import { setClusterName, getClusterName } from  '@/utils/cookie-util'
  import { getClusters } from '@/api/dashboard'
  export default {
    data() {
      return {
        clusterList: [],
      }
    },
    methods: {
      getClusterList(){
        getClusters().then(response => {
          if(response.data.status === 200 && response.status === 200){
            this.clusterList = []
            this.clusterList = response.data.data
            this.$store.dispatch('setClusterList', this.clusterList)
          }
        }).catch(error => {
          console.log("!!!!!", error)
        })
      },
      selectCluster(cluster_name){
        setClusterName(cluster_name)
        this.$store.dispatch('setSelectedCluster', cluster_name)
        this.$router.push({ path: '/' })
      }
    },
    created() {
      this.getClusterList()
    },
    mounted() {
    },
  }
</script>
<style rel="stylesheet/scss" lang="scss">
  @import "src/styles/mixin.scss";
  $bg:#2d3a4b;
  $dark_gray:#889aa4;
  $light_gray:#eee;

  .login-container {
    @include relative;
    height: 100vh;
    background-color: $bg;
    input:-webkit-autofill {
      -webkit-box-shadow: 0 0 0px 1000px #293444 inset !important;
      -webkit-text-fill-color: #fff !important;
    }
    input {
      background: transparent;
      border: 0px;
      -webkit-appearance: none;
      border-radius: 0px;
      padding: 12px 5px 12px 15px;
      color: $light_gray;
      height: 47px;
    }
    .el-input {
      display: inline-block;
      height: 47px;
      width: 85%;
    }
    .tips {
      font-size: 14px;
      color: #fff;
      margin-bottom: 10px;
    }
    .svg-container {
      padding: 6px 5px 6px 15px;
      color: $dark_gray;
      vertical-align: middle;
      width: 30px;
      display: inline-block;
      &_login {
        font-size: 20px;
      }
    }
    .title {
      font-size: 26px;
      font-weight: 400;
      color: $light_gray;
      margin: 0px auto 40px auto;
      text-align: center;
      font-weight: bold;
    }
    .select-div {
      position: absolute;
      left: 0;
      right: 0;
      width: 80%;
      padding: 35px 35px 15px 35px;
      margin: 120px auto;
    }
  }
  .help_url {
    text-align: center;
    margin: 20px;
    a{
      color: #c5d5e9;
      text-decoration:underline;
    }
    a:hover{
      color: #4ce90f;
    }
  }
</style>
