/**
* Create by wenboling on 2018/4/23
*/

<template>
  <div>
    <el-row>
      <div style="float:left;margin: 25px 100px 10px 100px;">
        <el-radio-group v-model="nodeListRadio" @change="nodeListSelect">
          <el-radio-button label="current" >当前集群</el-radio-button>
          <el-radio-button  label="noequ" >未配备</el-radio-button>
        </el-radio-group>
      </div>
      <div style="float:right;margin: 10px 100px 10px 0;">
        <el-button type="primary" @click="handleCreate">新建</el-button>
      </div>
    </el-row>
    <el-row style="margin: 5px">
      <el-table :data="nodeList" style="width: 98%; margin: 0px auto">
        <el-table-column prop="cluster_name" label="集群名" min-width="200"></el-table-column>
        <el-table-column prop="node_host_name" label="主机名" width="160"></el-table-column>
        <el-table-column prop="node_inet_ip" label="IP地址" width="160"></el-table-column>
        <el-table-column prop="node_replicate_ip" label="复制IP" width="160"></el-table-column>
        <el-table-column prop="node_role" label="节点角色" min-width="300">
          <template slot-scope="scope">
            <span>{{ scope.row.node_role | translateServerType}}</span>
          </template>
        </el-table-column>
        <el-table-column prop="add_time" label="增添时间" width="200"></el-table-column>
        <el-table-column label="操作" width="200">
          <template slot-scope="scope">
            <el-button size="mini" type="primary" icon="el-icon-edit" @click="handleUpdate(scope.row)"></el-button>
            <!--<el-button size="mini" type="danger" icon="el-icon-delete" @click="handleDelete(scope.row)"></el-button>-->
            <el-button size="mini" type="info" icon="el-icon-setting" @click="showNodeManager(scope.row)"></el-button>
          </template>
        </el-table-column>
        <!--<el-table-column-->
          <!--label="服务状态"-->
          <!--width="55"-->
          <!--prop="service">-->
        <!--</el-table-column>-->
      </el-table>
    </el-row>

    <!--执行任务框-->
    <el-dialog
      title="提示"
      :visible.sync="srvDialogVisible"
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
    <!--新建框-->
    <el-dialog :title="titleMap[dialogStatus]" :visible.sync="dialogVisible" :before-close="cancelAdd">
      <el-form :model="temp" :rules="rules" :label-width="formLabelWidth" label-position="left" ref="dialogForm" style='width: 100%; margin-left:20px;'>
        <el-form-item prop="node_host_name" label="主机名">
          <el-col :span="12">
            <el-input v-model="temp.node_host_name" auto-complete="off"></el-input>
          </el-col>
        </el-form-item>
        <el-form-item prop="node_inet_ip" label="IP地址">
          <el-col :span="12">
            <el-input v-model="temp.node_inet_ip" auto-complete="off"></el-input></el-col>
        </el-form-item>
        <el-form-item prop="node_replicate_ip" label="复制IP">
          <el-col :span="12">
            <el-input v-model="temp.node_replicate_ip" auto-complete="off"></el-input></el-col>
        </el-form-item>
        <el-form-item prop="node_role" label="节点角色">
          <el-checkbox-group v-model="checkedServers">
            <el-checkbox v-for="server in servers" :label="server" :key="server">{{server}}</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="安装相关服务">
          <el-checkbox v-model="temp.auto_install_srv">是</el-checkbox>
          <el-col v-if="temp.auto_install_srv == true">提示:软件安装过程需要等待1-3分钟</el-col>
        </el-form-item>
        <el-form-item label="添加到集群">
          <el-radio v-model="add_to_cluster" label="yes">是</el-radio>
          <el-radio v-model="add_to_cluster" label="no">否</el-radio>
        </el-form-item>
        <el-form-item v-if="add_to_cluster==='yes'" prop="cluster_name" label="选择集群">
          <el-select v-model="temp.cluster_name">
            <el-option v-for="cluster in clusterList"
                       :key="cluster.cluster_name"
                       :label="cluster.cluster_name"
                       :value="cluster.cluster_name">
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click.native="cancelAdd()">取消</el-button>
        <el-button v-if="dialogStatus==='create'" type="primary" @click.native="createNode" :loading="addLoading">提交</el-button>
        <el-button v-else  @click.native="updateNode" type="primary" :loading="addLoading">提交</el-button>
      </div>
    </el-dialog>

    <!--执行详细信息框-->
    <el-dialog :title="titleMap[dialogStatus]" :visible.sync="dialogServiceInfoVisible" :before-close="closeServiceInfoDialog" :width="'80%'">
      <el-main>
          <el-table :data="tasks" style="width: 100%; margin: 0px auto">
            <el-table-column
              type="expand">
              <template slot-scope="props">
                <el-form label-position="left" inline class="demo-table-expand" label-width="120">
                  <el-form-item label="任务ID">
                    <span>{{ props.row.guid }}</span>
                  </el-form-item>
                  <el-form-item label="主机名">
                    <span>{{ props.row.node_host_name }}</span>
                  </el-form-item>
                  <el-form-item label="执行人">
                    <span>{{ props.row.create_user }}</span>
                  </el-form-item>
                  <el-form-item label="执行操作">
                    <span>{{ operationMap[props.row.operation] }}</span>
                  </el-form-item>
                  <el-form-item label="服务类型">
                    <span>{{ srvMap[props.row.service_type] }}</span>
                  </el-form-item>
                  <el-form-item label="执行服务">
                    <span>{{ serviceMap[props.row.service_name] }}</span>
                  </el-form-item>
                  <el-form-item label="执行步骤">
                    <span>{{ props.row.service_task_running_flag }}</span>
                  </el-form-item>
                  <el-form-item label="执行状态">
                    <span>{{ endingMap[props.row.service_task_ending_flag] }}</span>
                  </el-form-item>
                  <el-form-item label="任务开始时间">
                    <span>{{ props.row.task_start_time }}</span>
                  </el-form-item>
                  <el-form-item label="任务结束时间">
                    <span>{{ props.row.task_end_time }}</span>
                  </el-form-item>
                </el-form>
              </template>
            </el-table-column>
            <el-table-column
              prop="node_host_name"
              label="主机名">
            </el-table-column>
            <el-table-column
              label="执行操作">
              <template slot-scope="scope">
                <span>{{ operationMap[scope.row.operation] }}</span>
              </template>
            </el-table-column>
            <el-table-column
              label="服务类型" >
              <template slot-scope="scope">
                <span>{{ srvMap[scope.row.service_type] }}</span>
              </template>
            </el-table-column>
            <el-table-column
              label="执行服务">
              <template slot-scope="scope">
                <span>
                 {{ serviceMap[props.row.service_name] }}
                </span>
              </template>
            </el-table-column>
            <el-table-column
              label="执行状态">
              <template slot-scope="scope">
                <span>{{ endingMap[scope.row.service_task_ending_flag] }}</span>
              </template>
            </el-table-column>
            <el-table-column
              prop="task_start_time"
              label="任务开始时间">
            </el-table-column>
            <el-table-column
              prop="task_end_time"
              label="任务结束时间">
            </el-table-column>
            <el-table-column
              label="操作">
              <template slot-scope="scope">
                <el-button
                  @click.native.prevent="taskDetail(scope.row.guid)"
                  type="text"
                  size="small">
                  查看日志详情
                </el-button>
              </template>
            </el-table-column>
          </el-table>
      </el-main>
      <el-footer></el-footer>
    </el-dialog>

    <!---节点管理框--->
    <el-dialog :title="titleMap[dialogStatus]" :visible.sync="dialogManagerVisible" width="80%" :before-close="closeManageDialog">
      <el-row style="margin-left: 10px; margin-bottom: 10px">
        <span style="color: #8c939d">当前主机: {{ temp.node_host_name }}({{temp.node_inet_ip}})</span>
      </el-row>
      <el-row :gutter="20" >
        <el-tabs :tab-position="'left'" style="height: 500px;" v-model="activeTab">
          <el-tab-pane label="配置修改" name="config"><span slot="label"><i class="el-icon-date"></i> 配置修改</span>
            <el-row :gutter="20">
              <el-col>
                <el-radio-group v-model="editorMode">
                  <el-radio-button
                    label="edit"
                    @click.native="setEditorMode"><i class="el-icon-edit"></i>编辑模式</el-radio-button>
                  <el-radio-button
                    label="readonly"
                    @click.native="setReadOnlyMode"><i class="el-icon-view"></i>查看模式</el-radio-button>
                </el-radio-group>
                <el-button
                  type="primary"
                  icon="el-icon-upload"
                  @click="updateConfigContent"
                  :disabled="editorMode==='readonly'">更新配置</el-button>
                <el-select v-model="selectedConfigFile" placeholder="请选择配置文件" @change="getContentFromConfigFile">
                  <el-option v-for="(file,index) in nodeRow.list"
                             :key="index"
                             :lable="file"
                             :value="file">
                  </el-option>
                </el-select>
              </el-col>
            </el-row>
            <el-row style="margin: 10px">
              <span v-if="selectedConfigFile">当前选择的配置文件：
                <span style="color: #00a0e9;font-size: large">{{ selectedConfigFile }}</span>
              </span>
              <span v-else>请先选择配置文件</span>
            </el-row>
          </el-tab-pane>
          <el-tab-pane label="服务启停" name="service"><span slot="label"><i class="el-icon-date"></i> 服务启停</span>
            <el-row style="margin-bottom: 10px">
              <el-col>
                <el-button icon="el-icon-circle-check" type="success" @click="startNodeService">启动所有服务</el-button>
                <el-button icon="el-icon-warning" type="warning" @click="stopNodeService">停止所有服务</el-button>
                <el-button icon="el-icon-circle-check" type="info" @click="showServiceInfo">操作记录</el-button>
              </el-col>
            </el-row>
            <el-row class="pane-row">
              <el-scrollbar wrap-class="list" wrap-style="color: red;" view-style="font-weight: bold;" view-class="view-box" :native="false">
                <el-card style="width: 80%;margin-bottom: 10px" v-if="isProxyServer">
                  <div slot="header" class="clearfix">
                    <span>proxy</span>
                  </div>
                  <div class="clearfix">
                    <template v-for="(item, index) in status_data.proxy">
                      <div  class="srv_status">
                        <label>{{ index.substr(4) }}</label>
                        <span><el-tag :type="el_tag_type[item]">{{ item }}</el-tag></span>
                        <svg v-if="item==='stopped'" class="my-svg-icon" aria-hidden="true" @click="controlNodeSrv(index.substr(4), 'start')">
                          <use xlink:href="#icon-start"></use>
                        </svg>
                        <svg v-if="item==='running'" class="my-svg-icon" aria-hidden="true" @click="controlNodeSrv(index.substr(4), 'stop')">
                          <use xlink:href="#icon-stop"></use>
                        </svg>
                        <svg v-if="item==='running'" class="my-svg-icon" aria-hidden="true" @click="controlNodeSrv(index.substr(4), 'restart')">
                          <use xlink:href="#icon-restart"></use>
                        </svg>
                      </div>
                    </template>
                  </div>
                </el-card>
                <el-card style="width: 80%;margin-bottom: 10px" v-if="isAccountServer">
                  <div slot="header" class="clearfix">
                    <span>account</span>
                  </div>
                  <div class="clearfix">
                    <template v-for="(item, index) in status_data.account">
                      <div  class="srv_status">
                        <label>{{ index.substr(4) }}</label>
                        <span><el-tag :type="el_tag_type[item]">{{ item }}</el-tag></span>
                        <svg v-if="item==='stopped'" class="my-svg-icon" aria-hidden="true" @click="controlNodeSrv(index.substr(4), 'start')">
                          <use xlink:href="#icon-start"></use>
                        </svg>
                        <svg v-if="item==='running'" class="my-svg-icon" aria-hidden="true" @click="controlNodeSrv(index.substr(4), 'stop')">
                          <use xlink:href="#icon-stop"></use>
                        </svg>
                        <svg v-if="item==='running'" class="my-svg-icon" aria-hidden="true" @click="controlNodeSrv(index.substr(4), 'restart')">
                          <use xlink:href="#icon-restart"></use>
                        </svg>
                      </div>
                    </template>
                  </div>
                </el-card>
                <el-card style="width: 80%;margin-bottom: 10px" v-if="isContainerServer">
                  <div slot="header" class="clearfix">
                    <span>container</span>
                  </div>
                  <div class="clearfix">
                    <template v-for="(item, index) in status_data.container">
                      <div  class="srv_status">
                        <label>{{ index.substr(4) }}</label>
                        <span><el-tag :type="el_tag_type[item]">{{ item }}</el-tag></span>
                        <svg v-if="item==='stopped'" class="my-svg-icon" aria-hidden="true" @click="controlNodeSrv(index.substr(4), 'start')">
                          <use xlink:href="#icon-start"></use>
                        </svg>
                        <svg v-if="item==='running'" class="my-svg-icon" aria-hidden="true" @click="controlNodeSrv(index.substr(4), 'stop')">
                          <use xlink:href="#icon-stop"></use>
                        </svg>
                        <svg v-if="item==='running'" class="my-svg-icon" aria-hidden="true" @click="controlNodeSrv(index.substr(4), 'restart')">
                          <use xlink:href="#icon-restart"></use>
                        </svg>
                      </div>
                    </template>
                  </div>
                </el-card>
                <el-card style="width: 80%;margin-bottom: 10px" v-if="isObjectServer">
                  <div slot="header" class="clearfix">
                    <span>object</span>
                  </div>
                  <div class="clearfix">
                    <template v-for="(item, index) in status_data.object">
                      <div  class="srv_status">
                        <label>{{ index.substr(4) }}</label>
                        <span><el-tag :type="el_tag_type[item]">{{ item }}</el-tag></span>
                        <svg v-if="item==='stopped'" class="my-svg-icon" aria-hidden="true" @click="controlNodeSrv(index.substr(4), 'start')">
                          <use xlink:href="#icon-start"></use>
                        </svg>
                        <svg v-if="item==='running'" class="my-svg-icon" aria-hidden="true" @click="controlNodeSrv(index.substr(4), 'stop')">
                          <use xlink:href="#icon-stop"></use>
                        </svg>
                        <svg v-if="item==='running'" class="my-svg-icon" aria-hidden="true" @click="controlNodeSrv(index.substr(4), 'restart')">
                          <use xlink:href="#icon-restart"></use>
                        </svg>
                      </div>
                    </template>
                  </div>
                </el-card>
              </el-scrollbar>
            </el-row>
          </el-tab-pane>
        </el-tabs>
      </el-row>
    </el-dialog>
  </div>
