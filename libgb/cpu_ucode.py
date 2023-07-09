
from sys import flags
from . import cpu_uhelper as h
from .cpu_constant import *


#region Generic helpers

def generic_fetch(cpu, op):
    '''Fetch next opcode unconditionally (basically NOP)'''
    # (void)op
    
    return UOP_GENERIC_FETCH

def generic_fetch_op1(cpu, op):
    '''Fetch first operand byte from [PC+] into DV'''
    # (void)op
    
    cpu.DoRead(cpu.reg.PCi)
    
    return UOP_CONTINUE

def generic_fetch_op2(cpu, op):
    '''Fetch second operand byte from [PC+] into DV'''
    # (void)op
    
    cpu.reg.ImmL = cpu.DV
    cpu.DoRead(cpu.reg.PCi)
    
    return UOP_CONTINUE

def generic_fetch_uHL(cpu, op):
    '''Fetch from [HL] into DV'''
    # (void)op
    
    cpu.DoRead(cpu.reg.HL)
    
    return UOP_CONTINUE

def generic_continue(cpu, op):
    # (void)op
    
    return UOP_CONTINUE

def generic_cc_check(cpu, op):
    # (void)op
    
    return UOP_CC_CHECK

def generic_cc_check_op1(cpu, op):
    
    generic_fetch_op1(cpu, op)
    
    return UOP_CC_CHECK

def generic_cc_check_op2(cpu, op):
    
    generic_fetch_op2(cpu, op)
    
    return UOP_CC_CHECK

def generic_store_DV_A(cpu, op):
    # (void)op
    
    cpu.reg.A = cpu.DV
    
    return UOP_GENERIC_FETCH

def generic_store_DV_r8(cpu, op):
    '''Load DV into r8'''
    
    regval = cpu.DV
    h.reg_write_by_id_8(cpu, (op >> 3) & 7, regval)
    
    return UOP_GENERIC_FETCH

def generic_push_decrement(cpu, op):
    # (void)op
    
    cpu.reg.ImmH = cpu.DV # for some instructions
    _ = cpu.reg.SPd
    
    return UOP_CONTINUE

def generic_push_PC_M1(cpu, op):
    # (void)op
    
    cpu.DoWrite(cpu.reg.SPd, cpu.reg.PCH)
    
    return UOP_CONTINUE

def generic_push_PC_M2(cpu, op):
    # (void)op
    
    cpu.DoWrite(cpu.reg.SP, cpu.reg.PCL)
    
    return UOP_CONTINUE

def generic_pop_M0(cpu, op):
    # (void)op
    
    cpu.DoRead(cpu.reg.SPi)
    
    return UOP_CONTINUE

def generic_pop_M1(cpu, op):
    # (void)op
    
    cpu.reg.ImmL = cpu.DV
    
    cpu.DoRead(cpu.reg.SPi)
    
    return UOP_CONTINUE

def ISR_decrement_PC(cpu, op):
    # (void)op
    
    _ = cpu.reg.PCd
    
    return UOP_CONTINUE

def ISR_push_PC_M2(cpu, op):
    # (void)op
    
    generic_push_PC_M2(cpu, op)
    if not cpu.IS_NMI:
        DI(cpu, op)
    cpu.reg.PC = cpu.IRQ_Address()
    
    return UOP_CONTINUE

#endregion

#region Table 1 (LD)

def MOV_r8_r8(cpu, op):
    '''Move one register to other (does not support [HL])'''
    regval = h.reg_read_by_id_8(cpu, op & 7)
    h.reg_write_by_id_8(cpu, (op >> 3) & 7, regval)
    
    return UOP_GENERIC_FETCH

def STR_r8_uHL(cpu, op):
    '''Store from register to [HL]'''
    # (void)op
    
    regval = h.reg_read_by_id_8(cpu, op & 7)
    cpu.DoWrite(cpu.reg.HL, regval)
    
    return UOP_CONTINUE

def HALT(cpu, op):
    '''Request HALT mode'''
    # (void)op
    
    cpu.REQ_HALT = True
    
    return UOP_GENERIC_FETCH

