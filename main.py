import sys
from glob import glob

from libgb.cpu import CPU
from libgb.ppu import PPU
from libgb.cartridge import Cartridge
from libgb.bus import BUS_ACCESS_READ, BUS_ACCESS_WRITE, BUS_ACCESS_MEMREQ
from junk.window import Window

from junk import WINAPI
from junk.WINAPI import HWND, LPARAM, WPARAM, UINT, HDC, PAINTSTRUCT, pointer, BITMAPINFOHEADER, sizeof, byref, BITMAPINFOHEADER_4PAL, RECT, c_void_p

def buslog(*args, **kwargs): pass
#def buslog(*args, **kwargs): print(*args, **kwargs)

def main():
    romdata = None
    bootmeme = None
    
    filename = None
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    
    if not filename:
        #filename = glob('C:/Downloads/02-*.gb')[0]
        #filename = glob('C:/Downloads/03-*.gb')[0]
        filename = 'C:/Downloads/cpu_instrs.gb'
    
    with open(filename, 'rb') as fi:
        romdata = fi.read()
    
    try:
        with open('C:/Data/lolol/PicoGB/testrom.gb', 'rb') as fi:
            bootmeme = fi.read(256)
    except:
        pass
    
    mappertype = Cartridge.ClassFromHeuristics(romdata)
    if not mappertype:
        print("Mapper not supported")
        sys.exit(1)
    
    cart = mappertype(romdata)
    
    cpu = CPU()
    
    cpu.ResetClear()
    cpu.RESET_STABLE = True
    
    cpu.reg.PC = 0x100
    
    cpubus = cpu.bus
    
    if bootmeme:
        cpu.ProtectOverlay = True
        cpu.reg.PC = 0
    
    ppu = PPU()
    
    tmpwram = [0xFF] * 0x2000
    tmpio = [0xFF] * 255
    
    JOYP_RAW = 0
    JOYP_PREV = 0xF
    
    def update_JOYP():
        nonlocal JOYP_PREV
        
        P1 = tmpio[0]
        
        if not (~P1 & 0x30):
            return
        
        jpsel = (P1 & 0x30) | 0xCF
        
        if not (P1 & 0x10):
            jpsel &= ~((JOYP_RAW >> 4) & 0xF)
        if not (P1 & 0x20):
            jpsel &= ~((JOYP_RAW >> 0) & 0xF)
        
        tmpio[0] = jpsel
        jpsel &= 0xF
        
        if JOYP_PREV == 0xF and jpsel != 0xF:
            cpu.IRQ_SetM(1 << 4)
        
        JOYP_PREV = jpsel
    
    tmpio[0x44] = 0x90
    tmpio[0x41] = 0x81
    tmpio[0x40] = 0x91
    
    pause = False
    autodump = False
    count = 0
    ppu_ticked = False
    
    bipal = BITMAPINFOHEADER_4PAL()
    bmi: BITMAPINFOHEADER = bipal.header
    bmi.biSize = sizeof(bmi)
    bipal.palette[0].value = 0x1F << 0
    bipal.palette[1].value = 0x3F << 5
    bipal.palette[2].value = 0x1F << 11
    bipal.palette[3].value = 0
    
    bmi.biPlanes = 1
    bmi.biWidth = ppu.FRAMEBUF_STRIDE
    bmi.biHeight = -ppu.FRAMEBUF_HEIGHT
    bmi.biBitCount = 16
    bmi.biSizeImage = abs(ppu.FRAMEBUF_STRIDE * ppu.FRAMEBUF_HEIGHT * 2)
    #bmi.biCompression = 3 # BI_BITFIELDS
    bmi.biCompression = 0 # BI_RGB
    
    winscale = 4
    fbpos = (0, 0, 176, 144)
    #rekt = (0, 0, ppu.FRAMEBUF_STRIDE * winscale, ppu.FRAMEBUF_HEIGHT * winscale)
    rekt = (0, 0, fbpos[2] * winscale, fbpos[3] * winscale)
    
    window: Window = None # type: ignore
    def wndproc(wnd: HWND, msg: UINT, wparam: WPARAM, lparam: LPARAM):
        if msg == 0x0F:
            pstr = PAINTSTRUCT()
            lppstr = byref(pstr)
            lpbmi = byref(bmi)
            dc: HDC = WINAPI.BeginPaint(wnd, lppstr)
            
            img_ptr = c_void_p(ppu.Framebuf.buffer_info()[0])
            
            
            WINAPI.StretchDIBits\
            (
                dc,
                rekt[0], rekt[1], rekt[2] - rekt[0], rekt[3] - rekt[1],
                fbpos[0], ppu.FRAMEBUF_HEIGHT - fbpos[3] + fbpos[1], fbpos[2], fbpos[3],
                img_ptr,
                lpbmi,
                0, # DIB_RGB_COLORS
                0x00CC0020 # SRCCOPY
            )
            
            WINAPI.EndPaint(wnd, lppstr)
        elif msg == 0x100 or msg == 0x101:
            nbit = 0
            
            if wparam == 88: # X
                nbit = 1 << 0
            elif wparam == 67: # C
                nbit = 1 << 1
            elif wparam == 8: # VK_BACK
                nbit = 1 << 2
            elif wparam == 13: # VK_RETURN
                nbit = 1 << 3
            elif wparam == 0x27: # VK_RIGHT
                nbit = 1 << 4
            elif wparam == 0x25: # VK_LEFT
                nbit = 1 << 5
            elif wparam == 0x26: # VK_UP
                nbit = 1 << 6
            elif wparam == 0x28: # VK_DOWN
                nbit = 1 << 7
            elif wparam == 81: # Q
                WINAPI.PostQuitMessage(0)
            
            if nbit:
                nonlocal JOYP_RAW
                
                if not (lparam & (1 << 31)): # type: ignore
                    JOYP_RAW |= nbit
                else:
                    JOYP_RAW &= ~nbit
                
                update_JOYP()
        
        return Window.DefaultWndProc(wnd, msg, wparam, lparam)
    
    #window = Window(wndproc, 168, 144)
    #window = Window(wndproc, ppu.FRAMEBUF_STRIDE, ppu.FRAMEBUF_HEIGHT)
    window = Window(wndproc, rekt[2] - rekt[0], rekt[3] - rekt[1])
    #window.SetWindowPos(274, 474)
    window.SetWindowPos(116, 300)
    window.Show()
    
    def dumpstate():
        print("! State dump")
        print("- BC: %04X" % cpu.reg.BC)
        print("- DE: %04X" % cpu.reg.DE)
        print("- HL: %04X" % cpu.reg.HL)
        print("- AF: %02X%01Xx" % (cpu.reg.A, cpu.reg.F >> 4))
        print("- PC: %04X" % cpu.reg.PC)
        print("- SP: %04X" % cpu.reg.SP)
        
        print("! Internals")
        print("- IME: %u" % (cpu.IME))
        print("- IE:  %02X" % cpu.REG_IE)
        print("- IF:  %02X (<-- %02X <-- %02X) & %02X" % (cpu.REG_IF, cpu.REG_IF_DELAY1, cpu.REG_IF_DELAY2, cpu.REG_IF_CLR))
        print("- ISR: %02X" % cpu.IRQ)
        print("- DV:  %02X" % (cpu.DV))
        if cpu.bus.Access:
            addrstr = ''
            datastr = '--'
            if cpu.bus.RD:
                addrstr += " /RD"
            if cpu.bus.WR:
                addrstr += " /WR"
                datastr = "%02X" % cpu.bus.Data
            if cpu.bus.MemReq:
                addrstr += " /MEMREQ"
            
            addrstr = "%04X %s%s" % (cpu.bus.Address, datastr, addrstr)
            print("- Bus: %s" % (addrstr))
        else:
            print("- Bus: ---- --")
        if cpu.STATE_CB:
            print("- $CB $%02X M%u" % (cpu.IR, cpu.STATE_IDX - 1))
        else:
            print("- $%02X M%u" % (cpu.IR, cpu.STATE_IDX - 1))
    
    def DIV_update(new, old):
        if tmpio[0x07] & 4:
            bit = 1 << (7, 1, 3, 5)[tmpio[0x07]&3]
            if not (new & bit) and not not (old & bit):
                val = tmpio[0x05]
                if val == 0xFF:
                    val = tmpio[0x06]
                    cpu.IRQ_SetM(1 << 2)
                else:
                    val += 1
                tmpio[0x05] = val
    
    from msvcrt import kbhit
    
    while True:
        if cpu.reg.PC == 0x101:
            #pause = True
            pass
        
        if count:
            count -= 1
        else:
            count = 1048
            
            window.Invalidate()
            window.Update()
            
            if not Window.LoopOnce():
                break
            
            if kbhit():
                pause = True
        
        if pause:
            print("! Break !")
            while True:
                if autodump:
                    autodump = False
                    dumpstate()
                
                line = input()
                if line == "c":
                    pause = False
                    break
                elif line == "i":
                    import code
                    code.InteractiveConsole(locals=locals()).interact()
                elif line == "q":
                    WINAPI.PostQuitMessage(0)
                    count = 0
                    break
                elif not line:
                    count = 0
                    autodump = True
                    break
                else:
                    dumpstate()
        
        cpu.StepPre()
        
        cpubus.Reset()
        
        DIV_update(cpu.DIV, cpu.DIV_PREV)
        
        try:
            status = cpu.Step()
        except:
            print("! Error at $%04X op $%02X M%u" % (cpu.reg.PC, cpu.IR, cpu.STATE_IDX - 1))
            raise
        
        if status != cpu.STATUS_RUNNING:
            #pause = True
            pass
        
        #buslog("$%04X: %12s " % (cpu.reg.PC, CPU.ToString_Status(status)), end='')
        
        busaccess = cpubus.Access
        if busaccess:
            assert busaccess & (BUS_ACCESS_READ | BUS_ACCESS_WRITE)
            
            address = cpubus.Address
            
            if busaccess & BUS_ACCESS_MEMREQ:
                if busaccess & BUS_ACCESS_READ:
                    if address < 0x8000:
                        cart.OnRead(cpubus)
                    elif address < 0xA000:
                        ppu.TickT(3)
                        ppu.OnRead(cpubus)
                        ppu.TickT(1)
                        ppu_ticked = True
                    elif address < 0xC000:
                        cart.OnRead(cpubus)
                    else:
                        cpubus.SetData(tmpwram[address & 0x1FFF])
                    
                    #buslog(("- Ext access [$%04X] --> $%02X" % (cpubus.Address, cpubus.Data)))
                elif busaccess & BUS_ACCESS_WRITE:
                    #buslog(("- Ext access [$%04X] <-- $%02X" % (cpubus.Address, cpubus.Data)))
                    
                    if address < 0x8000:
                        cart.OnWrite(cpubus)
                    elif address < 0xA000:
                        ppu.TickT(2)
                        ppu.OnWrite(cpubus)
                        ppu.TickT(2)
                        ppu_ticked = True
                    elif address < 0xC000:
                        cart.OnWrite(cpubus)
                    else:
                        tmpwram[address & 0x1FFF] = cpubus.Data
            else:
                if busaccess & BUS_ACCESS_READ:
                    if address >= 0xFF00:
                        if address == 0xFFFF:
                            cpubus.SetData(cpu.REG_IE)
                        elif address == 0xFF0F:
                            cpubus.SetData(cpu.REG_IF | 0xE0)
                            #pause = True
                        elif address == 0xFF04:
                            cpubus.SetData((cpu.DIV >> 6) & 0xFF)
                        elif address == 0xFF01 or address == 0xFF02:
                            pass
                        elif address == 0xFF00:
                            cpubus.SetData(tmpio[0])
                        elif address >= 0xFF40 and address < 0xFF50:
                            ppu.OnRead(cpubus)
                        else:
                            cpubus.SetData(tmpio[address & 0xFF])
                    elif bootmeme:
                        cpubus.SetData(bootmeme[address & 0xFF])
                    
                    #buslog(("- Int access [$%04X] --> $%02X" % (cpubus.Address, cpubus.Data)))
                elif busaccess & BUS_ACCESS_WRITE:
                    #buslog(("- Int access [$%04X] <-- $%02X" % (cpubus.Address, cpubus.Data)))
                    
                    if address >= 0xFF00:
                        if address == 0xFFFF:
                            cpu.REG_IE = cpubus.Data # type: ignore
                        elif address == 0xFF0F:
                            cpu.IRQ_SetM(cpubus.Data & 0x1F)
                            cpu.IRQ_Clear(~cpubus.Data & 0x1F)
                            #pause = True
                        elif address == 0xFF04:
                            DIV_update(0, cpu.DIV)
                            cpu.DIV = 0
                        elif address >= 0xFF40 and address < 0xFF50:
                            ppu.OnWrite(cpubus)
                        elif address == 0xFF00:
                            tmpio[0] = cpubus.Data
                            update_JOYP()
                        else:
                            tmpio[address & 0xFF] = cpubus.Data
                            if address == 0xFF01:
                                sys.stdout.write(chr(cpubus.Data))
                                sys.stdout.flush()
                            elif address == 0xFF50:
                                cpu.ProtectOverlay = False
                                bootmeme = None
                                pass
        elif cpubus.Address != 0xFFFF:
            buslog("- Bus idle %04X" % cpubus.Address)
            pass
        else:
            #buslog()
            pass
        
        if not ppu_ticked:
            ppu.TickT(4)
        else:
            ppu_ticked = False
        
        #TODO: inaccurate
        cpu.IRQ_SetT(ppu.PendingIRQ(), 3)
        

if __name__ == '__main__':
    main()
