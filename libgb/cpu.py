from libgb.cpu_constant import FLAG_CY, FLAG_ZERO, UOP_CC_CHECK, UOP_GENERIC_FETCH
from .cpu_instruction_set import OPCODES, OPCODES_CB, ISR
from .bus import Bus

class Regbank:
    __slots__ = ('B', 'C', 'D', 'E', 'H', 'L', 'F', 'A', 'PC', 'SP', 'ImmL', 'ImmH')
    
    def __init__(self):
        self.B = 0
        self.C = 0
        self.D = 0
        self.E = 0
        self.H = 0
        self.L = 0
        self.A = 0
        self.F = 0
        self.PC = 0
        self.SP = 0
        self.ImmL = 0
        self.ImmH = 0
    
    @property
    def BC(self):
        return (self.B << 8) | self.C
    @BC.setter
    def BC(self, value):
        self.B = (value >> 8) & 0xFF
        self.C = (value     ) & 0xFF
    
    @property
    def DE(self):
        return (self.D << 8) | self.E
    @DE.setter
    def DE(self, value):
        self.D = (value >> 8) & 0xFF
        self.E = (value     ) & 0xFF
    
    @property
    def HL(self):
        return (self.H << 8) | self.L
    @HL.setter
    def HL(self, value):
        self.H = (value >> 8) & 0xFF
        self.L = (value     ) & 0xFF
    
    @property
    def AF(self):
        return (self.A << 8) | self.F
    @AF.setter
    def AF(self, value):
        self.A = (value >> 8) & 0xFF
        self.F = (value     ) & 0xF0
    
    @property
    def Imm(self):
        return (self.ImmH << 8) | self.ImmL
    @Imm.setter
    def Imm(self, value):
        self.ImmH = (value >> 8) & 0xFF
        self.ImmL = (value     ) & 0xFF
    
    @property
    def PCL(self):
        return self.PC & 0xFF
    @PCL.setter
    def PCL(self, data):
        self.PC = (self.PC & 0xFF00) | (data)
    @property
    def PCH(self):
        return (self.PC >> 8) & 0xFF
    @PCH.setter
    def PCH(self, data):
        self.PC = (self.PC & 0x00FF) | (data << 8)
    
    @property
    def SPL(self):
        return self.SP & 0xFF
    @SPL.setter
    def SPL(self, data):
        self.SP = (self.SP & 0xFF00) | (data)
    @property
    def SPH(self):
        return (self.SP >> 8) & 0xFF
    @SPH.setter
    def SPH(self, data):
        self.SP = (self.SP & 0x00FF) | (data << 8)
    
    @property
    def PCi(self):
        retval = self.PC
        self.PC = (retval + 1) & 0xFFFF
        return retval
    
    @property
    def PCd(self):
        retval = self.PC
        self.PC = (retval - 1) & 0xFFFF
        return retval
    
    @property
    def SPi(self):
        retval = self.SP
        self.SP = (retval + 1) & 0xFFFF
        return retval
    
    @property
    def SPd(self):
        retval = self.SP
        self.SP = (retval - 1) & 0xFFFF
        return retval
    
    @property
    def HLi(self):
        retval = self.HL
        self.HL = (retval + 1) & 0xFFFF
        return retval
    
    @property
    def HLd(self):
        retval = self.HL
        self.HL = (retval - 1) & 0xFFFF
        return retval

