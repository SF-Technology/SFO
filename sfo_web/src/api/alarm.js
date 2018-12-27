/**
 * Create by wenboling on 2018/8/27
 */
import fetch from '@/utils/fetch'

export function updateAlarm(guid, data) {
  return fetch({
    url: `/api/alarmlog/${guid}/`,
    method: 'put',
    data: data
  })
}
