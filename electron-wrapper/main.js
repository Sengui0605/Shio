const { app, BrowserWindow, shell } = require("electron");
const http = require("http");

let win;

function createWindow() {
  win = new BrowserWindow({
    width: 1280, height: 800,
    minWidth: 900, minHeight: 600,
    title: "Shio AI",
    backgroundColor: "#08090e",
    frame: true,
    webPreferences: { nodeIntegration: false, contextIsolation: true },
    show: false,
  });

  win.setMenuBarVisibility(false);

  const tryLoad = (retries = 25) => {
    http.get("http://localhost:7860/health", res => {
      if (res.statusCode === 200) {
        win.loadURL("http://localhost:7860");
        win.once("ready-to-show", () => {
          win.show();
          win.maximize();
        });
      } else retry(retries);
    }).on("error", () => retry(retries));
  };

  const retry = (retries) => {
    if (retries <= 0) {
      win.loadURL("data:text/html,<body style=background:#08090e></body>");
      win.once("ready-to-show", () => win.show());
      return;
    }
    setTimeout(() => tryLoad(retries - 1), 1500);
  };

  tryLoad();
  win.webContents.setWindowOpenHandler(({ url }) => { shell.openExternal(url); return { action: "deny" }; });
  win.on("closed", () => { win = null; });
}

app.whenReady().then(createWindow);
app.on("window-all-closed", () => { if (process.platform !== "darwin") app.quit(); });
app.on("activate", () => { if (!win) createWindow(); });
