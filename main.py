import sys
from glob import glob

from libgb.cpu import CPU
from libgb.cartridge import Cartridge

def buslog(*args, **kwargs): pass
#def buslog(*args, **kwargs): print(*args, **kwargs)

def main():
    romdata = None
    
    # 07- is problem
    #with open(glob('C:/Downloads/07-*.gb')[0], 'rb') as fi:
    with open('C:/Downloads/cpu_instrs.gb', 'rb') as fi:
        romdata = fi.read()
    
    mappertype = Cartridge.ClassFromHeuristics(romdata)
    if not mappertype:
        print("Mapper not supported")
        sys.exit(1)
    
    cart = mappertype(romdata)
    
    cpu = CPU()
    
    cpu.ResetClear()
    cpu.RESET_STABLE = True
    
    cpu.reg.PC = 0x100
    
    tmpwram = [0] * 0x2000
    tmpvram = [0] * 0x2000
    tmpio = [0xFF] * 255
    
    tmpio[0x44] = 0x90
    tmpio[0x41] = 0x81
    tmpio[0x40] = 0x91
    
    pause = False
    
    while True:
        if cpu.reg.PC == 0x101:
            pause = True
        
        if pause:
            print("! Break !")
            while True:
                line = input()
                if line == "q":
                    pause = False
                    break
                elif not line:
                    break
                else:
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
                    if cpu.STATE_CB:
                        print("- $CB $%02X M%u" % (cpu.IR, cpu.STATE_IDX - 1))
                    else:
                        print("- $%02X M%u" % (cpu.IR, cpu.STATE_IDX - 1))
        
        if tmpio[0x07] & 4:
            bit = 1 << (7, 1, 3, 5)[tmpio[0x07]&3]
            if not (cpu.DIV & bit) and not not (cpu.DIV_PREV & bit):
                val = tmpio[0x05]
                if val == 0xFF:
                    val = tmpio[0x06]
                    cpu.IRQ_SetM(1 << 2)
                else:
                    val += 1
                tmpio[0x05] = val
        
        cpu.StepPre()
        
        cpu.bus.Reset()
        
        try:
            status = cpu.Step()
        except:
            print("! Error at $%04X op $%02X M%u" % (cpu.reg.PC, cpu.IR, cpu.STATE_IDX - 1))
            raise
        
        if status != cpu.STATUS_RUNNING:
            #pause = True
            pass
        
        buslog("$%04X: %12s " % (cpu.reg.PC, CPU.ToString_Status(status)), end='')
        
        if cpu.bus.MemReq:
            assert cpu.bus.RD or cpu.bus.WR
            
            address = cpu.bus.Address
            
            if cpu.bus.RD:
                if address < 0x8000:
                    cart.OnRead(cpu.bus)
                elif address < 0xA000:
                    cpu.bus.SetData(tmpvram[address & 0x1FFF])
                elif address < 0xC000:
                    cart.OnRead(cpu.bus)
                else:
                    cpu.bus.SetData(tmpwram[address & 0x1FFF])
                
                buslog(("- Ext access [$%04X] --> $%02X" % (cpu.bus.Address, cpu.bus.Data)))
            elif cpu.bus.WR:
                buslog(("- Ext access [$%04X] <-- $%02X" % (cpu.bus.Address, cpu.bus.Data)))
                
                if address < 0x8000:
                    cart.OnWrite(cpu.bus)
                elif address < 0xA000:
                    tmpvram[address & 0x1FFF] = cpu.bus.Data
                elif address < 0xC000:
                    cart.OnWrite(cpu.bus)
                else:
                    tmpwram[address & 0x1FFF] = cpu.bus.Data
                
        elif cpu.bus.RD or cpu.bus.WR:
            address = cpu.bus.Address
            
            if cpu.bus.RD:
                if address >= 0xFF00:
                    if address == 0xFFFF:
                        cpu.bus.SetData(cpu.REG_IE)
                    elif address == 0xFF0F:
                        cpu.bus.SetData(cpu.REG_IF | 0xE0)
                        #pause = True
                    elif address == 0xFF04:
                        cpu.bus.SetData((cpu.DIV >> 6) & 0xFF)
                    else:
                        cpu.bus.SetData(tmpio[address & 0xFF])
                
                buslog(("- Int access [$%04X] --> $%02X" % (cpu.bus.Address, cpu.bus.Data)))
            elif cpu.bus.WR:
                buslog(("- Int access [$%04X] <-- $%02X" % (cpu.bus.Address, cpu.bus.Data)))
                
                if address >= 0xFF00:
                    if address == 0xFFFF:
                        cpu.REG_IE = cpu.bus.Data
                    elif address == 0xFF0F:
                        cpu.IRQ_SetM(cpu.bus.Data & 0x1F)
                        cpu.IRQ_Clear(~cpu.bus.Data & 0x1F)
                        #pause = True
                    elif address == 0xFF04:
                        cpu.DIV = 0
                    else:
                        tmpio[address & 0xFF] = cpu.bus.Data
                        if address == 0xFF01:
                            sys.stdout.write(chr(cpu.bus.Data))
                            sys.stdout.flush()
                
        elif cpu.bus.Address != 0xFFFF:
            #buslog("- Bus idle %04X" % cpu.bus.Address)
            pass
        else:
            buslog()
            pass

if __name__ == '__main__':
    main()