#endregion

#region Table 2 (ALU)

def ALU_ADD_r8(cpu, op):
    
    regval = h.reg_read_by_id_8(cpu, op & 7)
    h.alu_ADD(cpu, regval)
    
    return UOP_GENERIC_FETCH

def ALU_ADD_DV(cpu, op):
    # (void)op
    
    regval = cpu.DV
    h.alu_ADD(cpu, regval)
    
    return UOP_GENERIC_FETCH

def ALU_ADC_r8(cpu, op):
    
    regval = h.reg_read_by_id_8(cpu, op & 7)
    h.alu_ADC(cpu, regval)
    
    return UOP_GENERIC_FETCH

def ALU_ADC_DV(cpu, op):
    # (void)op
    
    regval = cpu.DV
    h.alu_ADC(cpu, regval)
    
    return UOP_GENERIC_FETCH

def ALU_SUB_r8(cpu, op):
    
    regval = h.reg_read_by_id_8(cpu, op & 7)
    h.alu_SUB(cpu, regval, writeback=True)
    
    return UOP_GENERIC_FETCH

def ALU_SUB_DV(cpu, op):
    # (void)op
    
    regval = cpu.DV
    h.alu_SUB(cpu, regval, writeback=True)
    
    return UOP_GENERIC_FETCH

def ALU_SBC_r8(cpu, op):
    
    regval = h.reg_read_by_id_8(cpu, op & 7)
    h.alu_SBC(cpu, regval)
    
    return UOP_GENERIC_FETCH

def ALU_SBC_DV(cpu, op):
    # (void)op
    
    regval = cpu.DV
    h.alu_SBC(cpu, regval)
    
    return UOP_GENERIC_FETCH

def ALU_AND_r8(cpu, op):
    
    regval = h.reg_read_by_id_8(cpu, op & 7)
    h.alu_AND(cpu, regval)
    
    return UOP_GENERIC_FETCH

def ALU_AND_DV(cpu, op):
    # (void)op
    
    regval = cpu.DV
    h.alu_AND(cpu, regval)
    
    return UOP_GENERIC_FETCH

def ALU_XOR_r8(cpu, op):
    
    regval = h.reg_read_by_id_8(cpu, op & 7)
    h.alu_XOR(cpu, regval)
    
    return UOP_GENERIC_FETCH

def ALU_XOR_DV(cpu, op):
    # (void)op
    
    regval = cpu.DV
    h.alu_XOR(cpu, regval)
    
    return UOP_GENERIC_FETCH

def ALU_OR_r8(cpu, op):
    
    regval = h.reg_read_by_id_8(cpu, op & 7)
    h.alu_OR(cpu, regval)
    
    return UOP_GENERIC_FETCH

def ALU_OR_DV(cpu, op):
    # (void)op
    
    regval = cpu.DV
    h.alu_OR(cpu, regval)
    
    return UOP_GENERIC_FETCH

def ALU_CP_r8(cpu, op):
    
    regval = h.reg_read_by_id_8(cpu, op & 7)
    h.alu_SUB(cpu, regval, writeback=False)
    
    return UOP_GENERIC_FETCH

def ALU_CP_DV(cpu, op):
    # (void)op
    
    regval = cpu.DV
    h.alu_SUB(cpu, regval, writeback=False)
    
    return UOP_GENERIC_FETCH

#endregion

#region Table 0

def STR_A_r16(cpu, op):
    reg = (op >> 4) & 3
    regval = h.reg_read_by_id_16(cpu, reg)
    
    cpu.DoWrite(regval, cpu.reg.A)
    
    return UOP_CONTINUE

def STR_A_uHLi(cpu, op):
    '''Store from A to [HL+]'''
    # (void)op
    
    regval = cpu.reg.A
    cpu.DoWrite(cpu.reg.HLi, regval)
    
    return UOP_CONTINUE

def STR_A_uHLd(cpu, op):
    '''Store from A to [HL-]'''
    # (void)op
    
    regval = cpu.reg.A
    cpu.DoWrite(cpu.reg.HLd, regval)
    
    return UOP_CONTINUE

