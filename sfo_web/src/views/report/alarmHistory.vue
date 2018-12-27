/**
* Create by 80003129 on 2018/10/12
*/
<template>
  <div>
    <el-row>
      <el-form :inline="true" :model="selectTime" style="float: right; margin: 15px">
        <el-form-item>
          <el-date-picker
            v-model="selectTime.time"
            type="datetimerange"
            :picker-options="pickerOptions"
            range-separator="-"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            align="right"
            @change="selectChange"
            :clearable="false">
          </el-date-picker>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="onSubmit"
                     :disabled="!selectTime.time || selectTime.time.length===0"
                     size="small">查询</el-button>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="clear"
                     :disabled="!selectTime.time || selectTime.time.length===0"
                     size="small">清空</el-button>
        </el-form-item>
      </el-form>
    </el-row>
    <el-row>
      <el-table :data="alarmRecord" style="width: 98%;margin: 0px auto" :border=true>
        <el-table-column prop="cluster_name" label="集群名" min-width="190"></el-table-column>
        <el-table-column label="告警主机(主机ip)" min-width="230">
          <template slot-scope="scope">
            <span>{{scope.row.alarm.hostname}}({{scope.row.ip}})</span>
          </template>
        </el-table-column>
        <el-table-column label="告警设备" min-width="180">
          <template slot-scope="scope">
            <span>{{scope.row.alarm.device_name}}</span>
          </template>
        </el-table-column>
        <el-table-column label="告警信息" min-width="380">
          <template slot-scope="scope">
            <span>{{scope.row.alarm.alarm_message}}</span>
          </template>
        </el-table-column>
        <el-table-column label="告警状态(最近)" width="130">
          <template slot-scope="scope">
            <span v-if="scope.row.alarm.alarm_result == 1">正常</span>
            <span v-else>异常</span>
          </template>
        </el-table-column>
        <el-table-column prop="warning_total" label="Warning(次数)" width="120" style="color:yellow"></el-table-column>
        <el-table-column prop="critical_total" label="Critical(次数)" width="120"></el-table-column>
        <el-table-column prop="total" label="total(次数)" width="100"></el-table-column>
      </el-table>
    </el-row>
    <el-row style="margin: 10px">
      <el-pagination
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        :current-page.sync="currentPage"
        :page-sizes="[10, 15, 20, 30]"
        :page-size="page_size"
        layout="total, sizes, prev, pager, next"
        :total="total"
        style="float: right">
      </el-pagination>
    </el-row>
  </div>
</template>

<script>
  import { getAlarmLogsHistory } from '@/api/log'
  import pickerOptions from '@/commons/pickerOptions'

  export default {
    data() {
      return {
        alarmRecord: [],
        selectTime: {
          time: [],
        },
        pickerOptions: pickerOptions,
        //分页相关
        currentPage: 1,
        total: 0,
        page_size: 10,
      }
    },
    methods: {
      getAlarmLogList(parmas){
        this.alarmRecord = []
        getAlarmLogsHistory(parmas).then(res=>{
          if(res.status === 200 && res.data.status === 200){
            this.total = res.data.data.alarm_total
            this.alarmRecord = res.data.data.alarms
          }
        }).catch(err=>{
          console.log(err)
        })
      },
      handleCurrentChange(page){
        this.currentPage = page
        let params = {
          page: this.currentPage,
          limit: this.page_size
        }
        if(this.selectTime.time.length !== 0){
          params.starttime = Date.parse(this.selectTime.time[0])/1000
          params.endtime = Date.parse(this.selectTime.time[1])/1000
        }
        this.getAlarmLogList(params)
      },
      handleSizeChange(size){
        this.page_size = size
        this.currentPage = 1
        let params = {
          page: this.currentPage,
          limit: this.page_size
        }
        if(this.selectTime.time.length !== 0){
          params.starttime = Date.parse(this.selectTime.time[0])/1000
          params.endtime = Date.parse(this.selectTime.time[1])/1000
        }
        this.getAlarmLogList(params)
      },
      selectChange(value){
        if(!value){
          this.getAlarmLogList()
        }
      },
      onSubmit(){
        this.page_size = 10
        this.currentPage = 1
        let params = {
          starttime: Date.parse(this.selectTime.time[0])/1000,
          endtime: Date.parse(this.selectTime.time[1])/1000
        }
        this.getAlarmLogList(params)
      },
      clear(){
        this.page_size = 10
        this.currentPage = 1
        this.selectTime.time = []
        this.getAlarmLogList()
      },
    },
    created() {
      this.getAlarmLogList()
    },
    mounted() {

    },
  }
</script>
<style rel="stylesheet/scss" lang="scss" scoped>
</style>
