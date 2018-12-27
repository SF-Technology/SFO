/**
 * Create by wenboling on 2018/3/19
 */
import Mock from 'mockjs'

const List = []
const count = 30

for (let i = 0; i <= count; i++) {
  List.push(Mock.mock({
    id: '@increment',
    author: '@first',
    title: '@title(5, 10)',
    'status|1': ['published', 'draft', 'deleted'],
    display_time: '@datetime',
    pageviews: '@integer(1, 10)'
  }))
}

export default {
  getList: config => {
    return {
      total: List.length,
      items: List
    }
  }
}
