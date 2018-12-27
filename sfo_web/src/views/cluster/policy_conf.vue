/**
* Create by wenboling on 2018/5/2
*/

<template>
  <div>
    <el-row style="margin: 15px">
      <el-button style="float: right" type="primary" @click="showAddPolicyDialog">添加策略</el-button>
    </el-row>
    <el-row style="margin: 15px">
      <el-table :data="policyList" style="width: 90%; margin: 0 auto">
        <el-table-column prop="policy_num" label="策略编号"></el-table-column>
        <el-table-column prop="policy_name" label="策略名"></el-table-column>
        <el-table-column label="策略类型">
          <template slot-scope="scope">
            <span>{{ policyTypeMap[scope.row.policy_type] }}</span>
          </template>
        </el-table-column>
        <el-table-column label="策略状态">
          <template slot-scope="scope">
            <span v-if="scope.row.deprecated == 'no'"><i class="el-icon-success" style="color: #6ce26c"></i>使用中</span>
            <span v-else><i class="el-icon-error" style="color: #dd280d"></i>已弃用</span>
          </template>
        </el-table-column>
        <!--<el-table-column prop="add_time" label="创建时间"></el-table-column>-->
        <el-table-column label="操作">
          <template slot-scope="scope">
            <span v-if="scope.row.deprecated == 'no'">
              <el-button size="mini" type="danger" icon="el-icon-delete" @click="ensuredeprecatedPolicy(scope.row)">弃用</el-button>
            </span>
          </template>
        </el-table-column>
      </el-table>
    </el-row>

    <!--新建策略对话框-->
    <el-dialog title="新建策略" :visible.sync="dialogAddPolicyVisible" :before-close="cancelAdd">
      <el-form :model="addPolicyForm" :rules="addPolicyRules" ref="dialogForm" :label-position="labelPosition" label-width="120px" style='width: 100%; margin-left:20px;'>
        <el-form-item label="策略编码" prop="policy_num">
          <el-col :span="10">
            <el-input v-model="addPolicyForm.policy_num"></el-input>
          </el-col>
        </el-form-item>
        <el-form-item label="策略名" prop="policy_name">
          <el-col :span="10">
            <el-input v-model="addPolicyForm.policy_name"></el-input>
          </el-col>
        </el-form-item>
        <el-form-item label="策略类型" prop="policy_type">
            <el-col :span="10">
              <el-radio-group v-model="addPolicyForm.policy_type">
                <el-radio label="replication" >{{ policyTypeMap["replication"] }}</el-radio>
                <el-radio label="erasure_coding" >{{ policyTypeMap["erasure_coding"] }}</el-radio>
              </el-radio-group>
            </el-col>
        </el-form-item>
        <el-form-item label="同步建环" prop="deprecated">
          <el-col :span="10">
            <el-checkbox v-model="autoCreateRingChecked">是</el-checkbox>
          </el-col>
        </el-form-item>
        <div v-if="autoCreateRingChecked===true">
          <el-form-item  label="分区幂指数" prop="part_power">
            <el-col :span="10">
              <el-input v-model="addPolicyForm.part_power"></el-input>
            </el-col>
          </el-form-item>
          <el-form-item  label="副本数" prop="replicas" >
            <el-col :span="10">
              <el-input v-model="addPolicyForm.replicas"></el-input>
            </el-col>
          </el-form-item>
          <el-form-item  label="分区最小间隔" prop="min_part_hours">
            <el-col :span="10">
              <el-input v-model="addPolicyForm.min_part_hours"></el-input>
            </el-col>
          </el-form-item>
        </div>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="closeAddDialog">取 消</el-button>
        <el-button type="primary" @click="ensureAddPolicy">确 定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>

  import { mapGetters } from 'vuex'
  import { getPolicyList, addPolicy, deletePolicy } from '@/api/cluster'
  import { getClusterNodes } from '@/api/management'

  export default {
    data() {
      let validPolicyNum = (rule, value, callback) => {
        let policyNum = /^\d+$/
        if (!policyNum.test(value)) {
          callback(new Error('策略编号只能为数字类型'));
        } else {
          callback();
        }
      }
      let validPolicyNumIsExists = (rule, value, callback) => {
        let policyNum = this.policyList.map(function (item) {
          return item.policy_num
        })
        if (policyNum.indexOf(value) >= 0) {
          callback(new Error('策略编号已存在'));
        }else{
          callback();
        }
    }
      let validPolicyNameIsExists = (rule, value, callback) => {
      let policyName = this.policyList.map(function (item) {
        return item.policy_name.toLowerCase()
      })
      if (policyName.indexOf(value.toLowerCase()) >= 0) {
        callback(new Error('策略名已存在'));
      }else{
        callback();
      }
      }
      return {
        policyTypeMap:{
            "replication": "副本模式",
            "erasure_coding": "EC纠删码"
        },
        policyList:[],
        labelPosition: 'left',
        dialogAddPolicyVisible: false,
        addPolicyForm: {
          policy_num: '',
          policy_name: '',
          policy_alias: '',
          policy_type: 'replication',
          deprecated: '',
          part_power: '',
          replicas: '',
          min_part_hours: '',
        },
        nodeList: [],
        autoCreateRingChecked:false,
        policy_type:"replication",
        addPolicyRules: {
          policy_num: [
            {required: true, message: '策略编号不能为空', trigger: 'blur'},
            { validator: validPolicyNum,  trigger: 'blur' },
            { validator: validPolicyNumIsExists,  trigger: 'blur' }
          ],
          policy_name: [
            {required: true, message: '策略名不能为空', trigger: 'blur'},
            { validator: validPolicyNameIsExists,  trigger: 'blur' }
          ],
          policy_type: [
            {required: true, message: '策略类型不能为空', trigger: 'blur'},
          ],
          part_power: [
            {required: true, message: '分区幂指数不能为空', trigger: 'blur'},
          ],
          replicas: [
            {required: true, message: '副本数不能为空', trigger: 'blur'},
          ],
          min_part_hours: [
            {required: true, message: '最小间隔不能为空', trigger: 'blur'},
          ],
        },
      }
    },
    computed: {
      ...mapGetters([
        'selectedCluster',
      ])
    },
    methods: {
      showMsg(msg, type) {
        this.$message({
          message: msg,
          type: type
        });
      },
      cancelAdd() {
        this.dialogAddPolicyVisible = false
        this.$refs['dialogForm'].resetFields();
      },
      closeAddDialog(){
          this.dialogAddPolicyVisible = false
          this.cancelAdd()
      },
      showAddPolicyDialog() {
        this.dialogAddPolicyVisible = true
        this.autoCreateRingChecked = false
        this.addPolicyForm = {
          policy_num: '',
          policy_name: '',
          policy_alias: '',
          policy_type: 'replication',
          sync_policy_ring: false,
          part_power: '',
          replicas: '',
          min_part_hours: '',
        }
        this.$nextTick(() => {
          this.$refs['dialogForm'].clearValidate()
        })
      },
      ensureAddPolicy(){
        this.$confirm(`确认添加策略: ${this.addPolicyForm.policy_num}?`, '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          this.addPolicy(this.selectedCluster, this.addPolicyForm)
          this.closeAddDialog()
        }).catch((err) => {
          this.closeAddDialog()
        })
      },
      addPolicy(cluster_name, data) {
        let tmp = Object.assign({}, data)
        tmp.deprecated = 'no'
        if (this.autoCreateRingChecked) {
          tmp.sync_policy_ring = true
        }
        this.$refs['dialogForm'].validate((valid) => {
          if (valid) {
            addPolicy(cluster_name, tmp).then(response => {
              if (response.status == 201) {
                this.showMsg('执行成功','success')
                this.initPolicyList(this.selectedCluster)
              }
            }).catch(err => {
              this.showMsg('执行失败' + err,'error')
            })
          }
        })
      },
      ensuredeprecatedPolicy(row){
        this.$confirm(`确认弃用${row.policy_name}策略?`, '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          this.deprecatedPolicy(row)
        }).catch((err) => {
          // console.log(err)
        });
      },
      deprecatedPolicy(row) {
        let policyNum = row.policy_num
        let temp = {"policy_num": policyNum,"deprecated":"yes"}
        deletePolicy(this.selectedCluster, temp).then(response =>{
          if(response.status == 200){
            this.showMsg('执行成功','success')
            this.initPolicyList(this.selectedCluster)
          }
        }).catch(err => {
          this.showMsg('执行失败' + err,'success')
        })
      },
      initPolicyList(cluster_name) {
        getPolicyList(cluster_name).then(response => {
          if (response.status === 200) {
            this.policyList = response.data.data
          }
        }).catch(error => {
          console.log(error)
        })
      },
      getNodeList(cluster_name){
        let params = {"cluster": cluster_name}
        getClusterNodes(params).then(response => {
            if (response.status === 200){
              this.nodeList = response.data.data
            }
        })
      }
    },
    created() {},
    mounted() {
      this.initPolicyList(this.selectedCluster)
    },
  }
</script>
