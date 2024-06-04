# -*- coding: utf-8 -*-
"""
Training-specific register configurations for T234 support

Description:
This script sets up additional training-specific registers that are not part of the aremc file.
"""
train_registers         = {}

# Training registers are not in aremc file, so added below
EMC_SAVE_RESTORE_MOD_IB = []
EMC_SAVE_RESTORE_MOD_OB = []

for byte in range(8):
    register = f"SAVE_RESTORE_MOD_IB_BYTE{byte}_VREF_OFF"
    EMC_SAVE_RESTORE_MOD_IB.append(register)
    C = byte // 2
    S = byte % 2
    register = f"SAVE_RESTORE_MOD_OB_C{C}S{S}_VREF_OFF"
    EMC_SAVE_RESTORE_MOD_OB.append(register)

# Add EMC_SAVE_RESTORE_MOD_IB_ registers if not present
if 'EMC' not in train_registers:
    train_registers['EMC'] = {'register_list': []}

for register in EMC_SAVE_RESTORE_MOD_IB:
    train_registers['EMC'][register] = {
        'addr': 0x0,
        'secure': 0x0,
        'word_count': 0x1,
        'size': 0x8,
        'reset_val': 0x0,
        'array': False,
        'reset_mask': 0x8000007f,
        'sw_default_val': 0x0,
        'sw_default_mask': 0xcfffffff,
        'read_mask': 0xcfffffff,
        'write_mask': 0xcfffffff,
        '(signed bit)': {
            'lsb': 31,
            'msb': 31,
            'size': 1,
            'field': (0x1 << 31),
            'woffset': 0x0,
            'default': 0x0,
            'sw_default': 0x0,
            'action': 'rw',
            'enums': {},
        },
        register: {
            'lsb': 0,
            'msb': 6,
            'size': 7,
            'field': (0x7f << 0),
            'woffset': 0x0,
            'default': 0x0,
            'sw_default': 0x0,
            'action': 'rw',
            'enums': {},
        },
        'field_list': [
            '(signed bit)',
            register
        ],
    }
    train_registers['EMC']['register_list'].append(register)

# Add EMC_SAVE_RESTORE_MOD_OB_ registers if not present
for register in EMC_SAVE_RESTORE_MOD_OB:
    train_registers['EMC'][register] = {
        'addr': 0x0,
        'secure': 0x0,
        'word_count': 0x1,
        'size': 0x8,
        'reset_val': 0x0,
        'array': False,
        'reset_mask': 0x800000ff,
        'sw_default_val': 0x0,
        'sw_default_mask': 0x800000ff,
        'read_mask': 0x800000ff,
        'write_mask': 0x800000ff,
        '(signed bit)': {
            'lsb': 31,
            'msb': 31,
            'size': 1,
            'field': (0x1 << 31),
            'woffset': 0x0,
            'default': 0x0,
            'sw_default': 0x0,
            'action': 'rw',
            'enums': {},
        },
        register: {
            'lsb': 0,
            'msb': 7,
            'size': 8,
            'field': (0xff << 0),
            'woffset': 0x0,
            'default': 0x0,
            'sw_default': 0x0,
            'action': 'rw',
            'enums': {},
        },
        'field_list': [
            '(signed bit)',
            register
        ],
    }
    train_registers['EMC']['register_list'].append(register)

# Add CMDVREF register for R0_DRAM_MR12
if 'R0' not in train_registers:
    train_registers['R0'] = {'register_list': []}

train_registers['R0']['DRAM_MR12'] = {
    'addr': 0x00,
    'secure': 0x0,
    'word_count': 0x1,
    'size': 0x20,
    'reset_val': 0x0,
    'array': False,
    'reset_mask': 0x000000ff,
    'sw_default_val': 0x0,
    'sw_default_mask': 0x000000ff,
    'read_mask': 0x000000ff,
    'write_mask': 0x000000ff,
    'CMDVREF_MR12': {
        'lsb': 0,
        'msb': 7,
        'size': 8,
        'field': (0xff << 0),
        'woffset': 0x0,
        'default': 0x0,
        'sw_default': 0x0,
        'parity_protection': 1,
        'action': 'rw',
        'enums': {},
    },
    'field_list': [
        'CMDVREF_MR12',
    ],
}
train_registers['R0']['register_list'].append('DRAM_MR12')

# Add CMDVREF register for R0_DRAM_MR14
train_registers['R0']['DRAM_MR14'] = {
    'addr': 0x00,
    'secure': 0x0,
    'word_count': 0x1,
    'size': 0x20,
    'reset_val': 0x0,
    'array': False,
    'reset_mask': 0x000000ff,
    'sw_default_val': 0x0,
    'sw_default_mask': 0x000000ff,
    'read_mask': 0x000000ff,
    'write_mask': 0x000000ff,
    'DQVREF_MR14': {
        'lsb': 0,
        'msb': 7,
        'size': 8,
        'field': (0xff << 0),
        'woffset': 0x0,
        'default': 0x0,
        'sw_default': 0x0,
        'parity_protection': 1,
        'action': 'rw',
        'enums': {},
    },
    'field_list': [
        'DQVREF_MR14',
    ],
}
train_registers['R0']['register_list'].append('DRAM_MR14')

# Add CMDVREF register for R0_DRAM_MR15
train_registers['R0']['DRAM_MR15'] = {
    'addr': 0x00,
    'secure': 0x0,
    'word_count': 0x1,
    'size': 0x20,
    'reset_val': 0x0,
    'array': False,
    'reset_mask': 0x000000ff,
    'sw_default_val': 0x0,
    'sw_default_mask': 0x000000ff,
    'read_mask': 0x000000ff,
    'write_mask': 0x000000ff,
    'DQVREF_MR15': {
        'lsb': 0,
        'msb': 7,
        'size': 8,
        'field': (0xff << 0),
        'woffset': 0x0,
        'default': 0x0,
        'sw_default': 0x0,
        'parity_protection': 1,
        'action': 'rw',
        'enums': {},
    },
    'field_list': [
        'DQVREF_MR15',
    ],
}
train_registers['R0']['register_list'].append('DRAM_MR15')