</template>

<script>
  import { getClusterNodes, createClusterNode, updateClusterNode , delClusterNode ,
    getConfigFileContent , updateConfigFileContent , getServiceTasks , createService, getManagerLog, up_downSrv } from "@/api/management";
  import { getNodeSrvDetail } from '@/api/monitor'
  import { getClusters } from "@/api/dashboard";
  import { mapGetters } from 'vuex'
  import { getSrvs } from '@/api/cluster'
  import LoadingAnimation  from '@/components/LoadingAnimation'

  export default {
    data() {
      let validateIp = (rule, value, callback) => {
        // let ip = /^([1-9]|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])(\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])){3}$/
        let ip = /^(([01]?[\d]{1,2})|(2[0-4][\d])|(25[0-5]))(\.(([01]?[\d]{1,2})|(2[0-4][\d])|(25[0-5]))){3}$/
        if (!ip.test(value)) {
          callback(new Error('输入IP格式不正确，请重新输入！'));
        }else{
          callback();
        }
      };
      return {
        activeTab: 'config',
        titleMap: {
          'create': '新建',
          'update': '编辑',
          'manager': '管理',
          "message": '详细信息'
        },
        serviceMap: {
          "proxy": '代理服务',
          "account": '账户服务',
          "account-auditor": '账户-审计服务',
          "account-replicator": '账户-复制服务',
          "account-reaper": '账户-隔离服务',
          "container": '容器服务',
          "container-auditor": '容器-审计服务',
          "container-replicator": '容器-复制服务',
          "container-sync": '容器-同步服务',
          "container-updater": '容器-更新服务',
          "container-reconciler": '容器-调解服务',
          "object": '对象',
          "object-auditor": '对象-审计服务',
          "object-replicator": '对象-复制服务',
          "object-updater": '对象-更新服务',
          "object-expirer": '对象-过期服务',
          "object-reconstructor": '对象-再现服务',
        },
        endingMap: {
          "0": '处理中',
          "1": '已完成'
        },
        srvMap: {
            "node_manager": "节点管理服务"
        },
        operationMap: {
            "start": "启动",
            "stop": "停止",
            "restart": "重启",
        },
        dialogStatus: '',
        nodeList: [],
//        clusters: [{
//            "label":'',
//            "value":"",
//        }],
        hostSrvs: [],
        nodeListRadio:'current',
        multipleSelection: [],
        dialogManagerVisible: false,
        dialogServiceInfoVisible: false,
        nodeRow: {
            row: '',
            list: [],
        },
        tasks: [],
        radio: '',
        editorMode: 'readonly',
        ue: {
          container: '',
          content: ''
        },

        dialogVisible: false,
        addLoading: false,
        temp: {
          cluster_name: '',
          node_host_name: '',
          node_inet_ip: '',
          node_replicate_ip: '',
          node_role: '',
          auto_install_srv: '',
        },
        add_to_cluster: 'yes',
        formLabelWidth: '100px',
        isIndeterminate: true,
        servers: ['Proxy-Server', 'Container-Server', 'Account-Server', 'Object-Server'],
        node_role: {
          'Proxy-Server': 'NO',
          'Container-Server': 'NO',
          'Account-Server': 'NO',
          'Object-Server': 'NO',
        },
        checkedServers: [],
        rules: {
          node_host_name: [
            {required: true, message: '请输入主机名', trigger: 'blur'}
          ],
          node_inet_ip: [
            {required: true, message: '请输入主机IP', trigger: 'blur'},
            {validator: validateIp, trigger: 'blur'}
          ],
          // node_replicate_ip: [
          //   {required: true, message: '请输入复制IP', trigger: 'blur'},
          //   {validator: validateIp, trigger: 'blur'}
          // ],
          cluster_name: [
            { required: true, message: '请选择集群', trigger: 'change' }
          ],
        },
        clusterList: [],

        status_data: {},
        el_tag_type:{
          running: 'success',
          stopped: 'danger',
          warning: 'warning'
        },
        //dialog数据
        cmd_result: '',
        srvDialogVisible: false,
        isWaiting: false,
        selectedConfigFile: '',
      }
    },
    computed: {
      ...mapGetters([
        'selectedCluster',
      ]),
      isProxyServer(){
        if(this.temp.node_role){
          let node_role = JSON.parse(this.temp.node_role)
          return node_role["Proxy-Server"] === 'YES'
        }
        return false
      },
      isAccountServer(){
        if(this.temp.node_role){
          let node_role = JSON.parse(this.temp.node_role)
          return node_role["Account-Server"] === 'YES'
        }
        return false
      },
      isContainerServer(){
        if(this.temp.node_role) {
          let node_role = JSON.parse(this.temp.node_role)
          return node_role["Container-Server"] === 'YES'
        }
        return false
      },
      isObjectServer(){
        if(this.temp.node_role) {
          let node_role = JSON.parse(this.temp.node_role)
          return node_role["Object-Server"] === 'YES'
        }
        return false
      }
    },
    components: {
      LoadingAnimation
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
            result = result + server + '  '
          }
        }
        return result
      }
    },
    methods: {
      cancelAdd: function () {
        this.dialogVisible = false;
        this.$refs['dialogForm'].resetFields();
        this.resetData()
      },
      closeManageDialog(done){
        this.delayReboot = ''
        this.rebootAt = ''
        this.hostSrvs = []
        done()
      },
      closeServiceInfoDialog(done){
        this.delayReboot = ''
        this.rebootAt = ''
        this.dialogStatus = 'manager'
        done()
      },
      resetData: function () {
        this.node_role = {
          'Proxy-Server': 'NO',
          'Container-Server': 'NO',
          'Account-Server': 'NO',
          'Object-Server': 'NO',
        }
        this.checkedServers = []
      },
      resetTemp() {
        this.temp = {
          cluster_name: '',
          node_host_name: '',
          node_inet_ip: '',
          node_replicate_ip: '',
          node_role: '',
          auto_install_srv: '',
        }
      },
      nodeListSelect() {
        this.nodeList = []
        if(this.nodeListRadio === "current"){
          this.getNodes(this.selectedCluster)
        }else{
          this.getNodes()
        }
      },
      getClusterList(){
        getClusters().then(response => {
          if(response.data.status === 200 && response.status === 200){
            this.clusterList = response.data.data
          }
        }).catch(error => {
          console.log("!!!!!", error)
        })
      },
      getNodes(clusterName){
        let params = {
          cluster: clusterName
        }
        getClusterNodes(params).then(response=>{
          if(response.status == 200){
            this.nodeList = response.data.data
          }
        })
      },
      handleCreate() {
        this.getClusterList()
        this.resetTemp()
        this.dialogStatus = 'create'
        this.dialogVisible = true
        this.$nextTick(() => {
          this.$refs['dialogForm'].clearValidate()
        })
      },
      handleUpdate(row) {
        this.getClusterList()
        this.temp = Object.assign({}, row)
        if(this.temp.node_role.length !== 0){
          let tmp = JSON.parse(this.temp.node_role)
          for(let server in tmp){
            if(tmp.hasOwnProperty(server)){
              if(tmp[server] === 'YES'){
                this.checkedServers.push(server)
              }
            }
          }
        }
        this.dialogStatus = 'update'
        this.dialogVisible = true
        this.$nextTick(() => {
          this.$refs['dialogForm'].clearValidate()
        })
      },
      handleDelete(row) {
        this.$confirm(`确认删除主机: ${row.node_host_name}?`, '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          this.delNode(row.guid)
        }).catch(() => {
          this.showMsg('已取消删除', 'info')
        });
      },

      createNode() {
        this.$refs['dialogForm'].validate((valid) => {
          if(valid) {
            for(let server of this.checkedServers){
              this.node_role[server] = 'YES'
            }
            this.temp.node_role = JSON.stringify(this.node_role)
            let para = Object.assign({}, this.temp);
            createClusterNode(para).then(response=>{
              if(response.status === 200){
                this.showMsg('创建成功', 'success')
                this.nodeListSelect()
              }
            }).catch(err=>{
              this.showMsg(`创建失败${err}`, 'error')
            })
            this.$refs['dialogForm'].resetFields();
            this.resetData();
            this.dialogVisible = false;
          }
        })
      },
      updateNode(row) {
        this.$refs['dialogForm'].validate((valid) => {
          if(valid) {
            for(let server of this.checkedServers){
              this.node_role[server] = 'YES'
            }
            this.temp.node_role = JSON.stringify(this.node_role)
            let para = Object.assign({}, this.temp);
            updateClusterNode(para.guid, para).then(response=>{
              if(response.status === 200){
                this.showMsg('更新成功', 'success')
                this.nodeListSelect()
                this.$refs['dialogForm'].resetFields();
                this.resetData();
                this.dialogVisible = false;
              }
            }).catch(err=>{
              this.showMsg(`更新失败${err}`, 'error')
              this.nodeListSelect()
              this.$refs['dialogForm'].resetFields();
              this.resetData();
              this.dialogVisible = false;
            })
          }
        })
      },
      delNode(guid){
        delClusterNode(guid).then(response => {
          if(response.status === 200){
            this.showMsg('删除成功', 'success')
          }
          this.nodeListSelect()
        }).catch(err=>{
          this.showMsg(`删除失败${err}`, 'error')
        })
      },

      showMsg(msg, type) {
        this.$message({
          message: msg,
          type: type
        });
      },

      serviceSwitch(row) {
          console.log(row)
      },
      showNodeManager(row) {
        this.activeTab = 'config'
        this.dialogManagerVisible = true
        this.tasks = []
        this.getHostSrvs(row)
        this.getSrvsStatus(row.node_host_name)
        this.temp = Object.assign({}, row)
        this.dialogStatus = 'manager'
        this.nodeRow.row = row
        this.getConfigs(this.nodeRow.row)
        this.radio = ''
        this.editorMode = 'readonly'
        this.selectedConfigFile = ''
      },

      showServiceInfo(){
        this.dialogStatus = 'message'
        this.dialogServiceInfoVisible = true
        this.initServiceTasks(this.nodeRow.row.node_host_name)
      },
      getContentFromConfigFile(filename){
        let params = {"hostname": this.nodeRow.row.node_host_name,"filename":filename}
        getConfigFileContent(params).then(response =>{
          if(response.status == 200){
            this.editorMode = 'readonly'
            console.log(response.data)
          }
        }).catch(err=>{
          this.showMsg(`获取配置信息失败${err}`, 'error')
        })
      },
      getConfigs(row){
        let params = {"hostname":row.node_host_name}
        getConfigFileContent(params).then(response =>{
          if(response.status == 200){
            this.nodeRow.list = response.data.data
          }
        }).catch(err=>{
          this.showMsg(`获取配置文件列表失败${err}`, 'error')
        });
      },
      updateConfigContent() {
        const filename = this.nodeRow.list[this.radio]
        let updateTemp = {"hostname":this.nodeRow.row.node_host_name,"filename":filename, "configContent":this.ue.container.getContent()}
        updateConfigFileContent(updateTemp).then(response =>{
          if(response.status === 200 && response.data.status === 200){
            this.$notify({
              title: '更新成功',
              dangerouslyUseHTMLString: true,
              message: err,
              type: 'success'
            })
          }
        }).catch(err => {
          this.$notify({
            title: '失败',
            dangerouslyUseHTMLString: true,
            message: err,
            type: 'error'
          })
        });
      },
      setEditorMode(){

      },
      setReadOnlyMode() {

      },
      startNodeService() {
        this.$confirm('此操作将启动服务, 是否继续?', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'info'
        }).then(() => {
          this.ServiceLogic('start')
        }).catch(() => {
          this.$message({
            type: 'info',
            message: '已取消'
          })
        })
      },
      getHostSrvs(row){
        let tmp = {"query":"node_host_name", "node_host_name": row.node_host_name}
        getSrvs(this.selectedCluster, tmp).then(res => {
          if (res.status === 200 && res.data.status === 200) {
            this.hostSrvs = res.data.data
          }
        }).catch(err => {
          console.log(err)
        })
      },
      stopNodeService() {
        this.$confirm('此操作将停止服务, 是否继续?', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          this.ServiceLogic('stop')
        }).catch(() => {
          this.$message({
            type: 'info',
            message: '已取消'
          });
        });
      },
      ServiceLogic(operation){
        for(var i=0; i<this.hostSrvs.length; i++) {
          let nodeServiceTemp = { "service": this.hostSrvs[i].service_name, "operation": operation}
          createService(this.nodeRow.row.node_host_name, nodeServiceTemp).then(response =>{
            if (response.status === 200 && response.data.status === 200){
              this.$notify({
                title: '成功',
                dangerouslyUseHTMLString: true,
                message: '主机:' + this.nodeRow.row.node_host_name + '<br/>' + '操作:' + operation + '<br/>' + '服务:' + this.hostSrvs[i].service_name + '<br/>' + '结果:' + response.data.message,
                type: 'success'
              })
            }
          }).catch(err => {
            this.$notify({
              title: '失败',
              dangerouslyUseHTMLString: true,
              message: '主机:' + this.nodeRow.row.node_host_name + '<br/>' + '操作:' + operation + '<br/>' + '服务:' + this.hostSrvs[i].service_name + '<br/>' + '结果:' + err,
              type: 'error'
            })
          })
        }
      },
      initServiceTasks(hostname) {
        let taskTemp = {"query":"node_host_name-service_type", "node_host_name":hostname, "service_type": "node_manager"}
        getServiceTasks(taskTemp).then(response=>{
          if(response.status == 200){
            this.tasks = response.data.data
            console.log(this.tasks)
          }
        })
      },
      taskDetail(taskid){
        getManagerLog(taskid).then(response =>{
          if(response.status == 200){
              console.log(response.data.data)
          }
        })
      },
      //服务管理
      getSrvsStatus(node_host_name){
        getNodeSrvDetail(node_host_name).then(res=>{
          if(res.status === 200 && res.data.status === 200){
            this.status_data = res.data.data
          }
        }).catch(err=>{
          console.log(err)
        })
      },
      controlNodeSrv(service_name, action){
        this.$confirm(`确认执行操作: ${action} ${this.temp.node_host_name} 的 ${service_name}?`, '警告', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
          closeOnClickModal: false
        }).then(()=>{
          let action_data={
            action: action,
            service: service_name
          }
          this.manageSrv(this.temp.node_host_name, action_data)
        })
      },
      manageSrv(hostname, action_data){
        this.srvDialogVisible = true
        this.isWaiting = true
        up_downSrv(hostname, action_data).then(res=>{
          if(res.status===200){
            this.cmd_result = res.data.message
            this.isWaiting = false
          }
        }).catch(err=>{
          this.cmd_result = "failed:" + err
          this.isWaiting = false
        })
      },
      handleCloseDialog(){
        this.getSrvsStatus(this.temp.node_host_name)
        this.srvDialogVisible = false
      },
    },
    created(){
      this.getNodes(this.selectedCluster)
    },
    mounted(){
    },
  }
</script>

<style rel="stylesheet/scss" lang="scss" scoped>
  .demo-table-expand {
    font-size: 0;
  }
  .demo-table-expand label {
    width: 120px;
    color: #99a9bf;
  }
  .demo-table-expand .el-form-item {
    margin-right: 0;
    margin-bottom: 0;
    width: 50%;
  }
  .top25 {
    margin-top: 25px;
  }
  input::-webkit-outer-spin-button,
  input::-webkit-inner-spin-button {
    -webkit-appearance: none;
  }
  input[type="number"]{
    -moz-appearance: textfield;
  }
  .srv_status {
    width: 50%;
    float: left;
    margin-bottom: 5px;
  }
  .list {
    max-height: 480px;
    padding-bottom: 10px;
  }
  .el-scrollbar__wrap {
    overflow: visible;
    overflow-x: hidden;
  }
  .my-svg-icon {
    width: 1.2em;
    height: 1.2em;
    vertical-align: -0.15em;
    fill: currentColor;
    overflow: hidden;
    &:hover{
      cursor: pointer;
    }
  }
</style>
