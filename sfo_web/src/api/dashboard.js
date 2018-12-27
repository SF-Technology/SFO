/**
 * Create by wenboling on 2018/3/20
 */
import fetch from '@/utils/fetch'

export function getClusterInfo(clustername, params) {
  return fetch({
    url: `/api/cluster/${clustername}/`,
    method: 'get',
    params
  })
}

export function getClusters(params) {
  return fetch({
    url: '/api/cluster/',
    method: 'get',
    params
  })
}

export function getRequestStats(clustername, params) {
  return fetch({
    url: `/api/cluster/requeststat/${clustername}/`,
    method: 'get',
    params
  })
}
