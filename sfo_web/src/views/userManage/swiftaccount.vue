/**
* Create by wenboling on 2018/6/21
*/
<template>
  <el-row style="margin: 10px">
    <el-row>
      <el-table :data="swiftAccountList" style="width: 95%;margin: 5px auto">
        <el-table-column prop="system_code" label="系统编码" min-width="180"></el-table-column>
        <el-table-column prop="account_id" label="账户名" min-width="350">
          <template slot-scope="scope">
            <span>AUTH_{{ scope.row.account_id }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="system_env" label="环境" width="120"></el-table-column>
        <el-table-column prop="system_capacity" label="账户容量" width="120"></el-table-column>
        <el-table-column prop="account_used" label="已用容量" width="200">
          <template slot-scope="scope">
            <el-tooltip effect="dark" placement="top">
              <div slot="content">已用：{{ scope.row.account_used | formatterBytes(1024) }}</div>
              <el-progress v-if="parseFloat(scope.row.capacity_used_percent) >= 80" :text-inside="true" :stroke-width="16" :percentage="parseFloat(scope.row.capacity_used_percent)" status="exception"></el-progress>
              <el-progress v-else :text-inside="true" :stroke-width="16" :percentage="parseFloat(scope.row.capacity_used_percent)" status="success"></el-progress>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column label="操作" min-width="150">
          <template slot-scope="scope">
            <el-button type="text" @click="handleExpansion(scope.row)">扩容</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-row style="margin: 10px auto; width: 90%">
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
    </el-row>
    <el-dialog title="系统容量调整" :visible.sync="dialogVisible" width="40%">
      <el-form :model="expansionForm" label-width="100" label-position="left" ref="expansionForm">
        <el-form-item label="当前系统">
          <span style="color: #8c939d">{{ select_sys.system_code }} ( AUTH_{{ select_sys.account_id }} )</span>
        </el-form-item>
        <el-form-item label="当前容量">
          <el-col :span="10">
            <el-input v-model="this.select_sys.system_capacity" auto-complete="off" :disabled="true">
              <template slot="append">GB</template>
            </el-input>
          </el-col>
        </el-form-item><el-form-item label="调整容量">
          <el-col :span="10">
            <el-input v-model="expansionForm.capacity" auto-complete="off">
              <template slot="append">GB</template>
            </el-input>
          </el-col>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="submitExpansion" :loading="isLoading">确 定</el-button>
      </div>
    </el-dialog>
  </el-row>
</template>

<script>
  import { capacityExpansion, getSwiftAccountList } from '@/api/oss'
  export default {
    data() {
      return {
        swiftAccountList: [],
        expansionForm: {
          capacity: '',
          system_env: '',
        },
        select_sys: {},
        system_code: '',
        isLoading: false,
        dialogVisible: false,
        //分页相关
        currentPage: 1,
        total: 0,
        page_size: 10,
      }
    },
    created() {
      this.getSwiftAccounts()
    },
    mounted() {

    },
    methods: {
      getSwiftAccounts(params){
        getSwiftAccountList(params).then(res=>{
          if(res.status === 200 && res.data.status === 200){
            let data = res.data.data
            this.swiftAccountList = data.accounts
            this.total = data.accounts_total
          }
        }).catch(err=>{
          console.log(err)
        })
      },
      handleExpansion(row){
        this.dialogVisible = true
        this.expansionForm.system_env = row.system_env
        this.select_sys = row
      },
      submitExpansion(){
        this.$confirm(`确定将 ${this.select_sys.system_code} 的容量调整为 ${this.expansionForm.capacity} GB?`, '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          this.isLoading = true
          capacityExpansion(this.select_sys.system_code, this.expansionForm).then(res=>{
            if(res.status === 200 && res.data.status === 200){
              this.$message({
                type: 'success',
                message: '扩容成功'
              });
            }
            this.isLoading = false
            this.dialogVisible = false
            let params = {
              page: this.currentPage,
              limit: this.page_size
            }
            this.getSwiftAccounts(params)
          }).catch(err=>{
            console.log(err)
            this.$message({
              type: 'error',
              message: '扩容失败'
            });
            this.isLoading = false
            this.dialogVisible = false
          })
        }).catch(() => {
          this.$message({
            type: 'info',
            message: '已取消操作'
          });
        });
      },
      handleCurrentChange(page){
        this.currentPage = page
        let params = {
          page: this.currentPage,
          limit: this.page_size
        }
        this.getSwiftAccounts(params)
      },
      handleSizeChange(size){
        this.page_size = size
        this.currentPage = 1
        let params = {
          page: this.currentPage,
          limit: this.page_size
        }
        this.getSwiftAccounts(params)
      },
    }
  }
</script>
