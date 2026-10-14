# Elmer Weather Station

A simple weather program for Elmer, NJ, with a Mac OS X Tiger-style Aqua interface.

- Time and date
- Current temperature and conditions
- Week-ahead outlook
- Live NWS Doppler radar (nearest radar site, KDIX for Elmer)
- Active weather alerts for the selected area
- Change ZIP codes to see other areas (Elmer stays saved as Home)

## Use it

**Web page:** open `index.html` in Safari, Chrome or any browser.

**Mac app:** download `dist/Elmer-Weather-mac.zip`, unzip it, and drag **Elmer Weather** into Applications.
The app isn't signed by Apple, so before the first launch run this in Terminal:

```
xattr -dr com.apple.quarantine "/Applications/Elmer Weather.app"
```

## Rebuild the Mac app

```
cd mac-app
python3 build.py     # needs Python 3 and Pillow
```

The app opens a native window with a WebKit view using JavaScript for Automation, which is built into macOS. No compiler needed.

## Data and images

- Weather data, radar imagery and alerts: U.S. National Weather Service (api.weather.gov, radar.weather.gov), works of the U.S. Government in the public domain.
- ZIP code lookup: Zippopotam.us (place names and coordinates only).
- Weather icons and the app icon are original drawings released to the public domain (CC0).
- The Aqua-style window, buttons and pinstripes are drawn from scratch in CSS. No Apple artwork, logos or system images are used.
