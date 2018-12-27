/**
* Create by wenboling on 2018/5/2
*/
<template>
  <div>
    <el-row style="margin: 10px">
      <el-col :span="24">
        <el-card>
          <div slot="header" class="clearfix">
            <span>监管平台通用配置</span>
            <el-button style="float: right;" type="primary"  @click="handleAdd" round><i class="el-icon-plus">添加配置</i></el-button>
          </div>
          <el-table :data="tableData" style="width: 100%">
            <el-table-column prop="config_key" label="配置项" width="190"></el-table-column>
            <el-table-column prop="config_value" label="值" min-width="230"></el-table-column>
            <el-table-column prop="config_group" label="类别" width="150"></el-table-column>
            <el-table-column prop="remark" label="描述" min-width="250"></el-table-column>
            <el-table-column prop="add_time" label="添加时间" width="160"></el-table-column>
            <el-table-column label="操作" width="150">
              <template slot-scope="scope">
                <el-button
                  size="mini"
                  type="primary"
                  icon="el-icon-edit"
                  @click="handleUpdate(scope.row)"></el-button>
                <el-button
                  size="mini"
                  type="danger"
                  icon="el-icon-delete"
                  @click="handleDelete(scope.row)"></el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-row style="margin: 10px">
            <el-pagination
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
              :current-page.sync="currentPage"
              :page-sizes="[10, 15, 20, 30]"
              :page-size="page_size"
              layout="total, sizes, prev, pager, next"
              :total="total"
              style="float: right">
            </el-pagination>
          </el-row>
        </el-card>
      </el-col>
    </el-row>
    <!--新建框-->
    <el-dialog :title="titleMap[opeStatus]"  :visible.sync="dialogFormVisible">
      <el-form :model="form"  :rules="rules" ref="form" >
        <el-form-item  :label-width="formLabelWidth" prop="group"   :hidden="this.opeStatus == 'update'" label="类别">
          <el-radio v-model="group_type" label="exist">已有类别</el-radio>
          <el-radio v-model="group_type" label="new">新增类别</el-radio>
          <div v-if="group_type==='exist'">
            <el-select v-model="form.group" placeholder="选择已存在的类别">
              <el-option   v-for="group in form.groupList"
                           :key="group"
                           :label="group"
                           :value="group">
              </el-option>
            </el-select>
          </div>
          <div v-if="group_type==='new'">
            <el-col :span="8">
              <el-input v-model="form.group" auto-complete="off"></el-input>
            </el-col>
          </div>
        </el-form-item>
        <el-row>
          <el-col :span="10">
            <el-form-item label="配置项" :label-width="formLabelWidth" prop="key">
              <el-input v-model="form.key" auto-complete="off" :disabled="this.opeStatus == 'update'"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="10">
            <el-form-item label="值" :label-width="formLabelWidth" prop="value">
              <el-input v-model="form.value" auto-complete="off"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="12">
            <el-form-item label="描述" :label-width="formLabelWidth" prop="desc">
              <el-input type="textarea" v-model="form.desc" auto-complete="off"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">取 消</el-button>
          <el-button type="primary" v-if="this.opeStatus == 'create'" @click.native="createConfig">创 建</el-button>
          <el-button type="primary" v-if="this.opeStatus == 'update'" @click.native="updateConfig">更 新</el-button>
      </div>
    </el-dialog>
  </div>
</template>



