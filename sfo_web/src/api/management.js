/**
 * Create by wenboling on 2018/4/27
 */
import fetch from '@/utils/fetch'

//集群节点管理
export function getClusterNodes(params) {
  return fetch({
    url: `/api/clusternodes/`,
    method: 'get',
    params: params
  })
}

export function getClusterNodesDetail(clusterName, guid, params) {
  return fetch({
    url: `/api/clusternodes/${guid}/`,
    method: 'get',
    params: params
  })
}

export function getNodesDetailList(clusterName, params) {
  return fetch({
    url: `/api/cluster/${clusterName}/hostlist/ `,
    method: 'get',
    params: params
  })
}

export function createClusterNode(data) {
  return fetch({
    url: `/api/clusternodes/`,
    method: 'post',
    data: data
  })
}

export function updateClusterNode(guid, params) {
  return fetch({
    url: `/api/clusternodes/${guid}/`,
    method: 'put',
    data: params
  })
}

export function delClusterNode(guid, params) {
  return fetch({
    url: `/api/clusternodes/${guid}/`,
    method: 'delete',
    params: params
  })
}

//sfo用户管理
export function getUserList(params) {
  return fetch({
    url: '/api/userlist/',
    method: 'get',
    params: params
  })
}

export function getUserDetail(user_account, params) {
  return fetch({
    url: `/api/user/${user_account}/`,
    method: 'get',
    params: params
  })
}

export function updateUser(user_account, data) {
  return fetch({
    url: `/api/user/${user_account}/`,
    method: 'put',
    data: data
  })
}

//角色管理
export function getRoleList(params) {
  return fetch({
    url: '/api/rolelist/',
    method: 'get',
    params: params
  })
}

export function getRoleDetail(rolename, params) {
  return fetch({
    url: `/api/role/${rolename}/`,
    method: 'get',
    params: params
  })
}

export function createRole(data) {
  return fetch({
    url: '/api/rolelist/',
    method: 'post',
    data: data
  })
}

export function updateRole(rolename, data) {
  return fetch({
    url: `/api/role/${rolename}/`,
    method: 'put',
    data: data
  })
}

export function deleteRole(role, params) {
  return fetch({
    url: `/api/role/${role}/`,
    method: 'delete',
    params: params
  })
}

//权限列表
export function getPermissionList(params) {
  return fetch({
    url: '/api/permissionlist/',
    method: 'get',
    params: params
  })
}

//服务管理
export function up_downSrv(hostname, data) {
  return fetch({
    url: `/api/cluster/nodesrv/${hostname}/`,
    method: 'put',
    data: data
  })
}

//配置管理
export function getConfigFileContent(params) {
  return fetch({
    url: '/api/swift/config/',
    method: 'get',
    params: params
  })
}

export function updateConfigFileContent(params) {
  return fetch({
    url: '/api/swift/config/',
    method: 'put',
    data: params
  })
}

export function getConfigList(params) {
  return fetch({
    url: '/api/configlist/',
    method: 'get',
    params: params
  })
}

export function createConfig(params) {
  return fetch({
    url: '/api/configlist/',
    method: 'post',
    data: params
  })
}

export function createService(hostname,params) {
  return fetch({
    url: `/api/cluster/nodesrv/${hostname}/`,
    method: 'post',
    data: params
  })
}

export function updateConfig(params) {
  return fetch({
    url: '/api/configlist/',
    method: 'put',
    data: params
  })
}

export function deleteConfig(params) {
  return fetch({
    url: '/api/configlist/',
    method: 'delete',
    data: params
  })
}

export function getServiceTasks(params) {
  return fetch({
    url: '/api/tasks/',
    method: 'get',
    params: params
  })
}

export function getManagerLog(taskid, params) {
  return fetch({
    url: `/api/managerlog/${taskid}/`,
    method: 'get',
    params: params
  })
}
