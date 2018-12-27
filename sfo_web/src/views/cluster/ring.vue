/**
* Create by wenboling on 2018/7/4
*/
<template>
  <el-row>
    <el-row style="margin: 15px 10px;" :gutter="40">
      <el-col :offset="1" :span="4">
        <el-button type="primary" :loading="listLoading" @click="handleRefresh">刷新列表</el-button>
      </el-col>
      <el-col :offset="14" :span="5">
        <el-button type="primary" @click="handleCreate">新建环</el-button>
      </el-col>
    </el-row>
    <el-row>
      <el-table :data="ringList" style="width: 90%;margin: 5px auto">
        <el-table-column prop="ring_name" label="环文件" width="230">
          <template slot-scope="scope">
            <el-tooltip effect="dark" content="点击获取详情" placement="right">
              <span class="link-type" @click="handleRingNameClick(scope.row)">{{ scope.row.ring_name }}</span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="cluster_name" label="所在集群" min-width="200"></el-table-column>
        <el-table-column prop="part_power" label="分区数" width="120"></el-table-column>
        <el-table-column prop="replicas" label="分区副本数" min-width="120"></el-table-column>
        <el-table-column prop="min_part_hours" label="最小移动间隔" min-width="130"></el-table-column>
        <el-table-column label="操作" min-width="300">
          <template slot-scope="scope">
            <el-tooltip class="item" effect="dark" content="分发" placement="top">
              <el-button size="mini" type="primary" @click="handleDistribute(scope.row)">
                <icon-svg icon-class="distribute" />
              </el-button>
            </el-tooltip>
            <el-tooltip class="item" effect="dark" content="rebalace" placement="top">
              <el-button size="mini" type="primary" @click="handleRebalance(scope.row)">
                <icon-svg icon-class="recircle" />
              </el-button>
            </el-tooltip>
            <el-tooltip class="item" effect="dark" content="添加磁盘" placement="top">
              <el-button size="mini" type="primary" @click="handleAddDisk(scope.row)">
                <icon-svg icon-class="mount" />
              </el-button>
            </el-tooltip>
            <el-tooltip class="item" effect="dark" content="删除磁盘" placement="top">
              <el-button size="mini" type="danger" @click="handleRemoveDisk(scope.row)">
                <icon-svg icon-class="umount" />
              </el-button>
            </el-tooltip>
          </template>
        </el-table-column>
      </el-table>
    </el-row>

    <!--环详情框-->
    <el-dialog :title="dialogTitle" :visible.sync="ringDetailDialogVisible" :before-close="handleDialogClose">
      <span style="white-space: pre-line;line-height: 17pt">{{ ringDetail }}</span>
    </el-dialog>

    <!--新建环框-->
    <el-dialog :title="dialogTitle" :visible.sync="createRingDialogVisible" :before-close="handleRingDialogClose"
               :close-on-press-escape="false">
      <el-form :model="ring" :rules="rules" ref="ringForm"  label-position="right" label-width="120px">
        <el-form-item label="当前集群">
          <span style="color: #00a0e9;font-size: larger;font-weight: bold">{{ selectedCluster }}</span>
        </el-form-item>
        <el-form-item label="环名称" prop="ring_name">
          <!--<el-col :span="12">-->
            <!--<el-input v-model="ring.ring_name" auto-complete="off" placeholder="名字为account、container、object或object-n"></el-input>-->
          <!--</el-col>-->
          <el-select v-model="ring.ring_name" allow-create filterable placeholder="请选择">
            <el-option
              v-for="ring in ringnames"
              :key="ring"
              :label="ring"
              :value="ring">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="分区指数幂" prop="part_power">
          <el-col :span="12">
            <el-input v-model.number="ring.part_power" auto-complete="off" placeholder="请输入一个正整数"></el-input>
          </el-col>
        </el-form-item>
        <el-form-item label="副本数" prop="replicas">
          <el-col :span="12">
            <el-input v-model.number="ring.replicas" auto-complete="off" placeholder="请输入副本数">></el-input>
          </el-col>
        </el-form-item>
        <el-form-item label="最小移动间隔" prop="min_part_hours">
          <el-col :span="12">
            <el-input v-model.number="ring.min_part_hours" auto-complete="off" placeholder="请输入一个正整数，最小为1"></el-input>
          </el-col>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="handleRingDialogClose">取 消</el-button>
        <el-button type="primary" @click="submitCreate">提 交</el-button>
      </div>
    </el-dialog>

    <!--添加磁盘到环的框-->
    <el-dialog :title="dialogTitle" :visible.sync="diskOperationDialogVisible" :before-close="handleDiskDialogClose"
               :close-on-press-escape="false">
      <el-form :model="ringDisk" :rules="rules" ref="ringDiskForm"  label-position="right" label-width="120px">
        <el-form-item label="当前环文件">
          <span style="color: #00a0e9;font-size: larger;font-weight: bold">{{ selectedRing }}</span>
        </el-form-item>
        <el-form-item label="选择主机" prop="ip">
          <el-select v-model="ringDisk.ip">
            <el-option v-for="host in hostList"
                       :key="host.host_name"
                       :label="host.host_name"
                       :value="host.host_ip">
            </el-option>
          </el-select>
          <span style="color: #8c939d" v-for="host in hostList" v-if="host.host_ip === ringDisk.ip">{{ host.host_ip }}</span>
        </el-form-item>
        <el-form-item label="端口">
          <el-col :span="8">
            <el-input v-model.number="ringDisk.port" auto-complete="off" :disabled="true"></el-input>
          </el-col>
        </el-form-item>
        <el-form-item label="region" prop="region">
          <el-col :span="8">
            <el-input v-model="ringDisk.region" auto-complete="off" placeholder="请输入region"></el-input>
          </el-col>
        </el-form-item>
        <el-form-item label="zone" prop="zone">
          <el-col :span="8">
            <el-input v-model="ringDisk.zone" auto-complete="off" placeholder="请输入zone"></el-input>
          </el-col>
        </el-form-item>
        <el-form-item label="选择磁盘" prop="device">
          <el-select v-model="ringDisk.device">
            <el-option v-for="disk in idleDisk"
                       :key="disk.guid"
                       :label="disk.disk_name"
                       :value="disk.label">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="weight" prop="weight">
          <el-col :span="8">
            <el-input v-model.number="ringDisk.weight" auto-complete="off" placeholder="请输入weight"></el-input>
          </el-col>
        </el-form-item>
        <!--<el-form-item label="专用复制网络">-->
          <!--<el-radio v-model="hasReplicationNet" label="yes">是</el-radio>-->
          <!--<el-radio v-model="hasReplicationNet" label="no">否</el-radio>-->
        <!--</el-form-item>-->
        <el-form-item label="复制网络IP" v-if="hasReplicationNet==='yes'" prop="replication_ip">
          <el-col :span="8">
            <el-input v-model="ringDisk.replication_ip" auto-complete="off" placeholder="请输入IP"></el-input>
          </el-col>
        </el-form-item>
        <el-form-item label="复制网络PORT" v-if="hasReplicationNet==='yes'" prop="replication_port">
          <el-col :span="8">
           <el-input v-model="ringDisk.replication_port" auto-complete="off" placeholder="请输入PORT" disabled></el-input>
          </el-col>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="handleDiskDialogClose">取 消</el-button>
        <el-button type="primary" @click="submitAddDisk">提 交</el-button>
      </div>
    </el-dialog>

    <!--从环删除磁盘的框-->
    <el-dialog :title="dialogTitle" :visible.sync="diskRemoveDialogVisible" :before-close="handleRemoveDiskDialogClose"
               :close-on-press-escape="false">
      <el-form :model="removeRingDisk" :rules="rules" ref="removeRingDiskForm"  label-position="right" label-width="120px">
        <el-form-item label="操作类型">
          <el-radio v-model="operationType" label="remove_disk_imm">立即删除磁盘</el-radio>
          <el-radio v-model="operationType" label="remove_disk_grad">修改磁盘权重</el-radio>
        </el-form-item>
        <el-form-item label="当前环文件">
          <span style="color: #00a0e9;font-size: larger;font-weight: bold">{{ selectedRing }}</span>
        </el-form-item>
        <el-form-item label="选择主机" prop="ip">
          <el-select v-model="removeRingDisk.ip">
            <el-option v-for="host in hostList"
                       :key="host.host_name"
                       :label="host.host_name"
                       :value="host.host_ip">
            </el-option>
          </el-select>
          <span style="color: #8c939d" v-for="host in hostList" v-if="host.host_ip === removeRingDisk.ip">{{ host.host_ip }}</span>
        </el-form-item>
        <el-form-item label="端口">
          <el-col :span="8">
            <el-input v-model.number="removeRingDisk.port" disabled></el-input>
          </el-col>
        </el-form-item>
        <el-form-item label="选择磁盘" prop="device">
          <el-select v-model="removeRingDisk.device">
            <el-option v-for="disk in diskInRing"
                       :key="disk.guid"
                       :label="disk.disk_name"
                       :value="disk.label">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="weight" prop="weight" v-if="operationType==='remove_disk_grad'">
          <el-col :span="8">
            <el-input v-model.number="removeRingDisk.weight" auto-complete="off" placeholder="请输入weight"></el-input>
          </el-col>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="handleRemoveDiskDialogClose">取 消</el-button>
        <el-button type="primary" @click="submitRemoveDisk">提 交</el-button>
      </div>
    </el-dialog>
  </el-row>
