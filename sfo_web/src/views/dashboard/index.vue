<template>
  <div>
    <el-row :gutter="5" style="margin: 8px">
      <el-col :span="6">
        <el-card>
          <div slot="header" class="clearfix">
            <span>集群容量</span>
          </div>
          <div style="text-align:center;width:100%;"  v-if="no_cluster_info_data">
            <span style="color: #00a0e9;font-size: large;">暂无数据</span>
          </div>
          <div id="capacity-charts" style="width: 100%;height:180px;"></div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div slot="header" class="clearfix">
            <span>OPS<span class="comments">(最近24小时P95值)</span></span>
          </div>
          <div style="text-align:center;width:100%;"  v-if="no_cluster_info_data">
            <span style="color: #00a0e9;font-size: large;">暂无数据</span>
          </div>
          <div id="ops-chart" style="width: 100%;height:180px;"></div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div slot="header" class="clearfix">
            <span>集群带宽<span class="comments">(最近24小时P95值)</span></span>
          </div>
          <div style="text-align:center;width:100%;"  v-if="no_cluster_info_data">
            <span style="color: #00a0e9;font-size: large;">暂无数据</span>
          </div>
          <div id="bandwidth-chart" style="width: 100%;height:180px;"></div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div slot="header" class="clearfix">
            <span>复制网络带宽<span class="comments">(最近24小时P95值)</span></span>
          </div>
          <div style="text-align:center;width:100%;"  v-if="no_cluster_info_data">
            <span style="color: #00a0e9;font-size: large;">暂无数据</span>
          </div>
          <div id="rep-bandwidth-chart" style="width: 100%;height:180px;"></div>
        </el-card>
      </el-col>
    </el-row>
    <el-row :gutter="5" style="margin: 10px">
      <el-card>
        <div slot="header" class="clearfix">
          <span>主机状态</span>
        </div>
        <div style="text-align:center;width:100%;"  v-if="no_cluster_info_data">
          <span style="color: #00a0e9;font-size: large;">暂无数据</span>
        </div>
        <div id="server-status-chart" style="width: 100%;height:378px;"></div>
        <el-row style="margin-top: 10px">
          <span class="comments">注: Proxy-Server、Account-Server、Container-Server、Object-Server总数之和不一定与主机的总数相等，因为一台主机可能部署了多种Server</span>
        </el-row>
      </el-card>
    </el-row>
    <el-row :gutter="5" style="margin: 10px">
      <el-card>
        <div slot="header" class="clearfix">
          <span>集群用户</span>
        </div>
        <el-row style="margin-left: 10px">
          <span style="color: #8c939d">account总数:</span><span class="cluster">{{cluster_virtual.account_num}}</span>
          <span style="color: #8c939d">container总数:</span><span class="cluster">{{cluster_virtual.container_num}}</span>
          <span style="color: #8c939d">object总数:</span><span class="cluster">{{cluster_virtual.object_num}}</span>
        </el-row>
        <el-table :data="cluster_capacity_info.apply_systems_info" :max-height="300" style="width: 100%; margin-top: 10px">
          <el-table-column prop="account_id" label="账户名" min-width="130"></el-table-column>
          <el-table-column label="账户容量" min-width="130">
            <template slot-scope="scope">
              <span>{{ scope.row.system_capacity | formatterBytes(1024) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="已用容量" min-width="130">
            <template slot-scope="scope">
              <span>{{ scope.row.account_used | formatterBytes(1024) }}</span>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </el-row>
  </div>
</template>

<script>
  import { mapGetters } from 'vuex'
  import { formatterBytes } from '@/utils'
  import { getClusterInfo } from '@/api/dashboard'
  import echarts from 'echarts'

  export default {
    name: 'dashboard',
    computed: {
      ...mapGetters([
        'selectedCluster'
      ])
    },
    data() {
      return {
        serverStatusChart: null,
        bandwidthChart: null,
        repBandwidthChart: null,
        capacityChart: null,
        opsChart: null,
        intervalTask: '',
        server_status: {},
        capacity_summary: {
          total: 0,
          used: 0,
          available: 0
        },
        disk_num: 0,
        bandwidth_summary: {
          total: 0,
          used: 0,
          available: 0
        },
        rep_bandwidth_summary: {
          total: 0,
          used: 0,
          available: 0
        },
        ops_summary: {
          total: 0,
          used: 0,
          available: 0
        },
        abnormal: {
          account: [],
          object: [],
          container: [],
          proxy: [],
          nodes: [],
        },
        serverNameMap: {
          "Proxy-Server": 'proxy',
          "Account-Server": 'account',
          "Object-Server": 'object',
          "Container-Server": 'container',
        },
        cluster_node: {
          node_online: 0,
          node_total: 0,
          node_outline: 0
        },
        outline_nodes: [],
        cluster_virtual: {},
        cluster_capacity_info: {},
        no_cluster_info_data: true,
      }
    },
    methods: {
      getClusterInfo: function(cluster) {
        getClusterInfo(cluster).then(response => {
          if(response.data.status === 200 && response.status === 200) {
            this.no_cluster_info_data = false
            let data = response.data.data
            this.server_status.proxy_status = data.cluster_physical.proxy_num
            this.server_status.storage_status = data.cluster_physical.storage_num
            this.server_status.node_status = data.cluster_node
            this.outline_nodes = data.cluster_node.outline_nodes
            this.abnormal = data.abnormal
            this.disk_num = data.cluster_physical.disk_num
            this.cluster_virtual = data.cluster_virtual
            this.cluster_capacity_info = data.cluster_capacity_info
            this.initcapacitySummaryData(data.cluster_physical.capacity_total)
            this.initServerStatusData(this.server_status)
            this.initbandwidthSummaryData(data.cluster_physical.band_width.band_total, data.band_width_24h_ago.band_width_p95)
            this.initrepBandwidthSummaryData(data.cluster_physical.band_width.band_rep_total, data.band_width_24h_ago.band_width_rep_p95)
            this.initopsData(data.cluster_proxy_total_ops, data.cluster_ops_24h_ago.cluster_ops_p95)
          }
        }).catch(err => {
          this.no_cluster_info_data = true
          this.clearCharts()
        })
      },
      initServerStatusData(data) {
        this.server_status.proxy_status.proxy_offline = data.proxy_status.proxy_total - data.proxy_status.proxy_online
        this.server_status.storage_status.account_offline = data.storage_status.account_num - data.storage_status.account_online
        this.server_status.storage_status.container_offline = data.storage_status.container_num - data.storage_status.container_online
        this.server_status.storage_status.object_offline = data.storage_status.object_num - data.storage_status.object_online
        this.initServerStatusChart(this.server_status)
      },
      initServerStatusChart(data) {
        this.serverStatusChart = echarts.getInstanceByDom(document.getElementById('server-status-chart'))
        if(this.serverStatusChart === undefined){
          this.serverStatusChart = echarts.init(document.getElementById('server-status-chart'))
        }
        let option = {
          tooltip : {
            trigger: 'item',
            axisPointer : {            // 坐标轴指示器，坐标轴触发有效
              type : 'line'        // 默认为直线，可选为：'line' | 'shadow'
            },
            formatter: (params => {
              let color ="<span style='display:inline-block;margin-right:5px;border-radius:10px;width:10px;height:10px;background-color:"+params.color+";'></span>"
              if (params.value > 0) {
                return params.name + '<br />' + color + params.seriesName + ': ' + params.value + '<br />'
              } else {
                return '';
              }
            }),
          },
          legend: {
            data: ['正常', '异常']
          },
          color: ['#98F898', '#FF4500'],
          grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
          },
          xAxis:  {
            type: 'category',
            data: ['Proxy-Server','Account-Server','Container-Server','Object-Server', '主机']
          },
          yAxis: {
            show: false,
          },
          series: [
            {
              name: '正常',
              type: 'bar',
              stack: 'total',
              z: 10,
              label: {
                show: true,
                position: 'inside',
                formatter: function(params) {
                  if (params.value > 0) {
                    return params.seriesName + ': ' + params.value;
                  } else {
                    return '';
                  }
                },
              },
              data: [data.proxy_status.proxy_online, data.storage_status.account_online,
                data.storage_status.container_online,data.storage_status.object_online,
                data.node_status.node_online]
            },
            {
              name: '异常',
              type: 'bar',
              stack: 'total',
              z: 10,
              label: {
                show: true,
                position: 'inside',
                formatter: function(params) {
                  if (params.value > 0) {
                    return params.seriesName + ': ' + params.value;
                  } else {
                    return '';
                  }
                },
              },
              tooltip: {
                formatter: (params => {
                  let abnormal_server = []
                  if(params.name.indexOf('Server') > -1){
                    abnormal_server = this.abnormal[this.serverNameMap[params.name]]
                  }else {
                    abnormal_server = this.outline_nodes
                  }
                  let color ="<span style='display:inline-block;margin-right:5px;border-radius:10px;width:10px;height:10px;background-color:"+params.color+";'></span>"
                  if (params.value > 0) {
                    return params.name + '<br />' + color + params.seriesName + ': ' + params.value + '<br />' + abnormal_server;
                  } else {
                    return '';
                  }
                }),
              },
              data: [data.proxy_status.proxy_offline, data.storage_status.account_offline,
                data.storage_status.container_offline,data.storage_status.object_offline,
                data.node_status.node_outline]
            },
            {
              name: '总数',
              type: 'bar',
              // stack: 'total',
              label: {
                show: true,
                position: 'top',
                color:'#000',
                formatter: function(params) {
                  if (params.value > 0) {
                    return params.seriesName + ': ' + params.value;
                  } else {
                    return '';
                  }
                },
              },
              barGap: '-100%',
              itemStyle:{
                color:'rgba(128, 128, 128, 0)',
              },
              tooltip:{
                show: false,
              },
              data: [data.proxy_status.proxy_total, data.storage_status.account_num,
                data.storage_status.container_num,data.storage_status.object_num,
                data.node_status.node_total]
            },
          ]
        }
        this.serverStatusChart.setOption(option)
      },

      initcapacitySummaryData(data) {
        this.capacity_summary.total = parseFloat(data.disk_total)
        this.capacity_summary.used = parseFloat(data.disk_used)
        this.capacity_summary.available = parseFloat(data.disk_free)
        this.initcapacityChart(this.capacity_summary)
      },
      initcapacityChart(data) {
        this.capacityChart = echarts.getInstanceByDom(document.getElementById('capacity-charts'))
        if(this.capacityChart === undefined){
          this.capacityChart = echarts.init(document.getElementById('capacity-charts'))
        }
        let option = {
          title: {
            text: '总容量:' + formatterBytes(data.total, 1024) + '\n\n' + '磁盘数:' + this.disk_num,
            x: 'center',
            y: 'center',
            textStyle: {
              color: '#031f2d',
              align: 'center'
            }
          },
          tooltip: {
            trigger: 'item',
            // formatter: '{a} <br/>{b}: {c} ({d}%)',
            formatter: (params => {
              return params.name + ': ' + formatterBytes(params.value, 1024)
            }),
            position: ['5%', '50%']
          },
          series: [
            {
              name: '节点情况',
              type: 'pie',
              radius: ['50%', '70%'],
              avoidLabelOverlap: false,
              label: {
                show: true,
                // formatter: '{b}: {c}'
                formatter: (params => {
                  return params.name + ': ' + formatterBytes(params.value, 1024)
                })
              },
              data: [
                { value: data.available, name: '可用', itemStyle: { normal: { color: '#98F898' }}},
                { value: data.used, name: '已用', itemStyle: { normal: { color: '#FF4500' }}},
              ]
            }
          ]
        }
        this.capacityChart.setOption(option)
      },

      initbandwidthSummaryData(total, used) {
        this.bandwidth_summary.total = total
        this.bandwidth_summary.used = parseFloat(used).toFixed(2)
        this.bandwidth_summary.available = parseFloat(total - this.bandwidth_summary.used).toFixed(2)
        this.initbandwidthChart(this.bandwidth_summary)
      },
      initbandwidthChart(data) {
        this.bandwidthChart = echarts.getInstanceByDom(document.getElementById('bandwidth-chart'))
        if(this.bandwidthChart === undefined) {
          this.bandwidthChart = echarts.init(document.getElementById('bandwidth-chart'))
        }
        let option = {
          title: {
            text: '总带宽:' + data.total + 'MB',
            x: 'center',
            y: 'center',
            textStyle: {
              color: '#031f2d',
              align: 'center'
            }
          },
          tooltip: {
            trigger: 'item',
            formatter: '{a} <br/>{b}: {c}MB ({d}%)',
            position: ['5%', '50%']
          },
          series: [
            {
              name: '带宽情况',
              type: 'pie',
              radius: ['50%', '70%'],
              avoidLabelOverlap: false,
              stillShowZeroSum: false,
              label: {
                show: true,
                formatter: '{b}: {c}MB'
              },
              data: [
                { value: data.available, name: '可用', itemStyle: { normal: { color: '#98F898' }}},
                { value: data.used, name: '已用', itemStyle: { normal: { color: '#FF4500' }}},
              ]
            }
          ]
        }
        if(data.total === 0){
          option.series[0].label.show = false
        }
        this.bandwidthChart.setOption(option)
      },

      initrepBandwidthSummaryData(total, used) {
        this.rep_bandwidth_summary.total = total
        this.rep_bandwidth_summary.used = parseFloat(used).toFixed(2)
        this.rep_bandwidth_summary.available = parseFloat(total - this.rep_bandwidth_summary.used).toFixed(2)
        this.initrepBandwidthChart(this.rep_bandwidth_summary)
      },
      initrepBandwidthChart(data) {
        this.repBandwidthChart = echarts.getInstanceByDom(document.getElementById('rep-bandwidth-chart'))
        if(this.repBandwidthChart === undefined) {
          this.repBandwidthChart = echarts.init(document.getElementById('rep-bandwidth-chart'))
        }
        let option = {
          title: {
            text: '总带宽:' + data.total + 'MB',
            x: 'center',
            y: 'center',
            textStyle: {
              color: '#031f2d',
              align: 'center'
            }
          },
          tooltip: {
            trigger: 'item',
            formatter: '{a} <br/>{b}: {c}MB ({d}%)',
            position: ['5%', '50%']
          },
          series: [
            {
              name: '带宽情况',
              type: 'pie',
              radius: ['50%', '70%'],
              avoidLabelOverlap: false,
              stillShowZeroSum: false,
              label: {
                show: true,
                formatter: '{b}: {c}MB'
              },
              data: [
                { value: data.available, name: '可用', itemStyle: { normal: { color: '#98F898' }}},
                { value: data.used, name: '已用', itemStyle: { normal: { color: '#FF4500' }}},
              ]
            }
          ]
        }
        if(data.total === 0){
          option.series[0].label.show = false
        }
        this.repBandwidthChart.setOption(option)
      },

      initopsData(ops_total, ops_used) {
        this.ops_summary.total = ops_total
        this.ops_summary.used = parseFloat(ops_used)
        this.ops_summary.available = ops_total - parseFloat(ops_used)
        this.initopsChart(this.ops_summary)
      },
      initopsChart(data) {
        this.opsChart = echarts.getInstanceByDom(document.getElementById('ops-chart'))
        if(this.opsChart === undefined) {
          this.opsChart = echarts.init(document.getElementById('ops-chart'))
        }
        let option = {
          title: {
            text: '最大OPS:' + data.total,
            x: 'center',
            y: 'center',
            textStyle: {
              color: '#031f2d',
              align: 'center'
            }
          },
          tooltip: {
            trigger: 'item',
            formatter: '{a} <br/>{b}: {c}({d}%)',
            position: ['5%', '50%']
          },
          series: [
            {
              name: 'OPS情况',
              type: 'pie',
              radius: ['50%', '70%'],
              avoidLabelOverlap: false,
              stillShowZeroSum: false,
              label: {
                show: true,
                formatter: '{b}: {c}'
              },
              data: [
                { value: data.available, name: '可用', itemStyle: { normal: { color: '#98F898' }}},
                { value: data.used, name: '已用', itemStyle: { normal: { color: '#FF4500' }}},
              ]
            }
          ]
        }
        this.opsChart.setOption(option)
      },

      clearCharts(){
        if(this.serverStatusChart){
          this.serverStatusChart.clear()
        }
        if(this.opsChart){
          this.opsChart.clear()
        }
        if(this.capacityChart){
          this.capacityChart.clear()
        }
        if(this.bandwidthChart){
          this.bandwidthChart.clear()
        }
        if(this.repBandwidthChart){
          this.repBandwidthChart.clear()
        }
      },
      timerFunction(){
        this.getClusterInfo(this.selectedCluster)
        this.intervalTask = setTimeout(this.timerFunction, 60000)
      }
    },
    created() {
      // this.getOPSbyDuration(this.starttime, this.endtime)
      // this.getRequestData()
    },
    mounted() {
      // this.getSwiftACOInfo()
      setTimeout(() => {
        window.onresize = (() => {
          if(this.serverStatusChart){
            this.serverStatusChart.resize()
          }
          if(this.opsChart){
            this.opsChart.resize()
          }
          if(this.capacityChart){
            this.capacityChart.resize()
          }
          if(this.bandwidthChart){
            this.bandwidthChart.resize()
          }
          if(this.repBandwidthChart){
            this.repBandwidthChart.resize()
          }
        })
      }, 500)
      // this.intervalTask = setInterval(() => {
      //   this.getRequestData()
      //   this.getOPSbyDuration(this.starttime, this.endtime)
      // }, 15000);
      this.timerFunction()
    },
    beforeDestroy() {
      // clearInterval(this.intervalTask)
      clearTimeout(this.intervalTask)
      if(this.opsChart){
        this.opsChart.dispose()
      }
      if(this.capacityChart){
        this.capacityChart.dispose()
      }
      if(this.bandwidthChart){
        this.bandwidthChart.dispose()
      }
      if(this.serverStatusChart){
        this.serverStatusChart.resize()
      }
      if(this.repBandwidthChart){
        this.repBandwidthChart.resize()
      }
    },
  }
</script>

<style rel="stylesheet/scss" lang="scss" scoped>
  .dashboard {
    &-container {
      margin: 30px;
    }
    &-text {
      font-size: 30px;
      line-height: 46px;
    }
  }
  .clearfix:before,
  .clearfix:after {
    display: table;
    content: "";
  }
  .clearfix:after {
    clear: both
  }
  .inner_row {
    padding: 5px 10px 5px 10px;
  }
  .ACO {
    height: 300px;
    width: 100%;
  }
  .cluster {
    margin: 5px;
    color: #35e99f;
    font-size: larger;
  }
  .comments {
    color: #00a2d4;
    font-size: small;
  }
</style>
