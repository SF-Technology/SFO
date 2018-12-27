/**
* Create by wenboling on 2018/5/29
*/

<template>
  <el-row :gutter="10" style="margin: 10px auto">
    <el-col :span="10" style="margin-top: 10px">
      <el-form ref="form" :model="dataForm" label-width="80px" :rules="rules">
        <el-form-item label="账户" prop="account">
          <el-select v-model="dataForm.account" placeholder="请选择账户">
            <el-option  v-for="account in accountList"
                     :key="account.account_id"
                     :label="account.system_code"
                     :value="account.account_id">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="容器" prop="container">
          <el-col :span="18">
            <el-input v-model="dataForm.container" placeholder="请输入容器名"></el-input>
          </el-col>
        </el-form-item>
        <el-form-item label="对象" prop="object">
          <el-col :span="18">
            <el-input v-model="dataForm.object" placeholder="请输入对象名"></el-input>
          </el-col>
        </el-form-item>
        <el-form-item label="时间" required>
          <el-date-picker
            v-model="dataForm.time"
            type="datetime"
            placeholder="选择日期时间"
            default-time="12:00:00">
          </el-date-picker>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="onSubmit" :loading="isLoading">提交</el-button>
          <el-button :disabled="isLoading" @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-col>
    <el-col :span="13" style="margin-top: 10px;">
      <el-table
        :data="actionLog"
        style="width: 100%">
        <el-table-column
          prop="date"
          label="时间"
          width="200">
        </el-table-column>
        <el-table-column
          prop="operator"
          label="操作员"
          width="180">
        </el-table-column>
        <el-table-column
          prop="operator"
          label="操作结果"
          width="180">
        </el-table-column>
        <el-table-column
          prop="action"
          label="操作记录">
        </el-table-column>
      </el-table>
    </el-col>
  </el-row>
</template>

<script>
  import { undelete, getAccounts } from "@/api/oss";

  export default {
    data() {
      return {
        dataForm: {
          account: "",
          container: "",
          object: "",
          time: ""
        },
        accountList: [],
        actionLog: [],
        isLoading: false,
        rules: {
          account: [
            {required: true, message: '请选择账户名称', trigger: 'change'}
          ],
          container: [
            {required: true, message: '请输入容器名称', trigger: 'blur'}
          ],
          object: [
            {required: true, message: '请输入对象名称', trigger: 'blur'}
          ],
        }
      }
    },
    created() {
      this.getAccountList()
    },
    mounted() {

    },
    methods: {
      getAccountList(){
        getAccounts().then(res=>{
          if(res.status===200 && res.data.status===200){
            this.accountList = res.data.data
          }
        }).catch(err=>{
          console.log(err)
        })
      },
      resetData(){
        this.dataForm = {
          account: "",
          container: "",
          object: "",
          time: ""
        }
      },
      resetForm(){
        this.resetData()
        this.$refs['form'].resetFields();
      },
      onSubmit(){
        this.$refs.form.validate((valid)=>{
          if(valid){
            let para = Object.assign({}, this.dataForm)
            para.time = new Date(para.time).getTime()/1000
            para.account = 'AUTH_' + para.account
            this.isLoading = true
            this.objectRecover(para)
          }
        })
      },
      objectRecover(object_to_recover){
        undelete(object_to_recover).then(res=>{
          if(res.data.status==201){
            this.openNotify('成功', 'success', '对象恢复成功')
          }
          this.isLoading = false
        }).catch(err=>{
          console.log(err)
          this.openNotify('失败', 'error', '对象恢复失败，请检查')
          this.isLoading = false
        })
      },
      openNotify(title, type, message){
        this.$notify({
          title: title,
          message: message,
          type: type
        });
      }
    }
  }
</script>
