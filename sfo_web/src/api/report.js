import fetch from '@/utils/fetch'

export function getReportList(params) {
  return fetch({
    url: '/api/report/daily',
    method: 'get',
    params: params
  })
}
