/**
 * Create by wenboling on 2018/5/16
 */

import fetch from '@/utils/fetch'

//swift账户管理
export function getSwiftAccountList(params) {
  return fetch({
    url: '/api/accounts/',
    method: 'get',
    params: params
  })
}

export function createAccount(project_name, data) {
  return fetch({
    url: `/api/systemaccess/${project_name}/`,
    method: 'post',
    data: data
  })
}

export function undelete(data) {
  return fetch({
    url: `/api/resumer/`,
    method: 'put',
    data: data
  })
}

export function getAccounts(params) {
  return fetch({
    url: `/api/accounts/`,
    method: 'get',
    params: params
  })
}

export function capacityExpansion(syscode, data) {
  return fetch({
    url: `/api/systemaccess/${syscode}/`,
    method: 'put',
    data: data
  })
}

export function getRoles(params) {
  return fetch({
    url: `/api/swift/roles/`,
    method: 'get',
    params: params
  })
}

export function createRole(data) {
  return fetch({
    url: `/api/swift/roles/`,
    method: 'post',
    data: data
  })
}

export function updateRole(guid, data) {
  return fetch({
    url: `/api/swift/role/${guid}/`,
    method: 'put',
    data: data
  })
}

export function getUsers(clustername, params) {
  return fetch({
    url: `/api/swift/users/${clustername}/`,
    method: 'get',
    params: params
  })
}

export function createUser(clustername, data) {
  return fetch({
    url: `/api/swift/users/${clustername}/`,
    method: 'post',
    data: data
  })
}

export function getUserDetail(guid, params) {
  return fetch({
    url: `/api/swift/user/${guid}/`,
    method: 'get',
    params: params
  })
}

export function updateUser(guid, data) {
  return fetch({
    url: `/api/swift/user/${guid}/`,
    method: 'put',
    data: data
  })
}