def LDR_A_r16(cpu, op):
    reg = (op >> 4) & 3
    regval = h.reg_read_by_id_16(cpu, reg)
    
    cpu.DoRead(regval)
    
    return UOP_CONTINUE

def LDR_A_uHLi(cpu, op):
    '''Load from [HL+] to DV'''
    # (void)op
    
    cpu.DoRead(cpu.reg.HLi)
    
    return UOP_CONTINUE

def LDR_A_uHLd(cpu, op):
    '''Load from [HL-] to DV'''
    # (void)op
    
    cpu.DoRead(cpu.reg.HLd)
    
    return UOP_CONTINUE

def LD_r16_n16_M1(cpu, op):
    
    reg = (op >> 4) & 3
    if reg == 0:
        cpu.reg.C = cpu.DV
    elif reg == 1:
        cpu.reg.E = cpu.DV
    elif reg == 2:
        cpu.reg.L = cpu.DV
    elif reg == 3:
        cpu.reg.SPL = cpu.DV
    
    cpu.DoRead(cpu.reg.PCi)
    
    return UOP_CONTINUE

def LD_r16_n16_M2(cpu, op):
    
    reg = (op >> 4) & 3
    if reg == 0:
        cpu.reg.B = cpu.DV
    elif reg == 1:
        cpu.reg.D = cpu.DV
    elif reg == 2:
        cpu.reg.H = cpu.DV
    elif reg == 3:
        cpu.reg.SPH = cpu.DV
    
    return UOP_GENERIC_FETCH

def LD_uHL_n8(cpu, op):
    # (void)op
    
    cpu.DoWrite(cpu.reg.HL, cpu.DV)
    
    return UOP_CONTINUE

def JR(cpu, op):
    # (void)op
    
    offs = cpu.DV
    if offs >= 0x80:
        offs |= 0xFF00
    
    addr = (cpu.reg.PC + offs) & 0xFFFF
    cpu.reg.PC = addr
    
    return UOP_CONTINUE

def ADD_r16_r16(cpu, op):
    # Note: the high part gets added in the next cycle, but
    #  I don't bother to emulate it, considering
    #  the difference is unobservable
    
    reg = (op >> 4) & 3
    regval = h.reg_read_by_id_16(cpu, reg)
    
    src = cpu.reg.HL
    
    flags = 0
    
    if ((src & 0xFFF) + (regval & 0xFFF)) > 0xFFF:
        flags |= FLAG_HC
    if ((src & 0xFFFF) + (regval & 0xFFFF)) > 0xFFFF:
        flags |= FLAG_CY
    
    cpu.reg.F = (cpu.reg.F & FLAG_ZERO) | flags
    
    cpu.reg.HL = (src + regval) & 0xFFFF
    
    return UOP_CONTINUE

def INC_r16(cpu, op):
    
    reg = (op >> 4) & 3
    regval = h.reg_read_by_id_16(cpu, reg)
    
    regval = (regval + 1) & 0xFFFF
    
    h.reg_write_by_id_16(cpu, reg, regval)
    
    return UOP_CONTINUE

def DEC_r16(cpu, op):
    
    reg = (op >> 4) & 3
    regval = h.reg_read_by_id_16(cpu, reg)
    
    regval = (regval - 1) & 0xFFFF
    
    h.reg_write_by_id_16(cpu, reg, regval)
    
    return UOP_CONTINUE

def INC_r8(cpu, op):
    reg = (op >> 3) & 7
    regval = h.reg_read_by_id_8(cpu, reg)
    flags = 0
    
    if (regval & 0x0F) == 0x0F:
        flags |= FLAG_HC
    if regval == 0xFF:
        flags |= FLAG_ZERO
    
    regval = (regval + 1) & 0xFF
    
    h.reg_write_by_id_8(cpu, reg, regval)
    
    cpu.reg.F = (cpu.reg.F & FLAG_CY) | flags
    
    return UOP_GENERIC_FETCH

