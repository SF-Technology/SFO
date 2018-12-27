/**
* Create by wenboling on 2018/8/23
*/
<template>
  <div>
    <el-row style="margin: 10px;">
      <el-button style="float: right; margin-right: 20px;"
                 icon="el-icon-plus" type="primary" size="medium"
                 @click="handleCreateRole">新建</el-button>
    </el-row>
    <el-row>
      <el-table :data="swiftRoleList" style="width: 96%; margin: 5px auto">
        <el-table-column prop="role_name" label="角色名" min-width="100px"></el-table-column>
        <el-table-column prop="role_meta" label="角色属性" min-width="100px"></el-table-column>
        <el-table-column prop="role_desc" label="描述" min-width="200px"></el-table-column>
        <el-table-column prop="add_time" label="添加时间" min-width="200px"></el-table-column>
        <el-table-column label="操作" min-width="200px">
          <template slot-scope="scope">
            <el-button type="primary" icon="el-icon-edit" size="mini" @click="handleUpdateRole(scope.row)"></el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-row>

    <el-dialog :title="titleMap[dialogStatus]" :visible.sync="roleDialogVisible" :before-close="closeRoleDialog" width="60%">
      <el-form :model="roleFormData" label-width="80px" label-position="right" :rules="rules" ref="roleDialogForm" style='width: 100%; margin-left:20px;'>
        <el-form-item prop="role" label="角色名">
          <el-col :span="10">
            <el-input :disabled="dialogStatus !== 'create'"
                      v-model="roleFormData.role" auto-complete="off" placeholder="请输入角色名"></el-input>
          </el-col>
        </el-form-item>
        <el-form-item prop="role_meta" label="角色属性">
          <el-col :span="10">
            <el-input v-model="roleFormData.role_meta" auto-complete="off" placeholder="请输入角色属性"></el-input>
          </el-col>
        </el-form-item>
        <el-form-item prop="role_desc" label="描　述">
          <el-col :span="10">
            <el-input  :disabled="dialogStatus === 'detail'"
                       type="textarea" v-model="roleFormData.role_desc"
                       placeholder="请输入一些关于角色的描述"></el-input>
          </el-col>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click.native="closeRoleDialog">取消</el-button>
        <el-button v-if="dialogStatus==='update'" @click.native="updateRoleInfo" :loading="addLoading" type="primary">提交</el-button>
        <el-button v-if="dialogStatus==='create'" @click.native="createNewRole" :loading="addLoading" type="primary">提交</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
  import { getRoles, createRole, updateRole } from '@/api/oss'
  export default {
    data() {
      return {
        swiftRoleList: [],
        roleDialogVisible: false,
        roleFormData: {
          role: '',
          role_meta: '',
          role_desc: ''
        },
        selectRoleId: '',
        dialogStatus: 'create',
        titleMap: {
          create: '新建角色',
          modify: '编辑角色'
        },
        addLoading: false,
        rules: {
          role: [
            {required: true, message: '请输入角色名', trigger: 'blur'}
          ],
          role_meta: [
            {required: true, message: '请输入角色属性', trigger: 'blur'}
          ],
          role_desc: [
            {required: true, message: '请输入描述', trigger: 'blur'}
          ]
        }
      }
    },
    methods: {
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

      createNewRole(){
        this.$refs.roleDialogForm.validate(valid => {
          if(valid){
            this.addLoading = true
            createRole(this.roleFormData).then(res => {
              if (res.data.status === 201 && res.status === 201) {
                this.addLoading = false
                this.showMsg("创建成功", "success")
                this.getRoleList()
                this.closeRoleDialog()
              }else if(res.status === 202 && res.data.status === 202){
                this.addLoading = false
                this.showMsg(`角色: ${this.roleFormData.role} 已存在`, "error")
                this.closeRoleDialog()
              }
            }).catch(err => {
              this.addLoading = false
              this.showMsg(`创建失败: ${err.message}`, "error")
              this.closeRoleDialog()
            })
          }else {
            this.showMsg("请检查输入", "error")
          }
        })
      },
      updateRoleInfo(){
        this.$refs.roleDialogForm.validate(valid => {
          if(valid){
            this.addLoading = true
            updateRole(this.selectRoleId, this.roleFormData).then(res => {
              if(res.data.status === 201 && res.status === 201){
                this.addLoading = false
                this.showMsg("修改成功", "success")
                this.getRoleList()
                this.closeRoleDialog()
              }
            }).catch(err=>{
              this.addLoading = false
              this.showMsg(`修改失败: ${err.message}`, "err")
              this.closeRoleDialog()
            })
          }else {
            this.showMsg("请检查输入", "error")
          }
        })
      },
      resetData(){
        this.roleFormData = {
          role: '',
          role_meta: '',
          role_desc: ''
        }
      },
      handleUpdateRole(row){
        this.resetData()
        this.roleFormData.role_meta = row.role_meta
        this.roleFormData.role = row.role_name
        this.roleFormData.role_desc = row.role_desc
        this.selectRoleId = row.guid
        this.roleDialogVisible = true
        this.dialogStatus = 'update'
      },
      handleCreateRole(){
        this.resetData()
        this.roleDialogVisible = true
        this.dialogStatus = 'create'
      },
      closeRoleDialog(){
        this.resetData()
        this.addLoading = false
        this.$refs['roleDialogForm'].resetFields();
        this.roleDialogVisible = false
      },

      showMsg(msg, type) {
        this.$message({
          message: msg,
          type: type
        });
      },
    },
    created() {
      this.getRoleList()
    },
    mounted() {

    },
  }
</script>
<style rel="stylesheet/scss" lang="scss" scoped>
  .link-type,
  .link-type:focus {
    color: #337ab7;
    cursor: pointer;
    &:hover {
      color: rgb(32, 160, 255);
    }
  }
</style>
