# -*- coding: utf-8 -*-
"""从屏幕 DC 实时截取目标窗口顶部（先还原/置前），避免 PrintWindow 缓存旧帧。"""
import ctypes
import ctypes.wintypes as wt
import struct
import sys
import time
from pathlib import Path

user32 = ctypes.WinDLL("user32", use_last_error=True)
gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)
WNDENUMPROC = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)


def pick(pid):
    found = []

    def cb(hwnd, _):
        p = wt.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(p))
        if p.value == pid and user32.IsWindowVisible(hwnd):
            r = wt.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(r))
            w, h = r.right - r.left, r.bottom - r.top
            if w > 400 and h > 200:
                found.append((w * h, hwnd, r))
        return True

    user32.EnumWindows(WNDENUMPROC(cb), 0)
    return max(found)[1:] if found else (None, None)


def main():
    pid = int(sys.argv[1])
    h = int(sys.argv[2]) if len(sys.argv) > 2 else 160
    out = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("_shot.bmp")

    hwnd, r = pick(pid)
    if not hwnd:
        print("未找到窗口")
        return
    if user32.IsIconic(hwnd):
        user32.ShowWindow(hwnd, 9)
    user32.ShowWindow(hwnd, 5)
    user32.SetForegroundWindow(hwnd)
    time.sleep(1.2)

    user32.GetWindowRect(hwnd, ctypes.byref(r))
    x, y = r.left, r.top
    w, hh = r.right - r.left, min(r.bottom - r.top, h)

    hdc = user32.GetDC(0)
    mem = gdi32.CreateCompatibleDC(hdc)
    bmp = gdi32.CreateCompatibleBitmap(hdc, w, hh)
    gdi32.SelectObject(mem, bmp)
    gdi32.BitBlt(mem, 0, 0, w, hh, hdc, x, y, 0x00CC0020)

    class BIH(ctypes.Structure):
        _fields_ = [("biSize", wt.DWORD), ("biWidth", wt.LONG), ("biHeight", wt.LONG),
                    ("biPlanes", wt.WORD), ("biBitCount", wt.WORD), ("biCompression", wt.DWORD),
                    ("biSizeImage", wt.DWORD), ("biXPelsPerMeter", wt.LONG),
                    ("biYPelsPerMeter", wt.LONG), ("biClrUsed", wt.DWORD), ("biClrImportant", wt.DWORD)]
    bi = BIH(ctypes.sizeof(BIH), w, -hh, 1, 32, 0, w * hh * 4, 0, 0, 0, 0)
    buf = ctypes.create_string_buffer(w * hh * 4)
    gdi32.GetDIBits(mem, bmp, 0, hh, buf, ctypes.byref(bi), 0)
    header = struct.pack("<2sIHHI", b"BM", 54 + len(buf.raw), 0, 0, 54)
    info = struct.pack("<IiiHHIIiiII", 40, w, -hh, 1, 32, 0, w * hh * 4, 0, 0, 0, 0)
    out.write_bytes(header + info + buf.raw)
    gdi32.DeleteObject(bmp)
    gdi32.DeleteDC(mem)
    user32.ReleaseDC(0, hdc)
    print("saved", out, "%dx%d" % (w, hh))


if __name__ == "__main__":
    main()
