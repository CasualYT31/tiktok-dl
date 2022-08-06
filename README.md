# tiktok-dl
Command line utility to download TikTok videos and sort them by user.

# Installation Guide
1. Download this repository. The easiest way to do this as a user is to click on the Code button above, and then click on Download ZIP (or follow [this link](https://github.com/CasualYT31/tiktok-dl/archive/refs/heads/main.zip)). Extract the ZIP.
2. In order to use this program, you'll have to install Python 3.6+. Make sure to include the package manager `pip` in the installation.
3. Once Python has been installed, install the following packages using `pip install package_name`:
- `yt-dlp`
- `columnify`
- `requests_html`
4. Open a command line terminal. Use `cd` to navigate to where you downloaded [and extracted] the repository into. You are now ready to use tiktok-dl.

# Introduction
This program is split into two: `tiktok_dl` and `tiktok_config`. `tiktok_config` is used to set download properties for each user. `tiktok_dl` is then used to perform downloads. I have also written a Windows batch script, `ts.bat`, which will let you split the input links up into multiple `tiktok_dl` processes. `t.bat` is just to prevent you from having to type out `py[thon] tiktok_dl.py` each time.

It should be noted that `tiktok_dl.py` and `ts.bat` both accept command line arguments as the primary means of input, whilst `tiktok_config.py` is run without any command line arguments, and instead accepts input continuously until `Ctrl+C` is issued.

The manuals for both Python scripts can be found at the top of each script.

# Examples

# Feature Requests
If you would like to request a feature, feel free to make an issue on this repository. I will implement them at my own discretion.
