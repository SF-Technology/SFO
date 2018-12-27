import { loginByUsername, logout } from '@/api/login'
import { getToken, setToken, removeToken, setRole, getRole, setUsername, getUsername, removeRole } from '@/utils/cookie-util'

const user = {
  state: {
    token: getToken(),
    name: '',
    avatar: '',
    roles: []
  },

  mutations: {
    SET_TOKEN: (state, token) => {
      state.token = token
    },
    SET_NAME: (state, name) => {
      state.name = name
    },
    SET_AVATAR: (state, avatar) => {
      state.avatar = avatar
    },
    SET_ROLES: (state, roles) => {
      state.roles = roles
    }
  },

  actions: {
    // 登录
    Login({ commit }, userInfo) {
      const params = {
        server: window.location.href
      }
      const username = userInfo.username.trim()
      userInfo.username = username
      return new Promise((resolve, reject) => {
        loginByUsername(userInfo, params).then(response => {
          if(response.status === 200 || response.status === 201){
            // console.log(response)
            const data = response.data.data
            setToken(data.token)
            setRole(JSON.stringify(data.roles))
            setUsername(username)
            commit('SET_TOKEN', data.token)
            resolve()
          }
        }).catch(error => {
          reject(error)
        })
      })
    },

    // 获取用户信息
    GetInfo({ commit, state }) {
      return new Promise((resolve, reject) => {
        const roles = JSON.parse(getRole())
        const name = getUsername()
        commit('SET_ROLES', roles)
        commit('SET_NAME', name)
        resolve(roles)
      })
    },

    // 登出
    LogOut({ commit, state }) {
      return new Promise((resolve, reject) => {
        const data = {
          username: state.name
        }
        logout(data).then((response) => {
          if (response.status === 200 && response.data.status === 200){
            commit('SET_TOKEN', '')
            commit('SET_ROLES', [])
            commit('SET_NAME', '')
            // removeRole()
            // removeUsername()
            localStorage.clear()
            resolve()
          } else {
            reject(response)
          }
        }).catch(error => {
          reject(error)
        })
      })
    },

    // 前端 登出
    FedLogOut({ commit }) {
      return new Promise(resolve => {
        commit('SET_TOKEN', '')
        commit('SET_ROLES', [])
        removeToken()
        removeRole()
        resolve()
      })
    }
  }
}

export default user
