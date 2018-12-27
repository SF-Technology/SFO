<template>
  <el-select v-model="selected"
             @change="handleSelectedChange"
             @visible-change="handleVisibleChange">
    <el-option v-for="cluster in clusterList"
               :key="cluster.cluster_name"
               :label="cluster.cluster_name"
               :value="cluster.cluster_name">
    </el-option>
  </el-select>
</template>

<script>
  import { setClusterName, getClusterName } from  '@/utils/cookie-util'
  import { getClusters } from '@/api/dashboard'
  export default {
    name: "selectbar",
    data() {
      return{
        selected: '',
        clusterList: [],
      }
    },
    computed: {},
    methods: {
      getSelectCluster() {
        this.getClusterList()
        this.selected = getClusterName()
        this.$store.dispatch('setSelectedCluster', this.selected)
      },
      handleSelectedChange(value){
        this.$store.dispatch('setSelectedCluster', value)
        setClusterName(value)
        this.$router.push({
          path: '/dashboard',
          // query: {
          //   t: +new Date() //保证每次点击路由的query项都是不一样的，确保会重新刷新view
          // }
        })
        location.reload()
      },
      handleVisibleChange(status){
        if(status){
          this.getClusterList()
        }
      },
      getClusterList(){
        getClusters().then(response => {
          if(response.data.status === 200 && response.status === 200){
            this.clusterList = []
            this.clusterList = response.data.data
            this.$store.dispatch('setClusterList', this.clusterList)
          }
        }).catch(error => {
          console.log("!!!!!", error)
        })
      },
    },
    created(){
      this.getSelectCluster()
    },
    mounted() {
      // this.getCluster()
    }
  }
</script>

<style scoped>

</style>
