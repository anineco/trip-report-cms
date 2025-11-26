// vite.config.js
import { resolve } from 'path';
import { defineConfig } from 'vite';

const projectRoot = __dirname;
const srcRoot = resolve(projectRoot, 'src');
const base = './';
const outDir = resolve(projectRoot, 'dist/js');

export default defineConfig({
  root: srcRoot,
  envDir: projectRoot,
  base: base,
  build: {
    assetInlineLimit: 0,
    outDir: outDir,
    rollupOptions: {
      output: {
        entryFileNames: '[name].js',
        assetFileNames: '[name].js'
      },
      input: {
        tozan: resolve(srcRoot, 'tozan.js'),
        lightbox: resolve(srcRoot, 'lightbox.js')
      },
    }
  }
});
// __END__
