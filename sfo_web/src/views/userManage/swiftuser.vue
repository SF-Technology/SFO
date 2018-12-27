/**
* Create by wenboling on 2018/8/24
*/
<template>
  <div>
    <el-row style="margin: 10px;">
      <el-button style="float: right; margin-right: 20px;"
                 icon="el-icon-plus" type="primary" size="medium"
                 @click="handleCreateUser">新建</el-button>
    </el-row>
    <el-row>
      <el-table :data="swiftUserList" style="width: 96%; margin: 5px auto"
                :default-sort = "{prop: 'system_user'}">
        <el-table-column prop="system_user" label="用户名" min-width="280px"></el-table-column>
        <el-table-column prop="account_id" label="账户名" min-width="280px"></el-table-column>
        <el-table-column prop="role_name" label="角色" min-width="100px"></el-table-column>
        <el-table-column prop="cluster_name" label="所属集群" min-width="250px"></el-table-column>
        <el-table-column prop="add_time" label="添加时间" min-width="180px"></el-table-column>
        <el-table-column label="操作" min-width="120px">
          <template slot-scope="scope">
            <el-button type="primary" icon="el-icon-edit" size="mini" @click="handleUpdateUser(scope.row)" :disabled="scope.row.role_name === 'admin'"></el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-row>

    <el-dialog :title="titleMap[dialogStatus]" :visible.sync="userDialogVisible" :before-close="closeUserDialog" width="60%">
      <el-form :model="userFormData" label-width="80px" label-position="right" :rules="rules" ref="userDialogForm" style='width: 100%; margin-left:20px;'>
        <el-form-item prop="swift_username" label="用户名">
          <el-col :span="10">
            <el-input :disabled="dialogStatus !== 'create'"
                      v-model="userFormData.swift_username" auto-complete="off" placeholder="请输入用户名"></el-input>
          </el-col>
        </el-form-item>
        <el-form-item prop="account" label="账　户">
          <el-select :disabled="dialogStatus !== 'create'" v-model="userFormData.account">
            <el-option v-for="account in swiftAccountList"
                       :key="account.account_id"
                       :label="account.account_id"
                       :value="account.account_id">
            </el-option>
          </el-select>
          <span v-if="swiftRoleList.length === 0">请先申请账户资源</span>
        </el-form-item>
        <el-form-item prop="role" label="角　色">
          <el-select v-model="userFormData.role">
            <el-option v-for="role in swiftRoleList"
                       :key="role.guid"
                       :label="role.role_name"
                       :value="role.role_name">
            </el-option>
          </el-select>
          <span v-if="swiftRoleList.length === 0">请先创建角色</span>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click.native="closeUserDialog">取消</el-button>
        <el-button v-if="dialogStatus==='update'" @click.native="updateUserInfo" :loading="addLoading" type="primary">提交</el-button>
        <el-button v-if="dialogStatus==='create'" @click.native="createNewUser" :loading="addLoading" type="primary">提交</el-button>
      </div>
    </el-dialog>

    <el-dialog title="创建成功" :visible.sync="resultDialogVisible"
               :close-on-click-modal="false"
               :close-on-press-escape="false"
               :before-close="closeResultDialog" width="60%">
      <el-form :model="result" label-width="80px" label-position="right" style='width: 100%; margin-left:20px;'>
        <el-form-item prop="username" label="用户名">
          <span class="result">{{ result.username }}</span>
        </el-form-item>
        <el-form-item prop="password" label="密　码">
          <span class="result">{{ result.password }}</span>
        </el-form-item>
        <el-form-item prop="account" label="账　户">
          <span class="result">{{ result.account }}</span>
        </el-form-item>
        <el-form-item prop="auth_url" label="auth_url">
          <span class="result">{{ result.auth_url }}</span>
        </el-form-item>
        <el-form-item prop="storage_url" label="storage_url">
          <span class="result">{{ result.storage_url }}</span>
        </el-form-item>
      </el-form>
    </el-dialog>
  </div>
</template>

