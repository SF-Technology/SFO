import router from './router'
import store from './store'
import { Message } from 'element-ui'
import NProgress from 'nprogress' // Progress 进度条
import 'nprogress/nprogress.css'// Progress 进度条样式
import { getToken, getRole } from '@/utils/cookie-util' // 验权

const whiteList = ['/login']
router.beforeEach((to, from, next) => {
  NProgress.start()
  if (getToken()) {
    if (to.path === '/login') {
      next({ path: '/' })
    } else {
      // let roles = getRole()
      if (store.getters.roles.length === 0) {
        store.dispatch('GetInfo').then(res => {
          store.dispatch('GenerateRoutes', { res }).then(() => {
            router.addRoutes(store.getters.addRouters)
            // next({ ...to })
            next({ ...to, replace: true })
          })
        }).catch((err) => {
          console.error(err)
          store.dispatch('FedLogOut').then(() => {
            Message.error('认证失败，请重新登录')
            next({ path: '/login' })
          })
        })
      }else {
        next()
      }
    }
  } else {
    if (whiteList.indexOf(to.path) !== -1) {
      next()
    } else {
      next('/login')
      NProgress.done()
    }
  }
})

router.afterEach(() => {
  NProgress.done() // 结束Progress
})
