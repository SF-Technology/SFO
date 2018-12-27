import Cookies from 'js-cookie'

const TokenKey = 'Admin-Token'
const RoleList = 'Roles'
const clusterToken = 'Cluster'
const clusterList = 'ClusterList'
const UserName = 'Username'

export function getToken() {
  return Cookies.get(TokenKey)
}

export function setToken(token) {
  return Cookies.set(TokenKey, token)
}

export function removeToken() {
  return Cookies.remove(TokenKey)
}

export function getUsername() {
  return localStorage.getItem(UserName)
}

export function setUsername(token) {
  return localStorage.setItem(UserName, token)
}

export function removeUsername() {
  return localStorage.removeItem(UserName)
}

export function getRole() {
  return localStorage.getItem(RoleList)
}

export function setRole(Roles) {
  return localStorage.setItem(RoleList, Roles)
}

export function removeRole() {
  return localStorage.removeItem(RoleList)
}

export function getClusterName() {
  return localStorage.getItem(clusterToken)
}

export function setClusterName(cluster_name) {
  return localStorage.setItem(clusterToken, cluster_name)
}

export function removeClusterName() {
  return localStorage.removeItem(clusterToken)
}

export function getClusters() {
  return localStorage.getItem(clusterList)
}

export function setClusters(clusters) {
  return localStorage.setItem(clusterList, clusters)
}

export function removeClusters() {
  return localStorage.removeItem(clusterList)
}
