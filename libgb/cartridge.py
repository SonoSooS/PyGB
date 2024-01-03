from array import array

MAPPERS = \
(
    0,  1,  1,  1, -1,  2,  2, -1,
    0,  0, -1,  4,  4,  4, -1,  3,
    3,  3,  3,  3, -1, -1, -1, -1,
    -1, 5,  5,  5,  5,  5,  5, -1,
)

class Cartridge:
    __slots__ = ('ROM', 'NBANKS', 'RAM', 'NRAM', 'OFF0', 'OFFN', 'BANKSEL', 'BANKSEL2', 'BANKMODE', 'RAMENA', 'RAMSEL', 'OFFR')
    
    def __init__(self, data, ramsize=0):
        romlen = len(data)
        if romlen & (romlen - 1): # check for round size
            print("! Warning ! ROM not round !")
            upround = min(romlen, 0x8000)
            while not upround & (upround + 1): # check if we're 1 off from perfect round size
                upround |= upround >> 1
            upround += 1
            print("! %X --> %X" % (romlen, upround))
            self.ROM = data + (b'\xFF' * (upround - romlen))
            romlen = upround
        else:
            self.ROM = data
        
        self.NBANKS = romlen >> 14
        self.BANKSEL = 1
        self.BANKSEL2 = 0
        self.BANKMODE = False
        self.RAMSEL = 0
        self.RAMENA = False
        self.RAM = array('B', (0,) * ramsize)
        self.NRAM = ramsize >> 13
        
        self.UpdateCache()
            
    
    def OnRead(self, bus):
        address = bus.Address
        
        if not address & 0x8000:
            if not address & 0x4000:
                self.OnReadROM0(bus, address & 0x3FFF)
            else:
                self.OnReadROMN(bus, address & 0x3FFF)
        else:
            self.OnReadRAM(bus, address & 0x1FFF)
    
    def OnWrite(self, bus):
        address = bus.Address
        
        if not address & 0x8000:
            self.OnWriteROM(address & 0x7FFF, bus.Data)
        else:
            self.OnWriteRAM(address & 0x1FFF, bus.Data)
    
    def OnReadROM0(self, bus, address):
        offset = self.OFF0
        data = self.ROM[offset | address]
        bus.SetData(data)
    
    def OnReadROMN(self, bus, address):
        offset = self.OFFN
        data = self.ROM[offset | address]
        bus.SetData(data)
    
    def OnReadRAM(self, bus, address):
        if not self.RAMENA:
            return
        
        if not self.RAM:
            return
        
        data = self.RAM[self.OFFR | address]
        bus.SetData(data)
    
    def OnWriteROM(self, address, data):
        pass
    
    def OnWriteRAM(self, address, data):
        if not self.RAMENA:
            return
        
        if not self.RAM:
            return
        
        self.RAM[self.OFFR | address] = data
    
    def UpdateCache(self):
        self.OFF0 = 0
        self.OFFN = ((self.BANKSEL2 << 22) | (self.BANKSEL << 14)) & ((self.NBANKS << 14) - 1)
        self.OFFR = ((self.RAMSEL & (self.NRAM - 1)) << 13)
    
    @staticmethod
    def ClassFromHeuristics(hdr):
        mapper = hdr[0x147]
        if mapper < 0x20:
            from .cartridges.MBC1 import MBC1
            from .cartridges.MBC5 import MBC5
            
            mapper = MAPPERS[mapper]
            if mapper < 0:
                return None
            
            return (Cartridge, MBC1, None, None, None, MBC5)[mapper]
        
        return None
        
        