/**
* Create by wenboling on 2018/8/16
*/
<template>
  <div>
    <el-table :data="clusterList" style="width: 90%; margin: 10px auto" max-height="500">
      <el-table-column prop="cluster_name" min-width="120" label="集群名"></el-table-column>
      <el-table-column prop="alias" min-width="120" label="集群别名"></el-table-column>
      <el-table-column prop="description" min-width="120" label="描述"></el-table-column>
      <el-table-column min-width="120" label="集群属性">
        <template slot-scope="scope">
          <span v-if="scope.row.cluster_stat === 'dedicated'">专用资源池</span>
          <span v-if="scope.row.cluster_stat === 'public'">共享资源池</span>
        </template>
      </el-table-column>
      <el-table-column label="操作">
        <template slot-scope="scope">
          <el-button type="primary" @click="selectCluster(scope.row)" icon="el-icon-edit" size="small"></el-button>
          <el-button type="primary" @click="showSysList(scope.row.cluster_name)" icon="el-icon-view" size="small"
                     v-if="scope.row.cluster_stat === 'dedicated'"></el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog title="编辑" :visible.sync="dialogFormVisible">
      <el-form :model="clusterForm" label-width="80px">
        <el-form-item label="集群名">
          <el-col :span="12">
            <el-input v-model="clusterForm.cluster_name" disabled></el-input>
          </el-col>
        </el-form-item>
        <el-form-item label="集群别名">
          <el-col :span="12">
            <el-input v-model="clusterForm.alias"></el-input>
          </el-col>
        </el-form-item>
        <el-form-item label="描述">
          <el-col :span="12">
            <el-input type="textarea" v-model="clusterForm.desc"></el-input>
          </el-col>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">取 消</el-button>
        <el-button type="primary" @click="submitUpdateCluster(clusterForm)">确 定</el-button>
      </div>
    </el-dialog>

    <el-dialog title="专用资源池系统" :visible.sync="detailDialogVisible">
      <el-form :inline="true" :model="newSysForm" ref="sysform">
        <el-form-item label="系统编码"
                      prop="system_code"
                      :rules="[{ required: true, message: '系统编码不能为空'}]">
          <el-input v-model="newSysForm.system_code" placeholder="请输入系统编码"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="addRecord">添加</el-button>
        </el-form-item>
      </el-form>
      <el-row style="margin-top: 10px">
        <el-table :data="cluster_sys_map">
          <el-table-column property="cluster_name" label="集群名" min-width="180"></el-table-column>
          <el-table-column property="sys_code" label="系统编码" min-width="200"></el-table-column>
          <el-table-column label="操作" width="80">
            <template slot-scope="scope">
              <el-button type="text" @click="deleteRecord(scope.row)" style="color: red">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-row>
    </el-dialog>
  </div>
</template>

<script>
  import { getClusters } from '@/api/dashboard'
  import { updateCluster, getSysList, addSystoCluster, deleteSysfromCluster } from '@/api/cluster'
  export default {
    data() {
      return {
        clusterList: [],
        dialogFormVisible: false,
        clusterForm: {
          cluster_name: '',
          alias: '',
          desc: '',
        },
        cluster_sys_map: [],
        detailDialogVisible: false,
        newSysForm: {
          system_code: '',
        },
        selectClusterName: '',
      }
    },
    methods: {
      getClusterList(){
        getClusters().then(response => {
          if(response.data.status === 200 && response.status === 200){
            this.clusterList = []
            this.clusterList = response.data.data
          }
        }).catch(error => {
          console.log(error)
        })
      },
      selectCluster(row){
        this.dialogFormVisible = true
        this.clusterForm.cluster_name = row.cluster_name
        this.clusterForm.alias = row.alias
        this.clusterForm.desc = row.description
      },
      submitUpdateCluster(formData){
        let data = {}
        data.alias = formData.alias
        data.desc = formData.desc
        updateCluster(formData.cluster_name, data).then(res=>{
          if(res.status === 200 && res.data.status === 200){
            this.showMsg("更新成功", "success")
            this.getClusterList()
            this.dialogFormVisible = false
          }
        }).catch(err=>{
          console.log(err)
          this.showMsg(`更新失败${err}`, "error")
          this.dialogFormVisible = false
        })
      },
      showSysList(cluster_name){
        this.selectClusterName = cluster_name
        getSysList().then(res=>{
          if(res.status === 200 && res.data.status === 200){
            let data = res.data.data
            let tmp = data[this.selectClusterName]
            this.cluster_sys_map = tmp.map(item=>{
              return {cluster_name: this.selectClusterName, sys_code: item}
            })
            this.detailDialogVisible = true
            this.$nextTick(() => {
              this.$refs['sysform'].resetFields()
            })
          }
        }).catch(err=>{
          this.showMsg(`获取数据失败${err}`,"error")
        })
      },
      addRecord(){
        this.$refs["sysform"].validate((valid)=>{
          if(valid){
            this.$confirm(`确定要将${this.newSysForm.system_code}添加到${this.selectClusterName}?`, '提示', {
              confirmButtonText: '确定',
              cancelButtonText: '取消',
              type: 'warning'
            }).then(() => {
              let data = Object.assign({}, this.newSysForm)
              data.cluster_name = this.selectClusterName
              this.ensureAdd(data)
            }).catch(() => {
              this.$message({
                type: 'info',
                message: '已取消添加'
              });
            });
          }else{
            this.showMsg("请输入系统编码", "error")
          }
        })
      },
      ensureAdd(data){
        addSystoCluster(data).then(res=>{
          if(res.status === 201 && res.data.status === 201){
            this.showMsg("添加成功", "success")
            this.showSysList(this.selectClusterName)
            this.newSysForm.system_code = ''
          }else{
            this.showMsg(`添加失败: ${res.data.message}`, "error")
          }
        }).catch(err=>{
          this.showMsg("添加失败", "error")
        })
      },
      deleteRecord(row){
        this.$confirm(`确定要将${row.sys_code}从${row.cluster_name}中删除?`, '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          let data = {
            system_code: row.sys_code,
            cluster_name: row.cluster_name
          }
          this.ensureDelete(data)
        }).catch(() => {
          this.$message({
            type: 'info',
            message: '已取消删除'
          });
        });
      },
      ensureDelete(data){
        deleteSysfromCluster(data).then(res=>{
          if(res.status === 201 && res.data.status === 201){
            this.showMsg("删除成功", "success")
            this.showSysList(this.selectClusterName)
          }
        }).catch(err=>{
          this.showMsg("删除失败", "error")
        })
      },
      showMsg(msg, type) {
        this.$message({
          message: msg,
          type: type
        });
      },
    },
    created() {
      this.getClusterList()
    },
    mounted() {

    },
  }
</script>
<style rel="stylesheet/scss" lang="scss" scoped>
</style>
