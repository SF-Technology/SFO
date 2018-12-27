/**
 * Create by wenboling on 2018/6/12
 */

const alarms = {
  state: {
    connect: false,
    alarm_detail: {},
    alarm_total: 0
  },

  mutations: {
    SOCKET_CONNECT: (state, status) => {
      state.connect = true
    },
    SOCKET_ALARM_SERVER: (state, response) => {
      state.alarm_detail = response.data.alarm_detail
      state.alarm_total = response.data.alarm_total
    },
  },

  // actions: {
  //   socket_alarmServer:(context, message)=>{
  //     console.log("vuex log", message)
  //   }
  // }
}

export default alarms
