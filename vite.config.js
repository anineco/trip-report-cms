// vite.config.js
import { resolve } from 'path';
import { defineConfig } from 'vite';
import env from 'vite-plugin-env-compatible';

const root = resolve(__dirname, 'src');
const base = './';
const outDir = resolve(__dirname, 'dist/js');

export default defineConfig({
  root,
  base,
  plugins: [
    env({prefix: 'VITE', mountedPath: 'process.env'})
  ],
  build: {
    assetInlineLimit: 0,
    outDir,
    rollupOptions: {
      output: {
        entryFileNames: '[name].js',
        assetFileNames: '[name].js'
      },
      input: {
        tozan: resolve(root, 'tozan.js'),
        lightbox: resolve(root, 'lightbox.js')
      },
    }
  }
});
// __END__
