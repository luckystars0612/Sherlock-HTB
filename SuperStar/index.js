const { app, BrowserWindow } = require('electron');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

let mainWindow = '';
//const powershell = fs.readFileSync(`C:\\Users\\Public\\test.txt`, 'utf8', data => data);

function createWindow() {
    mainWindow = new BrowserWindow({ width: 800, height: 600,
	  webPreferences: {
		contextIsolation: false,
		nodeIntegration: true,
		nodeIntegrationInWorker: true,
		preload: path.resolve(`${process.resourcesPath}/../extraResources/preload.js`)
	}});
    mainWindow.loadFile(`${__dirname}/public/testPage.html`);
    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}
//path.resolve(`${__dirname}/preload.js`)
//fork(powershell);

app.on('ready', createWindow);

app.on('window-all-closed', () => process.platform !== 'darwin' && app.quit());
// re-create a window on mac
app.on('activate', () => mainWindow === null && createWindow());