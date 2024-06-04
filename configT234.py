## -*- coding: utf-8 -*-
"""
Created on Fri Jun 15 09:50:25 2018

Updated for T234 support

Description:
This script configures the T234 platform by defining registers and their mappings
for DVFS (Dynamic Voltage and Frequency Scaling) table management. It includes
axes for GUI display, registers to be displayed, and additional configurations.
"""

# Import the registers dictionary from accompanying aremc file
from aremcT234_m import registers
# Import training-specific register configurations

# Tuple of all axes to display in GUI axes selection
axes = ( "AutocaloffsetDQS", "AutocaloffsetDQ", "AutocaloffsetCA", "AutocaloffsetCMD",
        "AutocaloffsetCLK", "AutocaloffsetWCK", "AutocaloffsetDQTerm", "AutocaloffsetDQSTerm",
        "DQIVREF", "DQSIVREF", "DQVREF", "CMDVREF", "RDQS",
        "IBRXRT", "OBCLK", "OBCMD1t", "OBDQ", "WCKDQ", "PutermExtra", "QUSE"
)

"""
List of tuples that matches registers in DVFS, aremc, and cfg file together and designated an axis
Tuple:  First item is the register names in Regular Expression
        Second item is the corresponding register name in aremc dictionary using RegEx
        Third item is the corresponding register name in cfg file using RegEx
        Fourth item is the axis the registers are matched with
        Fifth item is whether the field values are in two's complement or not

Note: add " (training)" in axis name to direct to these registers when training is necessary
"""
registers_to_display = [
    (r"EMC_PMACRO_OB_DDLL_LONG_DQS_RANK([01])_4_0_CH(?P<CH>\d+)",              r'PMACRO_OB_DDLL_LONG_DQS_RANK\1_4_0',          r'EmcPmacroObDdllLongDqsRank\1_4_\g<CH>',   "OBCLK", False),
    (r"EMC_PMACRO_OB_DDLL_LONG_DQ_RANK([01])_([01])_0_CH(?P<CH>\d+)",          r'PMACRO_OB_DDLL_LONG_DQ_RANK\1_\2_0',          r'EmcPmacroObDdllLongDqRank\1_\2_\g<CH>',   "OBDQ", False),
    (r"EMC_PMACRO_OB_DDLL_LONG_DQS_RANK([01])_([01])_0_CH(?P<CH>\d+)",          r'PMACRO_OB_DDLL_LONG_DQS_RANK\1_\2_0',         r'EmcPmacroObDdllLongDqsRank\1_\2_\g<CH>',  "OBDQS", False),
    (r"EMC_PMACRO_OB_DDLL_LONG_WCK_RANK([01])_([01])_0_CH(?P<CH>\d+)",          r'PMACRO_OB_DDLL_LONG_WCK_RANK\1_\2_0',         r'EmcPmacroObDdllLongWckRank\1_\2_\g<CH>',  "WCKDQ", False),
    (r"EMC_PMACRO_OB_DDLL_SHORT_DQ_RANK([01])_CMD([01])_[01]_0_CH(?P<CH>\d+)",  r'PMACRO_OB_DDLL_SHORT_DQ_RANK\1_CMD\1_\1_0',   r'EmcPmacroObDdllLongDqRank\1_\2_\g<CH>',   "OBCMD1t", False),
    ##(r"EMC_MRW14_0_CH(?P<CH>\d+)", r'MRW14_0', "", "DQVREF", False), ## 05252024- Gil updated
    (r"EMC_PMACRO_IB_DDLL_LONG_DQS_RANK([01])_([01])_0_CH(?P<CH>\d+)",          r'PMACRO_IB_DDLL_LONG_DQS_RANK\1_\2_0',         r'EmcPmacroIbDdllLongDqsRank\1_\2_\g<CH>',  "RDQS", False),
    (r"EMC_PMACRO_IB_VREF_DQ_([01])_0_CH(?P<CH>\d+)",                           r'PMACRO_IB_VREF_DQ_\1_0',                      r'EmcPmacroIbVrefDq_\1',                    "DQIVREF", False),
    (r"EMC_PMACRO_RANK1_IB_VREF_DQ_([01])_0_CH(?P<CH>\d+)",                     r'PMACRO_IB_VREF_DQ_\1_0',                      r'EmcPmacroIbVrefDq_\1',                    "DQIVREF", False),
    (r"EMC_PMACRO_IB_VREF_DQS_([01])_0_CH(?P<CH>\d+)",                          r'PMACRO_IB_VREF_DQS_\1_0',                     r'EmcPmacroIbVrefDqs_\1',                   "DQSIVREF", False),
    (r"EMC_PMACRO_AUTO_CAL_CONFIG3_0_CH(?P<CH>\d+)",                            r'AUTO_CAL_CONFIG3_0',                          r'EmcPmacroAutoCalConfig3',                 "AutocaloffsetCLK", True),
    (r"EMC_PMACRO_AUTO_CAL_CONFIG4_0_CH(?P<CH>\d+)",                            r'AUTO_CAL_CONFIG4_0',                          r'EmcPmacroAutoCalConfig4',                 "AutocaloffsetCA", True),
    (r"EMC_PMACRO_AUTO_CAL_CONFIG5_0_CH(?P<CH>\d+)",                            r'AUTO_CAL_CONFIG5_0',                          r'EmcPmacroAutoCalConfig5',                 "AutocaloffsetCMD", True),
    (r"EMC_PMACRO_AUTO_CAL_CONFIG6_0_CH(?P<CH>\d+)",                            r'AUTO_CAL_CONFIG6_0',                          r'EmcPmacroAutoCalConfig6',                 "AutocaloffsetDQ", True),
    (r"EMC_PMACRO_AUTO_CAL_CONFIG7_0_CH(?P<CH>\d+)",                            r'AUTO_CAL_CONFIG7_0',                          r'EmcPmacroAutoCalConfig7',                 "AutocaloffsetDQS", True),
    (r"EMC_PMACRO_AUTO_CAL_CONFIG8_0_CH(?P<CH>\d+)",                            r'AUTO_CAL_CONFIG8_0',                          r'EmcPmacroAutoCalConfig8',                 "AutocaloffsetDQ/STerm", True),
    (r"EMC_PMACRO_AUTO_CAL_CONFIG10_0_CH(?P<CH>\d+)",                           r'AUTO_CAL_CONFIG10_0',                         r'EmcPmacroAutoCalConfig10',                "AutocaloffsetWCK", True),
    (r"EMC_MRW15_0.*",                                                          r'MRW15_0',                                         r'EmcMrw15',                                "DQVREF", False),    # Gil Jung
    (r"EMC_PUTERM_EXTRA_0.*",                                                   r'PUTERM_EXTRA_0',                              r'EmcPutermExtra',                          "PutermExtra", False),
    (r"EMC_QUSE_0.*",                                                           r'QUSE_0',                                      r'EmcQUse',                                 "QUSE", False),
    (r"EMC_PMACRO_PAD_CFG_CTRL_0.*",                                            r'PMACRO_PAD_CFG_CTRL_0',                       r'EmcPmacroIbRxrt',                         "IBRXRT", False),
    (r"R0_DRAM_MR12",                                                           r'DRAM_MR12',                                    r'EmcWarmBootMrwExtra',                       "CMDVREF", False),
    (r"EMC(?P<CH>\d+)_EMC_TRAINING_RW_OFFSET_IB_BYTE(\d)_0",                       r'TRAINING_RW_OFFSET_IB_BYTE\2_0',              "",                                "RDQS (training)", True),
    (r"EMC(?P<CH>\d+)_EMC_TRAINING_RW_OFFSET_IB_MISC_0",                           r'TRAINING_RW_OFFSET_IB_MISC_0',                "",                                "RDQS (training)", True),   
    (r"EMC(?P<CH>\d+)_EMC_TRAINING_RW_OFFSET_OB_BYTE(\d)_0",                      r'TRAINING_RW_OFFSET_OB_BYTE\2_0',                  "",                             "OBDQ (training)", True),
    (r"EMC(?P<CH>\d+)_EMC_TRAINING_RW_OFFSET_OB_MISC_0",                          r'TRAINING_RW_OFFSET_OB_MISC_0',                    "",                              "OBDQ (training)", True), 
    (r"EMC(?P<CH>\d+)_EMC_TRAINING_WR_LEVEL_OFFSET_OB_MISC_0",              r'TRAINING_WR_LEVEL_OFFSET_OB_MISC_0',                      "",                         "WCKDQ (training)", True),
    (r"EMC_SAVE_RESTORE_MOD_IB_BYTE(\d)_VREF_OFF",                          r"SAVE_RESTORE_MOD_IB_BYTE\1_VREF_OFF",             "",                             "DQIVREF (training)", False),
    (r"EMC_SAVE_RESTORE_MOD_OB_C(\d)S(\d)_VREF_OFF",                        r"SAVE_RESTORE_MOD_OB_C\1S\2_VREF_OFF",             "",                             "DQVREF (training)", False)    
]

