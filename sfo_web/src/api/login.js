import fetch from '@/utils/fetch'

export function loginByUsername(userInfo) {
  return fetch({
    url: '/api/userlogin/',
    method: 'post',
    data: userInfo
  })
}

export function getUserInfo(token) {
  return fetch({
    url: '/api/userinfo/',
    method: 'get',
    params: { token }
  })
}

export function logout(data) {
  return fetch({
    url: '/api/userlogout/',
    method: 'post',
    data: data
  })
}
