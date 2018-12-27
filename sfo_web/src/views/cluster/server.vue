/**
* Create on 2018/7/9
*/
<template>
  <div>
    <el-row style="margin: 15px 10px;" :gutter="40">
      <el-col :offset='1' :span="18">
        <el-select v-model="selectSrvModel" filterable placeholder="请选择服务名" @change="showHostsTable" style="width: 200px">
          <el-option :key="'all'" :value="'all'" label="全部服务"></el-option>
          <el-option
            v-for="item in srvsList"
            :key="item.service_name"
            :label="item.service_name"
            :value="item.service_name">
          </el-option>
        </el-select>
        <el-button style="margin-left: 10px" type="primary" size="medium" @click="multiServiceOperation('start')">批量启动</el-button>
        <el-button type="primary" size="medium" @click="multiServiceOperation('restart')">批量重启</el-button>
        <el-button type="danger" size="medium" @click="multiServiceOperation('stop')">批量停止</el-button>
      </el-col>
      <el-col :span="4" style="float: right">
        <el-button type="primary" size="medium" round @click="showAddServiceDialog" icon="el-icon-download">安装服务</el-button>
      </el-col>
    </el-row>
    <el-row>
      <el-table
        :data="srvRelationHosts"
        @selection-change="handleSelectHosts" style="width: 95%;margin: 5px auto">
        <el-table-column
          type="selection"
          width="55">
        </el-table-column>
        <el-table-column property="service_name" label="服务名" min-width="300"></el-table-column>
        <el-table-column property="node_host_name" label="主机名" min-width="200" v-if="selectSrvModel != 'all'"></el-table-column>
        <el-table-column property="srv_stat" label="服务状态" width="200"  v-if="selectSrvModel != 'all'">
          <template slot-scope="scope">
            <span v-if="scope.row.srv_stat == 1" >
              <el-tooltip content="正常" placement="top">
                <i class="el-icon-success" style="color: #67C23A;"></i>
              </el-tooltip>
            </span>
            <span v-else-if="scope.row.srv_stat == 0">
              <el-tooltip content="停止" placement="top">
                <i class="el-icon-error" style="color: #cc0d0a;"></i>
              </el-tooltip>
            </span>
            <span v-else>
              <el-tooltip content="服务异常" placement="top">
                <i class="el-icon-info" style="color: #f0a403;"></i>
              </el-tooltip>
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" min-width="200">
          <template slot-scope="scope">
            <el-button type="text" size="mini" @click="serviceOperation('start', scope.row)" v-if="scope.row.srv_stat != 1">启动</el-button>
            <el-button type="text" size="mini" @click="serviceOperation('stop', scope.row)" v-if="scope.row.srv_stat == 1">停止</el-button>
            <el-button type="text" size="mini" @click="serviceOperation('restart', scope.row)">重启</el-button>
            <!--<el-button type="text" size="mini">卸载</el-button>-->
          </template>
          </el-table-column>
        </el-table>
    </el-row>
    <el-dialog title="安装服务" :visible.sync="dialogInstallServiceVisible">
      <el-form :model="installServiceForm" :rules="installServiceRules" ref="dialogForm">
        <el-form-item label="主机节点" prop="host_name">
          <el-select v-model="installServiceForm.host_name" placeholder="请选择节点">
            <el-option
              v-for="item in clusterNodes"
              :key="item.node_host_name"
              :label="item.node_host_name"
              :value="item.node_host_name">
            </el-option>
          </el-select>
          <span v-for="item in clusterNodes" v-if="item.node_host_name === installServiceForm.host_name"
                style="color: #8c939d">
            ip: {{ item.node_inet_ip }}
          </span>
        </el-form-item>
        <el-form-item label="安装软件" prop="service_name" >
          <el-select v-model="installServiceForm.service_name" placeholder="请选择软件包">
            <el-option
              v-for="item in installSoftWare"
              :key="item"
              :label="item"
              :value="item">
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogInstallServiceVisible = false">取 消</el-button>
        <el-button type="primary" @click="installService">确 定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
  import { getSrvs, installSrvs } from '@/api/cluster'
  import { getClusterNodes, createService } from "@/api/management";
  import { mapGetters } from 'vuex'
  import ElOption from "element-ui/packages/select/src/option";
  export default {
    components: {ElOption},
    data() {
      return {
        srvsList: [],
        installSoftWare: [],
        clusterNodes :[],
        srvRelationHosts: [],
        dialogInstallServiceVisible: false,
        selectHosts: [],
        selectSrvModel: 'all',
        selectinstallSoftWareModel: '',
        installServiceForm: {
          service_name: '',
          host_name: '',
        },
        formLabelWidth:'120px',
        installServiceRules: {
          service_name: [
            {required: true, message: '请选择安装软件', trigger: 'change'},
          ],
          host_name: [
            {required: true, message: '请选择主机名', trigger: 'change'},
          ],
        },
        actionMap: {
            "start" : "启动",
            "stop" : "停止",
            "restart" : "重启",
        }
      }
    },
    computed: {
      ...mapGetters([
        'selectedCluster',
      ])
    },
    methods: {
      handleSelectHosts(val) {
          this.selectHosts = val
      },
      showHostsTable(srv) {
        this.selectHosts = []
        this.srvRelationHosts = []
        this.getClusterSrvRealtionHosts(srv)
      },
      getClusterSrvRealtionHosts(srv) {
        let tmp = undefined
        if(srv !== 'all'){
          tmp = {"query":"service_name", "service_name": srv}
        }
        getSrvs(this.selectedCluster, tmp).then(res => {
          if (res.status === 200 && res.data.status === 200) {
            if(this.srvsList.length === 0){
                this.srvsList = res.data.data
            }
            this.srvRelationHosts = res.data.data
            this.installSoftWare = res.data.software_packages
          }
        }).catch(err => {
          console.log(err)
        })
      },
      getClusterNodes(clustername) {
        let params = {
          cluster: clustername
        }
        getClusterNodes(params).then(response => {
          if (response.status === 200 && response.data.status === 200) {
            this.clusterNodes = response.data.data
          }
        }).catch(err => {
          console.log(err)
        })
      },
      serviceOperation(action, row){
        this.$confirm(`确认${this.actionMap[action]}${row.service_name}服务?`, '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          if (this.selectSrvModel != 'all') {
            this.operationServer(action, row.service_name, row.node_host_name)
          }else{
            var serviceName = row.service_name
            var tmp = {
              "query": "service_name", "service_name": serviceName
            }
            getSrvs(this.selectedCluster, tmp).then(res => {
              if (res.status === 200 && res.data.status === 200) {
                var hostList = res.data.data
                for(var host of hostList){
                  this.operationServer(action, serviceName, host.node_host_name)
                }
              }
            }).catch(err => {
              console.log(err)
            })
          }
        }).catch(() => {
            this.showMsg('已取消操作','info')
        });

      },
      multiServiceOperation(action){
        if(this.selectHosts.length === 0){
          this.showMsg('请至少选择一个服务', 'error')
          return
        }
        if(this.selectSrvModel == 'all') {
          this.$confirm(`确认${this.actionMap[action]}${this.selectHosts.map(function (item) {
            return item.service_name
          })}服务?`, '提示', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }).then(() => {
            for (var srvName of this.selectHosts){
              var serviceName = srvName.service_name
              var tmp = {
                "query": "service_name", "service_name": serviceName
              }
              getSrvs(this.selectedCluster, tmp).then(res => {
                if (res.status === 200 && res.data.status === 200) {
                  var hostList = res.data.data
                  for(var host of hostList){
                    this.operationServer(action, serviceName, host.node_host_name)
                  }
                }
              }).catch(err => {
                console.log(err)
              })
            }
          }).catch(() => {
            this.showMsg('已取消操作','info')
          })
        }else{
          var hostMapArray = this.selectHosts.map(function (item) {
            return item.node_host_name
          })
          this.$confirm(`确认${this.actionMap[action]}${hostMapArray.join('、')} ${this.selectSrvModel}服务?`, '提示', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }).then(() => {
            for(let i=0; i<this.selectHosts.length; i++){
              this.operationServer(action,this.selectHosts[i].service_name, this.selectHosts[i].node_host_name)
            }
          }).catch(() => {
            this.showMsg('已取消操作','info')
          })
        }
      },
      showAddServiceDialog() {
        this.dialogInstallServiceVisible = true
        this.installServiceForm = {
          service_name: '',
          host_name: '',
        }
        this.$nextTick(() => {
          this.$refs['dialogForm'].clearValidate()
        })
      },
      operationServer(operation, service, host) {
        let temp = { "service": service, 'operation': operation}
        createService(host, temp).then(response => {
          if (response.status === 200 && response.data.status === 200) {
            this.$notify({
              title: '成功',
              dangerouslyUseHTMLString: true,
              message: '主机:' + host + '<br/>' + '操作:' + operation + '<br/>' + '服务:' + service + '<br/>' + '结果:' + response.data.message,
              type: 'success'
            });
          }
        }).catch(err => {
          this.$notify({
            title: '失败',
            dangerouslyUseHTMLString: true,
            message: '主机:' + host + '<br/>' + '操作:' + operation + '<br/>' + '服务:' + service + '<br/>' + '结果:' + err,
            type: 'error'
          });
        })
      },
      installService() {
        this.$refs['dialogForm'].validate((valid) => {
          if(valid) {
            installSrvs(this.selectedCluster, this.installServiceForm).then(response => {
              if (response.status === 200 && response.data.status === 200) {
                this.showMsg('安装成功', 'success')
              }
            }).catch(err => {
              this.showMsg(err, 'error')
            })
            this.dialogInstallServiceVisible = false
          }
        })
      },
      showMsg(msg, type) {
        this.$message({
          message: msg,
          type: type
        });
      },
    },
    created() {
      this.getClusterSrvRealtionHosts('all')
      this.getClusterNodes(this.selectedCluster)
    },
    mounted() {

    },
  }
</script>

<style>

</style>
