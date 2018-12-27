<template>
  <div>
    <div class="login-container">
      <el-form autoComplete="on" :model="loginForm" :rules="loginRules" ref="loginForm"
             label-position="left" label-width="0px"
             class="card-box login-form">
        <h3 class="title">系统登录</h3>
        <el-form-item prop="username">
          <span class="svg-container svg-container_login">
            <icon-svg icon-class="yonghuming" />
          </span>
          <el-input name="username" type="text" v-model="loginForm.username" autoComplete="on" placeholder="用户名" />
        </el-form-item>
        <el-form-item prop="password">
          <span class="svg-container">
            <icon-svg icon-class="mima" ></icon-svg>
          </span>
          <el-input v-if="login_type === 'existed'" name="password" type="password" @keyup.enter.native="handleLogin" v-model="loginForm.password" autoComplete="on"
            placeholder="密码">
          </el-input>
          <el-input v-else name="password" type="password" @keyup.enter.native="handleLoginToCreateCluster" v-model="loginForm.password" autoComplete="on"
                    placeholder="密码">
          </el-input>
        </el-form-item>
        <el-form-item>
          <div style="padding: 5px 5px 5px 10px">
            <el-radio v-model="login_type" label="existed">登录已有集群</el-radio>
            <el-radio v-model="login_type" label="new">新建集群</el-radio>
          </div>
        </el-form-item>
        <el-form-item v-if="login_type === 'existed'">
          <span class="svg-container svg-container_login">
            <icon-svg icon-class="shouce" />
          </span>
          <el-select v-model="selected"
                     v-loading="clusterListLoading">
            <el-option v-for="cluster in clusterList"
                       :key="cluster.cluster_name"
                       :label="cluster.cluster_name"
                       :value="cluster.cluster_name">
            </el-option>
          </el-select>
          <span style="color: #8391a5"><<选择集群</span>
        </el-form-item>
        <div class="tips" v-for="cluster in clusterList" v-if="cluster.cluster_name === selected">
          <p style="margin-right:18px;">集群别名: {{ cluster.alias }}</p>
          <p style="margin-right:18px;">集群描述: {{ cluster.description }}</p>
        </div>
        <el-form-item>
          <el-button v-if="login_type==='existed'" :disabled="clusterListLoading" type="primary" style="width:100%;" :loading="loading" @click.native.prevent="handleLogin">
            登录
          </el-button>
          <el-button v-else type="primary" style="width:100%;" :loading="loading" @click.native.prevent="handleLoginToCreateCluster">
            登录
          </el-button>
        </el-form-item>
      </el-form>
    </div>
    <el-dialog title="集群创建向导" :visible.sync="createClusterDialogVisible"
               :close-on-click-modal="false" :close-on-press-escape="false" :show-close="false" width="80%">
      <create-cluster></create-cluster>
    </el-dialog>
  </div>
</template>

<script>
import { isvalidUsername } from '@/utils/validate'
import { loginByUsername } from '@/api/login'
import { getClusters } from '@/api/dashboard'
import { setClusterName, setClusters } from '@/utils/cookie-util'
import CreateCluster from '@/components/CreateCluster'

export default {
  name: 'login',
  components: {
    CreateCluster
  },
  data() {
    const validateUsername = (rule, value, callback) => {
      if (!isvalidUsername(value)) {
        callback(new Error('请输入正确的用户名'))
      } else {
        callback()
      }
    }
    const validatePass = (rule, value, callback) => {
      if (value.length < 0) {
        callback(new Error('密码不能小于6位'))
      } else {
        callback()
      }
    }
    return {
      loginForm: {
        username: '',
        password: ''
      },
      loginRules: {
        username: [{ required: true, trigger: 'blur', validator: validateUsername }],
        password: [{ required: true, trigger: 'blur', validator: validatePass }]
      },

      clusterList: [],
      selected: '',
      clusterListLoading: false,

      loading: false,
      login_type: 'existed',
      createClusterDialogVisible: false,

      new_cluster: {
        name: ''
      },
      active: 0
    }
  },
  methods: {
    getClusters() {
      this.clusterListLoading = true
      getClusters().then(response => {
        if (response.data.status === 200 && response.status === 200) {
          this.clusterList = response.data.data
          this.selected = this.clusterList[0].cluster_name
          this.clusterListLoading = false
          setClusters(JSON.stringify(this.clusterList))
          this.$store.dispatch('setClusterList', this.clusterList)
        }
      }).catch(error => {
        console.log('!!!!!', error)
      })
    },
    handleLogin() {
      this.$refs.loginForm.validate(valid => {
        if (valid) {
          this.loading = true
          setClusterName(this.selected)
          this.$store.dispatch('setSelectedCluster', this.selected)
          this.$store.dispatch('Login', this.loginForm).then(() => {
            this.loading = false
            this.$router.push({ path: '/' })
          }).catch(() => {
            this.$message({
              message: '认证失败，请检查',
              type: 'error'
            })
            this.loading = false
          })
        } else {
          console.log('error submit!!')
          return false
        }
      })
    },
    handleLoginToCreateCluster() {
      this.loading = true
      this.loginForm.username = this.loginForm.username.trim()
      loginByUsername(this.loginForm).then(res => {
        if (res.status === 200) {
          if (res.data.data.roles.indexOf('superadmin') > -1) {
            this.createClusterDialogVisible = true
          } else {
            this.$message({
              message: '没有权限',
              type: 'error'
            })
          }
        } else {
          this.$message({
            message: '登录失败，请检查',
            type: 'error'
          })
        }
        this.loading = false
      }).catch(err => {
        this.loading = false
        this.$message({
          message: `登录失败，${err}`,
          type: 'error'
        })
      })
    }
  },
  created() {
    this.getClusters()
  }
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
    .login-form {
      position: absolute;
      left: 0;
      right: 0;
      width: 400px;
      padding: 35px 35px 15px 35px;
      margin: 120px auto;
    }
    .el-form-item {
      border: 1px solid rgba(255, 255, 255, 0.1);
      background: rgba(0, 0, 0, 0.1);
      border-radius: 5px;
      color: #454545;
    }
    .show-pwd {
      position: absolute;
      right: 10px;
      top: 7px;
      font-size: 16px;
      color: $dark_gray;
      cursor: pointer;
    }
    .thirdparty-button{
      position: absolute;
      right: 35px;
      bottom: 28px;
    }
  }
  .help_url {
    text-align: center;
    a{
      color: #c5d5e9;
      text-decoration:underline;
    }
    a:hover{
      color: #4ce90f;
    }
  }
</style>
