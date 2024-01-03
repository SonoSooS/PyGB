from ..cartridge import Cartridge

class MBC5(Cartridge):
    def OnWriteROM(self, address, data):
        case = (address >> 12) & 7
        
        if case == 0 or case == 1:   # RAME
            self.RAMENA = (data & 0x0F) == 0x0A
        elif case == 2: # ROMB
            self.BANKSEL = data
        elif case == 3: # SEL2
            self.BANKSEL2 = data & 1
        elif case == 4 or case == 5: # RAMB
            self.RAMSEL = data & 0x0F
        
        self.UpdateCache()
    