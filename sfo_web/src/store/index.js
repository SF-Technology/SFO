import Vue from 'vue'
import Vuex from 'vuex'
import app from './modules/app'
import user from './modules/user'
import permission from './modules/permission'
import tagsView from './modules/tagsView'
import cluster from './modules/cluster'
import getters from './getters'
import alarms from './modules/alarms'
Vue.use(Vuex)

const store = new Vuex.Store({
  modules: {
    app,
    user,
    permission,
    tagsView,
    alarms,
    cluster
  },
  getters
})

export default store
