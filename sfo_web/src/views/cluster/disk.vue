/**
* Create by wenboling on 2018/7/4
*/
<template>
  <div>
    <el-row>
      <div style="float:right;margin: 10px 100px 10px 0;">
        <el-button type="primary" @click="batchOperation">批量操作</el-button>
      </div>
    </el-row>
    <el-row>
      <el-table :data="diskList" style="width: 95%;margin: 5px auto"
                :default-sort = "{prop: 'host_name'}"
                v-loading="tableLoading">
        <el-table-column type="expand">
          <template slot-scope="props">
            <el-form label-position="left" inline class="table-expand" label-width="80">
              <el-form-item>
                <div slot="label" style="color: #8c939d">主机名</div>
                <span>{{ props.row.host_name }}</span>
              </el-form-item>
              <el-form-item>
                <div slot="label" style="color: #8c939d">磁盘名</div>
                <span>{{ props.row.disk_name }}</span>
              </el-form-item>
              <el-form-item>
                <div slot="label" style="color: #8c939d">使用状态</div>
                <span>{{ props.row.is_used }}</span>
              </el-form-item>
              <el-form-item>
                <div slot="label" style="color: #8c939d">添加时间</div>
                <span>{{ props.row.add_time }}</span>
              </el-form-item>
              <el-form-item>
                <div slot="label" style="color: #8c939d">挂载参数</div>
                <span>{{ props.row.mount_params }}</span>
              </el-form-item>
            </el-form>
          </template>
        </el-table-column>
        <el-table-column prop="host_name" label="主机名" width="180"
                         :filters="hostnameFilters"
                         :filter-method="filterHostname"
                         filter-placement="bottom-end">
        </el-table-column>
        <el-table-column prop="disk_name" label="磁盘名" min-width="120"></el-table-column>
        <el-table-column prop="is_abnormal" label="磁盘状态" min-width="120">
          <template slot-scope="scope">
            <span v-if="scope.row.is_abnormal && scope.row.is_abnormal == 0"><i class="el-icon-success" style="color: #6ce26c"></i> 正常</span>
            <span v-else><i class="el-icon-error" style="color: #dd280d"></i> 异常</span>
          </template>
        </el-table-column>
        <el-table-column prop="is_mount" label="挂载状态" min-width="120">
          <template slot-scope="scope">
            <span v-if="scope.row.is_mount == 1"><i class="el-icon-success" style="color: #6ce26c"></i> 已挂载</span>
            <span v-else><i class="el-icon-error" style="color: #dd280d"></i> 未挂载</span>
          </template>
        </el-table-column>
        <el-table-column prop="mount_on" label="挂载点" min-width="150"></el-table-column>
        <el-table-column prop="system_type" label="文件系统" min-width="80"></el-table-column>
        <el-table-column prop="is_used" label="使用状态" min-width="150">
          <template slot-scope="scope">
            <span v-if="scope.row.is_used && scope.row.is_used.length !==0"><i class="el-icon-success" style="color: #6ce26c"></i> 已添加到{{scope.row.is_used.length}}个环</span>
            <span v-else><i class="el-icon-error" style="color: #dd280d"></i> 未添加到环</span>
          </template>
        </el-table-column>
        <el-table-column prop="label" label="标签" width="120"></el-table-column>
        <el-table-column label="操作" width="150">
          <template slot-scope="scope">
            <span v-if="scope.row.is_abnormal != 0">磁盘异常, 请检查</span>
            <span v-else>
              <el-button size="mini" type="primary" v-if="scope.row.is_mount != 1" @click="handleOperation('mount', scope.row)"><icon-svg icon-class="mount" /></el-button>
              <el-button size="mini" type="danger" v-else @click="handleOperation('umount',scope.row)"><icon-svg icon-class="umount" /></el-button>
            </span>
          </template>
        </el-table-column>
      </el-table>
    </el-row>

    <el-dialog title="批量操作" :visible.sync="dialogFormVisible"
               label-position="right" label-width="80px" :before-close="beforeClose">
      <el-form :model="operationData" :rules="rules" ref="operationForm">
        <el-form-item label="操作类型">
          <el-radio v-model="operationType" label="mount">批量挂载</el-radio>
          <el-radio v-model="operationType" label="umount">批量卸载</el-radio>
        </el-form-item>
        <el-form-item label="主机名" prop="host_name">
          <el-select v-model="operationData.host_name" placeholder="选择主机">
            <el-option v-for="host in hostnameList"
                       :key="host"
                       :label="host"
                       :value="host"></el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="beforeClose">取 消</el-button>
        <el-button type="primary" @click="handleBatchOperation" :loading="isLoading">确 定</el-button>
      </div>
    </el-dialog>

    <el-dialog
      title="提示"
      :visible.sync="batchOpeRstDVisible"
      width="30%"
      :close-on-press-escape=false
      :close-on-click-modal=false
      :show-close=false>
      <span>
        <loading-animation v-if="isWaiting" content="正在执行中。。。。"></loading-animation>
      </span>
      <span v-if="!isWaiting">执行结果: {{ cmd_result }}</span>
      <div slot="footer" class="dialog-footer">
        <el-button type="primary" @click="handleCloseDialog" :disabled="isWaiting">确 定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
  import { getDisks, mountDisks, umountDisks } from '@/api/cluster'
  import { mapGetters } from 'vuex'
  import LoadingAnimation  from '@/components/LoadingAnimation'

  export default {
    components: {
      LoadingAnimation
    },
    data() {
      return {
        diskList:[],
        hostnameFilters: [],
        hostnameList: [],
        dialogFormVisible: false,
        intervalTask: '',
        operationData: {
          host_name: '',
        },
        rules: {
          host_name: [
            { required: true, message: '请选择主机', trigger: 'change' }
          ],
        },
        tableLoading: false,
        operationType: 'mount',
        cmd_result: '',
        isLoading: false,
        batchOpeRstDVisible: false,
        isWaiting: false,
      }
    },
    computed: {
      ...mapGetters([
        'selectedCluster',
      ])
    },
    methods: {
      getClusterDisks(clustername){
        this.tableLoading = true
        getDisks(clustername).then(res=>{
          if(res.status ===200 && res.data.status === 200){
            this.diskList = res.data.data
            let tmp = ''
            this.hostnameFilters = []
            this.hostnameList = []
            for(let disk of this.diskList){
              if(disk.host_name !== tmp){
                this.hostnameList.push(disk.host_name)
                this.hostnameFilters.push({
                  text: disk.host_name,
                  value: disk.host_name,
                })
                tmp = disk.host_name
              }
            }
            this.tableLoading = false
          }
        }).catch(err=>{
          this.tableLoading = false
          console.log(err)
        })
      },
      mountDisk(data){
        this.isWaiting = true
        return new Promise((resolve, reject)=>{
          mountDisks(this.selectedCluster, data).then(res=>{
            this.isWaiting = false
            if(res.data.status === 200){
              if(data.disk_name) {
                this.showMsg(`挂载 ${data.host_name} 的 ${data.disk_name} 盘成功`, "success")
              }
              this.getClusterDisks(this.selectedCluster)
            }else{
              this.showMsg("挂载失败","success")
            }
            resolve(res)
          }).catch(err=>{
            this.isWaiting =false
            if(data.disk_name) {
              this.showMsg("挂载失败，请检查", "error")
            }
            reject('501')
          })
        })
      },
      umountDisk(data){
        this.isWaiting = true
        return new Promise((resolve, reject)=>{
          umountDisks(this.selectedCluster, data).then(res=>{
            this.isWaiting = false
            if(res.data.status === 200){
              if(data.disk_name){
                this.showMsg(`卸载${data.host_name} 的 ${data.disk_name} 盘成功`,"success")
              }
              this.getClusterDisks(this.selectedCluster)
            }else{
              this.showMsg("卸载失败","success")
            }
            resolve(res)
          }).catch(err=>{
            this.isWaiting = false
            if(data.disk_name){
              this.showMsg("卸载失败，请检查","error")
            }
            reject('501')
          })
        })
      },
      handleOperation(operation, row){
        this.$confirm(`是否${operation} ${row.host_name}  ${row.disk_name} ?`, '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          let data = {
            host_name: row.host_name,
            disk_name: row.disk_name
          }
          if(operation === 'mount'){
            this.mountDisk(data)
          }else if(operation === 'umount'){
            this.umountDisk(data)
          }
        }).catch((err) => {
          if(err !== '501'){
            this.$message({
              type: 'info',
              message: '已取消操作'
            });
          }
        });
      },
      filterHostname(value, row, column){
        const property = column['property'];
        return row[property] === value;
      },
      resetDialog(){
        this.operationData.host_name = ''
        this.operationType = 'mount'
      },
      batchOperation(){
        this.resetDialog()
        this.dialogFormVisible = true
      },
      beforeClose(){
        this.$refs['operationForm'].resetFields()
        this.dialogFormVisible = false;
      },
      handleBatchOperation(){
        this.$refs['operationForm'].validate((valid)=>{
          if(valid){
            this.isLoading = true
            this.dialogFormVisible = false
            this.batchOpeRstDVisible = true
            if(this.operationType === 'mount'){
              this.mountDisk(this.operationData).then(res=>{
                if(res.status === 200 && res.data.status === 200){
                  this.isLoading = false
                  this.cmd_result = res.data.message
                }
              }).catch(err=>{
                this.isLoading = false
              })
            }else if(this.operationType === 'umount'){
              this.umountDisk(this.operationData).then(res=>{
                if(res.status === 200 && res.data.status === 200){
                  this.isLoading = false
                  this.cmd_result = res.data.message
                }
              }).catch(err=>{
                this.isLoading = false
              })
            }
          }
        })
      },
      handleCloseDialog(){
        // this.getClusterDisks(this.selectedCluster)
        this.batchOpeRstDVisible = false
      },
      showMsg(msg, type) {
        this.$message({
          message: msg,
          type: type
        });
      },
    },
    created() {
      this.getClusterDisks(this.selectedCluster)
    },
    mounted() {
      // this.intervalTask = setInterval(()=>{
      //   this.getClusterDisks(this.selectedCluster)
      // }, 100000)
    },
    beforeDestroy() {
      // console.log('beforeDestroy')
      clearInterval(this.intervalTask)
    },
  }
</script>
<style rel="stylesheet/scss" lang="scss" scoped>
  .table-expand {
    font-size: 0;
  }
  .table-expand .el-form-item {
    margin-right: 0;
    margin-bottom: 0;
    width: 50%;
  }
</style>