def DEC_r8(cpu, op):
    reg = (op >> 3) & 7
    regval = h.reg_read_by_id_8(cpu, reg)
    flags = FLAG_SUB
    
    if (regval & 0x0F) == 0x00:
        flags |= FLAG_HC
    if regval == 0x01:
        flags |= FLAG_ZERO
    
    regval = (regval - 1) & 0xFF
    
    h.reg_write_by_id_8(cpu, reg, regval)
    
    cpu.reg.F = (cpu.reg.F & FLAG_CY) | flags
    
    return UOP_GENERIC_FETCH

def INC_uHL(cpu, op):
    regval = cpu.DV
    flags = 0
    
    if (regval & 0x0F) == 0x0F:
        flags |= FLAG_HC
    if regval == 0xFF:
        flags |= FLAG_ZERO
    
    regval = (regval + 1) & 0xFF
    
    cpu.reg.F = (cpu.reg.F & FLAG_CY) | flags
    
    cpu.DoWrite(cpu.reg.HL, regval)
    
    return UOP_CONTINUE

def DEC_uHL(cpu, op):
    regval = cpu.DV
    flags = FLAG_SUB
    
    if (regval & 0x0F) == 0x00:
        flags |= FLAG_HC
    if regval == 0x01:
        flags |= FLAG_ZERO
    
    regval = (regval - 1) & 0xFF
    
    cpu.reg.F = (cpu.reg.F & FLAG_CY) | flags
    
    cpu.DoWrite(cpu.reg.HL, regval)
    
    return UOP_CONTINUE

def CBA(cpu, op):
    regval = cpu.reg.A
    
    regval = h.CB0(cpu, op, regval)
    
    cpu.reg.A = regval
    
    cpu.reg.F &= FLAG_CY
    
    return UOP_GENERIC_FETCH

def DAA(cpu, op):
    # (void)op
    
    data = cpu.reg.A
    flags = cpu.reg.F & (FLAG_CY | FLAG_HC | FLAG_SUB)
    
    if not flags & FLAG_SUB: # ADD
        if (flags & FLAG_HC) or ((data & 0x0F) > 0x09):
            data += 0x06
            flags |= FLAG_HC
        if (flags & FLAG_CY) or ((data & 0x1FF) > 0x9F):
            data += 0x60
            flags |= FLAG_CY
    else: # SUB
        if flags & FLAG_HC:
            data -= 0x06
        if flags & FLAG_CY:
            data -= 0x60
    
    flags &= FLAG_SUB | FLAG_CY
    data &= 0xFF
    
    if not data:
        flags |= FLAG_ZERO
    
    cpu.reg.F = flags
    cpu.reg.A = data
    
    return UOP_GENERIC_FETCH

def CPL(cpu, op):
    # (void)op
    
    cpu.reg.A ^= 0xFF
    cpu.reg.F |= FLAG_SUB | FLAG_HC
    
    return UOP_GENERIC_FETCH

def SCF(cpu, op):
    # (void)op
    
    cpu.reg.F = (cpu.reg.F & FLAG_ZERO) | FLAG_CY
    
    return UOP_GENERIC_FETCH

def CCF(cpu, op):
    # (void)op
    
    cpu.reg.F = (cpu.reg.F & (FLAG_ZERO | FLAG_CY)) ^ FLAG_CY
    
    return UOP_GENERIC_FETCH

def LD_a16_SP_M2(cpu, op):
    # (void)op
    
    cpu.reg.ImmH = cpu.DV
    
    cpu.DoWrite(cpu.reg.Imm, cpu.reg.SPL)
    
    return UOP_CONTINUE

def LD_a16_SP_M3(cpu, op):
    # (void)op
    
    cpu.DoWrite((cpu.reg.Imm + 1) & 0xFFFF, cpu.reg.SPH)
    
    return UOP_CONTINUE

#endregion

#region Table 3

def DI(cpu, op):
    # (void)op
    
    cpu.IME_ASK = False
    cpu.IME = False
    
    return UOP_GENERIC_FETCH

def EI(cpu, op):
    # (void)op
    
    cpu.IME_ASK = True
    
    return UOP_GENERIC_FETCH

