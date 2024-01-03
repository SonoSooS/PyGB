from ctypes import GetLastError, c_bool, c_int, c_size_t, c_ubyte, c_void_p, c_wchar_p, windll, POINTER, pointer, c_long, WINFUNCTYPE, Structure, cast, WinDLL, c_uint, sizeof, byref
from ctypes.wintypes import HANDLE, HHOOK, HINSTANCE, BOOL, HMODULE, HRGN, LPRECT, LPUINT, POINT, WPARAM, LPARAM, MSG, LPMSG, HWND, UINT, HMENU, LPVOID, POINT, LPPOINT, RECT, ATOM, HDC, BYTE, DWORD, WORD

import enum


LRESULT = c_long
LONG = c_long

WNDPROC = WINFUNCTYPE(LRESULT, HWND, UINT, WPARAM, LPARAM)

class Win32Exception(Exception):
    def __init__(self, errcode=None):
        if errcode is None:
            errcode = GetLastError()
        
        if isinstance(errcode, LRESULT):
            errcode = errcode.value
        
        #TODO: FormatMessageW
        
        super().__init__("WINAPI error %08X" % errcode)

class SafeHandle(HANDLE):
    def __del__(self):
        self.Destroy()
    
    def Destroy(self):
        if CloseHandle(self.value):
            self.value = 0
        else:
            raise Win32Exception()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.Destroy()
        return False

def CheckResult(result=None):
    if result is not None:
        if not result:
            raise Win32Exception()
        return result
    
    errcode = GetLastError()
    if errcode:
        raise Win32Exception(errcode)
    
    return result

def WINAPI(func, res, params):
    func.restype = res
    func.argtypes = params
    
    return func

class WindowMessage(enum.IntEnum):
    WM_CREATE = 0x0001
    WM_DESTROY = 0x0002
    WM_SIZE = 0x0005
    WM_PAINT = 0x000F
    WM_CLOSE = 0x0010
    WM_KEYDOWN = 0x0100
    WM_KEYUP = 0x0101
    WM_EXITSIZEMOVE = 0x0232

class VirtualKey(enum.IntEnum):
    VK_BACK = 0x08
    VK_RETURN = 0x0D
    VK_LEFT = 0x25
    VK_UP = 0x26
    VK_RIGHT = 0x27
    VK_DOWN = 0x28
    VK_X = ord('X')
    VK_C = ord('C')

class IDHOOK(enum.IntEnum):
    WH_CALLWNDPROC = 4
    WH_CALLWNDPROCRET = 12
    #WH_FOREGROUNDIDLE = 11
    WH_GETMESSAGE = 3

class ActionMode(enum.IntFlag):
    AM_NONE = 0
    AM_REDRAW = 1
    AM_MOUSE = 2

class CWPSTRUCT(Structure):
    _fields_ =\
    [
        ("lParam", LPARAM),
        ("wParam", WPARAM),
        ("message", UINT),
        ("hwnd", HWND)
    ]
LPCWPSTRUCT = POINTER(CWPSTRUCT)

class CWPRETSTRUCT(Structure):
    _fields_ =\
    [
        ("lResult", LRESULT),
        ("lParam", LPARAM),
        ("wParam", WPARAM),
        ("message", UINT),
        ("hwnd", HWND)
    ]
LPCWPRETSTRUCT = POINTER(CWPRETSTRUCT)

class WNDCLASSW(Structure):
    _fields_ =\
    [
        ("style", UINT),
        ("lpfnWndProc", WNDPROC),
        ("cbClsExtra", c_int),
        ("cbWndExtra", c_int),
        ("hInstance", HINSTANCE),
        ("hIcon", LPVOID),
        ("hCursor", LPVOID),
        ("hbrBackground", LPVOID),
        ("lpszMenuName", c_wchar_p),
        ("lpszClassName", c_wchar_p)
    ]
LPWNDCLASSW = POINTER(WNDCLASSW)

class COPYDATASTRUCT(Structure):
    _fields_ =\
    [
        ("dwData", c_size_t),
        ("cbData", c_uint),
        ("lpData", LPVOID)
    ]
LPCOPYDATASTRUCT = POINTER(COPYDATASTRUCT)

class PAINTSTRUCT(Structure):
    _fields_ =\
    [
        ('hdc', HDC),
        ('fErase', BOOL),
        ('rcPaint', RECT),
        ('fRestore', BOOL),
        ('fIncUpdate', BOOL),
        ('rgbReserved', BYTE * 32)
    ]
LPPAINTSTRUCT = POINTER(PAINTSTRUCT)

class BITMAPINFOHEADER(Structure):
    _fields_ =\
    [
        ('biSize', DWORD),
        ('biWidth', LONG),
        ('biHeight', LONG),
        ('biPlanes', WORD),
        ('biBitCount', WORD),
        ('biCompression', DWORD),
        ('biSizeImage', DWORD),
        ('biXPelsPerMeter', LONG),
        ('biYPelsPerMeter', LONG),
        ('biClrUsed', DWORD),
        ('biClrImportant', DWORD)
    ]
