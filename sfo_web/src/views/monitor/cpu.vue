/**
* Create by wenboling on 2018/8/17
*/
<template>
  <div>
    <el-row :gutter="10" style="margin: 10px;">
      <el-card>
        <div slot="header">
          <span>集群CPU使用率</span>
        </div>
        <el-row>
          <div style="float: right">
            <el-form :inline="true" :model="selectTime.dynamicPic" style="float: right">
              <el-form-item>
                <el-date-picker
                  v-model="selectTime.dynamicPic.time"
                  type="datetimerange"
                  :picker-options="pickerOptions"
                  range-separator="-"
                  start-placeholder="开始时间"
                  end-placeholder="结束时间"
                  align="right"
                  @change="selectChange_1"
                  :clearable="false">
                </el-date-picker>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="getHistoryData"
                           :disabled="!selectTime.dynamicPic.time || selectTime.dynamicPic.time.length===0"
                           size="small">查询</el-button>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="clearHistoryData"
                           :disabled="!selectTime.dynamicPic.time || selectTime.dynamicPic.time.length===0"
                           size="small">重置</el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-row>
        <div style="text-align:center;width:100%;"  v-if="nodata">
          <span style="color: #00a0e9;font-size: large;">暂无数据</span>
        </div>
        <div id="cpu-Usage-Chart" style="width: 100%;height: 300px"></div>
      </el-card>
    </el-row>
  </div>
</template>

<script>
  import { mapGetters } from 'vuex'
  import echarts from 'echarts'
  import { getCPUOverview, cpuImageAPI } from '@/api/monitor'
  import { formatterBytes } from '@/utils'
  import pickerOptions from '@/commons/pickerOptions'

  export default {
    computed: {
      ...mapGetters([
        'selectedCluster'
      ]),
      img_src(){
        return `${cpuImageAPI(this.selectedCluster)}${this.timestamp}`
      }
    },
    data() {
      return {
        cpuUsageChart: null,
        cpuUsageData: {},
        intervalTask_1: null,
        intervalTask_2: null,
        nodata: true,
        timestamp: '',
        pickerOptions: pickerOptions,
        queryData: {
          start_time: null,
          end_time: null,
        },
        selectTime: {
          dynamicPic: {
            time: [],
          },
          staticPic: {
            time: [],
          }
        },
      }
    },
    methods: {
      getCPUData(clustername, params){
        getCPUOverview(clustername, params).then(res=>{
          if(res.status === 200 &&res.data.status === 200){
            this.nodata = false
            this.cpuUsageData = res.data.data.cpu_frequency_val
            this.initCpuUsageChart(this.cpuUsageData)
          }
        }).catch(err=>{
          this.cpuUsageChart.clear()
          this.nodata = true
        })
      },
      initCpuUsageChart(data) {
        this.cpuUsageChart = echarts.getInstanceByDom(document.getElementById('cpu-Usage-Chart'))
        if(this.cpuUsageChart === undefined){
          this.cpuUsageChart = echarts.init(document.getElementById('cpu-Usage-Chart'))
        }
        let options = {
          xAxis: {
            type: 'category',
            data: data.add_time,
            boundaryGap: false,
          },
          yAxis: {
            type: 'value',
            name: '单位：%',
          },
          tooltip: {
            trigger: 'axis'
          },
          series: [{
            data: data.cpu_frq,
            type: 'line',
            smooth: true,
            itemStyle:{
              color: '#1E90FF',
            },
            areaStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [{
                  offset: 0, color: '#1E90FF' // 0% 处的颜色
                }, {
                  offset: 1, color: '#00FFFF' // 100% 处的颜色
                }],
                globalCoord: false // 缺省为 false
              }
            }
          }]
        }
        this.cpuUsageChart.setOption(options)
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
      onSubmit(){
        this.queryData.start_time = Date.parse(this.selectTime.staticPic.time[0])/1000
        this.queryData.end_time = Date.parse(this.selectTime.staticPic.time[1])/1000
        this.timestamp = `${this.queryData.start_time}\&end=${this.queryData.end_time}`
      },
      clear(){
        this.selectTime.staticPic.time = []
        this.queryData.start_time = null
        this.queryData.end_time = null
        let start = Date.parse(new Date())/1000 - 1800,
          end = Date.parse(new Date())/1000
        this.timestamp = `${start}\&end=${end}`
      },
      selectChange_1(value){
        if(!value){
          this.timeFunction_1()
        }
      },
      selectChange_2(value){
        if(!value){
          this.timeFunction_2()
        }
      },
      getHistoryData(){
        clearTimeout(this.intervalTask_1)
        let params = {
          starttime: Date.parse(this.selectTime.dynamicPic.time[0])/1000,
          endtime: Date.parse(this.selectTime.dynamicPic.time[1])/1000
        }
        this.getCPUData(this.selectedCluster, params)
      },
      clearHistoryData(){
        this.selectTime.dynamicPic.time = []
        this.timeFunction_1()
      },
      timeFunction_1(){
        this.getCPUData(this.selectedCluster)
        this.intervalTask_1 = setTimeout(this.timeFunction_1, 60000)
      },
      timeFunction_2(){
        this.getTimestamp()
        this.intervalTask_2 = setTimeout(this.timeFunction_2, 60000)
      }
    },
    created() {

    },
    mounted() {
      this.cpuUsageChart = echarts.init(document.getElementById('cpu-Usage-Chart'))
      this.timeFunction_1()
      this.timeFunction_2()
      setTimeout(() => {
        window.onresize = (() => {
          if(this.cpuUsageChart){
            this.cpuUsageChart.resize()
          }
        })
      }, 500)
    },
    beforeDestroy() {
      // console.log('beforeDestroy')
      clearTimeout(this.intervalTask_1)
      clearTimeout(this.intervalTask_2)
      if(this.cpuUsageChart){
        this.cpuUsageChart.dispose()
      }
    },
  }
</script>
<style rel="stylesheet/scss" lang="scss" scoped>
</style>
