# Elmer Weather Station

A simple weather program for Elmer, NJ, with a Mac OS X Tiger-style Aqua interface.

- Time and date
- Current temperature and conditions
- Live video from the NJDOT traffic camera at Route 47 and Route 40, Franklin Township (shown for places within 30 miles of it)
- Week-ahead outlook
- Live NWS Doppler radar (nearest radar site, KDIX for Elmer)
- Active weather alerts for the selected area
- Change ZIP codes to see other areas (Elmer stays saved as Home)

## Use it

**Web page:** open `index.html` in Safari, Chrome or any browser.

**Mac app:** download `dist/Elmer-Weather.dmg` and double-click it. In the window that opens, drag **Elmer Weather** onto the **Applications** folder, then eject the disk.
The app isn't signed by Apple, so before the first launch run this in Terminal:

```
xattr -dr com.apple.quarantine "/Applications/Elmer Weather.app"
```

(Or open it once, then go to System Settings > Privacy & Security and click **Open Anyway**.)

A zip of the same app is also in `dist/Elmer-Weather-mac.zip`, for sending by email.

## Rebuild the Mac app

```
cd mac-app
python3 build.py                                        # app + zip; needs Python 3 and Pillow
python3 build.py --dmg-tools /path/to/libdmg-hfsplus    # also builds dist/Elmer-Weather.dmg
```

The .dmg step uses Mozilla's [libdmg-hfsplus](https://github.com/mozilla/libdmg-hfsplus) (build it with `cmake -B build && make -C build`), so it works on Linux too.
On a Mac you can make the disk image with the built-in tool instead:

```
hdiutil create -volname "Elmer Weather" -srcfolder mac-app/dist/dmg-root -format UDZO dist/Elmer-Weather.dmg
```

The app opens a native window with a WebKit view using JavaScript for Automation, which is built into macOS. No compiler needed.

## Data and images

- Weather data, radar imagery and alerts: U.S. National Weather Service (api.weather.gov, radar.weather.gov), works of the U.S. Government in the public domain.
- Live camera: New Jersey Department of Transportation traffic camera (via 511NJ), shown unchanged. NJDOT's terms of use let anyone view, copy or distribute its information.
- ZIP code lookup: Zippopotam.us (place names and coordinates only).
- Weather icons and the app icon are original drawings released to the public domain (CC0).
- The Aqua-style window, buttons and pinstripes are drawn from scratch in CSS. No Apple artwork, logos or system images are used.
