/**
 * Create by wenboling on 2018/4/9
 */
import fetch from '@/utils/fetch'

//agent管理
export function getAgents(clustername, params) {
  return fetch({
    url: `/api/clusteragents/${clustername}/`,
    method: 'get',
    params: params
  })
}

export function testAgents(clustername, data) {
  return fetch({
    url: `/api/clusteragents/${clustername}/`,
    method: 'post',
    data: data
  })
}

export function gethosts(clustername, params) {
  return fetch({
    url: `/api/cluster/${clustername}/hostlist/`,
    method: 'get',
    params: params
  })
}

export function gethostInfo(clustername, params) {
  return fetch({
    url: `/api/cluster/hostinfo/${clustername}/`,
    method: 'get',
    params
  })
}

export function getnodeStat(hostname, params) {
  return fetch({
    url: `/api/cluster/nodestat/${hostname}/`,
    method: 'get',
    params: params
  })
}

export function getNodeSrvDetail(clustername, params) {
  return fetch({
    url: `/api/cluster/nodesrv/${clustername}/`,
    method: 'get',
    params: params
  })
}

export function getOverview(clustername, params) {
  return fetch({
    url: `/api/cluster/${clustername}/overview/`,
    method: 'get',
    params: params
  })
}

export function getCPUOverview(clustername, params) {
  return fetch({
    url: `/api/cluster/${clustername}/overview/cpu/`,
    method: 'get',
    params: params
  })
}

export function getMemOverview(clustername, params) {
  return fetch({
    url: `/api/cluster/${clustername}/overview/mem/`,
    method: 'get',
    params: params
  })
}

export function getStorageOverview(clustername, params) {
  return fetch({
    url: `/api/cluster/${clustername}/overview/storage/`,
    method: 'get',
    params: params
  })
}

export function getProxyOverview(clustername, params) {
  return fetch({
    url: `/api/cluster/${clustername}/overview/proxy/`,
    method: 'get',
    params: params
  })
}

export function getClusterIOPS(clustername, params) {
  return fetch({
    url: `/api/cluster/${clustername}/diskio/`,
    method: 'get',
    params: params
  })
}

export function getDiskList(clustername, params) {
  return fetch({
    url: `/api/cluster/${clustername}/diskper/`,
    method: 'get',
    params: params
  })
}

export function getNodePerformance(clustername, params) {
  return fetch({
    url: `/api/cluster/${clustername}/node/`,
    method: 'get',
    params: params
  })
}

export function getDiskPerformanceDetail(clustername, params) {
  return fetch({
    url: `/api/cluster/disk/${clustername}/`,
    method: 'get',
    params: params
  })
}

export function getPartitionStatus(clustername, params) {
  return fetch({
    url: `/api/cluster/${clustername}/partition/`,
    method: 'get',
    params: params
  })
}

export function getAsyncStatus(clustername, params) {
  return fetch({
    url: `/api/cluster/${clustername}/async/`,
    method: 'get',
    params: params
  })
}
export function getSVTStatus(clustername, params) {
  return fetch({
    url: `/api/cluster/${clustername}/tps/`,
    method: 'get',
    params: params
  })
}

//上传集群拓扑图
export function uploadTopologyImage(clustername, data) {
  return fetch({
    url: `/api/topological/graph/${clustername}/`,
    headers:{'Content-Type':'multipart/form-data'},
    method: 'post',
    data: data,
  })
}

//获取集群图谱图api, 作为图片的源可以不用异步加载
export function topologyImageAPI(clustername) {
  return `${process.env.BASE_API}/api/topological/graph/${clustername}/`
}

//下面这些api是获取rrdtool生成的图片的, 作为图片的源可以不用异步加载
export function cpuImageAPI(clustername) {
  return `${process.env.IMAGE_BASE_URL}/api/cluster/${clustername}/overview/cpu/image/?start=`
}
export function memImageAPI(clustername) {
  return `${process.env.IMAGE_BASE_URL}/api/cluster/${clustername}/overview/mem/image/?start=`
}
export function diskReadIOPSImageAPI(clustername) {
 return `${process.env.IMAGE_BASE_URL}/api/cluster/${clustername}/overview/diskiops/read/image/?start=`
}
export function diskWriteIOPSImageAPI(clustername) {
 return `${process.env.IMAGE_BASE_URL}/api/cluster/${clustername}/overview/diskiops/write/image/?start=`
}
export function diskReadmbpsImageAPI(clustername) {
 return `${process.env.IMAGE_BASE_URL}/api/cluster/${clustername}/overview/diskmbps/read/image/?start=`
}
export function diskWritembpsImageAPI(clustername) {
 return `${process.env.IMAGE_BASE_URL}/api/cluster/${clustername}/overview/diskmbps/write/image/?start=`
}
export function diskAwaitImageAPI(clustername) {
 return `${process.env.IMAGE_BASE_URL}/api/cluster/${clustername}/overview/await/image/?start=`
}
