
class Bus:
    __slots__ = ('Address', 'Data', 'RD', 'WR', 'MemReq')
    
    def __init__(self):
        self.Reset()
    
    def Reset(self):
        self.Address = 0xFFFF
        self.Data = 0xFF
        self.RD = False
        self.WR = False
        self.MemReq = False
    
    def SetAddress(self, address):
        self.Address &= address
    
    def SetData(self, data):
        self.Data &= data
    
    def PerformRead(self, address):
        self.SetAddress(address)
        self.RD = True
    
    def PerformReadExt(self, address):
        self.PerformRead(address)
        self.MemReq = True
    
    def PerformWrite(self, address, data):
        self.SetAddress(address)
        self.SetData(data)
        self.WR = True
    
    def PerformWriteExt(self, address, data):
        self.PerformWrite(address, data)
        self.MemReq = True
    
    def AccessFrom(self, bus, force=False):
        if not force and self.MemReq:
            return
        
        self.MemReq = True
        self.RD = bus.RD
        self.WR = bus.WR
        
        self.SetAddress(bus.Address)
        self.SetData(bus.Data)
    
