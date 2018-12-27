/**
* Create by wenboling on 2018/8/17
*/
<template>
  <div>
    <el-row style="margin: 10px">
      <el-card>
        <div slot="header" class="clearfix">
          <span>async-pending-status</span>
        </div>
        <el-row>
          <el-form :inline="true" :model="selectTime.async" style="float: right">
            <el-form-item>
              <el-date-picker
                v-model="selectTime.async.time"
                type="datetimerange"
                :picker-options="pickerOptions"
                range-separator="-"
                start-placeholder="开始时间"
                end-placeholder="结束时间"
                align="right"
                @change="selectChange_async"
                :clearable="false">
              </el-date-picker>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="getHistoryData('async')"
                         :disabled="!selectTime.async.time || selectTime.async.time.length===0" size="small">查询</el-button>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="clearHistoryData('async')"
                         :disabled="!selectTime.async.time || selectTime.async.time.length===0" size="small">重置</el-button>
            </el-form-item>
          </el-form>
        </el-row>
        <div style="text-align:center;width:100%;"  v-if="no_async_pending_data">
          <span style="color: #00a0e9;font-size: large;">暂无数据</span>
        </div>
        <div id="async-pending-chart" style="width: 100%;height:378px;"></div>
      </el-card>
    </el-row>
    <el-row style="margin: 10px">
      <el-card>
        <div slot="header" class="clearfix">
          <span>集群响应时间</span>
        </div>
        <div style="text-align:center;width:100%;"  v-if="no_tps_data">
          <span style="color: #00a0e9;font-size: large;">暂无数据</span>
        </div>
        <div id="svt-chart" style="width: 100%;height:378px;"></div>
      </el-card>
    </el-row>
    <el-row style="margin: 10px">
      <el-col :span="24">
        <el-card style="height: 100%">
          <div slot="header" class="clearfix">
            <span>集群吞吐</span>
          </div>
          <el-row>
            <el-form :inline="true" :model="selectTime.iops" style="float: right">
              <el-form-item>
                <el-date-picker
                  v-model="selectTime.iops.time"
                  type="datetimerange"
                  :picker-options="pickerOptions"
                  range-separator="-"
                  start-placeholder="开始时间"
                  end-placeholder="结束时间"
                  align="right"
                  @change="selectChange_iops"
                  :clearable="false">
                </el-date-picker>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="getHistoryData('iops')"
                           :disabled="!selectTime.iops.time || selectTime.iops.time.length===0" size="small">查询</el-button>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="clearHistoryData('iops')"
                           :disabled="!selectTime.iops.time || selectTime.iops.time.length===0" size="small">重置</el-button>
              </el-form-item>
            </el-form>
          </el-row>
          <el-row>
            <div style="text-align:center;width:100%;"  v-if="no_proxy_data">
              <span style="color: #00a0e9;font-size: large;">暂无proxy-server的吞吐数据</span>
            </div>
            <div id="proxy-throughout-chart" style="width: 100%;height: 320px"></div>
          </el-row>
          <el-row>
            <div style="text-align:center;width:100%;"  v-if="no_storage_data">
              <span style="color: #00a0e9;font-size: large;">暂无storage-server的吞吐数据</span>
            </div>
            <div id="storage-throughout-chart" style="width: 100%;height: 320px"></div>
          </el-row>
        </el-card>
      </el-col>
    </el-row>
    <el-row :gutter="10" style="margin: 5px">
      <el-col :span="8">
        <el-card>
          <div slot="header" class="clearfix">
            <span>account</span>
          </div>
          <div class="ACO">
            <div>
              <el-tag size="small">auditor</el-tag><br/>
              <label>passed: </label>
              <span>{{auditor.account_audits_passed }}</span><br/>
              <label>errors: </label>
              <span>{{auditor.account_audits_failed }}</span><br/><br/>
            </div>
            <div>
              <br />
              <el-tag size="small">replicator</el-tag><br/>
              <label>no_change: </label>
              <span>{{ replicator.account_replication_no_change }}</span><br/>
              <label>success: </label>
              <span>{{ replicator.account_replication_success }}</span><br/>
              <label>failure: </label>
              <span>{{ replicator.account_replication_failure }}</span><br/>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <div slot="header" class="clearfix">
            <span>container</span>
          </div>
          <div class="ACO">
            <div>
              <el-tag size="small">auditor</el-tag><br />
              <label>passed: </label>
              <span>{{auditor.container_audits_passed }}</span><br/>
              <label>errors: </label>
              <span>{{auditor.container_audits_failed }}</span><br/><br />
            </div>
            <div>
              <br />
              <el-tag size="small">replicator</el-tag><br/>
              <label>no_change: </label>
              <span>{{ replicator.container_replication_no_change }}</span><br/>
              <label>success: </label>
              <span>{{ replicator.container_replication_success }}</span><br/>
              <label>failure: </label>
              <span>{{ replicator.container_replication_failure }}</span><br/>
            </div>
            <div>
              <br />
              <el-tag size="small">updater</el-tag><br />
              <label>sweep: </label>
              <span>{{ updater.container_updater_sweep.toFixed(2) }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <div slot="header" class="clearfix">
            <span>object</span>
          </div>
          <div class="ACO">
            <div>
              <el-tag size="small">auditor</el-tag><br />
              <label>passed: </label>
              <span>{{auditor.object_auditor_passed }}</span><br/>
              <label>errors: </label>
              <span>{{auditor.object_auditor_errors }}</span><br/>
              <label>quarantined: </label>
              <span>{{auditor.object_auditor_quarantined }}</span><br/>
            </div>
            <div>
              <br />
              <el-tag size="small">replicator</el-tag><br/>
              <label>remove: </label>
              <span>{{ replicator.object_replication_remove }}</span><br/>
              <label>success: </label>
              <span>{{ replicator.object_replication_success }}</span><br/>
              <label>failure: </label>
              <span>{{ replicator.object_replication_failure }}</span><br/>
            </div>
            <div>
              <br />
              <el-tag size="small">updater</el-tag><br />
              <label>sweep: </label>
              <span>{{ updater.object_updater_sweep.toFixed(2) }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    <el-row :gutter="10" style="margin: 10px;">
      <el-col :span="24">
        <el-card>
          <div slot="header" class="clearfix">
            <span>复制器状态</span>
          </div>
          <el-row>
            <span class="rep-title">object-replicator</span>
            <el-table :max-height="320" :data="replicatorTable" :border="true" style="margin-top: 3px">
              <el-table-column prop="host_name" label="主机名" width="130" fixed></el-table-column>
              <el-table-column prop="object_replication.replication_last" label="结束时间" width="180">
                <template slot-scope="scope">
                  <span>{{ scope.row.account_replication.replication_last | formatTime }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="object_replication.replication_time" label="所用时间" width="100">
                <template slot-scope="scope">
                  <span v-if="scope.row.object_replication.replication_time">{{ scope.row.object_replication.replication_time.toFixed(3) }}</span>
                  <span v-else>N/A</span>
                </template>
              </el-table-column>
              <el-table-column prop="object_replication.replication_stats.rsync" label="rsync" min-width="80"></el-table-column>
              <el-table-column prop="object_replication.replication_stats.attempted" label="attempted" min-width="110"></el-table-column>
              <el-table-column prop="object_replication.replication_stats.success" label="success" min-width="100"></el-table-column>
              <el-table-column prop="object_replication.replication_stats.failure" label="failure" min-width="100"></el-table-column>
              <el-table-column prop="object_replication.replication_stats.remove" label="remove" min-width="100"></el-table-column>
              <el-table-column prop="object_replication.replication_stats.hashmatch" label="hashmatch" min-width="120"></el-table-column>
            </el-table>
          </el-row>
          <el-row style="margin-top: 10px">
            <span class="rep-title">container-replicator</span>
            <el-table :max-height="320" :data="replicatorTable" :border="true" style="margin-top: 3px">
              <el-table-column prop="host_name" label="主机名" width="130" fixed></el-table-column>
              <el-table-column prop="container_replication.replication_last" label="结束时间" width="180">
                <template slot-scope="scope">
                  <span>{{ scope.row.container_replication.replication_last | formatTime }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="container_replication.replication_time" label="所用时间" width="100">
                <template slot-scope="scope">
                  <span v-if="scope.row.container_replication.replication_time">{{ scope.row.container_replication.replication_time.toFixed(3) }}</span>
                  <span v-else>N/A</span>
                </template>
              </el-table-column>
              <el-table-column prop="container_replication.replication_stats.no_change" label="nochange" min-width="100"></el-table-column>
              <el-table-column prop="container_replication.replication_stats.rsync" label="rsync" min-width="70"></el-table-column>
              <el-table-column prop="container_replication.replication_stats.attempted" label="attempted" min-width="90"></el-table-column>
              <el-table-column prop="container_replication.replication_stats.success" label="success" min-width="90"></el-table-column>
              <el-table-column prop="container_replication.replication_stats.failure" label="failure" min-width="90"></el-table-column>
              <el-table-column prop="container_replication.replication_stats.ts_repl" label="ts_repl" min-width="90"></el-table-column>
              <el-table-column prop="container_replication.replication_stats.remove" label="remove" min-width="90"></el-table-column>
              <el-table-column prop="container_replication.replication_stats.remote_merge" label="remote_merge" min-width="130"></el-table-column>
              <el-table-column prop="container_replication.replication_stats.diff_capped" label="diff_capped" min-width="120"></el-table-column>
              <el-table-column prop="container_replication.replication_stats.hashmatch" label="hashmatch" min-width="110"></el-table-column>
              <el-table-column prop="container_replication.replication_stats.empty" label="empty" min-width="90"></el-table-column>
              <el-table-column prop="container_replication.replication_stats.diff" label="diff" min-width="90"></el-table-column>
            </el-table>
          </el-row>
          <el-row style="margin-top: 10px">
            <span class="rep-title">account-replicator</span>
            <el-table :max-height="320" :data="replicatorTable" :border="true" style="margin-top: 3px">
              <el-table-column prop="host_name" label="主机名" width="130" fixed></el-table-column>
              <el-table-column prop="account_replication.replication_last" label="结束时间" width="180">
                <template slot-scope="scope">
                  <span>{{ scope.row.account_replication.replication_last | formatTime }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="account_replication.replication_time" label="所用时间" width="100">
                <template slot-scope="scope">
                  <span v-if="scope.row.account_replication.replication_time">{{ scope.row.account_replication.replication_time.toFixed(3) }}</span>
                  <span v-else>N/A</span>
                </template>
              </el-table-column>
              <el-table-column prop="account_replication.replication_stats.no_change" label="nochange" min-width="110"></el-table-column>
              <el-table-column prop="account_replication.replication_stats.rsync" label="rsync" min-width="70"></el-table-column>
              <el-table-column prop="account_replication.replication_stats.attempted" label="attempted" min-width="100"></el-table-column>
              <el-table-column prop="account_replication.replication_stats.success" label="success" min-width="90"></el-table-column>
              <el-table-column prop="account_replication.replication_stats.failure" label="failure" min-width="90"></el-table-column>
              <el-table-column prop="account_replication.replication_stats.ts_repl" label="ts_repl" min-width="90"></el-table-column>
              <el-table-column prop="account_replication.replication_stats.remove" label="remove" min-width="90"></el-table-column>
              <el-table-column prop="account_replication.replication_stats.remote_merge" label="remote_merge" min-width="130"></el-table-column>
              <el-table-column prop="account_replication.replication_stats.diff_capped" label="diff_capped" min-width="120"></el-table-column>
              <el-table-column prop="account_replication.replication_stats.hashmatch" label="hashmatch" min-width="110"></el-table-column>
              <el-table-column prop="account_replication.replication_stats.empty" label="empty" min-width="90"></el-table-column>
              <el-table-column prop="account_replication.replication_stats.diff" label="diff" min-width="90"></el-table-column>
            </el-table>
          </el-row>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
  import { mapGetters } from 'vuex'
  import echarts from 'echarts'
  import { getStorageOverview, getProxyOverview, getNodePerformance, getAsyncStatus, getSVTStatus } from '@/api/monitor'
  import { formatterBytes } from '@/utils'
  import pickerOptions from '@/commons/pickerOptions'

  export default {
    computed: {
      ...mapGetters([
        'selectedCluster'
      ])
    },
    data() {
      return {
        svtChart: null,
        proxyThroughoutChart: null,
        storageThroughoutChart: null,
        asyncChart: null,
        replicatorTable: [],
        intervalTask: null,
        intervalGetAsync: null,
        intervalGetSVT: null,
        intervalGetIOPS: null,
        svtData: {},
        swiftACOInfo: {},
        cluster_condition: {},
        auditor: {},
        replicator: {},
        updater: {
          container_updater_sweep: 0.00,
          object_updater_sweep: 0.00
        },
        no_async_pending_data: true,
        no_proxy_data: true,
        no_storage_data: true,
        no_tps_data: true,

        //历史数据相关
        pickerOptions: pickerOptions,
        selectTime: {
          async: {
            time: [],
          },
          iops: {
            time: []
          }
        },
      }
    },
    methods: {
      getNodePer(clustername){
        getNodePerformance(clustername).then(response => {
          if(response.status === 200 && response.data.status === 200){
            let data = response.data.data
            this.replicatorTable = []
            this.replicatorTable = data
          }
        }).catch(err=>{
          console.log(err)
        })
      },
      getClusterSvt(clustername, params){
        getSVTStatus(clustername, params).then(res=>{
          if(res.status === 200 && res.data.status){
            this.no_tps_data = false
            this.svtData = res.data.data
            this.initsvtChart(this.svtData)
          }
        }).catch(err=>{
          this.no_tps_data = true
          this.svtChart.clear()
        })
      },
      getStorageData(clustername, params){
        getStorageOverview(clustername, params).then(res=>{
          if(res.status === 200 &&res.data.status === 200){
            this.no_storage_data = false
            this.storageThroughoutData = res.data.data.storage
            this.initStorageThroughoutChart(this.storageThroughoutData)
          }
        }).catch(err=>{
          this.no_storage_data = true
          this.storageThroughoutChart.clear()
        })
      },
      getProxyData(clustername, params){
        getProxyOverview(clustername, params).then(res=>{
          if(res.status === 200 &&res.data.status === 200){
            this.no_proxy_data = false
            this.proxyThroughoutData = res.data.data.proxy
            this.initProxyThroughoutChart(this.proxyThroughoutData)
          }
        }).catch(err=>{
          this.no_proxy_data = true
          this.proxyThroughoutChart.clear()
        })
      },
      getSwiftStatus(clustername, params){
        getAsyncStatus(clustername, params).then(res=>{
          this.no_async_pending_data = false
          let data = res.data.data
          this.cluster_condition = {}
          this.cluster_condition = data.cluster_condition
          this.initClusterConditionData(this.cluster_condition)
          this.initsyncData(data.add_time_list, data.sync_num_list)
        }).catch(()=>{
          this.no_async_pending_data = true
          this.asyncChart.clear()
        })
      },
      initClusterConditionData(data) {
        this.auditor = data.auditor_queue
        this.replicator = data.replicate_num
        this.updater = data.update_num
      },
      initsyncData(xaxis, data) {
        this.sync = {}
        this.sync.xAxis = xaxis
        this.sync.num = data
        this.initsyncChart(this.sync)
      },
      initsyncChart(data) {
        this.asyncChart = echarts.getInstanceByDom(document.getElementById('async-pending-chart'))
        if(this.asyncChart === undefined) {
          this.asyncChart = echarts.init(document.getElementById('async-pending-chart'))
        }
        this.asyncChart.setOption({
          xAxis: {
            type: 'category',
            boundaryGap: false,
            axisLine: {
              lineStyle: {
                color: '#57617B'
              }
            },
            data: data.xAxis
          },
          yAxis: {
            type: 'value',
            minInterval: 1,
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
          series: [{
            data: data.num,
            type: 'line',
            smooth: true
          }]
        })
      },
      initsvtChart(data) {
        this.svtChart = echarts.getInstanceByDom(document.getElementById('svt-chart'))
        if(this.svtChart === undefined) {
          this.svtChart = echarts.init(document.getElementById('svt-chart'))
        }
        console.log(data)
        this.svtChart.setOption({
          legend: {
            show: true,
            data: ["avg_time", "head_time", "get_time", "put_time", "delete_time", "post_time"]
          },
          xAxis: {
            type: 'category',
            boundaryGap: false,
            axisLine: {
              lineStyle: {
                color: '#57617B'
              }
            },
            data: data.add_time_list
          },
          yAxis: {
            name: "ms",
            type: 'value',
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
          series: [{
            name: "avg_time",
            data: data.avg_time_list,
            type: 'line',
            smooth: true
          },{
            name: "head_time",
            data: data.head_time_list,
            type: 'line',
            smooth: true
          },{
            name: "get_time",
            data: data.get_time_list,
            type: 'line',
            smooth: true
          },{
            name: "put_time",
            data: data.put_time_list,
            type: 'line',
            smooth: true
          },{
            name: "delete_time",
            data: data.delete_time_list,
            type: 'line',
            smooth: true
          },{
            name: "post_time",
            data: data.post_time_list,
            type: 'line',
            smooth: true
          },]
        })
      },
      initProxyThroughoutChart(data) {
        this.proxyThroughoutChart = echarts.getInstanceByDom(document.getElementById('proxy-throughout-chart'))
        if(this.proxyThroughoutChart === undefined){
          this.proxyThroughoutChart = echarts.init(document.getElementById('proxy-throughout-chart'))
        }
        let options = {
          title: {
            text: 'proxy-server吞吐',
          },
          color: ['#c23531', '#419df8'],
          xAxis: {
            type: 'category',
            boundaryGap: false,
            data: data.add_time
          },
          yAxis: {
            type: 'value',
            axisLabel:{
              formatter: function (data) {
                return formatterBytes(data, 1024)
              }
            },
          },
          tooltip: {
            trigger: 'axis',
            formatter: ((params, ticket, callback) => {
              let res= '<div>' + params[0].name + '</div>'
              for(var i=0;i<params.length;i++){
                res+=`<span style=\"display:inline-block;margin-right:5px;border-radius:10px;width:10px;height:10px;background-color:${params[i].color};\"></span>`
                res+=`${params[i].seriesName}: ${formatterBytes(params[i].value, 1024)}<br />`
              }
              return res
            }),
          },
          series: [{
            name: 'send_bytes',
            data: data.send_bytes,
            type: 'line',
            smooth: true
          },{
            name: 'recv_bytes',
            data: data.recv_bytes,
            type: 'line',
            smooth: true
          }]
        }
        this.proxyThroughoutChart.setOption(options)
        if(this.proxyThroughoutChart && this.storageThroughoutChart){
          echarts.connect([this.proxyThroughoutChart, this.storageThroughoutChart])
        }
      },
      initStorageThroughoutChart(data) {
        this.storageThroughoutChart = echarts.getInstanceByDom(document.getElementById('storage-throughout-chart'))
        if(this.storageThroughoutChart === undefined){
          this.storageThroughoutChart = echarts.init(document.getElementById('storage-throughout-chart'))
        }
        let options = {
          title: {
            text: 'storage-server吞吐',
          },
          color: ['#c23531', '#419df8'],
          xAxis: {
            type: 'category',
            boundaryGap: false,
            data: data.add_time,
          },
          yAxis: {
            type: 'value',
            axisLabel:{
              formatter: function (data) {
                return formatterBytes(data)
              }
            },
          },
          tooltip: {
            trigger: 'axis',
            formatter: ((params, ticket, callback) => {
              let res= '<div>' + params[0].name + '</div>'
              for(var i=0;i<params.length;i++){
                res+=`<span style=\"display:inline-block;margin-right:5px;border-radius:10px;width:10px;height:10px;background-color:${params[i].color};\"></span>`
                res+=`${params[i].seriesName}: ${formatterBytes(params[i].value)}<br />`
              }
              return res
            }),
          },
          series: [{
            name: 'send_bytes',
            data: data.send_bytes,
            type: 'line',
            smooth: true
          },{
            name: 'recv_bytes',
            data: data.recv_bytes,
            type: 'line',
            smooth: true
          }]
        }
        this.storageThroughoutChart.setOption(options)
        if(this.proxyThroughoutChart && this.storageThroughoutChart){
          echarts.connect([this.proxyThroughoutChart, this.storageThroughoutChart])
        }
      },
      selectChange_async(value){
        if(!value){
          this.intervalGetAsyncFunc()
        }
      },
      selectChange_iops(value){
        if(!value){
          this.intervalGetIOPSFunc()
        }
      },
      getHistoryData(type){
        if(type === 'async'){
          if(this.intervalGetAsync){
            clearInterval(this.intervalGetAsync)
          }
          let params = {
            starttime: Date.parse(this.selectTime.async.time[0])/1000,
            endtime: Date.parse(this.selectTime.async.time[1])/1000,
          }
          this.getSwiftStatus(this.selectedCluster, params)
        }else if(type === 'iops'){
          if(this.intervalGetIOPS){
            clearInterval(this.intervalGetIOPS)
          }
          let params = {
            starttime: Date.parse(this.selectTime.iops.time[0])/1000,
            endtime: Date.parse(this.selectTime.iops.time[1])/1000,
          }
          this.getStorageData(this.selectedCluster, params)
          this.getProxyData(this.selectedCluster, params)
        }
      },
      clearHistoryData(type){
        if(type === 'async'){
          this.selectTime.async.time = []
          this.intervalGetAsyncFunc()
        }else if(type === 'iops'){
          this.selectTime.iops.time = []
          this.intervalGetIOPSFunc()
        }
      },
      intervalGetAsyncFunc(){
        this.getSwiftStatus(this.selectedCluster)
        this.intervalGetAsync = setTimeout(this.intervalGetAsyncFunc, 300000)
      },
      intervalGetIOPSFunc(){
        this.getProxyData(this.selectedCluster)
        this.getStorageData(this.selectedCluster)
        this.intervalGetIOPS = setTimeout(this.intervalGetIOPSFunc, 65000)
      },
      intervalGetSVTFunc(){
        this.getClusterSvt(this.selectedCluster)
        this.intervalGetSVT = setTimeout(this.intervalGetSVTFunc, 300000)
      },
      timeFunction(){
        this.getNodePer(this.selectedCluster)
        this.intervalTask = setTimeout(this.timeFunction, 30000)
      },
      clearIntervals(){
        if(this.intervalTask){
          clearTimeout(this.intervalTask)
        }
        if(this.intervalGetSVT){
          clearInterval(this.intervalGetSVT)
        }
        if(this.intervalGetAsync){
          clearInterval(this.intervalGetAsync)
        }
        if(this.intervalGetIOPS){
          clearInterval(this.intervalGetIOPS)
        }
      },
    },
    created() {

    },
    mounted() {
      this.proxyThroughoutChart = echarts.init(document.getElementById('proxy-throughout-chart'))
      this.storageThroughoutChart = echarts.getInstanceByDom(document.getElementById('storage-throughout-chart'))
      this.asyncChart = echarts.init(document.getElementById('async-pending-chart'))
      this.svtChart = echarts.init(document.getElementById('svt-chart'))
      this.timeFunction()
      this.intervalGetAsyncFunc()
      this.intervalGetIOPSFunc()
      this.intervalGetSVTFunc()
      setTimeout(() => {
        window.onresize = (() => {
          if(this.proxyThroughoutChart){
            this.proxyThroughoutChart.resize()
          }
          if(this.storageThroughoutChart){
            this.storageThroughoutChart.resize()
          }
          if(this.asyncChart){
            this.asyncChart.resize()
          }
          if(this.svtChart){
            this.svtChart.resize()
          }
        })
      }, 500)
    },
    beforeDestroy() {
      // console.log('beforeDestroy')
      this.clearIntervals()
      if(this.proxyThroughoutChart){
        this.proxyThroughoutChart.dispose()
      }
      if(this.storageThroughoutChart){
        this.storageThroughoutChart.dispose()
      }
      if(this.asyncChart){
        this.asyncChart.dispose()
      }
      if(this.svtChart){
        this.svtChart.dispose()
      }
    },
  }
</script>
<style rel="stylesheet/scss" lang="scss" scoped>
  .rep-title{
    font-size: 1.2rem;
    font-weight: bolder;
    padding: 3px;
  }
  .ACO {
    height: 250px;
    width: 100%;
  }
</style>
