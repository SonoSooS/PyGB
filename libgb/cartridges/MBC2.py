from ..cartridge import Cartridge

class MBC2(Cartridge):
    def OnWriteROM(self, address, data):
        if address >= 0x4000:
            return
        
        if address & (1 << 8): # ROMB
            self.BANKSEL = (data & 0x0F)
            if not self.BANKSEL:
                self.BANKSEL = 1
        else: # RAME
            self.RAMENA = ((data & 0x0F) == 0x0A)
        
        self.UpdateCache()
    
    def OnReadRAM(self, bus, address):
        if not self.RAMENA:
            return
        
        if not self.RAM:
            return
        
        data = self.RAM[address & 511]
        bus.SetData(data | 0xF0) #NOTE: wtf open bus value should I use here
    
    def OnWriteRAM(self, address, data):
        if not self.RAMENA:
            return
        
        if not self.RAM:
            return
        
        self.RAM[address & 511] = data
    