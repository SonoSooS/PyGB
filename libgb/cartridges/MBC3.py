from ..cartridge import Cartridge

class MBC3(Cartridge):
    def OnWriteROM(self, address, data):
        case = (address >> 13) & 3
        
        if case == 0:   # RAME
            self.RAMENA = (data & 0x0F) == 0x0A
        elif case == 1: # ROMB
            self.BANKSEL = data & 0x7F
            if not self.BANKSEL:
                self.BANKSEL = 1
        elif case == 2: # RAMB
            self.RAMSEL = data & 0x0F
        elif case == 3: # LATCH
            pass #TODO: yeah, RTC stuff
        
        self.UpdateCache()
    
    #TODO: RTC stuff
    