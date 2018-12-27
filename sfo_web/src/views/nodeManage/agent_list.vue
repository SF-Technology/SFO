/**
* Create by wenboling on 2018/9/3
*/
<template>
  <div>
    <el-row style="margin: 10px auto; width: 90%">
      <el-button type="primary" @click="refreshList" :loading="isRefreshing" size="medium">刷新列表</el-button>
      <!--<el-form :inline="true" style="float: right;margin: 10px">-->
        <!--<el-form-item>-->
          <!--<el-input prefix-icon="el-icon-search" placeholder="请输入主机名" size="medium" style="width: 180px"></el-input>-->
        <!--</el-form-item>-->
        <!--<el-form-item>-->
          <!--<el-button type="primary" size="medium">查询</el-button>-->
        <!--</el-form-item>-->
      <!--</el-form>-->
    </el-row>
    <el-row>
      <el-table :data="agents" style="width: 90%; margin: 0 auto">
        <el-table-column prop="hostname" label="主机名" min-width="250"></el-table-column>
        <el-table-column label="集群名" min-width="250">
          <template slot-scope="scope">
            <span>{{ selectedCluster }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="add_time" label="上次心跳时间" width="160"></el-table-column>
        <el-table-column label="测试" width="250">
          <template slot-scope="scope">
            <el-button type="text" @click="testSend('test_cmd_link', scope.row)">发送命令</el-button>
            <el-button type="text" @click="testSend('test_file_link', scope.row)">发送文件</el-button>
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
  </div>
</template>

<script>
  import { getAgents, testAgents } from '@/api/monitor'
  import { mapGetters } from 'vuex'

  export default {
    computed: {
      ...mapGetters([
        'selectedCluster',
      ])
    },
    data() {
      return {
        agents: [],
        isRefreshing: false,
        //分页相关
        currentPage: 1,
        total: 0,
        page_size: 10,
      }
    },
    created() {
      this.getAgentList(this.selectedCluster)
    },
    mounted() {

    },
    methods: {
      getAgentList(clustername, params){
        getAgents(clustername, params).then(res=>{
          if(res.data.status === 200 && res.status === 200){
            let data = res.data.data
            this.agents = data.agents
            this.total = data.agents_total
            this.isRefreshing = false
          }
        }).catch(err=>{
          console.log(err)
          this.isRefreshing = false
        })
      },
      refreshList(){
        this.isRefreshing = true
        let params = {
          page: this.currentPage,
          limit: this.page_size
        }
        this.getAgentList(this.selectedCluster, params)
      },
      handleCurrentChange(page){
        this.currentPage = page
        let params = {
          page: this.currentPage,
          limit: this.page_size
        }
        this.getAgentList(this.selectedCluster, params)
      },
      handleSizeChange(size){
        this.page_size = size
        this.currentPage = 1
        let params = {
          page: this.currentPage,
          limit: this.page_size
        }
        this.getAgentList(this.selectedCluster, params)
      },

      //连通性测试
      testSend(type, row){
        let data = {
          "operation": type,
          "host_name": row.hostname
        }
        testAgents(this.selectedCluster, data).then(res=>{
          if(res.status === 200 && res.data.status === 200){
            this.showMsg(`${row.hostname}测试成功：${res.data.message}`, 'success')
          }
        }).catch(err=>{
          this.showMsg(`${row.hostname}测试失败：${err}`, 'error')
        })
      },
      showMsg(msg, type) {
        this.$message({
          message: msg,
          type: type
        });
      },
    }
  }
</script>
