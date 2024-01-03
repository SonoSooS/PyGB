from ctypes import pointer
from ctypes.wintypes import MSG
from .WINAPI import CheckResult, CreateWindowExW, DefWindowProcW, DestroyWindow, DispatchMessageW, GetMessageW, GetModuleHandleW, WNDPROC, WNDCLASSW, InvalidateRect, RegisterClassW, CloseWindow, ShowWindow, UnregisterClassW, UpdateWindow, PeekMessageW, PostQuitMessage, SetWindowPos
from .WINAPI import HWND, UINT, LPARAM, WPARAM

class Window:
    _counter = 0
    _hInstance = GetModuleHandleW(None)
    _Msg = MSG()
    _LpMsg = pointer(_Msg)
    
    def __init__(self, wndproc=None, width=None, height=None):
        counter = self._counter
        self._counter = counter + 1
        
        if wndproc is None:
            wndproc = self.DefaultWndProc
        
        if not isinstance(wndproc, WNDPROC):
            wndproc = WNDPROC(wndproc)
        
        self.WndProc = wndproc # must store reference to prevent garbage collection of procedure
        self.ClassName = "PyJunkWndCls_%u" % counter
        
        wclass = WNDCLASSW()
        wclass.style = 0
        wclass.lpfnWndProc = self.WndProc
        wclass.hInstance = self._hInstance
        wclass.lpszClassName = self.ClassName
        
        width = width or 160
        height = height or 144
        
        #TODO: AdjustRect
        width += 16
        height += 40 - 1
        
        self.WndClass = CheckResult(RegisterClassW(pointer(wclass)))
        
        self.HWND = CheckResult(CreateWindowExW
        (
            0, self.WndClass, "PyJunkWnd", 0x008C0000,
            0, 0, width, height,
            None, None, self._hInstance, None
        ))
    
    def __del__(self):
        #CheckResult(CloseWindow(self.HWND))
        CheckResult(DestroyWindow(self.HWND) or True)
        self.HWND = None
        CheckResult(UnregisterClassW(self.WndClass, self._hInstance))
        self.WndClass = None
    
    @staticmethod
    def DefaultWndProc(wnd: HWND, msg: UINT, wparam: WPARAM, lparam: LPARAM):
        if msg == 0x10:
            PostQuitMessage(0)
        
        return DefWindowProcW(wnd, msg, wparam, lparam)
    
    @classmethod
    def LoopOnce(cls):
        lpMsg = cls._LpMsg
        while PeekMessageW(lpMsg, None, 0, 0, 1) > 0: # PM_REMOVE
            DispatchMessageW(lpMsg)
            
            if cls._Msg.message == 0x12: # WM_QUIT
                return False
        
        return True
    
    @classmethod
    def Loop(cls):
        lpMsg = cls._LpMsg
        while GetMessageW(lpMsg, None, 0, 0) > 0:
            DispatchMessageW(lpMsg)
    
    def Show(self):
        return ShowWindow(self.HWND, 1) # SW_SHOWNORMAL
    
    def Update(self):
        return UpdateWindow(self.HWND)
    
    def Invalidate(self):
        return InvalidateRect(self.HWND, None, False)
    
    def SetWindowPos(self, px, py):
        return SetWindowPos(self.HWND, None, px, py, 0, 0, 0x41)
