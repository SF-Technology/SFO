/**
 * Create by wenboling on 2018/7/6
 */

import fetch from '@/utils/fetch'

export function getLogs(params) {
  return fetch({
    url: '/api/tasks/',
    method: 'get',
    params: params
  })
}

export function getTaskLogs(params) {
  return fetch({
    url: '/api/tasks/logs/',
    method: 'get',
    params: params
  })
}

export function getAlarmLogsHistory(params) {
  return fetch({
    url: '/api/alarmlog/',
    method: 'get',
    params: params
  })
}
