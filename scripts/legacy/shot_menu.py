# -*- coding: utf-8 -*-
"""用 ctypes 抓取指定进程主窗口的顶部区域（仅菜单栏/工具栏），输出 BMP。

不依赖 .NET / COM；只截目标进程窗口，避免把桌面其它内容带出来。
用法：python scripts/shot_menu.py <pid> [高度]
"""
import ctypes
import ctypes.wintypes as wt
import struct
import sys
from pathlib import Path

user32 = ctypes.WinDLL("user32", use_last_error=True)
gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)

WNDENUMPROC = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)


def main():
    pid = int(sys.argv[1])
    height = int(sys.argv[2]) if len(sys.argv) > 2 else 220
    out = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("_menu.bmp")

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
    if not found:
        print("未找到窗口")
        return
    found.sort(reverse=True)
    _, hwnd, r = found[0]
    w, h = r.right - r.left, min(r.bottom - r.top, height)
    print("窗口 %dx%d，截取 %dx%d" % (r.right - r.left, r.bottom - r.top, w, h))

    hdc_screen = user32.GetWindowDC(hwnd)
    hdc_mem = gdi32.CreateCompatibleDC(hdc_screen)
    hbmp = gdi32.CreateCompatibleBitmap(hdc_screen, w, h)
    gdi32.SelectObject(hdc_mem, hbmp)
    # PW_RENDERFULLCONTENT=2 先试 PrintWindow，失败则 BitBlt
    ok = user32.PrintWindow(hwnd, hdc_mem, 2)
    if not ok:
        gdi32.BitBlt(hdc_mem, 0, 0, w, h, hdc_screen, 0, 0, 0x00CC0020)

    class BITMAPINFOHEADER(ctypes.Structure):
        _fields_ = [("biSize", wt.DWORD), ("biWidth", wt.LONG), ("biHeight", wt.LONG),
                    ("biPlanes", wt.WORD), ("biBitCount", wt.WORD),
                    ("biCompression", wt.DWORD), ("biSizeImage", wt.DWORD),
                    ("biXPelsPerMeter", wt.LONG), ("biYPelsPerMeter", wt.LONG),
                    ("biClrUsed", wt.DWORD), ("biClrImportant", wt.DWORD)]

    bi = BITMAPINFOHEADER()
    bi.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    bi.biWidth, bi.biHeight = w, -h          # 负数=自上而下
    bi.biPlanes, bi.biBitCount = 1, 32
    bi.biCompression = 0
    buf = ctypes.create_string_buffer(w * h * 4)
    gdi32.GetDIBits(hdc_mem, hbmp, 0, h, buf, ctypes.byref(bi), 0)

    header = struct.pack("<2sIHHI", b"BM", 14 + 40 + w * h * 4, 0, 0, 14 + 40)
    info = struct.pack("<IiiHHIIiiII", 40, w, -h, 1, 32, 0, w * h * 4, 0, 0, 0, 0)
    out.write_bytes(header + info + buf.raw)

    gdi32.DeleteObject(hbmp)
    gdi32.DeleteDC(hdc_mem)
    user32.ReleaseDC(hwnd, hdc_screen)
    print("saved", out, "PrintWindow=", bool(ok))


if __name__ == "__main__":
    main()
