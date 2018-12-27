import Vue from 'vue'
import Router from 'vue-router'
const _import = require('./_import_' + process.env.NODE_ENV)
// in development env not use Lazy Loading,because Lazy Loading too many pages will cause webpack hot update too slow.so only in production use Lazy Loading

/* layout */
import Layout from '../views/layout/Layout'

Vue.use(Router)

 /**
  * icon : the icon show in the sidebar
  * hidden : if `hidden:true` will not show in the sidebar
  * redirect : if `redirect:noredirect` will not redirct in the levelbar
  * noDropdown : if `noDropdown:true` will not has submenu in the sidebar
  * meta : `{ role: ['admin'] }`  will control the page role
  **/
export const constantRouterMap = [
  { path: '/login', component: _import('login/index'), hidden: true },
  { path: '/login/selectcluster', component: _import('login/selectCluster'), hidden: true },
  { path: '/404', component: _import('404'), hidden: true },
  {
    path: '',
    component: Layout,
    redirect: '/dashboard',
    icon: 'dashboard',
    noDropdown: true,
    children: [
      { path: 'dashboard', name: '首页', component: _import('dashboard/index') }
    ]
  },
  {
    path: '/monitor',
    component: Layout,
    redirect: 'noredirect',
    name: '集群监控',
    icon: 'monitoring',
    children: [
      { path: 'topology', name: '集群拓扑', component: _import('monitor/topology') },
      { path: 'disk', name: '磁盘监控', component: _import('monitor/disk') },
      { path: 'cpu', name: 'CPU监控', component: _import('monitor/cpu') },
      { path: 'memory', name: '内存监控', component: _import('monitor/memory') },
      { path: 'swift', name: 'swift状态', component: _import('monitor/swift') },
      { path: 'request_status', name: '请求状态', component: _import('monitor/request') },
      { path: 'node', name: '节点状态', component: _import('monitor/node_info') },
    ]
  },
  {
    path: '/report',
    component: Layout,
    redirect: 'noredirect',
    name: '集群报表',
    icon: 'EXCEL',
    children: [
      { path: 'reportdaily', name: '日常巡检', component: _import('report/daily') },
      { path: 'alarmhistory', name: '历史告警', component: _import('report/alarmHistory') },
    ]
  },
]

export default new Router({
  mode: 'history', //后端支持可开
  scrollBehavior: () => ({ y: 0 }),
  routes: constantRouterMap
})

export const asyncRouterMap = [
  {
    path: '/clustermanage',
    component: Layout,
    redirect: '/clustermanage/list',
    name: '集群管理',
    icon: 'cluster',
    meta: { role: ['admin', 'superadmin'] },
    children: [
      { path: 'list', name: '集群列表', component: _import('cluster/clusterlist')},
      { path: 'ring', name: '环管理', component: _import('cluster/ring') },
      { path: 'disk', name: '磁盘管理', component: _import('cluster/disk') },
      { path: 'server', name: '服务管理', component: _import('cluster/server') },
      { path: 'policy', name: '存储策略', component: _import('cluster/policy_conf') },
      { path: 'swiftnode', name: '节点管理', component: _import('nodeManage/node_list') },
      { path: 'apply', name: '申请资源', component: _import('ossResource/getResource') },
      { path: 'swiftaccount', name: 'account管理', component: _import('userManage/swiftaccount')},
      { path: 'swiftuser', name: 'swift用户管理', component: _import('userManage/swiftuser')},
      { path: 'swiftrole', name: 'swift角色管理', component: _import('userManage/swiftrole')},
      { path: 'agent', name: 'agent管理', component: _import('nodeManage/agent_list') },
      { path: 'create', name: '创建集群', component: _import('cluster/create') },
    ]
  },
  {
    path: '/confmanage',
    component: Layout,
    redirect: 'noredirect',
    name: '配置管理',
    icon: 'quanxian',
    meta: { role: ['admin', 'superadmin'] },
    children: [
      { path: 'commons', name: '通用配置', component: _import('confManage/common_conf') },
      { path: 'cluster', name: '集群配置', component: _import('confManage/cluster_conf') },
      { path: 'sfouser', name: 'sfo用户', component: _import('userManage/sfouser')},
    ]
  },
  {
    path: '/logmanage',
    component: Layout,
    redirect: '/logmanage/tasklog',
    icon: 'log',
    name: '日志管理',
    meta: { role: ['admin', 'superadmin'] },
    children: [
      { path: 'tasklog', name: '任务日志', component: _import('log/tasklog')},
    ]
  },

  { path: '*', redirect: '/404', hidden: true }
]

