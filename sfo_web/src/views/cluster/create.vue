/**
* Create by wenboling on 2018/7/4
*/
<template>
  <div>
    <el-row style="margin: 20px">
      <span style="color: red">警告: 在创建集群过程中，请勿刷新页面或切换页面！！！</span>
    </el-row>
    <el-row style="margin: 20px">
      <el-steps :active_step="active_step">
        <el-step title="添加集群名" :status="step_one_status"></el-step>
        <el-step title="选择主机" :status="step_two_status"></el-step>
        <el-step title="配置环" :status="step_three_status"></el-step>
        <el-step title="其它配置" :status="step_four_status"></el-step>
      </el-steps>
    </el-row>
    <!--建集群名-->
    <el-form label-width="80px" :model="new_cluster" v-if="active_step===1"  :rules="rules" ref="newClusterForm">
      <el-form-item label="集群名" prop="cluster_name">
        <el-col :span="8">
          <el-input v-model="new_cluster.cluster_name"></el-input>
        </el-col>
      </el-form-item>
      <el-form-item label="专用集群" prop="cluster_stat">
        <el-radio v-model="new_cluster.cluster_stat" label="public">否</el-radio>
        <el-radio v-model="new_cluster.cluster_stat" label="dedicated">是</el-radio>
      </el-form-item>
      <span v-if="isLoading"><i class="el-icon-loading"></i>请稍后</span>
    </el-form>
    <!--<el-input v-model="sendMessage"></el-input>-->
    <!--<el-button type="primary" @click="sendTaskId">发送消息</el-button>-->
    <!--<span>{{jobResult}}</span>-->
    <!--选择主机-->
    <el-row v-if="active_step===2" style="margin: 20px">
      <el-table :data="hostList" style="width: 100%">
        <el-table-column prop="node_host_name" label="主机名" width="180"></el-table-column>
        <el-table-column prop="node_inet_ip" label="选择绑定IP地址" width="200">
          <template slot-scope="scope">
            <el-col :span="20">
              <el-select v-model="scope.row.node_inet_ip">
                <el-option v-for="ip in scope.row.host_info.net_ip_address"
                           :key="ip" :label="ip" :value="ip">
                </el-option>
              </el-select>
            </el-col>
          </template>
        </el-table-column>
        <el-table-column prop="node_role" label="选择节点角色" width="500">
          <template slot-scope="scope">
            <el-checkbox-group v-model="scope.row.checkedServers">
              <el-checkbox v-for="server in server_types" :label="server.value" :key="server.type">{{server.type}}</el-checkbox>
            </el-checkbox-group>
          </template>
        </el-table-column>
        <el-table-column prop="node_replicate_ip" label="复制IP">
          <template slot-scope="scope">
            <span v-if="scope.row.checkedServers.length ===0">请先选择节点角色</span>
            <span v-else-if="scope.row.checkedServers.length === 1 && scope.row.checkedServers.indexOf('Proxy-Server')>-1">单是proxy无复制IP</span>
            <el-select v-model="scope.row.node_replicate_ip" v-else>
              <el-col :span="20">
                <el-option v-for="ip in scope.row.host_info.net_ip_address"
                           :key="ip" :label="ip" :value="ip">
                </el-option>
              </el-col>
            </el-select>
          </template>
        </el-table-column>
      </el-table>
      <el-row style="margin-left: 20px; margin-top: 10px">
        <p v-if="selectedProxyServers.length > 0">proxy-servers:
          <span v-for="server in selectedProxyServers" :key="server.host_name" style="color: #2D64B3">
            {{server.host_name}}&nbsp;
          </span>
        </p>
        <p v-if="selectedAccountServers.length > 0">account-servers:
          <span v-for="server in selectedAccountServers" :key="server.host_name" style="color: #2D64B3">
            {{server.host_name}}&nbsp;
          </span>
        </p>
        <p v-if="selectedContainerServers.length > 0">container-servers:
          <span v-for="server in selectedContainerServers" :key="server.host_name" style="color: #2D64B3">
            {{server.host_name}}&nbsp;
          </span>
        </p>
        <p v-if="selectedObjectServers.length > 0">object-servers:
          <span v-for="server in selectedObjectServers" :key="server.host_name" style="color: #2D64B3">
            {{server.host_name}}&nbsp;
          </span>
        </p>
      </el-row>
    </el-row>
    <!--建环-->
    <el-row v-if="active_step===3" style="margin: 20px">
      <el-card class="box-card" v-for="ring in rings" :key="ring">
        <div slot="header" class="clearfix">
          <span>{{ ring }}</span>
        </div>
        <el-row>
          <el-form :inline="true">
            <el-form-item label="part_power">
              <el-input v-model="ring_configs[ring].part_power"></el-input>
            </el-form-item>
            <el-form-item label="replicas">
              <el-input v-model="ring_configs[ring].replicas"></el-input>
            </el-form-item>
            <el-form-item label="min_part_hours">
              <el-input v-model="ring_configs[ring].min_part_hours"></el-input>
            </el-form-item>
          </el-form>
        </el-row>
        <el-row v-for="host in ring_server_map[ring]" :key="host.host_name" v-if="host.length !== 0">
          <el-col :span="3" style="padding-top: 13px">
            <span style="color: #2D64B3; font-weight: bold">{{host.host_name}}</span>
          </el-col>
          <el-col :span="21">
            <el-form :inline="true">
              <el-form-item label="region">
                <el-input v-model="host.region"></el-input>
              </el-form-item>
              <el-form-item label="zone">
                <el-input v-model="host.zone"></el-input>
              </el-form-item>
            </el-form>
          </el-col>
        </el-row>
      </el-card>
    </el-row>
    <!--其它配置-->
    <el-row v-if="active_step===4" style="margin: 20px">
      <el-form label-width="120px" :model="new_cluster_data">
        <el-form-item label="statsd服务器IP" prop="statsd_host_ip">
          <el-col :span="8">
            <el-input v-model="new_cluster_data.statsd_host_ip"></el-input>
          </el-col>
        </el-form-item>
      </el-form>
    </el-row>
    <el-row style="margin: 20px" v-if="active_step !== 4">
      <el-button type="primary" @click="nextStep" :loading="isLoading">下一步</el-button>
    </el-row>
    <el-row style="margin: 20px" v-if="active_step === 4">
      <el-button type="primary" @click="submit">提交</el-button>
    </el-row>
  </div>