<script>
  import { getConfigList, createConfig, updateConfig, deleteConfig } from '@/api/management'
  export default {
    data() {
      return {
        tableData: [],
        group_type: 'exist',
        dialogFormVisible: false,
        form: {
          key: '',
          value: '',
          desc: '',
          group: '',
          checked: false,
          groupList: []
        },
        formJson: {
          config_group: '',
          config_key: '',
          config_value: '',
          remark: ''
        },
        formLabelWidth: '120px',
        titleMap:{
          'update': "修改配置",
          'create': "添加配置",
        },
        opeStatus: '',
        rules: {
          key: [{ required: true, message: '请输入配置项', trigger: 'blur' }],
          value: [{ required: true, message: '请输入值', trigger: 'blur' }],
          group: [{ required: true, message: '请选择类别或者填写类别', trigger: 'blur' }]
        },
        //分页相关
        currentPage: 1,
        total: 0,
        page_size: 10,
      }
    },
    methods: {
      resetForm() {
        this.form.key = ''
        this.form.value = ''
        this.form.desc = ''
        this.form.group = ''
        this.form.checked = false
      },
      formatter(row, column) {
        return row.address;
      },
      initGroupList(data) {
        const groupList = new Array()
        for(var i=0; i<data.length; i++){
          if(groupList.indexOf(data[i].config_group)< 0){
            groupList.push(data[i].config_group)
          }
        }
        return groupList
      },
      getConfigs(params){
        getConfigList(params).then(res=>{
          if(res.status === 200 && res.data.status === 200){
            let data = res.data.data
            this.tableData = data.configs
            this.total = data.config_total
            this.form.groupList = this.initGroupList(this.tableData)
          }else if(res.data.status === 401) {
            this.showMsg('请先登录', 'error')
            this.$store.dispatch('LogOut').then(() => {
              location.reload()  // 为了重新实例化vue-router对象 避免bug
            })
          }
        }).catch(err=>{
          console.log(err)
        })
      },
      updateConfig() {
        this.formJson.config_group = this.form.group
        this.formJson.config_key = this.form.key
        this.formJson.config_value = this.form.value
        this.formJson.remark = this.form.desc
        let para = Object.assign({}, this.formJson)
        if (this.validParamNotNull()) {
          updateConfig(para).then(response => {
            if (response.status < 300) {
              this.showMsg('更新成功', 'success')
              let params = {
                page: this.currentPage,
                limit: this.page_size
              }
              this.getConfigs(params)
              this.$refs['form'].resetFields()
              this.dialogFormVisible = false
            }
          }).catch(err => {
            this.showMsg(`更新失败${err}`, 'error')
            this.$refs['form'].resetFields()
            this.dialogFormVisible = false
          })
        } else {
          this.showMsg('必填值不能为空', 'error')
        }
      },
      handleUpdate(row) {
        this.opeStatus = 'update'
        this.dialogFormVisible = true
        this.resetForm()
        this.form.key = row.config_key
        this.form.group = row.config_group
        this.form.value = row.config_value
        this.form.desc = row.remark
      },
      deleteConfig(key, group) {
        this.formJson.config_group = group
        this.formJson.config_key = key
        let para = Object.assign({}, this.formJson)
        deleteConfig(para).then(response => {
          if (response.status < 300) {
            this.showMsg('删除成功', 'success')
            let params = {
              page: this.currentPage,
              limit: this.page_size
            }
            this.getConfigs(params)
          }
        }).catch(err => {
          this.showMsg(`删除失败${err}`, 'error')
        })
      },
      handleDelete(row) {
        this.$confirm(`确认删除配置: ${row.config_key}?`, '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          this.deleteConfig(row.config_key, row.config_group)
        }).catch(() => {
          this.showMsg('已取消删除', 'info')
        });
      },
      createConfig() {
        this.formJson.config_group = this.form.group
        this.formJson.config_key = this.form.key
        this.formJson.config_value = this.form.value
        this.formJson.remark = this.form.desc
        let para = Object.assign({}, this.formJson)
        if (this.validParamNotNull()) {
          createConfig(para).then(response => {
            if (response.status < 300) {
              this.showMsg('创建成功', 'success')
              let params = {
                page: this.currentPage,
                limit: this.page_size
              }
              this.getConfigs(params)
              this.$refs['form'].resetFields()
              this.dialogFormVisible = false
            }
          }).catch(err => {
            this.showMsg(`创建失败${err}`, 'error')
            this.$refs['form'].resetFields()
            this.dialogFormVisible = false
          })
        } else {
          this.showMsg('必填值不能为空', 'error')
        }
      },
      handleAdd() {
        this.opeStatus = 'create'
        this.dialogFormVisible = true
        this.resetForm()
      },
      showMsg(msg, type) {
        this.$message({
          message: msg,
          type: type
        });
      },
      validParamNotNull() {
        if (this.form.group && this.form.key && this.form.value) {
          return true
        }
        return false
      },

      handleCurrentChange(page){
        this.currentPage = page
        let params = {
          page: this.currentPage,
          limit: this.page_size
        }
        this.getConfigs(params)
      },
      handleSizeChange(size){
        this.page_size = size
        this.currentPage = 1
        let params = {
          page: this.currentPage,
          limit: this.page_size
        }
        this.getConfigs(params)
      },
    },
    created() {
      this.getConfigs()
    },
    mounted() {

    }
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
</style>
