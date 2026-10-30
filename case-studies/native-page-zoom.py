#!/usr/bin/env python3
"""Send native Chromium page-zoom shortcuts in an isolated Xvfb display.

Use only while the intended Chromium window is focused. This is not a CSS,
DPR override, CDP pinch-scale or Playwright viewport emulation.
"""
import ctypes
import sys
import time


def zoom(steps):
    if not 1 <= steps <= 12:
        raise ValueError("steps must be 1..12")
    x11 = ctypes.CDLL("libX11.so.6")
    xtest = ctypes.CDLL("libXtst.so.6")
    x11.XOpenDisplay.argtypes = [ctypes.c_char_p]
    x11.XOpenDisplay.restype = ctypes.c_void_p
    x11.XGetInputFocus.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong), ctypes.POINTER(ctypes.c_int)]
    class ClassHint(ctypes.Structure):
        _fields_ = [("name", ctypes.c_void_p), ("klass", ctypes.c_void_p)]
    x11.XGetClassHint.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.POINTER(ClassHint)]
    x11.XGetClassHint.restype = ctypes.c_int
    x11.XKeysymToKeycode.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
    x11.XKeysymToKeycode.restype = ctypes.c_uint
    x11.XFlush.argtypes = [ctypes.c_void_p]
    x11.XFree.argtypes = [ctypes.c_void_p]
    x11.XCloseDisplay.argtypes = [ctypes.c_void_p]
    xtest.XTestFakeKeyEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_ulong]
    display = x11.XOpenDisplay(None)
    if not display:
        raise RuntimeError("An isolated X11 DISPLAY is required")
    try:
        focus = ctypes.c_ulong()
        revert = ctypes.c_int()
        x11.XGetInputFocus(display, ctypes.byref(focus), ctypes.byref(revert))
        hint = ClassHint()
        if not x11.XGetClassHint(display, focus.value, ctypes.byref(hint)):
            raise RuntimeError("Focused X11 window has no WM_CLASS")
        try:
            klass = ctypes.string_at(hint.klass).decode("utf-8", "replace")
        finally:
            x11.XFree(hint.name)
            x11.XFree(hint.klass)
        if klass not in ("Chromium", "Chromium-browser"):
            raise RuntimeError("Refusing to send keys outside focused Chromium: " + klass)
        ctrl = x11.XKeysymToKeycode(display, 0xFFE3)  # Control_L
        plus = x11.XKeysymToKeycode(display, 0x002B)  # plus
        if not ctrl or not plus:
            raise RuntimeError("Required X11 keysyms are unavailable")
        for _ in range(steps):
            for code, down in ((ctrl, 1), (plus, 1), (plus, 0), (ctrl, 0)):
                xtest.XTestFakeKeyEvent(display, code, down, 0)
            x11.XFlush(display)
            time.sleep(0.16)
        print("Sent", steps, "native Ctrl+plus shortcuts to focused", klass)
    finally:
        x11.XCloseDisplay(display)


if __name__ == "__main__":
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        raise SystemExit("Usage: native-page-zoom.py STEPS (1..12)")
    zoom(int(sys.argv[1]))
