/**
 * Create by wenboling on 2018/3/20
 */
import Mock from 'mockjs'

const proxy_server = 4
const storage_node = 9

const capacity_total = 100000000

const bandwidth_total = 100000000

const x_axis = []

for (let i = 1; i <= 30; i++) {
  x_axis.push(i)
}

const physical_scale = Mock.mock({
  proxy_server: {
    total: proxy_server,
    online: '@integer(1, 4)'
  },
  storage_server: {
    total: storage_node,
    online: '@integer(1, 9)'
  },
  capacity: {
    total: capacity_total,
    used: '@integer(1, 100000000)'
  },
  bandwidth: {
    total: bandwidth_total,
    used: '@integer(1, 100000000)'
  },
  ops: {
    xAxis: x_axis,
    'ops|30': ['@integer(1, 10000)']
  }
})

const swift_info = Mock.mock({
  accounts: '@integer(1, 100)',
  containers: '@integer(1, 1000)',
  objects: '@integer(1, 10000)'
})

export default {
  getPhysicalScale: config => {
    return {
      physical_scale
    }
  },
  getSwiftInfo: config => {
    return {
      swift_info
    }
  }
}
