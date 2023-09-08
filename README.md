# tuya-sync
Python script to change the colors of tuya smart lights to what is on the screen.

### Changes from forked repo
- Migration from pytuya to tinytuya
- Added dependencies on requirements.txt
- Made the Device ID, Device IP and Device Local Key available on .env file

### Future plans
- Initial Tuya Wizard/Scan and ditch env file to access the generated json files for the device information
- Recheck frame_color_lib for other improvements in generating colors from screenshot
- Check if possible to support DRM-locked content
- Web/Desktop/Mobile App
- Change tuya-sync to tuya-lights-controller-app for more functionalities other than light sync from screen

## Forked from
https://github.com/tvut/tuya-sync

### Based On
https://github.com/clach04/python-tuya

https://github.com/digital-concrete/light-sync
