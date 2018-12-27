/**
* Create by wenboling on 2018/5/7
*/

<template>
  <div>
    <el-row :gutter="10" style="margin: 10px">
      <el-col :span="12">
        <el-card>
          <div slot="header" class="clearfix">
            <span>用户列表</span>
          </div>
          <el-table :data="userList" style="width: 100%">
            <el-table-column prop="user_account" label="账号">
              <template slot-scope="scope">
                <el-tooltip effect="dark" content="点击获取详情" placement="right">
                  <span class="link-type" @click="handleUserNameClick(scope.row)">{{ scope.row.user_account }}</span>
                </el-tooltip>
              </template>
            </el-table-column>
            <el-table-column prop="display_name" label="显示名"></el-table-column>
            <el-table-column prop="add_time" label="添加时间"></el-table-column>
            <el-table-column prop="last_login_time" label="上次登录时间"></el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <div slot="header" class="clearfix">
            <span>角色列表</span>
            <el-button style="float: right; padding: 3px 0" type="text" @click="handleAddRole">添加角色</el-button>
          </div>
          <el-table :data="roleList" style="width: 100%">
            <el-table-column prop="role_name" label="角色名" width="100">
              <template slot-scope="scope">
                <el-tooltip effect="dark" content="点击获取详情或修改" placement="right">
                  <span class="link-type" @click="handleRoleNameClick(scope.row)">{{ scope.row.role_name }}</span>
                </el-tooltip>
              </template>
            </el-table-column>
            <el-table-column prop="last_modify_time" label="上次修改时间" width="180"></el-table-column>
            <el-table-column prop="add_time" label="添加时间" width="180"></el-table-column>
            <el-table-column prop="role_desc" label="角色描述" show-overflow-tooltip></el-table-column>
            <el-table-column
              label="操作"
              width="80">
              <template slot-scope="scope">
                <el-button
                  size="mini"
                  type="danger"
                  icon="el-icon-delete"
                  :disabled="scope.row.role_name === 'admin' || scope.row.role_name === 'visitor'"
                  @click="handleDeleteRole(scope.row)"></el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!--TODO: 用户详情对话框, 应当看到用户的角色-->
    <el-dialog :title="titleMap[dialogStatus]" :visible.sync="userDialogVisible" :before-close="closeUserDialog" width="60%">
      <el-form :model="userFormData" label-width="80" label-position="left" ref="userDialogForm" style='width: 100%; margin-left:20px;'>
        <el-form-item prop="user_account" label="角色名">
          <el-col :span="10">
            <el-input disabled
                      v-model="userFormData.user_account" auto-complete="off"></el-input>
          </el-col>
        </el-form-item>
        <el-form-item prop="display_name" label="描　述">
          <el-col :span="10">
            <el-input  :disabled="dialogStatus === 'detail'" v-model="userFormData.display_name"></el-input>
          </el-col>
        </el-form-item>
        <el-form-item prop="roles" label="角　色">
          <el-transfer v-model="userFormData.roles"
                       :data="roleNameList"
                       :titles="['可选角色', '已有角色']"
                       :button-texts="['移除角色', '添加角色']">
            <el-tooltip effect="dark" placement="top" slot-scope="{ option }" :open-delay="delayshowtip">
              <div slot="content">{{ option.label }}</div>
              <span>{{ option.label }}</span>
            </el-tooltip>
          </el-transfer>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click.native="closeUserDialog" v-if="dialogStatus==='update'">取消</el-button>
        <el-button v-if="dialogStatus==='detail'" :disabled="canUserEdit" @click.native="enableEditUser" :loading="addLoading" type="primary">启用编辑</el-button>
        <el-button v-else @click.native="updateUserInfo" :loading="addLoading" type="primary">提交</el-button>
      </div>
    </el-dialog>
    <!--TODO: 添加角色对话框-->
    <el-dialog :title="titleMap[dialogStatus]" :visible.sync="roleDialogVisible" :before-close="closeRoleDialog" width="60%">
      <el-form :model="roleFormData" label-width="80" label-position="left" ref="roleDialogForm" style='width: 100%; margin-left:20px;'>
        <el-form-item prop="role_name" label="角色名">
          <el-col :span="10">
            <el-input :disabled="dialogStatus !== 'create'"
                      v-model="roleFormData.role_name" auto-complete="off"></el-input>
          </el-col>
        </el-form-item>
        <el-form-item prop="role_desc" label="描　述">
          <el-col :span="10">
            <el-input  :disabled="dialogStatus === 'detail'"
                       type="textarea" v-model="roleFormData.role_desc"></el-input>
          </el-col>
        </el-form-item>
        <el-form-item prop="permissions" label="权　限">
          <el-transfer v-model="roleFormData.permissions"
                       :data="permissions"
                       :titles="['可选权限', '已选权限']"
                       :button-texts="['移除权限', '添加权限']">
            <el-tooltip effect="dark" placement="top" slot-scope="{ option }" :open-delay="delayshowtip">
              <div slot="content">{{ option.label }}</div>
              <span>{{ option.label }}</span>
            </el-tooltip>
            <el-select class="transfer-footer" v-model="value" placeholder="请选择" slot="left-footer" size="mini" @change="filterShowItem">
              <el-option v-for="item in options" :key="item.value" :label="item.label" :value="item.value">
              </el-option>
            </el-select>
          </el-transfer>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click.native="closeRoleDialog" v-if="dialogStatus==='create' || dialogStatus==='update'">取消</el-button>
        <el-button v-if="dialogStatus==='detail'" :disabled="canRoleEdit" @click.native="enableEditRole" :loading="addLoading" type="primary">启用编辑</el-button>
        <el-button v-if="dialogStatus==='update'" @click.native="updateRoleInfo" :loading="addLoading" type="primary">提交</el-button>
        <el-button v-if="dialogStatus==='create'" @click.native="addRole" :loading="addLoading" type="primary">提交</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
  import { getUserList, getRoleList, getPermissionList, createRole, deleteRole, updateRole, getRoleDetail, getUserDetail, updateUser } from '@/api/management'
  import { getRole, removeToken } from '@/utils/cookie-util'
  export default {
    data() {
      return {
        userList: [],
        roleList: [],
        roleNameList: [],
        titleMap: {
          'create': '新建',
          'update': '编辑',
          'detail': '详情',
        },
        dialogStatus: '',

        roleDialogVisible: false,
        addLoading: false,
        delayshowtip: 500,

        //新建角色框数据模型
        roleFormData: {
          role_name: '',
          role_desc: '',
          permissions: [], //角色拥有的权限
        },

        userDialogVisible: false,
        userFormData: {
          user_account: '',
          display_name: '',
          roles: [],
        },
        permissionList: [], //权限列表
        options: [{
          value: 'all',
          label: '全部权限'
        }, {
          value: 'get',
          label: 'get'
        }, {
          value: 'post',
          label: 'post'
        }, {
          value: 'put',
          label: 'put'
        }, {
          value: 'delete',
          label: 'delete'
        }],
        value: 'all',
        query: '',
      }
    },
    computed: {
      permissions() {
        return this.permissionList.filter(item => {
          const label = item['label'] || item['label'].toString();
          return label.toLowerCase().indexOf(this.query.toLowerCase()) > -1;
        });
      },
      canRoleEdit() {
        return this.roleFormData.role_name === 'admin' || this.roleFormData.role_name === 'visitor'
      },
      canUserEdit() {
        let roles = JSON.parse(getRole())
        return roles.indexOf('admin') <= -1 && roles.indexOf('superadmin') <= -1
      }
    },
    created() {
      this.getUsers()
      this.getRoles()
      this.getPermissions()
    },
    mounted() {
    },
    methods: {
      //user相关操作
      getUsers(){
        getUserList().then(res=>{
          if(res.status === 200 && res.data.status == 200){
            this.userList = res.data.data
          }else if(res.data.status === 401){
            this.handle401()
          }
        }).catch(err=>{
          console.log(err)
          // this.handle401()
        })
      },
      getUserDetailInfo(user_account){
        getUserDetail(user_account).then(res=>{
          if(res.status === 200 && res.data.status == 200){
            this.userFormData = Object.assign({}, res.data.data)
            this.userDialogVisible = true
          }
        }).catch(err=>{
          console.log(err)
          // this.handle401()
        })
      },
      updateUserInfo(){
        this.addLoading = true
        updateUser(this.userFormData.user_account, this.userFormData).then(res=>{
          if(res.status === 200){
            this.showMsg('修改成功', 'success')
          }else{
            this.showMsg("修改失败，请检查", "error")
          }
          this.addLoading = false
          this.getUsers()
          this.closeUserDialog()
        }).catch(err=>{
          console.log(err)
          this.showMsg("修改失败，请检查", "error")
          this.addLoading = false
          this.getUsers()
          this.closeUserDialog()
        })
      },
      handleUserNameClick(row){
        this.dialogStatus = 'detail'
        this.getUserDetailInfo(row.user_account)
        this.changeRoleNameListStatus(true)
      },
      enableEditUser(){
        this.dialogStatus = 'update'
        this.changeRoleNameListStatus(false)
      },
      closeUserDialog(){
        this.userDialogVisible = false
      },
      changeRoleNameListStatus(status){
        if(this.roleNameList){
          for(let role of this.roleNameList){
            role.disabled = status
          }
        }
      },

      //role相关操作
      getRoles(){
        getRoleList().then(res=>{
          if(res.status === 200 && res.data.status == 200){
            this.roleList = res.data.data
            this.roleNameList = []
            for(let data of res.data.data){
              this.roleNameList.push({
                key: data.role_name,
                label: data.role_name,
                disabled: false,
              })
            }
          }else if(res.data.status === 401){
            this.handle401()
          }
        }).catch(err=>{
          console.log(err)
          this.handle401()
        })
      },
      getRoleDetailInfo(role_name){
        getRoleDetail(role_name).then(res=>{
          if(res.status === 200 && res.data.status == 200){
            this.roleFormData = Object.assign({}, res.data.data)
            this.roleDialogVisible = true
          }
        }).catch(err=>{
          console.log(err)
          // this.handle401()
        })
      },
      getPermissions() {
        getPermissionList().then(res=>{
          if(res.status === 200 && res.data.status == 200){
              for(let data of res.data.data){
                this.permissionList.push({
                  key: data,
                  label: data,
                  disabled: false,
                }
              )
            }
          }
        }).catch(err=>{
          console.log(err)
          // this.handle401()
        })
      },
      handleAddRole(){
        this.dialogStatus = 'create'
        this.changePermissionListStatus(false)
        this.roleDialogVisible = true
      },
      changePermissionListStatus(status){
        if(this.permissionList){
          for(let permission of this.permissionList){
            permission.disabled = status
          }
        }
      },
      handleRoleNameClick(row){
        this.dialogStatus = 'detail'
        this.getRoleDetailInfo(row.role_name)
        this.changePermissionListStatus(true)
      },
      //启用编辑
      enableEditRole(){
        this.dialogStatus = 'update'
        this.changePermissionListStatus(false)
      },
      updateRoleInfo(){
        this.addLoading = true
        updateRole(this.roleFormData.role_name, this.roleFormData).then(res=>{
          if(res.status === 201){
            this.showMsg('修改成功', 'success')
          }else{
            this.showMsg("修改失败，请检查", "error")
          }
          this.addLoading = false
          this.getRoles()
          this.closeRoleDialog()
        }).catch(err=>{
          console.log(err)
          this.showMsg("修改失败，请检查", "error")
          this.addLoading = false
          this.getRoles()
          this.closeRoleDialog()
        })
      },
      handleDeleteRole(row){
        this.$confirm(`确认删除角色: ${row.role_name}?`, '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          this.delRole(row.role_name)
        }).catch(() => {
          this.showMsg('已取消删除', 'info')
        });
      },
      addRole(){
        this.addLoading = true
        let data = Object.assign({}, this.roleFormData);
        createRole(data).then(res=>{
          if(res.status === 200 && res.data.status === 200){
            this.showMsg("创建成功", "success")
          }else{
            this.showMsg("创建失败，请检查", "error")
          }
          this.addLoading = false
          this.getRoles()
          this.closeRoleDialog()
        }).catch(err=>{
          console.log(err)
        })
      },
      delRole(role_name){
        deleteRole(role_name).then(res=>{
          console.log(res)
          if(res.status===204){
            this.showMsg("删除成功", "success")
          }else {
            this.showMsg("删除失败，请稍后再试", "error")
          }
          this.getRoles()
        }).catch(err=>{
          this.showMsg(err.message, "error")
        })
      },
      closeRoleDialog(){
        this.roleDialogVisible = false
        this.$refs['roleDialogForm'].resetFields();
        this.resetData()
      },
      resetData(){
        this.roleFormData = {
          role_name: '',
          role_desc: '',
          permissions: [], //角色拥有的权限
        };
        this.query = ''
        this.value = 'all'
      },
      filterShowItem(value){
        if(value === 'all'){
          this.query = ''
        }else{
          this.query = value
        }
      },

      //公用函数
      handle401(){
        this.showMsg('请先登录', 'error')
        this.$store.dispatch('FedLogOut').then(() => {
          this.$router.push('/login')
          this.$store.dispatch('LogOut').then((res) => {
            location.reload()  // 为了重新实例化vue-router对象 避免bug
          })
        })
      },
      showMsg(msg, type) {
        this.$message({
          message: msg,
          type: type
        });
      },
    }
  }
</script>
<style rel="stylesheet/scss" lang="scss" scoped>
  .clearfix:before,
  .clearfix:after {
    display: table;
    content: "";
  }
  .clearfix:after {
    clear: both
  }
  .link-type,
  .link-type:focus {
    color: #337ab7;
    cursor: pointer;
    &:hover {
      color: rgb(32, 160, 255);
    }
  }
  .transfer-footer {
    margin-left: 10px;
    margin-right: 10px;
    margin-bottom: 5px;
    padding: 0 20px;
  }
</style>
