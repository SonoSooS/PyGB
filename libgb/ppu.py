from array import array

class PixelFIFO:
    __slots__ = ('FIFO', 'Output')
    
    TYPE_NONE = 0
    TYPE_BG = 1
    TYPE_OBJ0 = 2
    TYPE_OBJ1 = 3
    TYPE_WIN1 = 5
    TYPE_WIN2 = 7
    
    def __init__(self):
        self.FIFO = array('H', (0,) * 8)
        
        self.Reset()
    
    def Reset(self):
        for i in range(len(self.FIFO)):
            self.FIFO[i] = 0
        
        self.Output = 0
    
    def PutRaw(self, raw):
        self.FIFO[7] = raw
    
    def Shift(self):
        fifo = self.FIFO
        self.Output = fifo[0]
        for i in range(7):
            fifo[i] = fifo[i + 1]
        fifo[7] = 0
    
    def ShiftOut(self):
        self.Shift()
        return self.Output
    
    def ShiftInto(self, other):
        self.Shift()
        other.PutRaw(self.Output)
    
    def Refill(self, type, bit0, bit1, palette=0, prio=False, idx=0):
        common = (prio << 15) | (type << 12) | (palette << 2) | (idx << 5)
        
        bit1 <<= 1
        for i in range(8):
            data = ((bit0 >> 7) & 1) | ((bit1 >> 7) & 2) | common
            
            self.FIFO[i] = data
            
            bit0 <<= 1
            bit1 <<= 1
    
    @staticmethod
    def DecodePx(px):
        return px & 3
    
    @staticmethod
    def DecodePaletteIndex(px):
        return (px >> 2) & 7
    
    @staticmethod
    def DecodeSpriteIndex(px):
        return (px >> 5) & 127 # ???
    
    @staticmethod
    def DecodePixelType(px):
        return (px >> 12) & 7
    
    @staticmethod
    def DecodePrio(px):
        return not not ((px >> 15) & 1)
    
    def __bool__(self):
        return not not sum(self.FIFO) # cheap hack for testing empty FIFO

