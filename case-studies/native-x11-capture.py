#!/usr/bin/env python3
"""Capture a physical isolated Xvfb viewport as PNG via Xlib and stdlib.

At genuine Chromium page zoom, Playwright full-page PNG capture can contract
to the CSS viewport and crop content. A framebuffer image is viewport-only,
not a replacement for full-page inspection or accessibility testing.
"""
import ctypes
import struct
import sys
import zlib


class XImageHead(ctypes.Structure):
    _fields_ = [
        ("width", ctypes.c_int), ("height", ctypes.c_int),
        ("xoffset", ctypes.c_int), ("format", ctypes.c_int),
        ("data", ctypes.c_void_p), ("byte_order", ctypes.c_int),
        ("bitmap_unit", ctypes.c_int), ("bitmap_bit_order", ctypes.c_int),
        ("bitmap_pad", ctypes.c_int), ("depth", ctypes.c_int),
        ("bytes_per_line", ctypes.c_int), ("bits_per_pixel", ctypes.c_int),
        ("red_mask", ctypes.c_ulong), ("green_mask", ctypes.c_ulong),
        ("blue_mask", ctypes.c_ulong),
    ]


def chunk(tag, body):
    payload = tag + body
    return (struct.pack("!I", len(body)) + payload +
            struct.pack("!I", zlib.crc32(payload) & 0xFFFFFFFF))


def capture(filename):
    x11 = ctypes.CDLL("libX11.so.6")
    x11.XOpenDisplay.argtypes = [ctypes.c_char_p]
    x11.XOpenDisplay.restype = ctypes.c_void_p
    x11.XDefaultRootWindow.argtypes = [ctypes.c_void_p]
    x11.XDefaultRootWindow.restype = ctypes.c_ulong
    x11.XGetImage.argtypes = [ctypes.c_void_p, ctypes.c_ulong,
                             ctypes.c_int, ctypes.c_int, ctypes.c_uint,
                             ctypes.c_uint, ctypes.c_ulong, ctypes.c_int]
    x11.XGetImage.restype = ctypes.c_void_p
    x11.XCloseDisplay.argtypes = [ctypes.c_void_p]
    display = x11.XOpenDisplay(None)
    if not display:
        raise RuntimeError("Isolated Xvfb DISPLAY required")
    try:
        root = x11.XDefaultRootWindow(display)
        # Exact isolated GitHub Actions Xvfb screen. Do not capture any user's desktop.
        width, height = 1440, 1200
        image_ptr = x11.XGetImage(display, root, 0, 0, width, height,
                                 ctypes.c_ulong(-1).value, 2)  # ZPixmap
        if not image_ptr:
            raise RuntimeError("XGetImage failed")
        header = XImageHead.from_address(image_ptr)
        if (header.width != width or header.height != height or
                header.bits_per_pixel != 32 or header.byte_order != 0 or
                header.red_mask != 0xFF0000 or
                header.green_mask != 0xFF00 or header.blue_mask != 0xFF):
            raise RuntimeError("Unsupported Xvfb pixel format")
        raw = ctypes.string_at(header.data, header.bytes_per_line * height)
        scan = bytearray()
        for y in range(height):
            scan.append(0)
            start = y * header.bytes_per_line
            row = raw[start:start + 4 * width]
            for x in range(0, len(row), 4):
                scan.extend((row[x + 2], row[x + 1], row[x]))
        png = (b"\x89PNG\r\n\x1a\n" +
               chunk(b"IHDR", struct.pack("!2I5B", width, height, 8, 2, 0, 0, 0)) +
               chunk(b"IDAT", zlib.compress(scan, 6)) +
               chunk(b"IEND", b""))
        with open(filename, "wb") as out:
            out.write(png)
        print("Captured isolated physical Xvfb viewport", width, "x", height)
    finally:
        x11.XCloseDisplay(display)


if __name__ == "__main__":
    if len(sys.argv) != 2 or not sys.argv[1].endswith(".png"):
        raise SystemExit("Usage: native-x11-capture.py OUTPUT.png")
    capture(sys.argv[1])
