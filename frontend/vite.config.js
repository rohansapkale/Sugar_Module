import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig(({ command }) => {
  const isBuild = command === 'build'
  return {
    plugins: [vue()],
    base: isBuild ? '/assets/sugar_module/frontend/' : '/',
    build: {
      outDir: '../sugar_module/public/frontend',
      emptyOutDir: true,
      rollupOptions: {
        output: {
          entryFileNames: 'assets/[name].js',
          chunkFileNames: 'assets/[name].js',
          assetFileNames: 'assets/[name].[ext]',
        },
      },
    },
    server: {
      port: 8080,
      host: '0.0.0.0',
      watch: {
        ignored: ['**/node_modules/**', '**/.git/**', '**/public/**', '**/.system_generated/**'],
      },
      proxy: {
        '^/(api|app|login|logout|files)': {
          target: 'http://127.0.0.1:8001',
          changeOrigin: true,
          secure: false,
          headers: {
            'X-Frappe-Site-Name': 'sugar.local',
          },
        },
      },
    },
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
  }
})
