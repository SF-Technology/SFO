/**
 * Create by wenboling on 2018/3/19
 */
import Mock from 'mockjs'
import tableAPI from './table'
import loginAPI from './login'
import dashboardAPI from './dashboard'

// 登录相关
Mock.mock(/\/user\/login/, 'post', loginAPI.loginByUsername)
Mock.mock(/\/user\/logout/, 'post', loginAPI.logout)
Mock.mock(/\/user\/info\.*/, 'get', loginAPI.getUserInfo)

// table相关
Mock.mock(/\/table\/list/, 'get', tableAPI.getList)

// dashboard相关
Mock.mock(/\/dashboard\/info/, 'get', dashboardAPI.getPhysicalScale)
Mock.mock(/\/dashboard\/swift\/info/, 'get', dashboardAPI.getSwiftInfo)

export default Mock

