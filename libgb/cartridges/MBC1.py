from ..cartridge import Cartridge

class MBC1(Cartridge):
    def OnReadROM0(self, bus, address):
        offset = (self.BANKSEL2 << 19) & ((self.NBANKS << 14) - 1) if self.BANKMODE else 0
        data = self.ROM[offset | address]
        bus.SetData(data)
    
    def OnReadROMN(self, bus, address):
        offset = ((self.BANKSEL2 << 19) | (self.BANKSEL << 14)) & ((self.NBANKS << 14) - 1)
        data = self.ROM[offset | address]
        bus.SetData(data)
    
    def OnReadRAM(self, bus, address):
        if not self.RAMENA:
            return
        
        if not self.RAM:
            return
        
        offset = ((self.BANKSEL2 & (self.NRAM - 1)) << 13)
        data = self.RAM[offset | address]
        bus.SetData(data)
    
    def OnWriteROM(self, address, data):
        case = (address >> 13) & 3
        
        if case == 0:   # RAME
            self.RAMENA = (data & 0x0F) == 0x0A
        elif case == 1: # ROMB
            self.BANKSEL = (data & 0x1F)
            if not self.BANKSEL:
                self.BANKSEL = 1
        elif case == 2: # SEL2
            self.BANKSEL2 = data & 3
        elif case == 3: # MODE
            self.BANKMODE = not not (data & 1)
            
    
    def OnWriteRAM(self, address, data):
        if not self.RAMENA:
            return
        
        if not self.RAM:
            return
            
        offset = ((self.BANKSEL2 & (self.NRAM - 1)) << 13)
        self.RAM[offset | address] = data
        
