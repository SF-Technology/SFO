<template>
  <div>
    <badge :value="critical.num" class="item">
      <el-button type="danger" icon="el-icon-error" size="mini" @click="alarm_click('critical')"></el-button>
    </badge>
    <badge :value="warning.num" class="item">
      <el-button type="warning" icon="el-icon-warning" size="mini" @click="alarm_click('warning')"></el-button>
    </badge>

    <el-dialog :title="titleMap[listType]" :visible.sync="dialogTableVisible" width="85%">
      <el-table :data="dataList" style="width: 100%;margin-top: -50px" max-height="450" :default-sort = "{prop: 'add_time', order: 'descending'}">
        <el-table-column prop="alarm_host" label="告警主机" width="150"></el-table-column>
        <el-table-column prop="ip" label="主机IP" width="120"></el-table-column>
        <el-table-column prop="cluster_name" label="告警集群" width="180"></el-table-column>
        <el-table-column prop="alarm_device" label="告警设备" width="140"></el-table-column>
        <el-table-column prop="alarm_level" label="等级" width="80"></el-table-column>
        <el-table-column prop="alarm_message" label="告警内容"></el-table-column>
        <el-table-column prop="add_time" label="告警时间" width="160"></el-table-column>
        <el-table-column label="操作" width="80">
          <template slot-scope="scope">
            <!--<el-button type="danger" icon="el-icon-search" @click="clearAlarm(scope.row)"></el-button>-->
            <i class="el-icon-delete" style="color: red; cursor: pointer;" @click="clearAlarm(scope.row)"></i>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script>
  import Badge from '@/components/Badge'
  import { updateAlarm } from '@/api/alarm'
  import { mapGetters } from 'vuex'
  export default {
    name: "warning-bar",
    components:{
      Badge
    },
    data() {
      return{
        titleMap:{
          critical: "严重告警列表",
          warning: "警告列表",
          info: "信息列表",
        },
        listType: "",
        dialogTableVisible: false,
        dataList: [{}],
        isDeletedGuid: '',
      }
    },
    computed: {
      ...mapGetters([
        'alarm_detail'
      ]),
      critical(){
        let num = 0, critical_list = []
        if(this.alarm_detail.critical){
          num = this.alarm_detail.critical.critical_total
          critical_list = this.alarm_detail.critical.alarms
        }
        return {
          num: num,
          critical_list: critical_list
        }
      },
      warning(){
        let num = 0, warn_list = []
        if(this.alarm_detail.warning){
          num = this.alarm_detail.warning.warning_total
          warn_list = this.alarm_detail.warning.alarms
        }
        return {
          num: num,
          warn_list: warn_list
        }
      },
    },
    methods:{
      alarm_click(type){
        this.dataList = []
        if(type==="critical"){
          this.dataList = this.critical.critical_list
        }else if(type==="warning"){
          this.dataList = this.warning.warn_list
        }
        let index = this.dataList.findIndex(item=>{
          return item.alarm_guid === this.isDeletedGuid
        })
        if(index > -1){
          this.dataList.splice(index, 1)
        }
        this.listType = type
        this.dialogTableVisible = true
      },
      updateAlarmStatus(guid){
        updateAlarm(guid).then(res=>{
          if(res.data.status === 201){
            this.showMsg("处理成功, 列表将稍后刷新", "success")
            this.isDeletedGuid = guid
            this.dialogTableVisible = false
          }else{
            this.showMsg("处理失败", "error")
          }
        }).catch(err=>{
          this.showMsg("处理失败", "error")
          console.log(err)
        })
      },
      clearAlarm(row){
        this.$confirm('确定该条告警信息可以被清除?', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          this.updateAlarmStatus(row.alarm_guid)
        }).catch((err) => {
          this.$message({
            type: 'info',
            message: `已取消操作${err}`
          });
        });
      },
      showMsg(msg, type) {
        this.$message({
          message: msg,
          type: type
        });
      }
    },
    sockets:{
      connect: function(){
        // console.log('socket connected')
      },
    },
    mounted() {
      // this.$socket.emit('mounted', 'mounted');
    },
  }
</script>

<style>
  .item {
    margin-right: 13px;
  }
</style>
