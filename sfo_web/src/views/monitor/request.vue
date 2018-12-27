/**
* Create by wenboling on 2018/8/25
*/
<template>
  <el-row :gutter="5" style="margin: 9px">
    <el-card>
      <div slot="header" class="clearfix">
        <span>请求状态图</span>
      </div>
      <el-row>
        <div style="float: right">
          <el-form :inline="true" :model="selectTime" style="float: right">
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
              <el-button type="primary" @click="getHistoryData"
                         :disabled="!selectTime.time || selectTime.time.length===0" size="small">查询</el-button>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="clearHistoryData"
                         :disabled="!selectTime.time || selectTime.time.length===0" size="small">重置</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-row>
      <div style="text-align:center;width:100%;"  v-if="nodata"><span style="color: #00a0e9;font-size: large;">暂无数据</span></div>
      <div id="request-chart" style="width: 100%;height:378px;"></div>
    </el-card>
  </el-row>
</template>

<script>
  import { mapGetters } from 'vuex'
  import { getRequestStats } from '@/api/dashboard'
  import echarts from 'echarts'
  import pickerOptions from '@/commons/pickerOptions'
  export default {
    computed: {
      ...mapGetters([
        'name',
        'roles',
        'selectedCluster'
      ])
    },
    data() {
      return {
        requestSummary: {},
        requestChart: null,
        intervalTask: '',
        pickerOptions: pickerOptions,
        selectTime: {
          time: []
        },
        nodata: true,
        value: '',
        starttime: null,
        endtime: null,
      }
    },
    methods: {
      getRequestData(cluster_name, params){
        getRequestStats(cluster_name,params).then(res=>{
          if(res.data.status === 200 && res.status === 200) {
            this.nodata = false
            this.initrequestData(res.data.data)
          }else {
            this.requestChart.clear()
            this.nodata = true
          }
        }).catch(err=>{
          this.requestChart.clear()
          this.nodata = true
        })
      },
      // opstimeChange(){},
      initrequestData(data){
        this.requestSummary.add_times = data.add_times
        if(data.request_stats.HEAD){
          this.requestSummary.HEAD = data.request_stats.HEAD.map(item=>{
            return Math.round(item)
          })
        }
        if(data.request_stats.GET){
          this.requestSummary.GET = data.request_stats.GET.map(item=>{
            return Math.round(item)
          })
        }
        if(data.request_stats.POST){
          this.requestSummary.POST = data.request_stats.POST.map(item=>{
            return Math.round(item)
          })
        }
        if(data.request_stats.PUT){
          this.requestSummary.PUT = data.request_stats.PUT.map(item=>{
            return Math.round(item)
          })
        }
        if(data.request_stats.DELETE){
          this.requestSummary.DELETE = data.request_stats.DELETE.map(item=>{
            return Math.round(item)
          })
        }
        if(data.request_stats.COPY){
          this.requestSummary.COPY = data.request_stats.COPY.map(item=>{
            return Math.round(item)
          })
        }
        // console.log(this.requestSummary)
        this.initrequestChart(this.requestSummary)
      },

      initrequestChart(data){
        this.requestChart = echarts.getInstanceByDom(document.getElementById('request-chart'))
        if(this.requestChart === undefined) {
          this.requestChart = echarts.init(document.getElementById('request-chart'))
        }
        this.requestChart.setOption({
          legend: {
            show: true,
            data: ['HEAD', 'GET', 'POST', 'PUT', 'DELETE', 'COPY'],
            top: 'bottom'
          },
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              lineStyle: {
                color: '#57617B'
              }
            }
          },
          toolbox: {
            show: true,
            itemSize: 20,
            feature: {
              dataZoom: {
                show: true,
                title: {
                  zoom: '选择缩放区域',
                  back: '返回上一次缩放状态',
                },
              },
              restore: {
                show: true,
                title: '取消缩放'
              },
            }
          },
          xAxis: {
            type: 'category',
            boundaryGap: false,
            name: '时间',
            data: data.add_times
          },
          yAxis: [{
            name: '请求数',
            type: 'value'
          }],
          series: [{
            name: 'HEAD',
            type: 'line',
            data: data.HEAD,
            smooth: true
          },{
            name: 'GET',
            type: 'line',
            data: data.GET,
            smooth: true
          },{
            name: 'POST',
            type: 'line',
            data: data.POST,
            smooth: true
          },{
            name: 'PUT',
            type: 'line',
            data: data.PUT,
            smooth: true
          },{
            name: 'DELETE',
            type: 'line',
            data: data.DELETE,
            smooth: true
          },{
            name: 'COPY',
            type: 'line',
            data: data.COPY,
            smooth: true
          }]
        })
      },
      selectChange(value){
        if(!value){
          this.timerFunction()
        }
      },
      getHistoryData(){
        clearTimeout(this.intervalTask)
        let params = {
          starttime: Date.parse(this.selectTime.time[0])/1000,
          endtime: Date.parse(this.selectTime.time[1])/1000
        }
        this.getRequestData(this.selectedCluster, params)
      },
      clearHistoryData(){
        this.selectTime.time = []
        this.timerFunction()
      },
      timerFunction(){
        this.getRequestData(this.selectedCluster)
        this.intervalTask = setTimeout(this.timerFunction, 20000)
      }
    },
    created() {

    },
    mounted() {
      this.requestChart = echarts.init(document.getElementById('request-chart'))
      setTimeout(() => {
        window.onresize = (() => {
          if(this.requestChart){
            this.requestChart.resize()
          }
        })
      }, 500)
      this.timerFunction()
    },
    beforeDestroy() {
      clearInterval(this.intervalTask)
      if(this.requestChart){
        this.requestChart.dispose()
      }
    },
  }
</script>
<style rel="stylesheet/scss" lang="scss" scoped>
</style>
