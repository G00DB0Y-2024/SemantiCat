import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  base: '',
  plugins: [vue()],
  // server: {
  //   port: 8225, // Vite 前端使用的端口
  //   proxy: {
  //     '/api': {
  //       target: 'http://127.0.0.1:8225', //这一点很重要！代理是运行在本机的，而不是浏览器，因此代理相当于通过域名找到本机地址后，代理自己去请求本机的后端！
  //       changeOrigin: true,
  //       rewrite: (path) => path.replace(/^\/api/, ''), // 重写路径
  //     },
  //     '/ws': {
  //       target: 'ws://127.0.0.1:8225', 
  //       changeOrigin: true,
  //       rewrite: (path) => path.replace(/^\/ws/, ''), // 重写路径
  //     },
  //   },
  // },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  build: {
    target: 'es6',
    outDir: 'pdfbar',
    assetsDir: 'assets',
    emptyOutDir: true,
    sourcemap: false,
    rollupOptions: {
      output: {
        entryFileNames: 'assets/[name].js',
        chunkFileNames: 'assets/[name].js',
        assetFileNames: 'assets/[name].[ext]'
      }
    }
  }
})