def CB_mode(cpu, op):
    # (void)op
    
    cpu.STATE_CB = True
    cpu.STATE_IDX = -1 # force opcode fetch
    cpu.DoRead(cpu.reg.PCi)
    
    return UOP_CONTINUE

def RET_M2(cpu, op):
    # (void)op
    
    cpu.reg.ImmH = cpu.DV
    cpu.reg.PC = cpu.reg.Imm
    
    return UOP_CONTINUE

def RETI_M2(cpu, op):
    # (void)op
    
    RET_M2(cpu, op)
    if not cpu.IS_NMI:
        EI(cpu, op)
    
    cpu.IS_NMI = False
    
    return UOP_CONTINUE

def RST_M3(cpu, op):
    addr = op & 0x38
    cpu.reg.PC = addr
    
    return UOP_GENERIC_FETCH

def CALL(cpu, op):
    # (void)op
    
    cpu.reg.PC = cpu.reg.Imm
    
    return UOP_GENERIC_FETCH

def JP_ok(cpu, op):
    # (void)op
    
    cpu.reg.ImmH = cpu.DV
    cpu.reg.PC = cpu.reg.Imm
    
    return UOP_CONTINUE

def JP_HL(cpu, op):
    # (void)op
    
    cpu.reg.PC = cpu.reg.HL
    
    return UOP_GENERIC_FETCH

def PUSH_M0(cpu, op):
    # (void)op
    
    _ = cpu.reg.SPd
    
    return UOP_CONTINUE

def PUSH_M1(cpu, op):
    
    reg = (op >> 4) & 3
    if reg == 0:
        cpu.DoWrite(cpu.reg.SPd, cpu.reg.B)
    elif reg == 1:
        cpu.DoWrite(cpu.reg.SPd, cpu.reg.D)
    elif reg == 2:
        cpu.DoWrite(cpu.reg.SPd, cpu.reg.H)
    elif reg == 3:
        cpu.DoWrite(cpu.reg.SPd, cpu.reg.A)
    
    return UOP_CONTINUE

def PUSH_M2(cpu, op):
    
    reg = (op >> 4) & 3
    if reg == 0:
        cpu.DoWrite(cpu.reg.SP, cpu.reg.C)
    elif reg == 1:
        cpu.DoWrite(cpu.reg.SP, cpu.reg.E)
    elif reg == 2:
        cpu.DoWrite(cpu.reg.SP, cpu.reg.L)
    elif reg == 3:
        cpu.DoWrite(cpu.reg.SP, cpu.reg.F)
    
    return UOP_CONTINUE

def POP_M2(cpu, op):
    
    reg = (op >> 4) & 3
    if reg == 0:
        cpu.reg.C = cpu.reg.ImmL
        cpu.reg.B = cpu.DV
    elif reg == 1:
        cpu.reg.E = cpu.reg.ImmL
        cpu.reg.D = cpu.DV
    elif reg == 2:
        cpu.reg.L = cpu.reg.ImmL
        cpu.reg.H = cpu.DV
    elif reg == 3:
        cpu.reg.F = cpu.reg.ImmL & 0xF0
        cpu.reg.A = cpu.DV
    
    return UOP_GENERIC_FETCH

def LD_a16_A(cpu, op):
    # (void)op
    
    cpu.reg.ImmH = cpu.DV
    cpu.DoWrite(cpu.reg.Imm, cpu.reg.A)
    
    return UOP_CONTINUE

def LD_a8_A(cpu, op):
    # (void)op
    
    cpu.reg.ImmH = 0xFF
    cpu.reg.ImmL = cpu.DV
    cpu.DoWrite(cpu.reg.Imm, cpu.reg.A)
    
    return UOP_CONTINUE

def LD_C_A(cpu, op):
    # (void)op
    
    cpu.reg.ImmH = 0xFF
    cpu.reg.ImmL = cpu.reg.C
    cpu.DoWrite(cpu.reg.Imm, cpu.reg.A)
    
    return UOP_CONTINUE