</template>

<script>
  import { addClusterName, createCluster } from '@/api/cluster'
  import { getClusterNodes, getNodesDetailList } from '@/api/management'
  export default {
    data() {
      return {
        new_cluster: {
          cluster_name: '',
          cluster_stat: "public"
        },
        active_step: 1,
        step_one_status: "finish", //这个finish不是代表这个步骤完成了，而是因为finish的样式比较好看
        step_two_status: "wait",
        step_three_status: "wait",
        step_four_status: "wait",
        isLoading: false,

        rules:{
          cluster_name:[
            {required: true, message: '集群名不能为空'},
          ]
        },
        servers:{
          proxy_servers: [],
          account_servers: [],
          container_servers: [],
          object_servers: [],
        },
        server_types: [
          {type: 'proxy', value: 'Proxy-Server'},
          {type: 'account', value: 'Account-Server'},
          {type: 'container', value: 'Container-Server'},
          {type: 'object', value: 'Object-Server'},
        ],
        hostList: [],
        rings: ['account-ring', 'container-ring', 'object-ring'],
        ring_configs: {
          "account-ring": {
            ring_name: 'account.ring.gz',
            part_power: '',
            replicas: '',
            min_part_hours: '',
            nodes: [],
          },
          "container-ring": {
            ring_name: 'container.ring.gz',
            part_power: '',
            replicas: '',
            min_part_hours: '',
            nodes: [],
          },
          "object-ring": {
            ring_name: 'object.ring.gz',
            part_power: '',
            replicas: '',
            min_part_hours: '',
            nodes: [],
          }
        },
        new_cluster_data: {
          cluster_name: '',
          statsd_host_ip: '',
          proxy: {
            nodes: [],
          },
          account: {},
          container: {},
          object: {},
        },
        sendMessage: '',
        jobResult: ''
      }
    },
    computed:{
      selectedProxyServers(){
        let hosts = this.hostList.filter(host=>{
          return host.checkedServers.indexOf('Proxy-Server') > -1
        })
        let tempList = []
        for(let host of hosts){
          let tmp = {
            host_name: host.node_host_name,
            ip: host.node_inet_ip,
          }
          tempList.push(tmp)
        }
        return tempList
      },
      selectedAccountServers(){
        let hosts = this.hostList.filter(host=>{
          return host.checkedServers.indexOf('Account-Server') > -1
        })
        let tempList = []
        for(let host of hosts){
          let tmp = {
            host_name: host.node_host_name,
            ip: host.node_inet_ip,
            port: '6202',
            region: '',
            zone: '',
            replication_ip: host.node_replicate_ip,
            replication_port: "6302"
          }
          tempList.push(tmp)
        }
        return tempList
      },
      selectedContainerServers(){
        let hosts = this.hostList.filter(host=>{
          return host.checkedServers.indexOf('Container-Server') > -1
        })
        let tempList = []
        for(let host of hosts){
          let tmp = {
            host_name: host.node_host_name,
            ip: host.node_inet_ip,
            port: '6201',
            region: '',
            zone: '',
            replication_ip: host.node_replicate_ip,
            replication_port: "6301"
          }
          tempList.push(tmp)
        }
        return tempList
      },
      selectedObjectServers(){
        let hosts = this.hostList.filter(host=>{
          return host.checkedServers.indexOf('Object-Server') > -1
        })
        let tempList = []
        for(let host of hosts){
          let tmp = {
            host_name: host.node_host_name,
            ip: host.node_inet_ip,
            port: '6200',
            region: '',
            zone: '',
            replication_ip: host.node_replicate_ip,
            replication_port: "6300"
          }
          tempList.push(tmp)
        }
        return tempList
      },
      ring_server_map() {
        return {
          "account-ring": this.selectedAccountServers,
          "container-ring": this.selectedContainerServers,
          "object-ring": this.selectedObjectServers,
        }
      },
    },
    methods: {
      nextStep(){
        if(this.active_step === 1){
          this.$refs['newClusterForm'].validate((valid) => {
            if (valid) {
              this.isLoading = true
              this.newCluster(this.new_cluster)
            } else {
              return false;
            }
          });
        }else if(this.active_step === 2){
          this.step_two_status = "success"
          this.step_three_status = "finish"
          this.active_step += 1
        }else if(this.active_step === 3){
          this.addNodesData()
          this.step_three_status = "success"
          this.step_four_status = "finish"
          this.active_step += 1
        }
      },
      newCluster(data){
        addClusterName(data).then(res=>{
          if(res.status === 200){
            this.isLoading = false
            this.step_one_status = "success"
            this.step_two_status = "finish"
            this.active_step += 1
          }
        }).catch(err=>{
          this.showMsg(err, "error")
          this.isLoading = false
        })
      },
      getHostList(){
        getNodesDetailList('default').then(res=>{
          if(res.status === 200&&res.data.status === 200){
            const hosts = res.data.data
            this.hostList = hosts.map(host =>{
              host.checkedServers = []
              if(host.node_role === ""){
                return host
              }
              let temp = JSON.parse(host.node_role)
              let serverTypes = Object.keys(temp)
              for(let server of serverTypes){
                if(temp[server] === 'YES'){
                  host.checkedServers.push(server)
                }
              }
              return host
            })
          }
        }).catch(err=>{
          console.log(err)
        })
      },
      createNewCluster(data){
        createCluster(data).then(res=>{
          if(res.status===201){
            this.showMsg("创建集群任务已创建","success")
          }
        }).catch(err=>{
          console.log(err)
        })
      },
      addNodesData(){
        this.ring_configs["account-ring"].nodes = this.selectedAccountServers
        this.ring_configs["container-ring"].nodes = this.selectedContainerServers
        this.ring_configs["object-ring"].nodes = this.selectedObjectServers
      },
      submit(){
        this.new_cluster_data.cluster_name = this.new_cluster.cluster_name
        this.new_cluster_data.proxy.nodes = this.selectedProxyServers
        this.new_cluster_data.account = this.ring_configs["account-ring"]
        this.new_cluster_data.container = this.ring_configs["container-ring"]
        this.new_cluster_data.object = this.ring_configs["object-ring"]
        this.createNewCluster(this.new_cluster_data)
      },
      showMsg(msg, type) {
        this.$message({
          message: msg,
          type: type
        });
      },
      // sendTaskId(){
      //   this.$socket.emit('message', this.sendMessage)
      // }
    },
    // sockets:{
    //   job_result(data){
    //     this.jobResult = data
    //   }
    // },
    created() {
      this.getHostList()
    },
    mounted() {

    },
  }
</script>
<style rel="stylesheet/scss" lang="scss" scoped>
  .clearfix:before,
  .clearfix:after {
    display: table;
    content: "";
  }
  .clearfix:after {
    clear: both
  }
  .box-card {
    width: 98%;
    margin: 10px auto;
  }
</style>
