/**
* Create by wenboling on 2018/7/6
*/
<template>
  <div>
    <el-row>
      <el-table :data="taskLogList" style="width: 95%;margin: 5px auto">
        <el-table-column prop="create_user" label="创建者" width="150"></el-table-column>
        <el-table-column prop="node_host_name" label="执行主机" width="200"></el-table-column>
        <el-table-column prop="service_type" label="任务类型" width="180"></el-table-column>
        <el-table-column prop="operation" label="操作" width="200"></el-table-column>
        <el-table-column prop="service_name" label="任务名称"></el-table-column>
        <el-table-column label="任务状态" width="80">
          <template slot-scope="scope">
            <span v-if="scope.row.service_task_ending_flag && scope.row.service_task_ending_flag==1">已完成</span>
            <span v-if="scope.row.service_task_running_flag &&
                        scope.row.service_task_running_flag==1 &&
                        (!scope.row.service_task_ending_flag || scope.row.service_task_ending_flag != 1)">已完成</span>
          </template>
        </el-table-column>
        <el-table-column prop="task_start_time" label="任务开始时间" width="200"></el-table-column>
        <el-table-column prop="task_end_time" label="任务结束时间" width="200"></el-table-column>
      </el-table>
    </el-row>
  </div>
</template>

<script>
  import { getLogs } from '@/api/log'
  export default {
    data() {
      return {
        taskLogList: [],
      }
    },
    methods: {
      getTaskLogList(){
        getLogs().then(res=>{
          if(res.status == 200 && res.data.status ==200){
            this.taskLogList = res.data.data
          }
        }).catch(err=>{
          console.log(err)
        })
      }
    },
    created() {
      this.getTaskLogList()
    },
    mounted() {

    },
  }
</script>
<style rel="stylesheet/scss" lang="scss" scoped>
</style>
