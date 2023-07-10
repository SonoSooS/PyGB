
BUS_ACCESS_READ = 1
BUS_ACCESS_WRITE = 2
BUS_ACCESS_MEMREQ = 4

class Bus:
    __slots__ = ('Address', 'Data', 'Access')
    
    @property
    def RD(self):
        return not not (self.Access & BUS_ACCESS_READ)
    @property
    def WR(self):
        return not not (self.Access & BUS_ACCESS_WRITE)
    @property
    def MemReq(self):
        return not not (self.Access & BUS_ACCESS_MEMREQ)
    
    def __init__(self):
        self.Reset()
    
    def Reset(self):
        self.Address = 0xFFFF
        self.Data = 0xFF
        self.Access = 0
    
    def SetAddress(self, address):
        self.Address &= address
    
    def SetData(self, data):
        self.Data &= data
    
    def PerformRead(self, address):
        self.SetAddress(address)
        self.Access = BUS_ACCESS_READ
    
    def PerformReadExt(self, address):
        self.PerformRead(address)
        self.Access |= BUS_ACCESS_MEMREQ
    
    def PerformWrite(self, address, data):
        self.SetAddress(address)
        self.SetData(data)
        self.Access = BUS_ACCESS_WRITE
    
    def PerformWriteExt(self, address, data):
        self.PerformWrite(address, data)
        self.Access |= BUS_ACCESS_MEMREQ
    
    def AccessFrom(self, bus, force=False):
        if (not force and (self.Access & BUS_ACCESS_MEMREQ)) or not (bus.Access & BUS_ACCESS_MEMREQ):
            return
        
        self.Access = bus.Access | BUS_ACCESS_MEMREQ
        
        self.SetAddress(bus.Address)
        self.SetData(bus.Data)
    
