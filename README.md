# Spotify Remote UI
An application which displays a touch-friendly UI with Spotify playback information and controls.

# How to build?
Clone the repository and enter into it first:
```bash
git clone https://github.com/bartekmuzyk/spotify-remote-ui.git
cd spotify-remote-ui
```
Then install dependencies and build a binary:
```bash
pip install -r requirements.txt
pyinstaller SpotifyRemoteUI.spec
```
The binary will be located in `dist/SpotifyRemoteUI` in the format suitable for your current platform.
**To build a binary for a different platform use a virtual machine or Windows Subsystem for Linux (WSL).**

# How to run?
In order for the app to function properly it needs a pair of OAuth credentials - namely the client ID and secret - which
you pass to the program as two positional arguments, so you probably want to start this program with a terminal.

To run with default options you can use this syntax (assuming the name of the executable is `SpotifyRemoteUI`):
```bash
./SpotifyRemoteUI CLIENT_ID CLIENT_SECRET
```
Where `CLIENT_ID` and `CLIENT_SECRET` are proper values.

If no additional configuration is passed, the displayed window will be 480 pixels in width, 320 pixels in height and frame-less.
Also, the default `en_US.utf8` locale will be used, which means that some text will be in the *English (United States)* language.

To change those properties you can use options as described in the help text:
```bash
./SpotifyRemoteUI --help
```
