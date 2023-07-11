from .cpu_ucode import *

OP_NOP = (generic_fetch,)
OP_STOP = (STOP,)
OP_LD_a16_SP = (generic_fetch_op1, generic_fetch_op2, LD_a16_SP_M2, LD_a16_SP_M3, generic_fetch)
OP_JR = (generic_fetch_op1, JR, generic_fetch)
OP_JR_cc = (generic_cc_check_op1, JR, generic_fetch)
OP_LD_r16_n16 = (generic_fetch_op1, LD_r16_n16_M1, LD_r16_n16_M2)
OP_ADD_HL_r16 = (ADD_r16_r16, generic_fetch)
OP_LD_r16_A = (STR_A_r16, generic_fetch)
OP_LD_A_r16 = (LDR_A_r16, generic_store_DV_A)
OP_LD_HLi_A = (STR_A_uHLi, generic_fetch)
OP_LD_HLd_A = (STR_A_uHLd, generic_fetch)
OP_LD_A_HLi = (LDR_A_uHLi, generic_store_DV_A)
OP_LD_A_HLd = (LDR_A_uHLd, generic_store_DV_A)
OP_INC_r16 = (INC_r16, generic_fetch)
OP_DEC_r16 = (DEC_r16, generic_fetch)
OP_INC_r8 = (INC_r8,)
OP_DEC_r8 = (DEC_r8,)
OP_INC_uHL = (generic_fetch_uHL, INC_uHL, generic_fetch)
OP_DEC_uHL = (generic_fetch_uHL, DEC_uHL, generic_fetch)
OP_LD_r8_n8 = (generic_fetch_op1, generic_store_DV_r8)
OP_LD_uHL_n8 = (generic_fetch_op1, LD_uHL_n8, generic_fetch)
OP_RLCA = (CBA,)
OP_RRCA = (CBA,)
OP_RLA = (CBA,)
OP_RRA = (CBA,)
OP_DAA = (DAA,)
OP_CPL = (CPL,)
OP_SCF = (SCF,)
OP_CCF = (CCF,)

OP_LD_r8_r8 = (MOV_r8_r8,)
OP_LD_r8_uHL = (generic_fetch_uHL, generic_store_DV_r8)
OP_LD_uHL_r8 = (STR_r8_uHL, generic_fetch)
OP_HALT = (HALT,)

OP_ALU_ADD_r8 = (ALU_ADD_r8,)
OP_ALU_ADC_r8 = (ALU_ADC_r8,)
OP_ALU_SUB_r8 = (ALU_SUB_r8,)
OP_ALU_SBC_r8 = (ALU_SBC_r8,)
OP_ALU_AND_r8 = (ALU_AND_r8,)
OP_ALU_XOR_r8 = (ALU_XOR_r8,)
OP_ALU_OR_r8  = (ALU_OR_r8,)
OP_ALU_CP_r8  = (ALU_CP_r8,)
OP_ALU_ADD_uHL = (generic_fetch_uHL, ALU_ADD_DV)
OP_ALU_ADC_uHL = (generic_fetch_uHL, ALU_ADC_DV)
OP_ALU_SUB_uHL = (generic_fetch_uHL, ALU_SUB_DV)
OP_ALU_SBC_uHL = (generic_fetch_uHL, ALU_SBC_DV)
OP_ALU_AND_uHL = (generic_fetch_uHL, ALU_AND_DV)
OP_ALU_XOR_uHL = (generic_fetch_uHL, ALU_XOR_DV)
OP_ALU_OR_uHL  = (generic_fetch_uHL, ALU_OR_DV)
OP_ALU_CP_uHL  = (generic_fetch_uHL, ALU_CP_DV)

