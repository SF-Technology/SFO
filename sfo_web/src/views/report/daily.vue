<template>
    <div id="app">
        <h1 align="center">{{ msg }}</h1>
        <div id="tb-report">
            <el-table :data="repData" :span-method="columnSpanMethod" style="width: 97%;margin: 0 auto " :stripe="true" :border="true" :fit="true">
                <el-table-column prop="cluster_name" label="OSS集群" min-width="80" align="center"></el-table-column>
                <el-table-column prop="subject_name" label="检查项目" min-width="60" align="center"></el-table-column>
                <el-table-column prop="item_name" label="检查子项" min-width="100" align="left"></el-table-column>
                <el-table-column prop="check_command" label="检查命令/方法" min-width="160" align="left"></el-table-column>
                <el-table-column prop="check_result" label="检查结果" min-width="40" align="center">
                    <template slot-scope="scope">
                        <span v-if="scope.row.check_result==='OK'" style="color: green">正常</span>
                        <span v-else style="color: red">异常</span>
                    </template>
                </el-table-column>
                <el-table-column prop="check_remark" label="备注" min-width="50" align="center"></el-table-column>
            </el-table>
        </div>
    </div>
</template>
<script>
import { mapGetters } from 'vuex'
import { getReportList } from '@/api/report'
export default {
computed: {
      ...mapGetters([
        'selectedCluster'
      ])
    },
    data () {
        return {msg: '集群巡检报告',repData:[],};
    },
    created() {
        this.getRepData()
    },
    mounted() {
    },
    methods: {
        startHacking () {
            this.$notify({
                title: 'It Works',
                message: 'We have laid the groundwork for you. Now it\'s your time to build something epic!',
                duration: 6000
            })
        },
        getRepData(){
            getReportList().then(res=>{
                if(res.status === 200 && res.data.status == 200){
                    this.repData = res.data.data
                }
                else if(res.data.status === 401){
                    this.handle401()
                }
            }).catch(err=>{
                console.log(err)
                this.handle401()
            })
        },
        columnSpanMethod({ row, column, rowIndex, columnIndex }) {

    },
    //公用函数
    handle401(){
      this.showMsg('请先登录', 'error')
      this.$store.dispatch('FedLogOut').then(() => {
        this.$router.push('/login')
        this.$store.dispatch('LogOut').then((res) => {
          location.reload()  // 为了重新实例化vue-router对象 避免bug
        })
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

<style>
body {
  font-family: Helvetica, sans-serif;
}
</style>
