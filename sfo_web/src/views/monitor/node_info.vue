/**
* Create by wenboling on 2018/4/8
*/
<template>
  <div>
    <el-row v-if="!isInfoShow">
      <el-table :data="hostlist" style="width: 97%; margin: 5px auto" border stripe>
        <el-table-column prop="node_host_name" label="主机名" min-width="150"></el-table-column>
        <el-table-column prop="node_inet_ip" label="IP地址" min-width="150"></el-table-column>
        <el-table-column prop="node_replicate_ip" label="复制IP" min-width="150"></el-table-column>
        <el-table-column prop="node_role" label="节点角色" min-width="280">
          <template slot-scope="scope">
            <span>{{ scope.row.node_role | translateServerType}}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" min-width="120">
          <template slot-scope="scope">
            <el-button type="text" size="small" @click="handleHostClick(scope.row)">查看详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-row>
    <el-row :gutter="10"  style="margin-right: 5px; margin-top: 5px">
      <el-col :span="4" v-show="isInfoShow">
        <el-tree
          :props="servers"
          :data="hostnamelist"
          node-key="id"
          :highlight-current="true"
          @node-click="handleNodeClick"
          default-expand-all
          ref='hostListTree'>
        </el-tree>
        <el-row style="margin: 10px">
          <el-button type="primary" size="mini" icon="el-icon-back" @click="backToList">返回</el-button>
        </el-row>
      </el-col>
      <el-col :span="20"  v-if="isInfoShow">
        <el-tabs v-model="activetab" @tab-click="handleTabClick">
          <el-tab-pane label="主机信息" name="info">
            <el-row class="pane-row">
              <el-table :data="mf_info" style="width: 100%"  :border="true">
                <el-table-column prop="host_name" label="主机名称" width="180"></el-table-column>
                <el-table-column prop="mf_name" label="厂商" width="100"></el-table-column>
                <el-table-column prop="mf_model" label="型号" min-width="150"></el-table-column>
                <el-table-column prop="mf_bios_date" label="bios日期" width="100"></el-table-column>
                <el-table-column prop="mf_bios_version" label="bios版本" width="120"></el-table-column>
                <el-table-column prop="mf_serial_number" label="序列号" width="120"></el-table-column>
                <el-table-column prop="os_version" label="系统版本" min-width="150"></el-table-column>
                <el-table-column prop="os_kernel_version" label="内核版本" min-width="150"></el-table-column>
              </el-table>
            </el-row>
            <el-row class="pane-row">
              <el-table :data="mem_info" style="width: 100%" :border="true">
                <el-table-column prop="mem_total" label="总内存" width="180"></el-table-column>
                <el-table-column prop="mem_number" label="条数" width="180"></el-table-column>
                <el-table-column prop="mem_single_size" label="单条大小"></el-table-column>
                <el-table-column prop="mem_frequency" label="频率"></el-table-column>
              </el-table>
            </el-row>
            <el-row class="pane-row">
              <el-table :data="CPU_info" style="width: 100%" :border="true">
                <el-table-column prop="cpu_model" label="CPU型号" min-width="300"></el-table-column>
                <el-table-column prop="cpu_processors" label="CPU个数" width="180"></el-table-column>
                <el-table-column prop="cpu_cores" label="CPU核数"></el-table-column>
                <el-table-column prop="cpu_sockets" label="CPU插槽"></el-table-column>
                <el-table-column prop="cpu_frequency" label="主频(MHz)" width="200"></el-table-column>
              </el-table>
            </el-row>
            <el-row class="pane-row">
              <el-table :data="netcard_info" style="width: 100%" :border="true" :stripe="true">
                <el-table-column prop="name" label="网卡" width="150"></el-table-column>
                <el-table-column prop="model_name" label="网卡型号" width="500"></el-table-column>
                <el-table-column prop="speed" label="网卡速率" width="180"></el-table-column>
                <el-table-column prop="mac_address" label="MAC地址"></el-table-column>
                <el-table-column prop="ip_address" label="IP地址"></el-table-column>
              </el-table>
            </el-row>
            <el-row class="pane-row">
              <el-table :data="disk_info" style="width: 100%" :border="true" :stripe="true">
                <el-table-column prop="disk_name" label="硬盘名" width="180"></el-table-column>
                <el-table-column prop="disk_useful_size" label="容量"></el-table-column>
                <el-table-column prop="disk_capacity" label="磁盘类型"></el-table-column>
                <el-table-column prop="disk_type" label="RAID"></el-table-column>
                <el-table-column prop="address" label="接口速率"></el-table-column>
              </el-table>
            </el-row>
          </el-tab-pane>
          <el-tab-pane label="节点状态" name="status">
            <el-row>
              <el-form :inline="true" :model="selectTime.nodeStatus" style="float: right">
                <el-form-item>
                  <el-date-picker
                    v-model="selectTime.nodeStatus.time"
                    type="datetimerange"
                    :picker-options="pickerOptions"
                    range-separator="-"
                    start-placeholder="开始时间"
                    end-placeholder="结束时间"
                    align="right"
                    @change="selectChange_status"
                    :clearable="false">
                  </el-date-picker>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="getHistoryData('status')"
                             :disabled="!selectTime.nodeStatus.time || selectTime.nodeStatus.time.length===0" size="small">查询</el-button>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="clearHistoryData('status')"
                             :disabled="!selectTime.nodeStatus.time || selectTime.nodeStatus.time.length===0" size="small">重置</el-button>
                </el-form-item>
              </el-form>
            </el-row>
            <el-row class="pane-row">
              <el-card>
                <div slot="header" class="clearfix">
                  <span>系统状态</span>
                </div>
                <div style="text-align:center;width:100%;"  v-if="no_status_data"><span style="color: #00a0e9;font-size: large;">暂无数据</span></div>
                <div id="sys-status-charts" style="width: 100%;height:320px;"></div>
                <div style="width: 100%;height:100px;">
                  <el-table :data="host_info" style="width: 60%;margin: 0 auto">
                    <el-table-column prop="host_name" label="名称" min-width="180"></el-table-column>
                    <el-table-column prop="host_time" label="主机当前时间" min-width="180"></el-table-column>
                    <el-table-column prop="host_runtime" label="开机时间" min-width="180"></el-table-column>
                  </el-table>
                </div>
              </el-card>
            </el-row>
            <el-row class="pane-row">
              <el-card>
                <div slot="header" class="clearfix">
                  <span>CPU状态</span>
                </div>
                <div style="text-align:center;width:100%;"  v-if="no_status_data"><span style="color: #00a0e9;font-size: large;">暂无数据</span></div>
                <div id="cpu-status-charts" style="width: 100%;height:320px;"></div>
                <div id="cpu-core-status-charts" style="width: 100%;height:320px;"></div>
              </el-card>
            </el-row>
            <el-row class="pane-row">
              <el-card>
                <div slot="header" class="clearfix">
                  <span>内存状态</span>
                </div>
                <div style="text-align:center;width:100%;"  v-if="no_status_data"><span style="color: #00a0e9;font-size: large;">暂无数据</span></div>
                <div id="mem-status-charts" style="width: 100%;height:320px;"></div>
                <div style="width: 100%;height:100px;">
                  <el-table :data="memStatusData.total" style="width: 320px;margin: 0 auto">
                    <el-table-column prop="mem_total" label="总内存" min-width="160px"></el-table-column>
                    <el-table-column prop="swap_total" label="swap total"></el-table-column>
                  </el-table>
                </div>
              </el-card>
            </el-row>
            <el-row class="pane-row">
              <el-card>
                <div slot="header" class="clearfix">
                  <span>网卡状态</span>
                </div>
                <div style="text-align:center;width:100%;"  v-if="no_status_data"><span style="color: #00a0e9;font-size: large;">暂无数据</span></div>
                <div id="net-status-charts" style="width: 100%;height:320px;"></div>
                <div style="width: 100%;height:320px;">
                  <el-table :data="netStatus_info" style="width: 200%" max-height="320">
                    <el-table-column prop="name" label="name" width="150"></el-table-column>
                    <el-table-column prop="net_recv_packages" label="recv_packages" width="180"></el-table-column>
                    <el-table-column prop="net_send_packages" label="send_packages" width="180"></el-table-column>
                    <el-table-column prop="net_recv_bytes" label="recv_bytes" width="180"></el-table-column>
                    <el-table-column prop="net_send_bytes" label="send_bytes" width="180"></el-table-column>
                    <el-table-column prop="net_in_err" label="in_err"></el-table-column>
                    <el-table-column prop="net_out_err" label="out_err" width="150"></el-table-column>
                    <el-table-column prop="net_in_drop" label="in_drop" width="150"></el-table-column>
                    <el-table-column prop="net_out_drop" label="out_drop" width="150"></el-table-column>
                  </el-table>
                </div>
              </el-card>
            </el-row>
          </el-tab-pane>
          <el-tab-pane label="节点服务" name="service">
            <el-row class="pane-row">
              <el-card style="width: 80%;margin-bottom: 10px" v-if="selectHostType.indexOf('Proxy-Server') >= 0">
                <div slot="header" class="clearfix">
                  <span>proxy</span>
                </div>
                <div class="clearfix">
                  <template v-for="(item, index) in proxy_srvs_status">
                    <div  class="srv_status">
                      <label>{{ index.substr(4) }}</label>
                      <span><el-tag :type="el_tag_type[item]">{{ item }}</el-tag></span>
                    </div>
                  </template>
                </div>
              </el-card>
              <el-card style="width: 80%;margin-bottom: 10px" v-if="selectHostType.indexOf('Account-Server') >= 0">
                <div slot="header" class="clearfix">
                  <span>account</span>
                </div>
                <div class="clearfix">
                  <template v-for="(item, index) in account_srvs_status">
                    <div  class="srv_status">
                      <label>{{ index.substr(4) }}</label>
                      <span><el-tag :type="el_tag_type[item]">{{ item }}</el-tag></span>
                    </div>
                  </template>
                </div>
              </el-card>
              <el-card style="width: 80%;margin-bottom: 10px" v-if="selectHostType.indexOf('Container-Server') >= 0">
                <div slot="header" class="clearfix">
                  <span>container</span>
                </div>
                <div class="clearfix">
                  <template v-for="(item, index) in container_srvs_status">
                    <div  class="srv_status">
                      <label>{{ index.substr(4) }}</label>
                      <span><el-tag :type="el_tag_type[item]">{{ item }}</el-tag></span>
                    </div>
                  </template>
                </div>
              </el-card>
              <el-card style="width: 80%;margin-bottom: 10px" v-if="selectHostType.indexOf('Object-Server') >= 0">
                <div slot="header" class="clearfix">
                  <span>object</span>
                </div>
                <div class="clearfix">
                  <template v-for="(item, index) in object_srvs_status">
                    <div  class="srv_status">
                      <label>{{ index.substr(4) }}</label>
                      <span><el-tag :type="el_tag_type[item]">{{ item }}</el-tag></span>
                    </div>
                  </template>
                </div>
              </el-card>
            </el-row>
          </el-tab-pane>
          <!--<el-tab-pane label="节点性能" name="performance">101</el-tab-pane>-->
          <el-tab-pane label="磁盘监控" name="diskMonitor" v-if="isStorageNode">
            <el-row>
              <el-form :inline="true" :model="selectTime.diskStatus" style="float: right">
                <el-form-item>
                  <el-date-picker
                    v-model="selectTime.diskStatus.time"
                    type="datetimerange"
                    :picker-options="pickerOptions"
                    range-separator="-"
                    start-placeholder="开始时间"
                    end-placeholder="结束时间"
                    align="right"
                    @change="selectChange_disk"
                    :clearable="false">
                  </el-date-picker>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="getHistoryData('disk')"
                             :disabled="!selectTime.diskStatus.time || selectTime.diskStatus.time.length===0" size="small">查询</el-button>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="clearHistoryData('disk')"
                             :disabled="!selectTime.diskStatus.time || selectTime.diskStatus.time.length===0" size="small">重置</el-button>
                </el-form-item>
              </el-form>
            </el-row>
            <el-row class="pane-row">
              <el-card>
                <div slot="header" class="clearfix">
                  <span>磁盘读写IO</span>
                </div>
                <div style="text-align:center;width:100%;"  v-if="no_status_data"><span style="color: #00a0e9;font-size: large;">暂无数据</span></div>
                <div id="disks-iops" style="width: 100%; height: 500px;" ></div>
              </el-card>
            </el-row>
            <el-row class="pane-row">
              <el-card>
                <div slot="header" class="clearfix">
                  <span>磁盘读写带宽</span>
                </div>
                <div style="text-align:center;width:100%;"  v-if="no_status_data"><span style="color: #00a0e9;font-size: large;">暂无数据</span></div>
                <div id="disks-mbps" style="width: 100%;height:500px;" ></div>
              </el-card>
            </el-row>
            <el-row class="pane-row">
              <el-card>
                <div slot="header" class="clearfix">
                  <span>磁盘响应时间</span>
                </div>
                <div style="text-align:center;width:100%;"  v-if="no_status_data"><span style="color: #00a0e9;font-size: large;">暂无数据</span></div>
                <div id="disks-svt" style="width: 100%;height:500px;" ></div>
              </el-card>
            </el-row>
            <el-row class="pane-row">
              <el-card>
                <div slot="header" class="clearfix">
                  <span>磁盘状态信息</span>
                </div>
                <el-row>
                  <el-table :data="respData" height="500">
                    <el-table-column label="磁盘名" prop="disk.disk_name"></el-table-column>
                    <el-table-column label="总容量" prop="disk.disk_total" :formatter="fmttotalbytes"></el-table-column>
                    <el-table-column label="使用量" prop="disk.disk_used" :formatter="fmtbusedytes"></el-table-column>
                    <el-table-column label="剩余容量" prop="disk.disk_free" :formatter="fmtbfreeytes"></el-table-column>
                    <el-table-column label="占用比" prop="disk.disk_percent"></el-table-column>
                    <!--<el-table-column label="在线状态" prop="disk"></el-table-column>-->
                  </el-table>
                </el-row>
              </el-card>
            </el-row>
          </el-tab-pane>
        </el-tabs>
      </el-col>
    </el-row>
  </div>