class PPU:
    TICKS_PER_SCANLINE = 456
    NUM_SCANLINES = 154
    VISIBLE_WIDTH = 160
    VISIBLE_HEIGHT = 144
    
    FRAMEBUF_STRIDE = TICKS_PER_SCANLINE
    FRAMEBUF_HEIGHT = NUM_SCANLINES
    
    @property
    def IsEnabled(self):
        return not not (self.LCDC & 0x80)
    
    def PendingIRQ(self):
        result = self.PendingIRQ_
        if result:
            self.PendingIRQ_ = 0
        
        return result
    
    def __init__(self):
        self.VRAM = array('B', (0,) * 0x4000)
        self.OAM = array('B', (0,) * 0xA0) # interleaved banks of OAM_A and OAM_B
        
        self.BGFIFO = PixelFIFO()
        self.OBJFIFO = PixelFIFO()
        self.OUTFIFO = PixelFIFO()
        
        self.Framebuf = array('H', [0] * (self.FRAMEBUF_STRIDE * self.NUM_SCANLINES))
        
        self.LCDC = 0
        self.STAT = 0
        self.SCX = 0
        self.SCY = 0
        self.LYC = 0
        self.BGP = 0
        self.OBP0 = 0
        self.OBP1 = 0
        self.WX = 0
        self.WY = 0
        
        self.PendingIRQ_ = 0
        
        self.Palette = (0x5FB0, 0x3EB3, 0x21AA, 0x1084)
        
        self.Reset()
    
    def OnRead(self, bus):
        address = bus.Address
        
        if address < 0xFE00:
            if not self.InaccessibleVRAM:
                bus.SetData(self.VRAM[address & 0x1FFF])
        elif address < 0xFF00:
            address &= 0xFF
            if address < 0xA0:
                if not self.InaccessibleOAM:
                    bus.SetData(self.OAM[address])
        else:
            address &= 0xF
            if address == 0:
                bus.SetData(self.LCDC)
            elif address == 1:
                bus.SetData(self.STAT)
            elif address == 4:
                bus.SetData(self.PixelY)
                #bus.SetData(0x90)
            elif address == 2:
                bus.SetData(self.SCY)
            elif address == 3:
                bus.SetData(self.SCX)
            elif address == 5:
                bus.SetData(self.LYC)
            elif address == 7:
                bus.SetData(self.BGP)
            elif address == 8:
                bus.SetData(self.OBP0)
            elif address == 9:
                bus.SetData(self.OBP1)
            elif address == 10:
                bus.SetData(self.WY)
            elif address == 11:
                bus.SetData(self.WX)
            
    
    def OnWrite(self, bus):
        address = bus.Address
        
        if address < 0xFF00:
            if address < 0xFE00:
                if not self.InaccessibleVRAM:
                    self.VRAM[address & 0x1FFF] = bus.Data
            else:
                if not self.InaccessibleOAM:
                    self.OAM[address & 0xFF] = bus.Data
        else:
            address &= 0xF
            
            #print("PPU reg $4%X = %02X" % (address, bus.Data))
            
            if address == 0:
                self.LCDC = bus.Data
            elif address == 1:
                self.STAT = bus.Data
            elif address == 2:
                self.SCY = bus.Data
            elif address == 3:
                self.SCX = bus.Data
            elif address == 5:
                self.LYC = bus.Data
            elif address == 7:
                self.BGP = bus.Data
            elif address == 8:
                self.OBP0 = bus.Data
            elif address == 9:
                self.OBP1 = bus.Data
            elif address == 10:
                self.WY = bus.Data
            elif address == 11:
                self.WX = bus.Data
    
    def Reset(self):
        self.BGFIFO.Reset()
        self.OBJFIFO.Reset()
        self.OUTFIFO.Reset()
        
        self.OAMREAD0 = 0
        self.OAMREAD1 = 0
        self.OAMREAD2 = 0
        
        self.InaccessibleVRAM = False
        self.InaccessibleOAM = False
        
        self.CycleInScanline = 0
        self.PixelX = 0
        self.PixelY = 0
        self.LY = 0
        self.Mode = 0
        self.OAMScanCycle = 0
        self.TileFetchCycle = 0
        self.ShiftOff = 0
        self.SCXCC = 0
        
        self.FetchTile = 0
        self.FetchAttr = 0
        self.FetchData0 = 0
        self.FetchData1 = 0
        self.LatchedSCX = 0
        self.LatchedSCY = 0
        self.TileOffset = 0
    
    def CalculateTileOffset(self):
        tile_offs = self.TileOffset
        self.TileOffset = (tile_offs + 1) & 31
        srcY = (self.LatchedSCY + self.PixelY) & 255
        return (((srcY >> 3) & 31) << 5) | tile_offs
    
    def CalculateDataOffset(self, linear):
        tile = self.FetchTile
        #attr = self.FetchAttr
        
        line = self.PixelY + self.LatchedSCY
        #if (attr & 64):
        #    line = ~line
        
        base = (line & 7) << 1
        if linear:
            return base | (tile << 4)
        else:
            if tile < 0x80:
                tile += 0x100
            return base | (tile << 4)
    
    def TickT(self, tcycles, toffset=0):
        if not self.IsEnabled:
            return
        
        while tcycles:
            while True: # due to lack of goto
                if self.Mode == 3:
                    if self.PixelX >= (self.VISIBLE_WIDTH + 8):
                        self.Mode = 0
                        self.STAT &= 0xFC
                        self.TileFetchCycle = 0
                        continue
                    
                    if self.SCXCC is not None:
                        if self.SCXCC == (self.SCX & 7):
                            self.SCXCC = None
                        else:
                            self.SCXCC = (self.SCXCC + 1) & 7
                            break
                    
                    if self.BGFIFO:
                        px = self.BGFIFO.ShiftOut()
                        fbpos = (self.PixelY * self.FRAMEBUF_STRIDE) + self.PixelX
                        #fbpos = (self.PixelY * self.FRAMEBUF_STRIDE) + self.CycleInScanline
                        
                        rawpx = self.BGFIFO.DecodePx(px)
                        palpx = (self.BGP >> (rawpx * 2)) & 3
                        
                        self.Framebuf[fbpos] = self.Palette[palpx]
                        
                        self.PixelX += 1
                    
                    if True:
                        bgcycle = self.TileFetchCycle
                        if bgcycle == 0:
                            vram_addr = ((self.LCDC & 8) << 7) | 0x1800 | self.CalculateTileOffset()
                            self.FetchTile = self.VRAM[vram_addr]
                            #self.FetchAttr = self.VRAM[vram_addr | 0x2000]
                            self.TileFetchCycle = 1
                        elif bgcycle == 1:
                            vram_addr = self.CalculateDataOffset(self.LCDC & 16)
                            self.FetchData0 = self.VRAM[vram_addr]
                            self.TileFetchCycle = 2
                        elif bgcycle == 2:
                            vram_addr = self.CalculateDataOffset(self.LCDC & 16)
                            self.FetchData1 = self.VRAM[vram_addr | 1]
                            self.TileFetchCycle = 3
                        elif not self.BGFIFO:
                            self.BGFIFO.Refill(PixelFIFO.TYPE_BG, self.FetchData0, self.FetchData1)
                            self.TileFetchCycle = 0
                        
                    pass
                elif self.Mode == 1:
                    pass
                elif self.Mode == 2:
                    if self.OAMScanCycle >= 80:
                        self.Mode = 3
                        self.STAT |= 3
                        self.OAMScanCycle = 0
                        self.PixelX = 0
                        self.TileOffset = self.SCX >> 3
                        continue
                    else:
                        self.OAMScanCycle += 1
                else:
                    
                    pass
                
                break
            
            scan_cycle = self.CycleInScanline
            scan_cycle += 1
            if scan_cycle >= self.TICKS_PER_SCANLINE:
                scan_cycle = 0
                
                self.PixelX = 0
                
                py = self.PixelY
                py += 1
                
                if py < self.VISIBLE_HEIGHT:
                    self.Mode = 2
                    self.STAT = (self.STAT & 0xFC) | 2
                    self.LatchedSCY = self.SCY
                    self.TileOffset = self.SCX >> 3
                elif py == self.VISIBLE_HEIGHT:
                    self.Mode = 1
                    self.STAT = (self.STAT & 0xFC) | 1
                    self.PendingIRQ_ |= 1
                elif py >= self.NUM_SCANLINES:
                    #self.LatchedSCY = (self.LatchedSCY + 1) & 255
                    py = 0
                    self.STAT = (self.STAT & 0xFC) | 2
                    self.Mode = 2
                
                if py == self.LYC and self.STAT & (1 << 6):
                    self.PendingIRQ_ |= 2
                
                self.PixelY = py
                self.LY = py
            
            self.CycleInScanline = scan_cycle
            
            tcycles -= 1
            toffset += 1
