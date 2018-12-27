/**
 * Create by wenboling on 2018/4/16
 */

import { getClusters } from '@/api/dashboard'
import { setClusterName, setClusters } from  '@/utils/cookie-util'

const clusters = {
  state: {
    clusterList: [],
    selectedCluster: ''
  },

  mutations: {
    SET_CLUSTER_LIST: (state, clusters) => {
      state.clusterList = clusters
    },
    SET_SELECTED_CLUSTER: (state, s_cluster) => {
      state.selectedCluster = s_cluster
    },
  },

  actions: {
    setClusterList({ commit, state }, data) {
      commit('SET_CLUSTER_LIST', data)
    },
    setSelectedCluster({commit, state}, data){
      commit('SET_SELECTED_CLUSTER', data)
    },
    setClusterWithoutSelected({commit, state}){
      return new Promise((resolve, reject)=>{
        getClusters().then(response=>{
          if(response.data.status === 200 && response.status === 200){
            let clusterList = response.data.data
            let selected = clusterList[0]
            setClusters(JSON.stringify(clusterList))
            setClusterName(selected)
            commit('SET_CLUSTER_LIST', clusterList)
            commit('SET_SELECTED_CLUSTER', selected)
            resolve()
          }
        }).catch(err=>{
          reject(err)
        })
      })
    }
  }
}

export default clusters