<script>
  import { getAccounts, getRoles, getUsers, createUser, getUserDetail, updateUser } from '@/api/oss'
  import { mapGetters } from 'vuex'

  export default {
    computed: {
      ...mapGetters([
        'selectedCluster',
      ])
    },
    data() {
      return {
        swiftUserList: [],
        swiftRoleList: [],
        swiftAccountList: [],
        userDialogVisible: false,
        resultDialogVisible: false,
        userFormData: {
          role: '',
          account: '',
          swift_username: ''
        },
        selectUserId: '',
        dialogStatus: 'create',
        titleMap: {
          create: '新建角色',
          modify: '编辑角色'
        },
        addLoading: false,
        rules: {
          swift_username: [
            {required: true, message: '请输入用户名', trigger: 'blur'}
          ],
          account: [
            {required: true, message: '请选择账户', trigger: 'change'}
          ],
          role: [
            {required: true, message: '请选择角色', trigger: 'change'}
          ]
        },
        result: {},
      }
    },
    methods: {
      getUserList(clustername){
        getUsers(clustername).then(res=>{
          if(res.status === 200 && res.data.status === 200){
            this.swiftUserList = []
            this.swiftUserList = res.data.data
          }
        }).catch(err=>{
          console.log(err)
        })
      },
      getRoleList(){
        getRoles().then(res=>{
          if(res.status === 200 && res.data.status === 200){
            this.swiftRoleList = []
            this.swiftRoleList = res.data.data
          }
        }).catch(err=>{
          console.log(err)
        })
      },
      getAccountList(){
        getAccounts().then(res=>{
          if(res.status === 200 && res.data.status === 200){
            this.swiftAccountList = []
            this.swiftAccountList = res.data.data
          }
        }).catch(err=>{
          console.log(err)
        })
      },
      resetData(){
        this.userFormData = {
          role: '',
          account: '',
          swift_username: ''
        }
      },
      createNewUser(){
        this.$refs['userDialogForm'].validate(valid=>{
          if(valid){
            createUser(this.selectedCluster, this.userFormData).then(res=>{
              if(res.status === 200 && res.data.status === 200){
                this.result = {}
                this.result = res.data.data
                this.getUserList(this.selectedCluster)
                this.closeUserDialog()
                this.showResultDialog()
              }else{
                this.showMsg(`创建失败: ${res.data.message}`, "error")
                this.closeUserDialog()
              }
            }).catch(err=>{
              console.log(err)
              this.showMsg(`创建失败${err.message}`, "error")
              this.closeUserDialog()
            })
          }else{
            this.showMsg("请检查输入", "error")
          }
        })
      },
      updateUserInfo(){
        this.$refs['userDialogForm'].validate(valid=>{
          if(valid){
            updateUser(this.selectUserId, this.userFormData).then(res=>{
              if(res.status === 200 && res.data.status === 200){
                this.result = {}
                this.result = res.data.data
                this.getUserList(this.selectedCluster)
                this.closeUserDialog()
                this.showMsg("更新成功", "success")
              }else{
                this.showMsg(`更新失败: ${res.data.message}`, "error")
                this.closeUserDialog()
              }
            }).catch(err=>{
              console.log(err)
              this.showMsg(`更新失败${err.message}`, "error")
              this.closeUserDialog()
            })
          }else{
            this.showMsg("请检查输入", "error")
          }
        })
      },
      handleCreateUser(){
        this.getRoleList()
        this.getAccountList()
        this.dialogStatus = 'create'
        this.userDialogVisible = true
      },
      handleUpdateUser(row){
        this.getRoleList()
        this.getAccountList()
        this.selectUserId = row.guid
        console.log(this.selectUserId)
        this.userFormData.role = row.role_name
        this.userFormData.account = row.account_id
        this.userFormData.swift_username = row.system_user
        this.dialogStatus = 'update'
        this.userDialogVisible = true
      },
      closeUserDialog(){
        this.resetData()
        this.$refs['userDialogForm'].resetFields();
        this.userDialogVisible = false
      },
      showResultDialog(){
        this.resultDialogVisible = true
      },
      closeResultDialog(done){
        this.$confirm('你确定已经记住密码了吗?', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          done()
        }).catch(()=>{
          this.showMsg("请牢记信息", "info")
        })
      },
      showMsg(msg, type) {
        this.$message({
          message: msg,
          type: type
        });
      }
    },
    created() {
      this.getUserList(this.selectedCluster)
    },
    mounted() {

    },
  }
</script>
<style rel="stylesheet/scss" lang="scss" scoped>
  .result {
    font-size: larger;
    color: #00a0e9;
  }
</style>
