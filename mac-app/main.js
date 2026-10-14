// Elmer Weather Station — Mac app window.
// Uses JavaScript for Automation (built into macOS) to open a native window with a WebKit view
// that runs the weather page bundled in this app's Resources folder. No compiler or extra software needed.
ObjC.import("Cocoa");
ObjC.import("WebKit");

var keep = {};   // hold references so nothing is cleaned up while the app runs

function addItem(menu, title, action, key, mods) {
  var item = menu.addItemWithTitleActionKeyEquivalent(title, action, key);
  if (mods !== undefined) item.keyEquivalentModifierMask = mods;
  return item;
}
function submenu(main, title) {
  var holder = $.NSMenuItem.alloc.init;
  var m = $.NSMenu.alloc.initWithTitle(title);
  holder.submenu = m;
  main.addItem(holder);
  return m;
}

// If anything goes wrong, say so on screen, write it to a log, and open the page in the web browser instead
function run(argv) {
  var res = argv[0];
  try { start(res); }
  catch (e) {
    var msg = String(e && e.message || e);
    try {
      var log = $.NSHomeDirectory().js + "/Library/Logs/Elmer Weather.log";
      $.NSString.alloc.initWithUTF8String(new Date().toString() + "\n" + msg + "\n")
        .writeToFileAtomicallyEncodingError(log, true, 4, null);
    } catch (e2) {}
    var sa = Application.currentApplication();
    sa.includeStandardAdditions = true;
    try {
      sa.displayDialog("Elmer Weather couldn't open its window:\n\n" + msg +
        "\n\nThe weather page will open in your web browser instead.",
        { withTitle: "Elmer Weather", buttons: ["OK"], defaultButton: "OK", withIcon: "caution" });
    } catch (e3) {}
    sa.doShellScript("open " + JSON.stringify(res + "/index.html"));
  }
}

function start(res) {
  var app = $.NSApplication.sharedApplication;
  app.setActivationPolicy(0);   // regular app: Dock icon and menu bar

  // Quit when the window closes
  ObjC.registerSubclass({
    name: "EWAppDelegate",
    methods: {
      "applicationShouldTerminateAfterLastWindowClosed:": {
        types: ["bool", ["id"]],
        implementation: function (sender) { return true; }
      }
    }
  });

  // The page sends links here so they open in the default web browser
  ObjC.registerSubclass({
    name: "EWLinkHandler",
    methods: {
      "userContentController:didReceiveScriptMessage:": {
        types: ["void", ["id", "id"]],
        implementation: function (controller, message) {
          var href = ObjC.unwrap(message.body);
          if (typeof href === "string" && /^https?:\/\//.test(href)) {
            $.NSWorkspace.sharedWorkspace.openURL($.NSURL.URLWithString(href));
          }
        }
      }
    }
  });

  keep.delegate = $.EWAppDelegate.alloc.init;
  app.delegate = keep.delegate;

  // Menu bar: app, Edit (so copy/paste work in the ZIP field), View, Window
  var CMD = 1 << 20, SHIFT = 1 << 17;
  var main = $.NSMenu.alloc.init;
  var appMenu = submenu(main, "Elmer Weather");
  addItem(appMenu, "Hide Elmer Weather", "hide:", "h");
  appMenu.addItem($.NSMenuItem.separatorItem);
  addItem(appMenu, "Quit Elmer Weather", "terminate:", "q");
  var edit = submenu(main, "Edit");
  addItem(edit, "Undo", "undo:", "z");
  addItem(edit, "Redo", "redo:", "z", CMD | SHIFT);
  edit.addItem($.NSMenuItem.separatorItem);
  addItem(edit, "Cut", "cut:", "x");
  addItem(edit, "Copy", "copy:", "c");
  addItem(edit, "Paste", "paste:", "v");
  addItem(edit, "Select All", "selectAll:", "a");
  var view = submenu(main, "View");
  addItem(view, "Reload", "reload:", "r");
  var win = submenu(main, "Window");
  addItem(win, "Minimize", "performMiniaturize:", "m");
  addItem(win, "Close", "performClose:", "w");
  app.mainMenu = main;
  app.windowsMenu = win;

  // Web view that runs the weather page
  var config = $.WKWebViewConfiguration.alloc.init;
  try { config.preferences.setValueForKey($.NSNumber.numberWithBool(true), "allowFileAccessFromFileURLs"); } catch (e) {}
  keep.links = $.EWLinkHandler.alloc.init;
  config.userContentController.addScriptMessageHandlerName(keep.links, "wxApp");

  var rect = $.NSMakeRect(0, 0, 1100, 880);
  var style = 1 | 2 | 4 | 8;   // titled, closable, minimizable, resizable
  keep.window = $.NSWindow.alloc.initWithContentRectStyleMaskBackingDefer(rect, style, 2, false);   // 2 = buffered backing store
  keep.window.title = "Elmer Weather Station";
  keep.window.releasedWhenClosed = false;
  keep.window.minSize = $.NSMakeSize(420, 520);
  keep.window.center;
  keep.window.setFrameAutosaveName("ElmerWeatherMainWindow");   // remembers size and position

  keep.web = $.WKWebView.alloc.initWithFrameConfiguration(rect, config);
  keep.web.autoresizingMask = 2 | 16;   // grow with the window
  keep.window.contentView = keep.web;

  var page = $.NSURL.fileURLWithPath(res + "/index.html");
  keep.web.loadFileURLAllowingReadAccessToURL(page, $.NSURL.fileURLWithPath(res));

  keep.window.makeKeyAndOrderFront(null);
  app.activateIgnoringOtherApps(true);
  app.run;
}