"""
Dictionary used to select particular fields to display
key: Axis where not all fields need to be displayed
value: First item in tuple is another tuple containing the index of the fields that should be changed together
       Second item is the total number of fields for each register in the axis
"""
counter_specific_fields = {
    'AutocaloffsetDQS': ((0, 2), 4),
    'AutocaloffsetDQ': ((0, 2), 4),
    'AutocaloffsetCA': ((0, 2), 4),
    'AutocaloffsetCMD': ((0, 2), 4),
    'AutocaloffsetCLK': ((0, 2), 4),
    'AutocaloffsetWCK': ((0, 2), 4),
}

"""
Dictionary used to display certain channels depending on data bus size
key:    Data bus number of bits
value:  Tuple of channels to display/change
        (Empty string used for registers that don't have channel)
"""
channel_select = {
    '128': ('', '0', '1', '2', '3', '4', '5', '6', '7'),
    '256': ('', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15')
}


# Training registers are not in aremc file, so added below
EMC_SAVE_RESTORE_MOD_IB = []
EMC_SAVE_RESTORE_MOD_OB = []

for byte in range(0,8):
    register = "SAVE_RESTORE_MOD_IB_BYTE" + str(byte) + "_VREF_OFF"
    EMC_SAVE_RESTORE_MOD_IB.append(register)
    C = byte // 2
    S = byte % 2
    register = "SAVE_RESTORE_MOD_OB_C" + str(C) + "S" + str(S) + "_VREF_OFF"
    EMC_SAVE_RESTORE_MOD_OB.append(register)

# Registers EMC_SAVE_RESTORE_MOD_IB_
if 'EMC' not in registers:
    registers['EMC'] = {}
    registers['EMC']['register_list']  = []

for register in EMC_SAVE_RESTORE_MOD_IB:
    registers['EMC'][register] = {
        'addr'            : 0x0,
        'secure'          : 0x0,
        'word_count'      : 0x1,
        'size'            : 0x8,
        'reset_val'       : 0x0,
        'array'           : False,
        'reset_mask'      : 0x8000007f,
        'sw_default_val'  : 0x0,
        'sw_default_mask' : 0xcfffffff,
        'read_mask'       : 0xcfffffff,
        'write_mask'      : 0xcfffffff,
        '(signed bit)' : {
            'lsb'        : 31,
            'msb'        : 31,
            'size'       : 1,
            'field'      : (0x1 << 31),
            'woffset'    : 0x0,
            'default'    : 0x0,
            'sw_default' : 0x0,
            'action'     : 'rw',
            'enums' : {
            },
        },
        register : {
            'lsb'        : 0,
            'msb'        : 6,
            'size'       : 7,
            'field'      : (0x7f << 0),
            'woffset'    : 0x0,
            'default'    : 0x0,
            'sw_default' : 0x0,
            'action'     : 'rw',
            'enums' : {
            },
        },
        # Fields sorted in order of declaration in register
        'field_list' : [
            '(signed bit)',
            register
        ],
    } # End of registers: EMC_SAVE_RESTORE_MOD_IB_
            
    registers['EMC']['register_list'].append(register)
            
# Registers EMC_SAVE_RESTORE_MOD_OB_
for register in EMC_SAVE_RESTORE_MOD_OB:
    registers['EMC'][register] = {
        'addr'            : 0x0,
        'secure'          : 0x0,
        'word_count'      : 0x1,
        'size'            : 0x8,
        'reset_val'       : 0x0,
        'array'           : False,
        'reset_mask'      : 0x800000ff,
        'sw_default_val'  : 0x0,
        'sw_default_mask' : 0x800000ff,
        'read_mask'       : 0x800000ff,
        'write_mask'      : 0x800000ff,
        '(signed bit)' : {
            'lsb'        : 31,
            'msb'        : 31,
            'size'       : 1,
            'field'      : (0x1 << 31),
            'woffset'    : 0x0,
            'default'    : 0x0,
            'sw_default' : 0x0,
            'action'     : 'rw',
            'enums' : {
            },
        },
        register : {
            'lsb'        : 0,
            'msb'        : 7,
            'size'       : 8,
            'field'      : (0xff << 0),
            'woffset'    : 0x0,
            'default'    : 0x0,
            'sw_default' : 0x0,
            'action'     : 'rw',
            'enums' : {
            },
        },
        # Fields sorted in order of declaration in register
        'field_list' : [
            '(signed bit)',
            register
        ],
    } # End of registers: EMC_SAVE_RESTORE_MOD_OB_

    registers['EMC']['register_list'].append(register)
    ## print(EMC_SAVE_RESTORE_MOD_OB)    

# CMDVREF register is not in aremc. just added - Gil Jung

# R0_DRAM_MR12
if 'R0' not in registers:
    registers['R0'] = {}
    registers['R0']['register_list']  = []

registers['R0']['DRAM_MR12'] = {
    'addr'            : 0x00,
    'secure'          : 0x0,
    'word_count'      : 0x1,
    'size'            : 0x20,
    'reset_val'       : 0x0,
    'array'           : False,
    'reset_mask'      : 0x000000ff,
    'sw_default_val'  : 0x0,
    'sw_default_mask' : 0x000000ff,
    'read_mask'       : 0x000000ff,
    'write_mask'      : 0x000000ff,
    'CMDVREF_MR12' : {
        'lsb'               : 0,
        'msb'               : 7,
        'size'              : 8,
        'field'             : (0xff << 0),
        'woffset'           : 0x0,
        'default'           : 0x0,
        'sw_default'        : 0x0,
        'parity_protection' : 1,
        'action'            : 'rw',
        'enums' : {
        },
    },    
    # Fields sorted in order of declaration in register
    'field_list' : [
        'CMDVREF_MR12',
    ],
} # End of register: R0_DRAM_MR12

registers['R0']['register_list'].append('DRAM_MR12')

# R0_DRAM_MR14
if 'R0' not in registers:
    registers['R0'] = {}
    registers['R0']['register_list']  = []

registers['R0']['DRAM_MR14'] = {
    'addr'            : 0x00,
    'secure'          : 0x0,
    'word_count'      : 0x1,
    'size'            : 0x20,
    'reset_val'       : 0x0,
    'array'           : False,
    'reset_mask'      : 0x000000ff,
    'sw_default_val'  : 0x0,
    'sw_default_mask' : 0x000000ff,
    'read_mask'       : 0x000000ff,
    'write_mask'      : 0x000000ff,
    'DQVREF_MR14' : {
        'lsb'               : 0,
        'msb'               : 7,
        'size'              : 8,
        'field'             : (0xff << 0),
        'woffset'           : 0x0,
        'default'           : 0x0,
        'sw_default'        : 0x0,
        'parity_protection' : 1,
        'action'            : 'rw',
        'enums' : {
        },
    },    
    # Fields sorted in order of declaration in register
    'field_list' : [
        'DQVREF_MR14',
    ],
} # End of register: R0_DRAM_MR14

registers['R0']['register_list'].append('DRAM_MR14')

# R0_DRAM_MR15
if 'R0' not in registers:
    registers['R0'] = {}
    registers['R0']['register_list']  = []

registers['R0']['DRAM_MR15'] = {
    'addr'            : 0x00,
    'secure'          : 0x0,
    'word_count'      : 0x1,
    'size'            : 0x20,
    'reset_val'       : 0x0,
    'array'           : False,
    'reset_mask'      : 0x000000ff,
    'sw_default_val'  : 0x0,
    'sw_default_mask' : 0x000000ff,
    'read_mask'       : 0x000000ff,
    'write_mask'      : 0x000000ff,
    'DQVREF_MR15' : {
        'lsb'               : 0,
        'msb'               : 7,
        'size'              : 8,
        'field'             : (0xff << 0),
        'woffset'           : 0x0,
        'default'           : 0x0,
        'sw_default'        : 0x0,
        'parity_protection' : 1,
        'action'            : 'rw',
        'enums' : {
        },
    },    
    # Fields sorted in order of declaration in register
    'field_list' : [
        'DQVREF_MR15',
    ],
} # End of register: R0_DRAM_MR14

registers['R0']['register_list'].append('DRAM_MR15')