</template>

<script>
  import { gethosts, gethostInfo, getnodeStat, getNodeSrvDetail, getDiskPerformanceDetail,getClusterIOPS } from '@/api/monitor'
  import { getClusterNodesDetail, up_downSrv } from '@/api/management'
  import echarts from 'echarts'
  import { mapGetters } from 'vuex'
  import { formatterBytes } from '@/utils'
  import LoadingAnimation  from '@/components/LoadingAnimation'
  import pickerOptions from '@/commons/pickerOptions'

  export default {
    components: {
      LoadingAnimation
    },
    data() {
      return {
        isInfoShow: false,
        hasDiskAtr: true,
        //树形菜单相关数据
        servers: {
          label: 'name',
          children: 'children',
        },
        hostlist: [],
        selectHostGuid: '',
        selectHostType: '',
        selectHostName: '',
        hostnamelist: [{
          name: '主机列表',
          children: []
        }],
        activetab: 'info',

        //主机信息相关数据
        mf_info: null,
        mem_info: null,
        CPU_info: null,
        netcard_info: [],
        disk_info: [],

        //查看历史数据相关
        selectTime: {
          nodeStatus: {
            time: [],
          },
          diskStatus: {
            time: [],
          }
        },
        pickerOptions: pickerOptions,
        //节点状态相关数据
        addtime_list: [],
        host_info: [],
        netStatus_info: [],
        netUsed_info: {},
        sysStatusData: {
          host_average_load_list: [],
          host_login_users_list: [],
          thread_total_list: [],
          thread_running_list: [],
          thread_stopedl_list: [],
          thread_sleeping_list: [],
          thread_zombie_list: []
        },
        memStatusData: {
          total: [],
          mem_used_list: [],
          mem_free_list: [],
          swap_total_list: [],
          swap_used_list: [],
          swap_free_list: [],
          swap_cached_list: [],
        },
        cpuStatusData: {
          cpu_usr: [],
          cpu_sys: [],
          cpu_ni: [],
          cpu_idel: [],
          cpu_wait: [],
          cpu_hi: [],
          cpu_si: [],
          cpu_st: [],
        },
        cpuCoreStatusData: [],
        sysStatusChart: null,
        memStatusChart: null,
        CPUStatusChart: null,
        NetCardStatusChart: null,
        CPUCoreStatusChart: null,

        //节点服务相关数据
        proxy_srvs_status: {},
        account_srvs_status: {},
        container_srvs_status: {},
        object_srvs_status: {},
        el_tag_type:{
          running: 'success',
          stoped: 'danger',
          stopped: 'danger',
          warning: 'warning'
        },
        no_status_data: true,
        //定时刷新
        intervalGetNodeStatus: null,
        intervalGetSrvStatus: null,

        //磁盘监控相关数据
        respData: null,
        addTimeList: null,
        diskIopsChart: null,
        diskMbpsChart: null,
        diskSVTChart: null,

        //dialog数据
        cmd_result: '',
        dialogVisible: false,
        isWaiting: false,

      };
    },
    computed: {
      ...mapGetters([
        'selectedCluster'
      ]),
      isStorageNode(){
        return this.selectHostType.indexOf('Account-Server') > -1
          || this.selectHostType.indexOf('Container-Server') > -1
          ||this.selectHostType.indexOf('Object-Server') > -1
      }
    },
    filters: {
      translateServerType(str) {
        if(str.length === 0){
          return "暂未配置"
        }
        let temp = JSON.parse(str)
        let serverTypes = Object.keys(temp)
        let result = ''
        for(let server of serverTypes){
          if(temp[server] === 'YES'){
            result = result + server + ' '
          }
        }
        return result
      }
    },
    methods: {
      resetData() {
        this.mf_info = null
        this.CPU_info = null
        this.mem_info = null
        this.netcard_info = null
        this.proxy_srvs_status = {}
        this.account_srvs_status = {}
        this.container_srvs_status = {}
        this.object_srvs_status = {}
        this.addtime_list = []
        this.host_info = []
        this.disk_info = []
        this.netStatus_info = []
        this.sysStatusData = {}
        this.memStatusData = {}
        this.cpuStatusData = {}
        this.cpuCoreStatusData = []
        this.netStatus_info = []
        this.netUsed_info = {}
      },
      clearCharts(){
        if(this.sysStatusChart){
          this.sysStatusChart.clear()
        }
        if(this.memStatusChart){
          this.memStatusChart.clear()
        }
        if(this.CPUStatusChart){
          this.CPUStatusChart.clear()
        }
        if(this.NetCardStatusChart){
          this.NetCardStatusChart.clear()
        }
        if(this.CPUCoreStatusChart){
          this.CPUCoreStatusChart.clear()
        }
        if(this.diskIopsChart){
          this.diskIopsChart.clear()
        }
        if(this.diskMbpsChart){
          this.diskMbpsChart.clear()
        }
        if(this.diskSVTChart){
          this.diskSVTChart.clear()
        }
      },

      getHostList() {
        gethosts(this.selectedCluster).then(response => {
          if(response.data.status === 200){
            this.hostlist = response.data.data
            for(var host of this.hostlist){
              let data = {
                id: host.node_host_name,
                name: host.node_host_name
              }
              this.hostnamelist[0].children.push(data)
            }
          }
        })
      },
      getHostDetailInfo(guid) {
        gethostInfo(guid).then(response => {
          if(response.status === 200 && response.data.status === 200){
            let data = response.data.data
            this.mf_info = new Array(1);
            this.CPU_info = new Array(1);
            this.mem_info = new Array(1);
            this.mf_info[0] = data.mf
            this.mem_info[0] = data.mem
            this.CPU_info[0] = data.cpu
            // this.netcard_info.push(data.net)
            this.netcard_info = new Array(data.net.net_number)
            let net = data.net
            let net_name_list = Object.keys(net.net_ip_address)
            for(let i=0; i < net.net_number; i++) {
              let temp = {
                name: net_name_list[i],
                ip_address: net.net_ip_address[net_name_list[i]],
                mac_address: net.net_mac_address[net_name_list[i]],
                model_name: net.net_model[net_name_list[i]],
                speed: net.net_speed[net_name_list[i]],
              }
              this.netcard_info[i] = temp
            }
            if(data.disk && data.disk.disk_number){
              this.disk_info = new Array(data.disk.disk_number.diskgroup)
              let disk = data.disk
              let disk_name_list = Object.keys(disk.disk_type)
              for(let j=0; j < disk.disk_number.diskgroup; j++){
                let temp = {
                  disk_name: disk_name_list[j],
                  disk_useful_size: disk.disk_useful_size[disk_name_list[j]],
                  disk_capacity: disk.disk_capacity[disk_name_list[j]],
                  disk_type: disk.disk_type[disk_name_list[j]],
                }
                this.disk_info[j] = temp
              }
            }
          }else{
            this.resetData()
          }
        }).catch(err=>{
          console.log(err)
          this.resetData()
        })
      },
      getNodeStat(hostname, params) {
        getnodeStat(hostname, params).then(response => {
          if(response.status === 200 && response.data.status === 200){
            this.no_status_data = false
            let data = response.data.data
            this.addtime_list = data.addtime_list

            this.host_info = new Array(1)
            this.host_info[0] = data.host_info
            this.initSysStatusData(data)
            this.initMemStatusData(data)
            this.initCPUStatusData(data)
            this.initCPUCoreStatusData(data.cpu_core_used_list)
            this.initNetStatusData(data.net, data.net_used_list.map)
          }
        }).catch(err=>{
          this.no_status_data = true
          this.clearCharts()
          this.resetData()
        })
      },
      getNodeSrvStatus(hostname) {
        getNodeSrvDetail(hostname).then(response => {
          if(response.status === 200 && response.data.status === 200){
            let data = response.data.data
            this.proxy_srvs_status = data.proxy
            this.account_srvs_status = data.account
            this.container_srvs_status = data.container
            this.object_srvs_status = data.object
          }
        }).catch(err=>{
          this.resetData()
        })
      },
      getDiskPerformance(hostname, params){
          getDiskPerformanceDetail(hostname, params).then(response =>{
            if(response.status === 200 && response.data.status === 200) {
              this.respData = response.data.data
              this.addTimeList = this.respData[0].disk.read_count.map(item=>{
                return item[0]
              })
              this.no_status_data = false
              // this.addTimeList = response.data.add_time
              this.initDiskIopsChart()
              this.initDiskMbpsChart()
              // this.initDiskMbpsChart()
              this.initDiskSvtChart()
              // this.initDiskSvtChart()
            }
          }).catch(err=>{
            this.no_status_data = true
            this.clearCharts()
            this.resetData()
          })
      },
      handleTabClick(tab, event) {
        this.clearIntervals()
        this.no_status_data = true
        this.selectTime ={
          nodeStatus: { time: [], },
          diskStatus: { time: [], }
        }
        if(tab.name === 'info'){
          this.clearCharts()
          this.getHostDetailInfo(this.selectHostName)
        }else if(tab.name === 'status'){
          this.clearCharts()
          this.$nextTick(()=>{
            this.getNodeStat(this.selectHostName)
            this.intervalGetNodeStatus = setInterval(() => {
              this.getNodeStat(this.selectHostName)
            }, 30000)
            this.resizeCharts()
            window.onresize = (() => {
              this.sysStatusChart.resize()
              this.memStatusChart.resize()
              this.CPUStatusChart.resize()
              this.CPUCoreStatusChart.resize()
              this.NetCardStatusChart.resize()
            })
          })
        }else if(tab.name === 'service'){
          this.clearCharts()
          this.getNodeSrvStatus(this.selectHostName)
          this.intervalGetSrvStatus = setInterval(() => {
            this.getNodeSrvStatus(this.selectHostName)
          }, 30000)
        }else if (tab.name === 'diskMonitor')
        {
          this.clearCharts()
          this.$nextTick(()=>{
            this.getDiskPerformance(this.selectHostName)
            this.intervalGetNodeStatus = setInterval(() => {
              this.getDiskPerformance(this.selectHostName)
            }, 60000)
            this.resizeCharts()
            window.onresize = (() => {
              this.diskIopsChart.resize()
              this.diskMbpsChart.resize()
              // this.diskSVTChart.resize()
            })
          })
        }
      },

      handleNodeClick(data, node, con){
        this.resetData()
        this.clearCharts()
        if(node.level > 1){
          this.selectHostName = node.label
          if(this.selectHostName) {
            this.isInfoShow = true
            this.activetab = 'info'
            this.selectHostType = this.getHostType(this.selectHostName)
            this.getHostDetailInfo(this.selectHostName)
            this.clearIntervals()
          }
        }
      },

      handleHostClick(row){
        this.$refs['hostListTree'].setCurrentKey(row.node_host_name)
        this.selectHostName = row.node_host_name
        this.isInfoShow = true
        this.activetab = 'info'
        this.selectHostType = this.getHostType(this.selectHostName)
        this.getHostDetailInfo(this.selectHostName)
        this.clearIntervals()
      },
      backToList(){
        this.$refs['hostListTree'].setCurrentKey(null)
        this.isInfoShow = false
      },
      getHostType(hostname){
        let tmp = this.hostlist.find(host=>{
          return host.node_host_name === hostname
        })
        let node_role = JSON.parse(tmp.node_role)
        let serverTypes = Object.keys(node_role)
        let result = ''
        for(let server of serverTypes){
          if(node_role[server] === 'YES'){
            result = result + server + '  '
          }
        }
        return result
      },

      //TODO: 节点状态绘图
      //系统状态
      initSysStatusData(data){
        this.sysStatusData.host_average_load_list = data.host_average_load_list
        this.sysStatusData.thread_running_list =data.thread_running_list
        this.sysStatusData.thread_sleeping_list = data.thread_sleeping_list
        this.sysStatusData.thread_stopedl_list = data.thread_stopedl_list
        this.sysStatusData.thread_total_list = data.thread_total_list
        this.sysStatusData.thread_zombie_list = data.thread_zombie_list
        this.sysStatusData.host_login_users_list = data.host_login_users_list
        this.initSysStatusChart(this.sysStatusData)
      },
      initSysStatusChart(data){
        let load_1min = [], load_5min = [], load_15min = []
        for(let i = 0; i < data.host_average_load_list.length; i++) {
          load_1min.push(data.host_average_load_list[i][0])
          load_5min.push(data.host_average_load_list[i][1])
          load_15min.push(data.host_average_load_list[i][2])
        }
        this.sysStatusChart = echarts.init(document.getElementById('sys-status-charts'))
        this.sysStatusChart.setOption({
          legend: {
            show: true,
            type: 'scroll',
            data: ['平均负载：1min', '平均负载：5min', '平均负载：15min', '用户数', '总进程数', '运行进程数', '睡眠进程数', '停止进程数', '僵尸进程数']
          },
          tooltip: {
            trigger: 'axis'
          },
          xAxis: {
            type: 'category',
            name: '时间',
            boundaryGap: false,
            data: this.addtime_list
          },
          yAxis: [{
            name: '数目',
            type: 'value'
          },{
            name: '负载',
            type: 'value'
          }],
          series: [{
            name: '平均负载：1min',
            type: 'line',
            yAxisIndex: 1,
            smooth: true,
            data: load_1min
          },{
            name: '平均负载：5min',
            type: 'line',
            yAxisIndex: 1,
            smooth: true,
            data: load_5min
          },{
            name: '平均负载：15min',
            type: 'line',
            yAxisIndex: 1,
            smooth: true,
            data: load_15min
          },{
            name: '用户数',
            type: 'line',
            yAxisIndex: 0,
            smooth: true,
            data: data.host_login_users_list
          },{
            name: '总进程数',
            type: 'line',
            yAxisIndex: 0,
            smooth: true,
            data: data.thread_total_list
          },{
            name: '运行进程数',
            type: 'line',
            yAxisIndex: 0,
            smooth: true,
            data: data.thread_running_list
          },{
            name: '睡眠进程数',
            type: 'line',
            yAxisIndex: 0,
            smooth: true,
            data: data.thread_sleeping_list
          },{
            name: '停止进程数',
            type: 'line',
            yAxisIndex: 0,
            smooth: true,
            data: data.thread_stopedl_list
          },{
            name: '僵尸进程数',
            type: 'line',
            yAxisIndex: 0,
            smooth: true,
            data: data.thread_zombie_list
          }]
        })
      },
      //内存状态
      initMemStatusData(data){
        this.memStatusData.mem_free_list = data.mem_free_list
        this.memStatusData.mem_used_list = data.mem_used_list
        this.memStatusData.swap_cached_list = data.swap_cached_list
        this.memStatusData.swap_free_list = data.swap_free_list
        this.memStatusData.swap_used_list = data.swap_used_list
        this.memStatusData.total = new Array(1) //直接赋值为啥不行？
        this.memStatusData.total[0] = {
          mem_total: formatterBytes(data.mem_total_list[data.mem_total_list.length - 1]),
          swap_total: formatterBytes(data.swap_total_list[data.swap_total_list.length - 1])
        }
        this.initMemStatusChart(this.memStatusData)
      },
      initMemStatusChart(data){
        this.memStatusChart = echarts.init(document.getElementById('mem-status-charts'))
        this.memStatusChart.setOption({
          legend: {
            show: true,
            data: ['已用内存', '可用内存', 'buffer memory', 'swap_used', 'swap_free', 'swap_cached']
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
          xAxis: {
            type: 'category',
            name: '时间',
            boundaryGap: false,
            data: this.addtime_list
          },
          yAxis: {
            name: '内存',
            type: 'value',
            axisLabel: {
              formatter: function (value, index) {
                return formatterBytes(value)
              }
            }
          },
          series: [{
            name: '已用内存',
            type: 'line',
            data: data.mem_used_list
          },{
            name: '可用内存',
            type: 'line',
            data: data.mem_free_list
          },/*{
            name: 'buffer memory',
            type: 'line',
            data: [0.13,0.38,0.54,0.21]
          },*/{
            name: 'swap_used',
            type: 'line',
            yAxisIndex: 0,
            data: data.swap_used_list
          },{
            name: 'swap_free',
            type: 'line',
            yAxisIndex: 0,
            data: data.swap_free_list
          },{
            name: 'swap_cached',
            type: 'line',
            yAxisIndex: 0,
            data: data.swap_cached_list
          }]
        })
      },
      //CPU状态
      initCPUStatusData(data){
        this.cpuStatusData.cpu_usr = data.cpu_us_list
        this.cpuStatusData.cpu_sys = data.cpu_sy_list
        this.cpuStatusData.cpu_ni = data.cpu_ni_list
        this.cpuStatusData.cpu_idel = data.cpu_id_list
        this.cpuStatusData.cpu_wait = data.cpu_wa_list
        this.cpuStatusData.cpu_hi = data.cpu_hi_list
        this.cpuStatusData.cpu_si = data.cpu_si_list
        this.cpuStatusData.cpu_st = data.cpu_st_list
        this.initCPUStatusChart(this.cpuStatusData)
      },
      initCPUStatusChart(data){
        this.CPUStatusChart = echarts.init(document.getElementById('cpu-status-charts'))
        this.CPUStatusChart.setOption({
          legend: {
            show: true,
            data: ['usr', 'sys', 'ni', 'idel', 'wait', 'hi', 'si', 'st']
          },
          tooltip: {
            trigger: 'axis',
          },
          xAxis: {
            type: 'category',
            name: '时间',
            boundaryGap: false,
            data: this.addtime_list
          },
          yAxis: [{
            name: '单位：%',
            type: 'value'
          }],
          series: [{
            name: 'usr',
            type: 'line',
            smooth: true,
            data: data.cpu_usr
          },{
            name: 'sys',
            type: 'line',
            smooth: true,
            data: data.cpu_sys
          },{
            name: 'ni',
            type: 'line',
            yAxisIndex: 0,
            smooth: true,
            data: data.cpu_ni
          },{
            name: 'idel',
            type: 'line',
            yAxisIndex: 0,
            smooth: true,
            data: data.cpu_idel
          },{
            name: 'wait',
            type: 'line',
            yAxisIndex: 0,
            smooth: true,
            data: data.cpu_wait
          },{
            name: 'hi',
            type: 'line',
            yAxisIndex: 0,
            smooth: true,
            data: data.cpu_hi
          },{
            name: 'si',
            type: 'line',
            yAxisIndex: 0,
            smooth: true,
            data: data.cpu_si
          },{
            name: 'st',
            type: 'line',
            yAxisIndex: 0,
            smooth: true,
            data: data.cpu_st
          }]
        })
      },
      //CPU-core状态
      initCPUCoreStatusData(data){
        let len = data[0].length
        for(let i = 0; i < len; i++){
          this.cpuCoreStatusData[i] = [];
        }
        for(let i = 0; i < data.length; i++){
          for(let j = 0; j < len; j++){
            this.cpuCoreStatusData[j][i] = data[i][j]
          }
        }
        this.initCPUCoreStatusChart(this.cpuCoreStatusData)
      },
      initCPUCoreStatusChart(data){
        this.CPUCoreStatusChart = echarts.init(document.getElementById('cpu-core-status-charts'))
        let option = {
          legend: {
            show: true,
            type: 'scroll',
            data: []
          },
          tooltip: {
            trigger: 'axis',
            position: function (pos, params, dom, rect, size) {
              // 鼠标在左侧时 tooltip 显示到右侧，鼠标在右侧时 tooltip 显示到左侧。
              var obj = {top: pos[1]};
              obj[['left', 'right'][+(pos[0] < size.viewSize[0] / 2)]] = 5;
              return obj;
            },
            formatter: function (datas) {
              var res = datas[0].name + '<br/>'
              for (var i = 0, length = datas.length; i < length; i++) {
                let num_per_line = 8
                if(i % num_per_line < num_per_line - 1) {
                  res +=
                    "<span style='display:inline-block;margin-right:5px;border-radius:10px;width:10px;height:10px;background-color:"
                    + datas[i].color
                    + ";'></span>"
                    + datas[i].seriesName + ' '+ datas[i].value + '&nbsp;&nbsp;&nbsp;'
                }else {
                  res +=
                    "<span style='display:inline-block;margin-right:5px;border-radius:10px;width:10px;height:10px;background-color:"
                    + datas[i].color
                    + ";'></span>"
                    + datas[i].seriesName + ' '+ datas[i].value + '<br />'
                }
              }
              return res
            }
          },
          xAxis: {
            type: 'category',
            name: '时间',
            boundaryGap: false,
            data: this.addtime_list
          },
          yAxis: [{
            name: '单位：%',
            type: 'value'
          }],
          series: []
        }
        let legendArr = []
        for(let i = 0; i < data.length; i++) {
          legendArr[i] = 'core' + (i + 1)
          let item = {
            name: legendArr[i],
            type: 'line',
            smooth: true,
            data: data[i]
          }
          option.series.push(item)
        }
        option.legend.data = legendArr
        this.CPUCoreStatusChart.setOption(option)
      },

      //net状态
      initNetStatusData(net_data, net_used_data){
        let temp = Object.keys(net_data.net_in_drop)
        let net_name_list = Array.from(temp)
        this.netStatus_info = null
        this.netStatus_info = new Array(net_name_list.length)
        for(let i = 0; i < net_name_list.length; i++){
          this.netStatus_info[i] = {
            name: net_name_list[i],
            net_in_drop: net_data.net_in_drop[net_name_list[i]],
            net_in_err: net_data.net_in_err[net_name_list[i]],
            net_out_drop: net_data.net_out_drop[net_name_list[i]],
            net_out_err: net_data.net_out_err[net_name_list[i]],
            net_recv_bytes: net_data.net_recv_bytes[net_name_list[i]],
            net_recv_packages: net_data.net_recv_packages[net_name_list[i]],
            net_send_bytes: net_data.net_send_bytes[net_name_list[i]],
            net_send_packages: net_data.net_send_packages[net_name_list[i]],
          }
        }
        this.initNetStatusChart(net_used_data)
      },
      initNetStatusChart(data) {
        this.NetCardStatusChart = echarts.init(document.getElementById('net-status-charts'))
        if(!data.net_recv_bytes){
          return
        }
        let option = {
          legend: {
            show: true,
            type: 'scroll',
            data: []
          },
          tooltip: {
            trigger: 'axis',
            position: function (pos, params, dom, rect, size) {
              // 鼠标在左侧时 tooltip 显示到右侧，鼠标在右侧时 tooltip 显示到左侧。
              var obj = {top: pos[1]};
              obj[['left', 'right'][+(pos[0] < size.viewSize[0] / 2)]] = 5;
              return obj;
            },
            formatter: ((params, ticket, callback) => {
              let res= '<div>' + params[0].name + '</div>'
              const num_per_line = 6
              for(var i=0;i<params.length;i++){
                res+=`<span style=\"display:inline-block;margin-right:5px;border-radius:10px;width:10px;height:10px;background-color:${params[i].color};\"></span>`
                if((i % num_per_line) < (num_per_line - 1)){
                  res+=`${params[i].seriesName}: ${formatterBytes(params[i].value, 1024)}&nbsp;&nbsp;&nbsp;`
                }else{
                  res+=`${params[i].seriesName}: ${formatterBytes(params[i].value, 1024)}<br />`
                }
              }
              return res
            }),
          },
          xAxis: {
            type: 'category',
            name: '时间',
            boundaryGap: false,
            data: this.addtime_list
          },
          yAxis: [{
            name: 'Bytes/s',
            type: 'value',
            axisLabel:{
              formatter: function (data) {
                return formatterBytes(data, 1024)
              }
            },
          }],
          series: []
        }
        let legendArr = []
        let net_card_list = Object.keys(data.net_recv_bytes)
        for (let i = 0; i < net_card_list.length; i++) {
          legendArr[i] = net_card_list[i] + '-recv'
          let item = {
            name: legendArr[i],
            type: 'line',
            smooth: true,
            data: data.net_recv_bytes[net_card_list[i]]
          }
          option.series.push(item)
        }
        for (let i = 0; i < net_card_list.length; i++) {
          legendArr.push(net_card_list[i] + '-send')
          let item = {
            name: legendArr[i + net_card_list.length],
            type: 'line',
            smooth: true,
            data: data.net_send_bytes[net_card_list[i]]
          }
          option.series.push(item)
        }
        option.legend.data = legendArr
        this.NetCardStatusChart.setOption(option)
      },
      clearIntervals() {
        if(this.intervalGetNodeStatus){
          clearInterval(this.intervalGetNodeStatus)
        }
        if(this.intervalGetSrvStatus){
          clearInterval(this.intervalGetSrvStatus)
        }
      },

      //磁盘状态
      initDiskIopsChart() {
        this.diskIopsChart = echarts.init(document.getElementById('disks-iops'))
        var seriesList = this.initDiskGradientSeriesIopsList()
        this.diskIopsChart.setOption({
          // Make gradient line here
          legend:{
            left: 'center',
            top: 'center',
            data: this.respData.map(function (item) {
              return item.disk.disk_name
            }),
            type: 'scroll',
          },
          title: [{
            left: 'right',
            text: 'Read IO'
          }, {
            top: '50%',
            left: 'right',
            text: 'Write IO'
          }],
          tooltip: {
            trigger: 'axis',
            position: function (pos, params, dom, rect, size) {
              // 鼠标在左侧时 tooltip 显示到右侧，鼠标在右侧时 tooltip 显示到左侧。
              var obj = {top: pos[1]};
              obj[['left', 'right'][+(pos[0] < size.viewSize[0] / 2)]] = 5;
              return obj;
            },
            formatter: function (datas) {
              var res = datas[0].name + '<br/>'
              for (var i = 0, length = datas.length; i < length; i++) {
                let num_per_line = 8
                if(i % num_per_line < num_per_line - 1) {
                  res +=
                    "<span style='display:inline-block;margin-right:5px;border-radius:10px;width:10px;height:10px;background-color:"
                    + datas[i].color
                    + ";'></span>"
                    + datas[i].seriesName + ' '+ datas[i].value + '&nbsp;&nbsp;&nbsp;'
                }else {
                  res +=
                    "<span style='display:inline-block;margin-right:5px;border-radius:10px;width:10px;height:10px;background-color:"
                    + datas[i].color
                    + ";'></span>"
                    + datas[i].seriesName + ' '+ datas[i].value + '<br />'
                }
              }
              return res
            }
          },
          toolbox: {
            left: 10,
            feature: {
              dataZoom: {
                yAxisIndex: 'none'
              },
              restore: {},
              saveAsImage: {}
            }
          },
          dataZoom: [{
            type: 'inside',
            zoomOnMouseWheel: 'ctrl'
          }],
          xAxis: [{
            name: '日期-时间',
            boundaryGap: false,
            data: this.addTimeList
          },{
            name: '日期-时间',
            boundaryGap: false,
            data: this.addTimeList,
            gridIndex: 1
          }],
          yAxis: [{
            type : 'value',
            max: 'dataMax',
            name: '读取次数',
            minInterval: 1,
            splitLine: {show: true},

          }, {
            type : 'value',
            max: 'dataMax',
            name: '写入次数',
            minInterval: 1,
            splitLine: {show: true},
            gridIndex: 1
          }],
          grid: [{
            bottom: '60%'
          }, {
            top: '60%'
          }],
          series: seriesList
        })
      },
      initDiskMbpsChart() {
        this.diskMbpsChart = echarts.init(document.getElementById('disks-mbps'))
        var seriesList = this.initDiskGradientSeriesMbpsList()
        this.diskMbpsChart.setOption({
          // Make gradient line here
          legend:{
            left: 'center',
            top: 'center',
            data: this.respData.map(function (item) {
              return item.disk.disk_name
            }),
            type: 'scroll',
          },
          title: [{
            left: 'right',
            text: 'Read BandWidth'
          }, {
            top: '50%',
            left: 'right',
            text: 'Write BandWidth'
          }],
          tooltip: {
            trigger: 'axis',
            position: function (pos, params, dom, rect, size) {
              // 鼠标在左侧时 tooltip 显示到右侧，鼠标在右侧时 tooltip 显示到左侧。
              var obj = {top: pos[1]};
              obj[['left', 'right'][+(pos[0] < size.viewSize[0] / 2)]] = 5;
              return obj;
            },
            formatter: function (datas) {
              var res = datas[0].name + '<br/>'
              for (var i = 0, length = datas.length; i < length; i++) {
                let num_per_line = 8
                if(i % num_per_line < num_per_line - 1) {
                  res +=
                    "<span style='display:inline-block;margin-right:5px;border-radius:10px;width:10px;height:10px;background-color:"
                    + datas[i].color
                    + ";'></span>"
                    + datas[i].seriesName + ' '+ formatterBytes(datas[i].value, 1024) + '&nbsp;&nbsp;&nbsp;'
                }else {
                  res +=
                    "<span style='display:inline-block;margin-right:5px;border-radius:10px;width:10px;height:10px;background-color:"
                    + datas[i].color
                    + ";'></span>"
                    + datas[i].seriesName + ' '+ formatterBytes(datas[i].value, 1024) + '<br />'
                }
              }
              return res
            }
          },
          toolbox: {
            left: 10,
            feature: {
              dataZoom: [{
                yAxisIndex: 'none',
              },{
                yAxisIndex: 1
              },],
              restore: {},
              saveAsImage: {}
            }
          },
          dataZoom: [{
            type: 'inside',
          },
            {
              type: 'inside',
              yAxisIndex: 1
            }],
          xAxis: [{
            name: '日期-时间',
            boundaryGap: false,
            data: this.addTimeList
          },{
            name: '日期-时间',
            boundaryGap: false,
            data: this.addTimeList,
            gridIndex: 1
          }],
          yAxis: [{
            type : 'value',
            max: 'dataMax',
            axisLabel:{formatter: function (data) {
              return formatterBytes(data, 1024)
            }},
            name: '读取带宽',
            splitLine: {show: true},

          }, {
            type : 'value',
            max: 'dataMax',
            axisLabel:{formatter: function (data) {
              return formatterBytes(data)
            }},
            name: '写入带宽',
            splitLine: {show: true},
            gridIndex: 1
          }],
          grid: [{
            bottom: '60%'
          }, {
            top: '60%'
          }],
          series: seriesList
        })
      },
      initDiskSvtChart() {
        this.diskSVTChart = echarts.init(document.getElementById('disks-svt'))
        var data = this.initDiskSeriesSvtList()
        var diskNameList = data.map(function (item) {
          return item.name
        })
        this.diskSVTChart.setOption({
          xAxis: {
            type: 'category',
            boundaryGap: false,
            name: '日期-时间',
            axisLine: {
              lineStyle: {
                color: '#57617B'
              }
            },
            data: this.addTimeList
          },
          legend: {
            data: diskNameList,
            type: 'scroll',
          },
          yAxis: {
            type: 'value',
            max: 'dataMax',
            name: '响应时间 单位ms',
            splitLine: {show: true},
            axisLabel:{formatter: function (data) {
              return data + 'ms'
            }},
          },
          tooltip: {
            trigger: 'axis',
            position: function (pos, params, dom, rect, size) {
              // 鼠标在左侧时 tooltip 显示到右侧，鼠标在右侧时 tooltip 显示到左侧。
              var obj = {top: pos[1]};
              obj[['left', 'right'][+(pos[0] < size.viewSize[0] / 2)]] = 5;
              return obj;
            },
            axisPointer: {
              lineStyle: {
                color: '#57617B'
              }
            },
            formatter: function (datas) {
              var res = datas[0].name + '<br/>'
              for (var i = 0, length = datas.length; i < length; i++) {
                let num_per_line = 8
                if(i % num_per_line < num_per_line - 1) {
                  res +=
                    "<span style='display:inline-block;margin-right:5px;border-radius:10px;width:10px;height:10px;background-color:"
                    + datas[i].color
                    + ";'></span>"
                    + datas[i].seriesName + ' '+ (datas[i].value + ' ms') + '&nbsp;&nbsp;&nbsp;'
                }else {
                  res +=
                    "<span style='display:inline-block;margin-right:5px;border-radius:10px;width:10px;height:10px;background-color:"
                    + datas[i].color
                    + ";'></span>"
                    + datas[i].seriesName + ' '+ (datas[i].value + ' ms') + '<br />'
                }
              }
              return res
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
          series:data
        })
      },
      initDiskGradientSeriesIopsList() {
        let seriesObjectList = new Array()
        for(let i=0; i<this.respData.length; i++) {
          let read_count_object = new Object()
          let write_count_object = new Object()
          let disk = this.respData[i].disk
          read_count_object.name = disk.disk_name
          write_count_object.name = disk.disk_name
          read_count_object.type = 'line'
          write_count_object.type = 'line'
          read_count_object.data = disk.read_count.map(item=>{
            return item[1]
          })
          write_count_object.data = disk.write_count.map(item=>{
            return item[1]
          })
          read_count_object.smooth = true
          write_count_object.smooth = true
          write_count_object.xAxisIndex = 1
          write_count_object.yAxisIndex = 1
          seriesObjectList.push(read_count_object)
          seriesObjectList.push(write_count_object)
        }
        return seriesObjectList
      },
      initDiskGradientSeriesMbpsList() {
        let seriesObjectList = new Array()
        for(let i=0; i<this.respData.length; i++) {
          let readSeriesObject = new Object()
          let writeSeriesObject = new Object()
          let disk = this.respData[i].disk
          readSeriesObject.name = disk.disk_name
          writeSeriesObject.name = disk.disk_name
          readSeriesObject.type = 'line'
          writeSeriesObject.type = 'line'
          readSeriesObject.data = disk.read.map(item=>{
            return item[1]
          })
          writeSeriesObject.data = disk.write.map(item=>{
            return item[1]
          })
          readSeriesObject.smooth = true
          writeSeriesObject.smooth = true
          writeSeriesObject.xAxisIndex = 1
          writeSeriesObject.yAxisIndex = 1
          seriesObjectList.push(readSeriesObject)
          seriesObjectList.push(writeSeriesObject)
        }
        return seriesObjectList
      },
      initDiskSeriesSvtList() {
        let seriesObjectList = new Array()
        for(let i=0; i<this.respData.length; i++) {
          let seriesObject = new Object()
          let disk = this.respData[i].disk
          seriesObject.name = disk.disk_name
          seriesObject.type = 'line'
          seriesObject.smooth = true
          seriesObject.data = disk.await.map(item=>{
            return item[1]
          })
          seriesObjectList.push(seriesObject)
        }
        return seriesObjectList
      },

      resizeCharts(){
        if(this.sysStatusChart){
          this.sysStatusChart.resize()
        }
        if(this.memStatusChart){
          this.memStatusChart.resize()
        }
        if(this.CPUStatusChart){
          this.CPUStatusChart.resize()
        }
        if(this.CPUCoreStatusChart){
          this.CPUCoreStatusChart.resize()
        }
        if(this.NetCardStatusChart){
          this.NetCardStatusChart.resize()
        }
        if(this.diskIopsChart){
          this.diskIopsChart.resize()
        }
        if(this.diskMbpsChart){
          this.diskMbpsChart.resize()
        }
      },
      fmttotalbytes(row, column) {
        let bytes = row.disk.disk_total

        return formatterBytes(bytes)
      },
      fmtbusedytes(row, column) {
        let bytes = row.disk.disk_used

        return formatterBytes(bytes)
      },
      fmtbfreeytes(row, column) {
        let bytes = row.disk.disk_free

        return formatterBytes(bytes)
      },

      selectChange_disk(value){
        if(!value){
          this.getDiskPerformance(this.selectHostName)
          this.intervalGetNodeStatus = setInterval(() => {
            this.getDiskPerformance(this.selectHostName)
          }, 60000)
        }
      },
      selectChange_status(value){
        if(!value){
          this.getNodeStat(this.selectHostName)
          this.intervalGetNodeStatus = setInterval(() => {
            this.getNodeStat(this.selectHostName)
          }, 30000)
        }
      },
      getHistoryData(type){
        this.clearIntervals()
        if(type === 'status'){
          let params = {
            starttime: Date.parse(this.selectTime.nodeStatus.time[0])/1000,
            endtime: Date.parse(this.selectTime.nodeStatus.time[1])/1000
          }
          this.getNodeStat(this.selectHostName, params)
        }else if(type === 'disk'){
          let params = {
            starttime: Date.parse(this.selectTime.diskStatus.time[0])/1000,
            endtime: Date.parse(this.selectTime.diskStatus.time[1])/1000
          }
          this.getDiskPerformance(this.selectHostName, params)
        }
      },
      clearHistoryData(type){
        if(type === 'status'){
          this.selectTime.nodeStatus.time = []
          this.getNodeStat(this.selectHostName)
          this.intervalGetNodeStatus = setInterval(() => {
            this.getNodeStat(this.selectHostName)
          }, 30000)
        }else if(type === 'disk'){
          this.selectTime.diskStatus.time = []
          this.getDiskPerformance(this.selectHostName)
          this.intervalGetNodeStatus = setInterval(() => {
            this.getDiskPerformance(this.selectHostName)
          }, 60000)
        }
      }
    },
    mounted(){
      this.getHostList()
    },
    beforeDestroy(){
      this.clearIntervals()
      if(this.sysStatusChart){
        this.sysStatusChart.dispose()
      }
      if(this.memStatusChart){
        this.memStatusChart.dispose()
      }
      if(this.CPUStatusChart){
        this.CPUStatusChart.dispose()
      }
      if(this.CPUCoreStatusChart){
        this.CPUCoreStatusChart.dispose()
      }
      if(this.NetCardStatusChart){
        this.NetCardStatusChart.dispose()
      }
      if(this.diskIopsChart){
        this.diskIopsChart.dispose()
      }
      if(this.diskMbpsChart){
        this.diskMbpsChart.dispose()
      }
    }
  }
</script>
<style rel="stylesheet/scss" lang="scss" scoped>
  .pane-row {
    margin-bottom: 15px;
  }
  .clearfix:before,
  .clearfix:after {
    display: table;
    content: "";
  }
  .clearfix:after {
    clear: both
  }
  .srv_status {
    width: 50%;
    float: left;
    margin-bottom: 5px;
  }
  .app-contanier{
    margin: auto;
    margin-top: 5px;
  }
  .inner_row {
    padding: 5px 10px 5px 10px;
  }
  .space {
    margin-left: 20px;
  }
  .spacetop {
    margin-top: 20px;
  }
  .link-type,
  .link-type:focus {
    color: #337ab7;
    cursor: pointer;
    &:hover {
      color: rgb(32, 160, 255);
    }
  }
  .svg-icon{
    cursor: pointer;
  }
</style>
