import axios from 'axios'
import { Message } from 'element-ui'
import store from '../store'
import { getToken,removeToken } from '@/utils/cookie-util'

// 创建axios实例
const service = axios.create({
  baseURL: process.env.BASE_API, // api的base_url
  timeout: 60000,                  // 请求超时时间
  withCredentials: true          //允许携带cookies访问
})

// request拦截器
service.interceptors.request.use(config => {
  if (store.getters.token) {
    return config
  }
  return config
}, error => {
  // Do something with request error
  Promise.reject(error)
})

// respone拦截器
service.interceptors.response.use(
  response => response,
  error => {
    let res = error.response
    if(res.status && res.status >= 500){
      Message({
          message: "服务器错误, 请稍候",
          type: 'error',
          duration: 5 * 1000
        })
    }else if(res.status && res.status === 401){
      Message({
        message: "请先登录",
        type: 'error',
        duration: 5 * 1000
      })
      removeToken()
      localStorage.clear()
      this.$router.push('/login')
    }
    return Promise.reject(error)
  }
)

export default service