OP_ALU_ADD_n8 = (generic_fetch_op1, ALU_ADD_DV)
OP_ALU_ADC_n8 = (generic_fetch_op1, ALU_ADC_DV)
OP_ALU_SUB_n8 = (generic_fetch_op1, ALU_SUB_DV)
OP_ALU_SBC_n8 = (generic_fetch_op1, ALU_SBC_DV)
OP_ALU_AND_n8 = (generic_fetch_op1, ALU_AND_DV)
OP_ALU_XOR_n8 = (generic_fetch_op1, ALU_XOR_DV)
OP_ALU_OR_n8  = (generic_fetch_op1, ALU_OR_DV)
OP_ALU_CP_n8  = (generic_fetch_op1, ALU_CP_DV)
OP_RET = (generic_pop_M0, generic_pop_M1, RET_M2, generic_fetch)
OP_RET_cc = (generic_cc_check, generic_pop_M0, generic_pop_M1, RET_M2, generic_fetch)
OP_RETI = (generic_pop_M0, generic_pop_M1, RETI_M2, generic_fetch)
OP_JP = (generic_fetch_op1, generic_fetch_op2, JP_ok, generic_fetch)
OP_JP_cc = (generic_fetch_op1, generic_cc_check_op2, JP_ok, generic_fetch)
OP_JP_HL = (JP_HL,)
OP_CALL = (generic_fetch_op1, generic_fetch_op2, generic_push_decrement, generic_push_PC_M1, generic_push_PC_M2, CALL)
OP_CALL_cc = (generic_fetch_op1, generic_cc_check_op2, generic_push_decrement, generic_push_PC_M1, generic_push_PC_M2, CALL)
OP_RST = (generic_push_decrement, generic_push_PC_M1, generic_push_PC_M2, RST_M3)
OP_DI = (DI,)
OP_EI = (EI,)
OP_CB = (CB_mode,)
OP_PUSH = (PUSH_M0, PUSH_M1, PUSH_M2, generic_fetch)
OP_POP = (generic_pop_M0, generic_pop_M1, POP_M2)
OP_LDH_a8_A = (generic_fetch_op1, LD_a8_A, generic_fetch)
OP_LDH_A_a8 = (generic_fetch_op1, LD_A_a8, generic_store_DV_A)
OP_LDH_C_A = (LD_C_A, generic_fetch)
OP_LDH_A_C = (LD_A_C, generic_store_DV_A)
OP_LD_a16_A = (generic_fetch_op1, generic_fetch_op2, LD_a16_A, generic_fetch)
OP_LD_A_a16 = (generic_fetch_op1, generic_fetch_op2, LD_A_a16, generic_store_DV_A)
OP_LD_SP_HL = (LD_SP_HL, generic_fetch)
OP_LD_HL_SP_e8 = (generic_fetch_op1, LD_HL_SP_e8, generic_fetch)
OP_ADD_SP_e8 = (generic_fetch_op1, ADD_SP_e8, generic_continue, generic_fetch)

OP_WEDGE = None

ISR = (ISR_decrement_PC, generic_push_decrement, generic_push_PC_M1, ISR_push_PC_M2, generic_fetch)


CB_OP_0_r8 = (CB0_r8,)
CB_OP_0_uHL = (generic_fetch_uHL, CB0_uHL, generic_fetch)
CB_OP_1_r8 = (CB1_r8,)
CB_OP_1_uHL = (generic_fetch_uHL, CB1_uHL)
CB_OP_2_r8 = (CB2_r8,)
CB_OP_2_uHL = (generic_fetch_uHL, CB2_uHL, generic_fetch)
CB_OP_3_r8 = (CB3_r8,)
CB_OP_3_uHL = (generic_fetch_uHL, CB3_uHL, generic_fetch)


OPCODES0 = \
(
    OP_NOP,       OP_LD_r16_n16, OP_LD_r16_A, OP_INC_r16, OP_INC_r8,  OP_DEC_r8,  OP_LD_r8_n8,  OP_RLCA,
    OP_LD_a16_SP, OP_ADD_HL_r16, OP_LD_A_r16, OP_DEC_r16, OP_INC_r8,  OP_DEC_r8,  OP_LD_r8_n8,  OP_RRCA,
    OP_STOP,      OP_LD_r16_n16, OP_LD_r16_A, OP_INC_r16, OP_INC_r8,  OP_DEC_r8,  OP_LD_r8_n8,  OP_RLA,
    OP_JR,        OP_ADD_HL_r16, OP_LD_A_r16, OP_DEC_r16, OP_INC_r8,  OP_DEC_r8,  OP_LD_r8_n8,  OP_RRA,
    OP_JR_cc,     OP_LD_r16_n16, OP_LD_HLi_A, OP_INC_r16, OP_INC_r8,  OP_DEC_r8,  OP_LD_r8_n8,  OP_DAA,
    OP_JR_cc,     OP_ADD_HL_r16, OP_LD_A_HLi, OP_DEC_r16, OP_INC_r8,  OP_DEC_r8,  OP_LD_r8_n8,  OP_CPL,
    OP_JR_cc,     OP_LD_r16_n16, OP_LD_HLd_A, OP_INC_r16, OP_INC_uHL, OP_DEC_uHL, OP_LD_uHL_n8, OP_SCF,
    OP_JR_cc,     OP_ADD_HL_r16, OP_LD_A_HLd, OP_DEC_r16, OP_INC_r8,  OP_DEC_r8,  OP_LD_r8_n8,  OP_CCF,
)

