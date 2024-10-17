const chokidar = require('chokidar');
const { exec } = require('child_process');

const watcher = chokidar.watch('.', {
  ignored: /node_modules/,
  persistent: true
});

console.log('Watching for file changes...');

watcher
  .on('change', path => {
    console.log(`File ${path} has been changed`);
    exec('nginx -s reload', (error, stdout, stderr) => {
      if (error) {
        console.error(`Error: ${error.message}`);
        return;
      }
      if (stderr) {
        console.error(`stderr: ${stderr}`);
        return;
      }
      console.log(`Nginx reloaded: ${stdout}`);
    });
  });