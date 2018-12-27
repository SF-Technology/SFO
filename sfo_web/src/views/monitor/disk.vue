/**
* Create by wenboling on 2018/8/17
*/
<template>
  <div>
    <el-row :gutter="10" style="margin: 10px;">
      <el-card>
        <div slot="header" class="clearfix">
          <span>磁盘信息</span>
        </div>
        <el-row>
          <label style="width: 10rem;">磁盘总数:</label>
          <span class="_span">{{ disk_total_num }}</span>
          <label style="width: 10rem;">总容量:</label>
          <span class="_span"> {{ capacity_total.disk_total | formatterBytes(1024) }}</span>
          <label>已用</label>
          <span class="_span">{{ capacity_total.disk_used | formatterBytes(1024) }}</span>
          <label>可用</label>
          <span class="_span">{{ capacity_total.disk_free | formatterBytes(1024) }}</span>
        </el-row>
        <el-row>
          <el-table :data="diskInfoTable" :max-height="350" style="width: 100%; margin-top: 10px">
            <el-table-column prop="host_name" label="主机名" min-width="130">
            </el-table-column>
            <el-table-column prop="disk_name" label="磁盘名" min-width="90">
            </el-table-column>
            <el-table-column prop="disk_total" label="容量" min-width="110">
              <template slot-scope="scope">
                <span>{{ scope.row.disk_total | formatterBytes(1024) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="disk_used" label="已用" min-width="110">
              <template slot-scope="scope">
                <span>{{ scope.row.disk_used | formatterBytes(1024) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="disk_percent" label="使用率" sortable>
              <template slot-scope="scope">
                <el-progress v-if="parseFloat(scope.row.disk_percent) >= 80" :text-inside="true" :stroke-width="16" :percentage="parseFloat(scope.row.disk_percent)" status="exception"></el-progress>
                <el-progress v-else-if="scope.row.disk_percent == 100.0" :text-inside="true" :stroke-width="16" :percentage="100" status="exception"></el-progress>
                <el-progress v-else :text-inside="true" :stroke-width="16" :percentage="parseFloat(scope.row.disk_percent)" status="success"></el-progress>
              </template>
            </el-table-column>
          </el-table>
        </el-row>
      </el-card>
    </el-row>
  </div>
</template>

<script>
  import { mapGetters } from 'vuex'
  import echarts from 'echarts'
  import { getOverview, getClusterIOPS, getDiskList, gethosts, getDiskPerformanceDetail,
    diskReadIOPSImageAPI, diskWriteIOPSImageAPI, diskReadmbpsImageAPI, diskWritembpsImageAPI, diskAwaitImageAPI } from '@/api/monitor'
  import { formatterBytes } from '@/utils'
  import pickerOptions from '@/commons/pickerOptions'

  export default {
    computed: {
      ...mapGetters([
        'selectedCluster'
      ]),
      read_iops_img_src(){
        return `${diskReadIOPSImageAPI(this.selectedCluster)}${this.timestamp}`
      },
      write_iops_img_src(){
        return `${diskWriteIOPSImageAPI(this.selectedCluster)}${this.timestamp}`
      },
      read_mbps_img_src(){
        return `${diskReadmbpsImageAPI(this.selectedCluster)}${this.timestamp}`
      },
      write_mbps_img_src(){
        return `${diskWritembpsImageAPI(this.selectedCluster)}${this.timestamp}`
      },
      await_img_src(){
        return `${diskAwaitImageAPI(this.selectedCluster)}${this.timestamp}`
      },
    },
    data() {
      return {
        iopsChart: null,
        capacity_total: {
          disk_total: '',
          disk_used: '',
          disk_free: '',
        },
        disk_total_num: '',
        diskInfoTable: [],
        intervalTask: null,
        timestamp: null,
        pickerOptions: pickerOptions,
        queryData: {
          start_time: null,
          end_time: null,
        },
        selectTime: {
          time: [],
        },
        activeNames: 'read_iops',
      }
    },
    methods: {
      getOverViewData(clustername) {
        getOverview(clustername).then(response => {
          if (response.status === 200 && response.data.status === 200) {
            let data = response.data.data
            this.capacity_total = data.capacity_total
          }
        }).catch(err => {
          console.log(err)
        })
      },
      getDisks(clustername){
        getDiskList(clustername).then(response => {
          if (response.status === 200 && response.data.status === 200) {
            let data = response.data.data
            this.diskInfoTable = []
            this.diskInfoTable = data
            this.disk_total_num = response.data.disk_num_total
          }
        }).catch(err => {
          console.log(err)
        })
      },
      getTimestamp(){
        if(this.queryData.start_time && this.queryData.end_time) {
          this.timestamp = `${this.queryData.start_time}\&end=${this.queryData.end_time}`
        }else{
          let start = Date.parse(new Date())/1000 - 1800,
            end = Date.parse(new Date())/1000
          this.timestamp = `${start}\&end=${end}`
        }
      },
      selectChange(value){
        if(!value){
          this.clear()
        }
      },
      onSubmit(){
        this.queryData.start_time = Date.parse(this.selectTime.time[0])/1000
        this.queryData.end_time = Date.parse(this.selectTime.time[1])/1000
        this.timestamp = `${this.queryData.start_time}\&end=${this.queryData.end_time}`
      },
      clear(){
        this.selectTime.time = []
        this.queryData.start_time = null
        this.queryData.end_time = null
        let start = Date.parse(new Date())/1000 - 1800,
          end = Date.parse(new Date())/1000
        this.timestamp = `${start}\&end=${end}`
      },
      timeFunction(){
        this.getOverViewData(this.selectedCluster)
        this.getTimestamp()
        this.getDisks(this.selectedCluster)
        this.intervalTask = setTimeout(this.timeFunction, 60000)
      },
    },
    created() {
    },
    mounted() {
      this.timeFunction()
    },
    beforeDestroy() {
      clearTimeout(this.intervalTask)
    },
  }
</script>
<style rel="stylesheet/scss" lang="scss" scoped>
  ._span {
    color: #00a0e9;
    padding-right: 5px;
    font-size: 1.2rem;
  }
</style>
