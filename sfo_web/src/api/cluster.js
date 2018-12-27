/**
 * Create by wenboling on 2018/7/4
 */

import fetch from '@/utils/fetch'

export function getDisks(cluster_name, params) {
  return fetch({
    url: `/api/clusterdisks/${cluster_name}/`,
    method: 'get',
    params: params
  })
}

export function mountDisks(cluster_name, data) {
  return fetch({
    url: `/api/clusterdisks/${cluster_name}/`,
    method: 'post',
    data: data
  })
}

export function getSrvs(cluster_name, params) {
  return fetch({
    url: `/api/clustersrvs/${cluster_name}/`,
    method: 'get',
    params: params
  })
}

export function installSrvs(cluster_name, data) {
  return fetch({
    url: `/api/clustersrvs/${cluster_name}/`,
    method: 'post',
    data: data
  })
}

export function umountDisks(cluster_name, data) {
  return fetch({
    url: `/api/clusterdisks/${cluster_name}/`,
    method: 'delete',
    data: data
  })
}

//环相关
export function getRings(cluster_name, params) {
  return fetch({
    url: `/api/clusterrings/${cluster_name}/`,
    method: 'get',
    params: params
  })
}

export function getRingDetail(cluster_name, params) {
  return fetch({
    url: `/api/clusterdetail/${cluster_name}/`,
    method: 'get',
    params: params
  })
}

export function createRing(cluster_name, data) {
  return fetch({
    url: `/api/clusterrings/${cluster_name}/`,
    method: 'post',
    data: data
  })
}

export function modifyRing(cluster_name, data) {
  return fetch({
    url: `/api/clusterrings/${cluster_name}/`,
    method: 'put',
    data: data
  })
}

export function getPolicyList(cluster_name, params) {
  return fetch({
    url: `/api/clusterpolicys/${cluster_name}/`,
    method: 'get',
    params: params
  })
}

export function addPolicy(cluster_name, data) {
  return fetch({
    url: `/api/clusterpolicys/${cluster_name}/`,
    method: 'post',
    data: data
  })
}

export function deletePolicy(cluster_name, data) {
  return fetch({
    url: `/api/clusterpolicys/${cluster_name}/`,
    method: 'delete',
    data: data
  })
}

//创建集群相关
export function addClusterName(data) {
  return fetch({
    url: `/api/cluster/`,
    method: 'post',
    data: data
  })
}

export function createCluster(data) {
  return fetch({
    url: `/api/cluster/`,
    method: 'put',
    data: data
  })
}

export function updateCluster(clustername, data) {
  return fetch({
    url: `/api/cluster/${clustername}/`,
    method: 'put',
    data: data
  })
}

//集群专用资源池系统
export function getSysList(params) {
  return fetch({
    url: `/api/properpool/`,
    method: 'get',
    params: params
  })
}

export function addSystoCluster(data) {
  return fetch({
    url: `/api/properpool/`,
    method: 'post',
    data: data
  })
}

export function deleteSysfromCluster(data) {
  return fetch({
    url: `/api/properpool/`,
    method: 'delete',
    data: data
  })
}