LPBITMAPINFOHEADER = POINTER(BITMAPINFOHEADER)

class RGBQUAD(Structure):
    _fields_ =\
    [
        ('rgbBlue', BYTE),
        ('rgbGreen', BYTE),
        ('rgbRed', BYTE),
        ('rgbReserved', BYTE)
    ]
    
    def SetColorRGBA8(self, px):
        self.rgbRed = (px >> 0) & 0xFF
        self.rgbGreen = (px >> 8) & 0xFF
        self.rgbBlue = (px >> 16) & 0xFF
        self.rgbReserved = (px >> 24) & 0xFF
    
    def SetColorRGB565(self, px):
        self.rgbReserved = 0xFF
        self.rgbRed = (px << 3) & 0xF8
        self.rgbGreen = (px >> 3) & 0xFC
        self.rgbBlue = (px >> 8) & 0xF8

class BITMAPINFOHEADER_4PAL(Structure):
    _fields_ =\
    [
        ('header', BITMAPINFOHEADER),
        ('palette', RGBQUAD * 4)
    ]

class BITMAPINFOHEADER_4BF(Structure):
    _fields_ =\
    [
        ('header', BITMAPINFOHEADER),
        ('palette', DWORD * 4)
    ]

# type: ignore
GetMessageW = WINAPI(windll.user32.GetMessageW, c_int, [LPMSG, HWND, UINT, UINT])
PeekMessageW = WINAPI(windll.user32.PeekMessageW, c_int, [LPMSG, HWND, UINT, UINT, UINT])
TranslateMessage = WINAPI(windll.user32.TranslateMessage, BOOL, [LPMSG])
DispatchMessageW = WINAPI(windll.user32.DispatchMessageW, LRESULT, [LPMSG])

CreateWindowExW = WINAPI(windll.user32.CreateWindowExW, HWND, [c_uint, ATOM, c_wchar_p, c_uint, c_int, c_int, c_int, c_int, HWND, HMENU, HINSTANCE, LPVOID])
ShowWindow = WINAPI(windll.user32.ShowWindow, BOOL, [HWND, c_uint])
CloseWindow = WINAPI(windll.user32.CloseWindow, BOOL, [HWND])
UpdateWindow = WINAPI(windll.user32.UpdateWindow, BOOL, [HWND])
SetWindowPos = WINAPI(windll.user32.SetWindowPos, BOOL, [HWND, HWND, c_int, c_int, c_int, c_int, c_uint])
DestroyWindow = WINAPI(windll.user32.DestroyWindow, BOOL, [HWND])

RegisterClassW = WINAPI(windll.user32.RegisterClassW, ATOM, [LPWNDCLASSW])
UnregisterClassW = WINAPI(windll.user32.UnregisterClassW, BOOL, [ATOM, HINSTANCE])
DefWindowProcW = WINAPI(windll.user32.DefWindowProcW, LRESULT, [HWND, UINT, WPARAM, LPARAM])

PostQuitMessage = WINAPI(windll.user32.PostQuitMessage, None, [c_int])
RedrawWindow = WINAPI(windll.user32.RedrawWindow, BOOL, [HWND, LPRECT, HRGN, UINT])
PostMessageW = WINAPI(windll.user32.PostMessageW, BOOL, [HWND, UINT, WPARAM, LPARAM])
PostThreadMessageW = WINAPI(windll.user32.PostThreadMessageW, BOOL, [UINT, UINT, WPARAM, LPARAM])

InvalidateRect = WINAPI(windll.user32.InvalidateRect, BOOL, [HWND, LPRECT, BOOL])
SetWindowLongW = WINAPI(windll.user32.SetWindowLongW, LONG, [HWND, c_int, LONG])
GetClientRect = WINAPI(windll.user32.GetClientRect, BOOL, [HWND, LPRECT])
GetWindowRect = WINAPI(windll.user32.GetWindowRect, BOOL, [HWND, LPRECT])
ClientToScreen = WINAPI(windll.user32.ClientToScreen, BOOL, [HWND, LPPOINT])

GetModuleHandleW = WINAPI(windll.kernel32.GetModuleHandleW, HINSTANCE, [c_wchar_p])
CloseHandle = WINAPI(windll.kernel32.CloseHandle, c_bool, [HANDLE])
LoadLibraryW = WINAPI(windll.kernel32.LoadLibraryW, HMODULE, [c_wchar_p])
#GetLastError = WINAPI(windll.kernel32.GetLastError, LRESULT, None)

BeginPaint = WINAPI(windll.user32.BeginPaint, HDC, [HWND, LPPAINTSTRUCT])
EndPaint = WINAPI(windll.user32.EndPaint, BOOL, [HWND, LPPAINTSTRUCT])

StretchDIBits = WINAPI(windll.gdi32.StretchDIBits, c_int, [HDC, c_int, c_int, c_int, c_int, c_int, c_int, c_int, c_int, c_void_p, LPBITMAPINFOHEADER, UINT, DWORD])
