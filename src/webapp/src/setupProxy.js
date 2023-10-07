const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http:/192.168.1.43:5000/api/v1/status',
      changeOrigin: true,
      // pathRewrite: {'^/api' : '/api/v1'}
    })
  );
};
