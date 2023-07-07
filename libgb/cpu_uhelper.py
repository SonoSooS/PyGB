from .cpu_constant import *

#region Helpers

def reg_read_by_id_8(cpu, regid):
    if regid == 0:
        return cpu.reg.B
    elif regid == 1:
        return cpu.reg.C
    elif regid == 2:
        return cpu.reg.D
    elif regid == 3:
        return cpu.reg.E
    elif regid == 4:
        return cpu.reg.H
    elif regid == 5:
        return cpu.reg.L
    elif regid == 7:
        return cpu.reg.A
    else:
        assert False, "Wrong RegID %u" % regid

def reg_write_by_id_8(cpu, regid, value):
    if regid == 0:
        cpu.reg.B = value
    elif regid == 1:
        cpu.reg.C = value
    elif regid == 2:
        cpu.reg.D = value
    elif regid == 3:
        cpu.reg.E = value
    elif regid == 4:
        cpu.reg.H = value
    elif regid == 5:
        cpu.reg.L = value
    elif regid == 7:
        cpu.reg.A = value
    else:
        assert False, "Wrong RegID %u" % regid

def reg_read_by_id_16(cpu, regid):
    if regid == 0:
        return cpu.reg.BC
    elif regid == 1:
        return cpu.reg.DE
    elif regid == 2:
        return cpu.reg.HL
    elif regid == 3:
        return cpu.reg.SP
    else:
        assert False

def reg_write_by_id_16(cpu, regid, value):
    if regid == 0:
        cpu.reg.BC = value
    elif regid == 1:
        cpu.reg.DE = value
    elif regid == 2:
        cpu.reg.HL = value
    elif regid == 3:
        cpu.reg.SP = value
    else:
        assert False

#endregion

#region ALU

def alu_ADD(cpu, value):
    res = cpu.reg.A
    flag = 0
    
    hc =  ((res & 15) + (value & 15)) > 15
    cy = ((res & 255) + (value & 255)) > 255
    
    res = (res + value) & 255
    
    if hc:
        flag |= FLAG_HC
    if cy:
        flag |= FLAG_CY
    if not res:
        flag |= FLAG_ZERO
    
    cpu.reg.F = flag
    cpu.reg.A = res

def alu_ADC(cpu, value):
    res = cpu.reg.A
    flag = 0
    
    cyval = 1 if cpu.reg.F & FLAG_CY else 0
    
    hc =  ((res & 15) + (value & 15) + cyval) > 15
    cy = ((res & 255) + (value & 255) + cyval) > 255
    
    res = (res + value + cyval) & 255
    
    if hc:
        flag |= FLAG_HC
    if cy:
        flag |= FLAG_CY
    if not res:
        flag |= FLAG_ZERO
    
    cpu.reg.F = flag
    cpu.reg.A = res

def alu_SUB(cpu, value, writeback=True):
    res = cpu.reg.A
    flag = FLAG_SUB
    
    hc =  (res & 15) < (value & 15)
    cy = (res & 255) < (value & 255)
    
    res = (res - value) & 255
    
    if hc:
        flag |= FLAG_HC
    if cy:
        flag |= FLAG_CY
    if not res:
        flag |= FLAG_ZERO
    
    cpu.reg.F = flag
    if writeback:
        cpu.reg.A = res

def alu_SBC(cpu, value):
    res = cpu.reg.A
    flag = FLAG_SUB
    
    cyval = 1 if cpu.reg.F & FLAG_CY else 0
    
    hc =  (res & 15) < ((value & 15) + cyval)
    cy = (res & 255) < ((value & 255) + cyval)
    
    res = (res - value - cyval) & 255
    
    if hc:
        flag |= FLAG_HC
    if cy:
        flag |= FLAG_CY
    if not res:
        flag |= FLAG_ZERO
    
    cpu.reg.F = flag
    cpu.reg.A = res

def alu_AND(cpu, value):
    res = cpu.reg.A
    flag = FLAG_HC
    
    res = (res & value) & 255
    
    if not res:
        flag |= FLAG_ZERO
    
    cpu.reg.F = flag
    cpu.reg.A = res

def alu_XOR(cpu, value):
    res = cpu.reg.A
    flag = 0
    
    res = (res ^ value) & 255
    
    if not res:
        flag |= FLAG_ZERO
    
    cpu.reg.F = flag
    cpu.reg.A = res

def alu_OR(cpu, value):
    res = cpu.reg.A
    flag = 0
    
    res = (res | value) & 255
    
    if not res:
        flag |= FLAG_ZERO
    
    cpu.reg.F = flag
    cpu.reg.A = res

#endregion

#region CB

def CB0(cpu, op, value):
    cy = not not (cpu.reg.F & FLAG_CY)
    flags = 0
    
    op = (op >> 3) & 7
    
    res = value
    
    if op == 0:   # RLC
        res = (value << 1) | (value >> 7)
        flags = (res >> 4) & 0x10
    elif op == 1: # RRC
        res = (value << 7) | (value >> 1)
        flags = (res >> 3) & 0x10
    elif op == 2: # RL
        res = (value << 1) | cy
        flags = (res >> 4) & 0x10
    elif op == 3: # RR
        res = (value << 8) | (value >> 1) | (cy << 7)
        flags = (res >> 4) & 0x10
    elif op == 4: # SLA
        res = (value << 1)
        flags = (res >> 4) & 0x10
    elif op == 5: # SRA
        flags = (value & 1) << 4
        res = (value >> 1) | (value & 0x80)
    elif op == 6: # SWAP
        res = ((value >> 4) | (value << 4))
    elif op == 7: # SRL
        flags = (value & 1) << 4
        res = (value >> 1)
    
    res &= 0xFF
    
    if not res:
        flags |= FLAG_ZERO
    
    cpu.reg.F = flags
    
    return res

def CB1(cpu, op, value):
    bit = (op >> 3) & 7
    flags = FLAG_HC | (cpu.reg.F & FLAG_CY)
    
    if not (value & (1 << bit)):
        flags |= FLAG_ZERO
    
    cpu.reg.F = flags

def CB2(cpu, op, value):
    bit = (op >> 3) & 7
    
    return value & ~(1 << bit)

def CB3(cpu, op, value):
    bit = (op >> 3) & 7
    
    return value | (1 << bit)

#endregion