</template>

<script>
  import { getRings, createRing, modifyRing, getRingDetail, getDisks } from '@/api/cluster'
  import { mapGetters } from 'vuex'
  export default {
    data() {
      let validateRingName = (rule, value, callback) => {
        let pattern = /^((account)|(container)|(object(-([0-9]+))?))$/
        if(!pattern.test(value)){
          callback(new Error('输入的环名不正确，请重新输入！'));
        }else{
          callback();
        }
      };
      let validateInteger = (rule, value, callback) => {
        if(!Number.isInteger(value) || value < 0){
          callback(new Error('输入的格式不正确，请输入一个正整数！'));
        }else{
          callback();
        }
      };
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
        ringList: [],

        listLoading: false,
        ringDetail: '',
        ringDetailDialogVisible: false,
        createRingDialogVisible: false,
        diskOperationDialogVisible: false,
        diskRemoveDialogVisible: false,
        dialogTitle: '',
        selectedRing: '',
        hasReplicationNet: 'yes',
        ringnames: ['account', 'container', 'object'],
        ring: {
          ring_name: '',
          part_power: '',
          replicas: '',
          min_part_hours: ''
        },
        ringDisk: {
          region: '',
          zone: '',
          weight: '',
          device: '',
          ip: '',
          port: '',
          replication_ip: '',
          replication_port: '',
        },
        removeRingDisk: {
          device: '',
          ip: '',
          port: '',
          weight: '',
        },
        ring_port_map: {
          "account": [6202, 6302],
          "container": [6201, 6301],
          "object": [6200, 6300],
        },

        rules: {
          ring_name: [
            { required: true, message: '环名不能为空', trigger: 'blur'},
            {validator: validateRingName, trigger: 'blur'}
          ],
          part_power: [
            { required: true, message: '分区指数幂不能为空', trigger: 'blur'},
            {validator: validateInteger, trigger: 'blur'}
          ],
          replicas: [
            { required: true, message: '副本数不能为空', trigger: 'blur'},
            { type: 'number', message: '副本数必须为数字值', trigger: 'blur'},
          ],
          min_part_hours: [
            { required: true, message: '最小移动间隔不能为空', trigger: 'blur'},
            {validator: validateInteger, trigger: 'blur'}
          ],
          weight: [
            { required: true, message: 'weight不能为空', trigger: 'blur'},
          ],
          zone: [
            { required: true, message: 'zone不能为空', trigger: 'blur'},
          ],
          region: [
            { required: true, message: 'region不能为空', trigger: 'blur'},
          ],
          ip: [
            { required: true, message: '请选择主机', trigger: 'change'},
          ],
          device: [
            { required: true, message: '请选择磁盘', trigger: 'change'},
          ],
          replication_ip: [
            { required: true, message: 'replication_ip不能为空', trigger: 'blur'},
            {validator: validateIp, trigger: 'blur'}
          ],
          replication_port: [
            { required: true, message: 'replication_port不能为空', trigger: 'blur'},
          ]
        },
        diskList: [],
        hostList: [],
        operationType: 'remove_disk_imm',
      }
    },
    computed: {
      ...mapGetters([
        'selectedCluster',
      ]),
      idleDisk(){
        return this.diskList.filter(item => {
          if(item.host_ip === this.ringDisk.ip && item.is_used){
            return item.is_abnormal !=1 && item.is_used.indexOf(this.selectedRing) < 0 && item.is_mount == 1
          }
        })
      },
      diskInRing(){
        return this.diskList.filter(item => {
          if(item.host_ip === this.removeRingDisk.ip && item.is_used){
            return item.is_abnormal != 1 && item.is_used.indexOf(this.selectedRing) > -1 && item.is_mount == 1
          }
        })
      },
    },
    methods: {
      resetData(){
        this.ring = {
          ring_name: '',
          part_power: '',
          replicas: '',
          min_part_hours: ''
        }
      },
      resetRingDisk(){
        this.hasReplicationNet = 'yes'
        this.diskList = []
        this.hostList = []
        this.ringDisk = {
          ring_name: '',
          region: '',
          zone: '',
          weight: '',
          device: '',
          ip: '',
          port: '',
          replication_ip: '',
          replication_port: '',
        }
      },
      getDiskList(clustername){
        this.diskList = []
        getDisks(clustername).then(res=>{
          if(res.status ===200 && res.data.status === 200){
            this.diskList = res.data.data
            this.hostList = []
            let tmp = ''
            for(let disk of this.diskList){
              if(disk.host_name !== tmp) {
                this.hostList.push({
                  host_name: disk.host_name,
                  host_ip: disk.host_ip,
                })
              }
              tmp = disk.host_name
            }
          }
        }).catch(err=>{
          // console.log(err)
        })
      },
      getRingList(clustername){
        getRings(clustername).then(res=>{
          if(res.status === 200 && res.data.status === 200){
            this.ringList = res.data.data
            this.listLoading = false
          }
        }).catch(err=>{
          this.listLoading = false
          // console.log(err)
        })
      },
      getRingDetailInfo(clustername, ring_name){
        let params = {
          ring_name: ring_name
        }
        getRingDetail(clustername, params).then(res=>{
          if(res.status === 200 && res.data.status === 200){
            this.ringDetail = res.data.data
          }
        }).catch(err=>{
          this.ringDetail = err
          // this.showMsg(err, "error")
          // console.log(err)
        })
      },
      createNewRing(clustername, data){
        createRing(clustername, data).then(res=>{
          this.createRingDialogVisible = false
          this.getRingList(this.selectedCluster)
          if(res.data.status === 201){
            this.showMsg("创建成功","success")
          }
        }).catch(err=>{
          this.createRingDialogVisible = false
          this.showMsg(`创建失败${err.message}`, "error")
        })
      },
      ringOperation(clustername, data){
        modifyRing(clustername, data).then(res=>{
          if(res.data.status === 201){
            this.showMsg("执行成功","success")
          }
        }).catch(err=>{
          this.showMsg(`执行失败：${err.message}`, "error")
        })
      },
      handleRefresh(){
        this.listLoading = true
        this.getRingList(this.selectedCluster)
      },
      handleDialogClose(done){
        this.ringDetail = ''
        done()
      },
      handleRingDialogClose(){
        this.resetData()
        this.$refs['ringForm'].resetFields()
        this.createRingDialogVisible = false
      },
      handleDiskDialogClose(){
        this.resetRingDisk()
        this.$refs['ringDiskForm'].resetFields()
        this.diskOperationDialogVisible = false
      },
      handleRemoveDiskDialogClose(){
        this.removeRingDisk = {
          device: '',
          ip: '',
          port: '',
          weight: '',
        }
        this.$refs['removeRingDiskForm'].resetFields()
        this.diskRemoveDialogVisible = false
      },
      handleCreate(){
        this.dialogTitle = "新建环"
        this.resetData()
        this.createRingDialogVisible = true
        this.$nextTick(() => {
          this.$refs['ringForm'].clearValidate()
        })
      },
      handleDistribute(row){
        this.$confirm(`确定要将${row.ring_name}分发到所有节点?`, '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          let data = {
            operation: "give_away_ring",
            ring_name: row.ring_name
          }
          this.ringOperation(this.selectedCluster, data)
        }).catch(() => {
          this.$message({
            type: 'info',
            message: '已取消操作'
          });
        });
      },
      handleAddDisk(row){
        this.dialogTitle = "增添磁盘到环"
        this.diskOperationDialogVisible = true
        this.$nextTick(() => {
          this.$refs['ringDiskForm'].clearValidate()
        })
        this.selectedRing = row.ring_name
        let ring_type = this.getRingType(row.ring_name)
        this.ringDisk.port = this.ring_port_map[ring_type][0]
        this.ringDisk.replication_port = this.ring_port_map[ring_type][1]
        this.getDiskList(this.selectedCluster)
      },
      handleRemoveDisk(row){
        this.removeRingDisk = {
          device: '',
          ip: '',
          port: '',
          weight: '',
        }
        let ring_type = this.getRingType(row.ring_name)
        this.removeRingDisk.port = this.ring_port_map[ring_type][0]
        this.operationType = 'remove_disk_imm'
        this.dialogTitle = "从环删除磁盘"
        this.selectedRing = row.ring_name
        this.diskRemoveDialogVisible = true
        this.$nextTick(() => {
          this.$refs['removeRingDiskForm'].clearValidate()
        })
        this.getDiskList(this.selectedCluster)
      },
      handleRebalance(row){
        this.$confirm(`确定要对${row.ring_name}进行rebalance?`, '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          let data = {
            operation: "rebalance",
            ring_name: row.ring_name
          }
          this.ringOperation(this.selectedCluster, data)
        }).catch(() => {
          this.$message({
            type: 'info',
            message: '已取消操作'
          });
        });
      },
      handleRingNameClick(row){
        this.dialogTitle = row.ring_name
        this.ringDetailDialogVisible = true
        this.getRingDetailInfo(this.selectedCluster, row.ring_name)
      },

      submitCreate(){
        this.$refs['ringForm'].validate((valid) => {
          if(valid){
            let ring_name = this.ring.ring_name
            let tmp = this.ringList.find(ring=>{
              return ring.ring_name.indexOf(ring_name) >= 0
            })
            if(tmp){
              this.showMsg(`${ring_name}环已存在，请重新输入`, "error")
              return
            }
            // console.log(this.ring)
            this.createNewRing(this.selectedCluster, this.ring)
          }else{
            this.showMsg("输入的格式有问题，请检查", "error")
          }
        })
      },
      submitAddDisk(){
        this.$refs['ringDiskForm'].validate((valid)=>{
          if(valid){
            let data = Object.assign({}, this.ringDisk)
            data.ring_name = this.selectedRing
            data.operation = "add_disk_cluster"
            if(data.replication_ip === ""){
              delete data.replication_ip
              delete data.replication_port
            }
            this.ringOperation(this.selectedCluster, data)
            this.diskOperationDialogVisible = false
            this.resetRingDisk()
          }else {
            this.showMsg("输入的格式有问题，请检查", "error")
          }
        })
      },
      submitRemoveDisk(){
        this.$refs['removeRingDiskForm'].validate((valid)=>{
          if(valid){
            let data = Object.assign({}, this.removeRingDisk)
            data.ring_name = this.selectedRing
            data.operation = this.operationType
            if(data.weight === ""){
              delete data.weight
            }
            this.ringOperation(this.selectedCluster, data)
            this.diskRemoveDialogVisible = false
            this.resetRingDisk()
          }else {
            this.showMsg("输入的格式有问题，请检查", "error")
          }
        })
      },

      getRingType(ring_name){
        if(ring_name.indexOf('object') > -1){
          return 'object'
        }else if(ring_name.indexOf('account') > -1){
          return 'account'
        }else if(ring_name.indexOf('container')> -1){
          return 'container'
        }
      },
      showMsg(msg, type) {
        this.$message({
          message: msg,
          type: type
        });
      },
    },
    created() {
      this.getRingList(this.selectedCluster)
    },
    mounted() {
    },
  }
</script>
<style rel="stylesheet/scss" lang="scss" scoped>
  .link-type,
  .link-type:focus {
    color: #337ab7;
    cursor: pointer;
    &:hover {
      color: rgb(32, 160, 255);
    }
  }
</style>