OPCODES1 = \
(
    ((((OP_LD_r8_r8,)  * 6) + (OP_LD_r8_uHL,) + ((OP_LD_r8_r8,)  * 1)) * 6) + \
    ((((OP_LD_uHL_r8,) * 6) + (OP_HALT,)      + ((OP_LD_uHL_r8,) * 1)) * 1) + \
    ((((OP_LD_r8_r8,)  * 6) + (OP_LD_r8_uHL,) + ((OP_LD_r8_r8,)  * 1)) * 1)
)

OPCODES2 = \
(
    (((OP_ALU_ADD_r8,) * 6) + (OP_ALU_ADD_uHL,) + ((OP_ALU_ADD_r8,) * 1)) + \
    (((OP_ALU_ADC_r8,) * 6) + (OP_ALU_ADC_uHL,) + ((OP_ALU_ADC_r8,) * 1)) + \
    (((OP_ALU_SUB_r8,) * 6) + (OP_ALU_SUB_uHL,) + ((OP_ALU_SUB_r8,) * 1)) + \
    (((OP_ALU_SBC_r8,) * 6) + (OP_ALU_SBC_uHL,) + ((OP_ALU_SBC_r8,) * 1)) + \
    (((OP_ALU_AND_r8,) * 6) + (OP_ALU_AND_uHL,) + ((OP_ALU_AND_r8,) * 1)) + \
    (((OP_ALU_XOR_r8,) * 6) + (OP_ALU_XOR_uHL,) + ((OP_ALU_XOR_r8,) * 1)) + \
    (((OP_ALU_OR_r8,)  * 6) + (OP_ALU_OR_uHL,)  + ((OP_ALU_OR_r8,)  * 1)) + \
    (((OP_ALU_CP_r8,)  * 6) + (OP_ALU_CP_uHL,)  + ((OP_ALU_CP_r8,)  * 1))
)

OPCODES3 = \
(
    OP_RET_cc,      OP_POP,      OP_JP_cc,    OP_JP,    OP_CALL_cc, OP_PUSH,  OP_ALU_ADD_n8, OP_RST,
    OP_RET_cc,      OP_RET,      OP_JP_cc,    OP_CB,    OP_CALL_cc, OP_CALL,  OP_ALU_ADC_n8, OP_RST,
    OP_RET_cc,      OP_POP,      OP_JP_cc,    OP_WEDGE, OP_CALL_cc, OP_PUSH,  OP_ALU_SUB_n8, OP_RST,
    OP_RET_cc,      OP_RETI,     OP_JP_cc,    OP_WEDGE, OP_CALL_cc, OP_WEDGE, OP_ALU_SBC_n8, OP_RST,
    OP_LDH_a8_A,    OP_POP,      OP_LDH_C_A,  OP_WEDGE, OP_WEDGE,   OP_PUSH,  OP_ALU_AND_n8, OP_RST,
    OP_ADD_SP_e8,   OP_JP_HL,    OP_LD_a16_A, OP_WEDGE, OP_WEDGE,   OP_WEDGE, OP_ALU_XOR_n8, OP_RST,
    OP_LDH_A_a8,    OP_POP,      OP_LDH_A_C,  OP_DI,    OP_WEDGE,   OP_PUSH,  OP_ALU_OR_n8,  OP_RST,
    OP_LD_HL_SP_e8, OP_LD_SP_HL, OP_LD_A_a16, OP_EI,    OP_WEDGE,   OP_WEDGE, OP_ALU_CP_n8,  OP_RST
)

OPCODES = OPCODES0 + OPCODES1 + OPCODES2 + OPCODES3


CB0 = (((CB_OP_0_r8,) * 6) + (CB_OP_0_uHL, CB_OP_0_r8)) * 8
CB1 = (((CB_OP_1_r8,) * 6) + (CB_OP_1_uHL, CB_OP_1_r8)) * 8
CB2 = (((CB_OP_2_r8,) * 6) + (CB_OP_2_uHL, CB_OP_2_r8)) * 8
CB3 = (((CB_OP_3_r8,) * 6) + (CB_OP_3_uHL, CB_OP_3_r8)) * 8

OPCODES_CB = CB0 + CB1 + CB2 + CB3
