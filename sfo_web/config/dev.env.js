var merge = require('webpack-merge')
var prodEnv = require('./prod.env')

module.exports = merge(prodEnv, {
  NODE_ENV: '"development"',
  ENV_NAME: '"dev"',
  BASE_API: '"http://localhost"',
  SOCKET_BASE_URL: '"http://localhost"',
})