class CPU:
    __slots__ = \
    (
        'reg', 'bus', 'DV', 'IR',
        'STATE_CB', 'STATE_IDX',
        'IME', 'IME_ASK', 'IRQ', 'ISR',
        'REG_IE', 'REG_IF', 'REG_IF_DELAY1', 'REG_IF_DELAY2', 'REG_IF_CLR',
        'ProtectOverlay',
        'DIV', 'DIV_PREV',
        '__dict__'
    )
    
    STATUS_WAKE_EARLY = -3
    STATUS_RESET = -2
    STATUS_WEDGED = -1
    STATUS_RUNNING = 0
    STATUS_HALTED = 1
    STATUS_STOPPED = 2
    STATUS_STOP_GLITCH = 3
    STATUS_ISR = 4
    STATUS_WAKE = 5
    STATUS_UNHALT = 6
    STATUS_NOSLEEP = 7
    
    def __init__(self):
        self.reg = Regbank()
        
        self.bus = Bus()
        
        self.ProtectOverlay = False
        self.ProtectList = ( (0x00, 0xFF) )
        
        self.ResetSet()
    
    def ResetSet(self):
        self.bus.Reset()
        self.DV = 0
        
        self.REQ_HALT = False
        self.REQ_STOP = False
        self.REQ_NMI = False
        self.IS_HALT = True
        self.IS_STOP = True
        self.IS_NMI = False
        self.IS_RESET = True
        self.RESET_STABLE = False
        self.RESET_DELAY = 1
        self.WAKE = False
        
        self.IR = 0
        self.STATE_CB = False
        self.STATE_IDX = 7
        
        self.IME = False
        self.IME_ASK = False
        self.IRQ = 0
        self.ISR = False
        
        self.REG_IE = 0
        self.REG_IF = 0
        self.REG_IF_DELAY1 = 0
        self.REG_IF_DELAY2 = 0
        self.REG_IF_CLR = 0
        
        self.DIV = 0
        self.DIV_PREV = 0
        
        self.UpdateResetGating()
    
    @staticmethod
    def ToString_Status(status):
        list = \
        (
            "WAKE_EARLY",
            "RESET",
            "WEDGED",
            "RUNNING",
            "HALTED",
            "STOPPED",
            "STOP_GLITCH",
            "ISR",
            "WAKE",
            "UNHALT",
            "NOSLEEP"
        )
        
        status -= -3
        if status < 0 or status >= len(list):
            return "Invalid status %i" % (status + -3)
        
        return list[status]
    
    def ResetClear(self):
        self.IS_RESET = False
    
    def UpdateResetGating(self):
        if self.IS_RESET or not self.RESET_STABLE or self.IS_STOP or self.IS_HALT or self.REQ_HALT or self.REQ_STOP or self.REQ_NMI or self.RESET_DELAY or self.WAKE:
            self.RESET_GATE = True
        else:
            self.RESET_GATE = False
    
    def IsProtected(self, address):
        if address >= 0xFE00:
            return True
        
        if not self.ProtectOverlay:
            return False
        
        for range in self.ProtectList:
            if range[0] <= address and range[1] >= address:
                return True
        
        return False
    
    def DoRead(self, address):
        if not self.IsProtected(address):
            self.bus.PerformReadExt(address)
        else:
            self.bus.PerformRead(address)
    
    def DoWrite(self, address, data):
        if not self.IsProtected(address):
            self.bus.PerformWriteExt(address, data)
        else:
            self.bus.PerformWrite(address, data)
    
    def DoPassive(self, address):
        self.bus.SetAddress(address)
    
    def LatchBus(self):
        self.DV = self.bus.Data
    
    def IRQ_SetT(self, bits, tcycle):
        '''Fire an interrupt with T-cycle accuracy'''
        
        # Note: in HALT mode IRQ latching is constantly happening
        #  until the next M-cycle
        # Note: IE & IF calculation is done from T0 to T2,
        #  so any interrupt happening from T2 to T0
        #  will not be seen until 2 M-cycles in, as
        #  the IRQ signal is calculated at T30,
        #  which is only effective the next M-cycle
        
        if self.IS_HALT or tcycle < 2:
            self.REG_IF_DELAY1 |= bits
        else:
            self.REG_IF_DELAY2 |= bits
    
    def IRQ_SetM(self, bits):
        '''Fire an interrupt at the start of the current M-cycle'''
        
        # Note: IRQ sheduling detection happens in T3,
        #  effectively delaying detection by 1 M-cycle
        self.REG_IF_DELAY1 |= bits
    
    def IRQ_Clear(self, bits):
        '''Schedule an interrupt for clear'''
        
        # Note: In real hardware /RESET is held for the entire M-cycle,
        #  so this behavior should be as accurate as possible
        self.REG_IF_CLR |= bits
    
    def IRQ_Address(self):
        if self.IS_NMI:
            self.REQ_NMI = False
            return 0x80
        
        if self.IRQ:
            nbit = 0
            while not (self.IRQ & (1 << nbit)):
                nbit += 1
            
            self.IRQ_Clear(1 << nbit) #TODO: is timing correct?
            return 0x40 | (nbit << 3)
        
        return 0x00 # bugged IRQ
    
    def Clock_STOP(self):
        self.IS_STOP = True
        self.RESET_STABLE = False
        self.RESET_DELAY = 1
        self.DIV = 0
        self.UpdateResetGating()
    
    def Clock_HALT(self):
        self.IS_HALT = True
        self.STATE_IDX = 7
        self.UpdateResetGating()
    
    def StepPre(self):
        '''Call this at the end of the previous M-cycle before beginning the next'''
        
        self.REG_IF = (self.REG_IF | self.REG_IF_DELAY1) & ~self.REG_IF_CLR
        self.REG_IF_DELAY1 = self.REG_IF_DELAY2 & ~self.REG_IF_CLR
        self.REG_IF_DELAY2 = 0
        self.REG_IF_CLR = 0
        
        self.IRQ = self.REG_IE & self.REG_IF
        
        if self.IME_ASK:
            self.IME = True
            self.IME_ASK = False
        
        self.DIV_PREV = self.DIV
        if not self.IS_STOP:
            self.DIV = (self.DIV + 1) & ((1 << 20) - 1)
        
        if self.bus.RD:
            self.LatchBus()
    
    def Step(self):
        status = self.STATUS_RUNNING
        
        if self.RESET_GATE:
            if self.IS_RESET:
                return self.STATUS_RESET
            
            if self.IS_STOP:
                if not self.WAKE and not self.RESET_STABLE:
                    return self.STATUS_STOPPED
                
                self.IS_STOP = False
                status = self.STATUS_WAKE
            
            if not self.RESET_STABLE:
                if not self.IRQ:
                    return self.STATUS_WAKE
                
                status = self.STATUS_WAKE_EARLY
                self.RESET_STABLE = True
                self.RESET_DELAY = 0
                self.STATE_IDX = 7
                self.IS_HALT = False
            
            if self.RESET_DELAY:
                self.RESET_DELAY -= 1
                if not self.RESET_DELAY:
                    self.IS_HALT = False
                return self.STATUS_WAKE
            
            if self.IS_HALT:
                if not self.IRQ:
                    return self.STATUS_HALTED
                
                self.IS_HALT = False
                status = self.STATUS_UNHALT
            
            if self.REQ_HALT or self.REQ_STOP:
                if self.REQ_HALT:
                    self.REQ_HALT = False
                    if not self.IRQ:
                        self.Clock_HALT()
                if self.REQ_STOP:
                    self.REQ_STOP = False
                    if not self.WAKE:
                        self.Clock_STOP()
                
                if self.IS_HALT:
                    if self.IS_STOP:
                        return self.STATUS_STOPPED
                    else:
                        return self.STATUS_HALTED
                elif self.IS_STOP:
                    return self.STATUS_STOP_GLITCH
                else:
                    status = self.STATUS_NOSLEEP
                    
            self.UpdateResetGating()
        
        if self.STATE_IDX < 0:
            self.STATE_IDX = 0
            self.IR = self.DV
            
            if ((self.IME and self.IRQ) or self.REQ_NMI) and not self.STATE_CB and not self.IS_NMI:
                self.ISR = True
        
        result = UOP_GENERIC_FETCH
        op = 0
        
        idx = self.STATE_IDX
        if idx < 7:
            self.STATE_IDX = idx + 1
            
            op = self.IR
            
            if self.ISR:
                result = ISR[idx](self, 0)
                status = self.STATUS_ISR
                if result == UOP_GENERIC_FETCH:
                    self.ISR = False
            elif not self.STATE_CB:
                result = OPCODES[op][idx](self, op)
            else:
                #print("? op $%02X M%u" % (op, idx))
                result = OPCODES_CB[op][idx](self, op)
            
            if result == UOP_CC_CHECK:
                cc_idx = (op >> 3) & 3
                if cc_idx == 0:
                    if self.reg.F & FLAG_ZERO:
                        self.STATE_IDX = 7
                elif cc_idx == 1:
                    if not self.reg.F & FLAG_ZERO:
                        self.STATE_IDX = 7
                elif cc_idx == 2:
                    if self.reg.F & FLAG_CY:
                        self.STATE_IDX = 7
                elif cc_idx == 3:
                    if not self.reg.F & FLAG_CY:
                        self.STATE_IDX = 7
                
        
        if result == UOP_GENERIC_FETCH:
            if op != 0x76:
                self.DoRead(self.reg.PCi)
            else:
                self.DoRead(self.reg.PC)
            self.STATE_IDX = -1
            self.STATE_CB = False
        
        return status