def LD_A_a16(cpu, op):
    # (void)op
    
    cpu.reg.ImmH = cpu.DV
    cpu.DoRead(cpu.reg.Imm)
    
    return UOP_CONTINUE

def LD_A_a8(cpu, op):
    # (void)op
    
    cpu.reg.ImmH = 0xFF
    cpu.reg.ImmL = cpu.DV
    cpu.DoRead(cpu.reg.Imm)
    
    return UOP_CONTINUE

def LD_A_C(cpu, op):
    # (void)op
    
    cpu.reg.ImmH = 0xFF
    cpu.reg.ImmL = cpu.reg.C
    cpu.DoRead(cpu.reg.Imm)
    
    return UOP_CONTINUE

def LD_SP_HL(cpu, op):
    # (void)op
    
    cpu.reg.SP = cpu.reg.HL
    
    return UOP_CONTINUE

def LD_HL_SP_e8(cpu, op):
    
    # Note: this happens in two cycles, but let's not emulate it, as it's pointless
    
    flags = 0
    src = cpu.reg.SP
    offset = cpu.DV
    if offset >= 0x80:
        offset |= 0xFF00
    
    if ((src & 0xF) + (offset & 0xF)) > 0xF:
        flags |= FLAG_HC
    if ((src & 0xFF) + (offset & 0xFF)) > 0xFF:
        flags |= FLAG_CY
    
    cpu.reg.HL = (cpu.reg.SP + offset) & 0xFFFF
    cpu.reg.F = flags
    
    return UOP_CONTINUE

def ADD_SP_e8(cpu, op):
    # (void)op
    
    flags = 0
    src = cpu.reg.SP
    offset = cpu.DV
    if offset >= 0x80:
        offset |= 0xFF00
    
    if ((src & 0xF) + (offset & 0xF)) > 0xF:
        flags |= FLAG_HC
    if ((src & 0xFF) + (offset & 0xFF)) > 0xFF:
        flags |= FLAG_CY
    
    cpu.reg.SP = (cpu.reg.SP + offset) & 0xFFFF
    cpu.reg.F = flags
    
    return UOP_CONTINUE

#endregion

#region CB

def CB0_r8(cpu, op):
    reg = op & 7
    regval = h.reg_read_by_id_8(cpu, reg)
    
    regval = h.CB0(cpu, op, regval)
    
    h.reg_write_by_id_8(cpu, reg, regval)
    
    return UOP_GENERIC_FETCH

def CB0_uHL(cpu, op):
    regval = cpu.DV
    
    regval = h.CB0(cpu, op, regval)
    
    cpu.DoWrite(cpu.reg.HL, regval)
    
    return UOP_CONTINUE

def CB1_r8(cpu, op):
    reg = op & 7
    regval = h.reg_read_by_id_8(cpu, reg)
    
    h.CB1(cpu, op, regval)
    
    return UOP_GENERIC_FETCH

def CB1_uHL(cpu, op):
    regval = cpu.DV
    
    h.CB1(cpu, op, regval)
    
    return UOP_GENERIC_FETCH

def CB2_r8(cpu, op):
    reg = op & 7
    regval = h.reg_read_by_id_8(cpu, reg)
    
    regval = h.CB2(cpu, op, regval)
    
    h.reg_write_by_id_8(cpu, reg, regval)
    
    return UOP_GENERIC_FETCH

def CB2_uHL(cpu, op):
    regval = cpu.DV
    
    regval = h.CB2(cpu, op, regval)
    
    cpu.DoWrite(cpu.reg.HL, regval)
    
    return UOP_CONTINUE

def CB3_r8(cpu, op):
    reg = op & 7
    regval = h.reg_read_by_id_8(cpu, reg)
    
    regval = h.CB3(cpu, op, regval)
    
    h.reg_write_by_id_8(cpu, reg, regval)
    
    return UOP_GENERIC_FETCH

def CB3_uHL(cpu, op):
    regval = cpu.DV
    
    regval = h.CB3(cpu, op, regval)
    
    cpu.DoWrite(cpu.reg.HL, regval)
    
    return UOP_CONTINUE

#endregion
