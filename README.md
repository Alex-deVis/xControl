# XControl

## About

[XControl](#xcontrol) is an automation framework for Linux that runs applications in nested X servers, enabling seamless communication without interfering with other applications.
It allows for sending keystrokes or mouse movements, searching for images on the application screen, and taking screenshots.

## Prerequisites

[`Xephyr`](https://wiki.archlinux.org/title/Xephyr), [`xdotool`](https://manpages.ubuntu.com/manpages/trusty/man1/xdotool.1.html), and [`spectrwm`](https://wiki.archlinux.org/title/spectrwm) are required for the nested X server.

```console
sudo apt-get install xserver-xephyr xdotool spectrwm
```

[`vglrun`](https://github.com/VirtualGL/virtualgl) is required to enable hardware acceleration.
You can get it from [github/releases](https://github.com/VirtualGL/virtualgl/releases/tag/3.1).

```console
wget https://github.com/VirtualGL/virtualgl/releases/download/3.1/virtualgl_3.1_amd64.deb
sudo dpkg -i virtualgl_3.1_amd64.deb
```

## Examples

### Launch Application

```python
from xControl import XControl

xc: XControl = XControl.get_instance(":15", 1024, 768)
xc.launch("firefox")
```

### Launch Applications On Multiple Xservers

`Note:` Running the same application on multiple Xservers seems to not work properly.

```python
from xControl import XControl

xc: XControl = XControl.get_instance(":15", 1024, 768)
xc.launch("firefox")
xc.type("Hello, World!")
xc.key("Return")

xc: XControl = XControl.get_instance(":15", 1024, 768)
xc.launch("subl")
xc.type("!dlroW ,olleH")
xc.key("Return")
```

### Extract Text From The Screen

```python
import time
from xControl import XControl, Frame, Point, OCR_SPEC, PSM

xc: XControl = XControl.get_instance(f":15", 1024, 768)
xc.launch("subl")
# Wait for the application to start
time.sleep(1)
xc.type("Hello world!")

# Capture the top-left corner of the screen
spec = OCR_SPEC(PSM.SINGLE_LINE, [0, 0, 0], [10, 10, 10])
txt = xc.extract_text(Frame(Point(0, 40), 200, 200), spec, preview=True)
```
