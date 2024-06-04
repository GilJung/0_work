#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 15 18:11:24 2018

@author: christophers
"""
#import fileinput
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from config import processor_register
from shutil import copyfile
import re
import tempfile
import importlib
import os
import configT234

class Field_Info:
    ''' Stores value and information of a single field
    
    Parameters:
        value: integer representation of value for field
        bits: Number of bits the field is allocated in register value
        two: Boolean if value is in two's complement or not
        lsb: Location of lsb in register value
    '''
    def __init__(self, value, bits, two, lsb, counter = None):
        self.value = value
        self.bits = bits
        self.two = two
        self.lsb = lsb
        self.counter = counter
    
    def set_counter(self, counter):
        self.remove_counter()
        self.counter = counter
        
    def remove_counter(self):
        if self.counter is not None:
            del self.counter
        self.counter = None

class Counter:
    ''' Creates GUI of counter buttons and stores the new value for corresponding field
    
        value:  counter's value
        total:  new value
    '''
    def __init__(self, counter_frame, total_frame, field):
        self.decrement_button = ttk.Button(counter_frame, text="-", command=self.decrement, width=3)
        self.decrement_button.grid(row = 0, column = 0)
        self.increment_button = ttk.Button(counter_frame, text="+", command=self.increment, width=3)
        self.increment_button.grid(row = 0, column = 2)
        self.value = IntVar()
        self.counter_field = ttk.Entry(counter_frame, width = 3, textvariable = self.value)
        self.counter_field.grid(row = 0, column = 1)
        self.counter_field.state(['readonly'])
        self.total = StringVar()
        self.total_field = ttk.Entry(total_frame, width = 6, textvariable = self.total)
        self.total_field.state(['readonly'])
        self.total_field.grid(row = 0, column = 0)
        self.total.set(hex(field.value))

    def decrement(self):
        self.value.set(self.value.get() - 1)
        self.total.set(hex(int(self.total.get(), 16) - 1))

    def increment(self):
        self.value.set(self.value.get() + 1)
        self.total.set(hex(int(self.total.get(), 16) + 1))
        
    def get_value(self):
        return self.value.get()
    
    def reset_value(self):
        self.value.set(0)

    def get_change(self):
        return int(self.total.get(), 16)
        
class Two_Counter(Counter):
    ''' Similar to Counter class but increment and decrement rules are different
        due to representation in two's complement
        
        self.bits:      Number of bits the field has
        self.bin_value: binary value of the new number
                        cannot use self.total because total needs to store the two's complement
                        form of the new value in binary as a string
    '''
    def __init__(self, counter_frame, total_frame, field):
        super().__init__(counter_frame, total_frame, field)
        self.bits = field.bits
        self.bin_value = twos_complement_value(field.value, self.bits)
                
    def increment(self):
        self.bin_value += 1
        if within_bounds(self.bin_value, self.bits, True):
            if self.bin_value < 0:
                self.total.set(hex(twos_complement(self.bin_value, self.bits)))
            else:
                self.total.set(hex(self.bin_value))
        else:
            self.total.set("N/A")
        self.value.set(self.value.get() + 1)
        
    def decrement(self):
        self.bin_value -= 1
        if within_bounds(self.bin_value, self.bits, True):
            if self.bin_value < 0:
                self.total.set(hex(twos_complement(self.bin_value, self.bits)))
            else:
                self.total.set(hex(self.bin_value))
        else:
            self.total.set("N/A")
        self.value.set(self.value.get() - 1)
        
    def get_change(self):
        return self.bin_value
        

class Group_Counter:
    ''' Class that stores a list of Counter objects and can change them all at once
    '''
    def __init__(self, master, step_size):
        self.decrement_button = ttk.Button(master, text="-", command=self.decrement, width=3)
        self.decrement_button.grid(row = 0, column = 0)
        self.increment_button = ttk.Button(master, text="+", command=self.increment, width=3)
        self.increment_button.grid(row = 0, column = 2)
        self.counters = list()
        self.step = step_size
    
    def add(self, counter):
        self.counters.append(counter)
        
    def decrement(self):
        for counter in self.counters:
            for times in range(self.step):
                counter.decrement()

    def increment(self):
        for counter in self.counters:
            for times in range(self.step):
                counter.increment()

class VREF_Counter(Group_Counter):
    ''' Special group counter because VREF registers have a sign field
    '''
    def __init__(self, master, step):
        super().__init__(master, step)
        self.sign = list()
        self.size = 0
        
    def add(self, counter):
        if (self.size % 2) == 0:
            self.sign.append(counter)
        else:
            self.counters.append(counter)
        self.size += 1
        
    def decrement(self):
        for sign, counter in zip(self.sign, self.counters):
            for times in range(self.step):
                current_sign = sign.get_change()
                current_total = counter.get_change()
                if current_sign == 1:
                    counter.increment()
                elif current_total == 0:
                    sign.increment()
                    counter.increment()
                else:
                    counter.decrement()

    def increment(self):
        for sign, counter in zip(self.sign, self.counters):
            for times in range(self.step):
                current_sign = sign.get_change()
                current_total = counter.get_change()
                if (current_sign == 1) & (current_total == 1):
                    sign.decrement()
                    counter.decrement()
                elif current_sign == 1:
                    counter.decrement()
                else:
                    counter.increment()

class GUI:
    ''' Displays the GUI and handles all the actions
    '''
    def __init__(self, master):
        self.data = Data()
        self.inputfilepath = None
        self.inputfile = None
        self.current_axis = None
        self.current_frequency = None

        # DVFS table selection
        self.frame_file = ttk.Frame(master)
        self.frame_file.grid(row = 0, column = 0, padx = (20, 20), pady= (10,5))
        ttk.Label(self.frame_file, text = "Select DVFS Table text file:").grid(row = 0, column = 0, sticky = W)

        self.entry = ttk.Entry(self.frame_file, width = 120)
        self.entry.grid(row = 1, column = 0)
        self.entry.state(['disabled'])
        
        self.browse = ttk.Button(self.frame_file, text="Browse", command=self.browse_file, width=10)
        self.browse.grid(row = 1, column = 1)
        
        self.load_file = ttk.Button(self.frame_file, text="Load", command=self.load_file, width=10)
        self.load_file.grid(row = 1, column = 2)
        
        # Other files
        self.frame_additional = ttk.Frame(master)
        self.frame_additional.grid(row = 1, column = 0, padx = (20,20), sticky = W)
        ttk.Label(self.frame_additional, text = "Derated:").grid(row = 0, column = 0, sticky = W)
        ttk.Label(self.frame_additional, text = "Cfg:").grid(row = 1, column = 0, sticky = W)
        
        self.entry_derated = ttk.Entry(self.frame_additional, width = 120)
        self.entry_derated.grid(row = 0, column = 1)
        self.entry_derated.state(['readonly'])
        self.deratedpath = ""
        self.browse_derated = ttk.Button(self.frame_additional, text="...", command=self.select_derated, width=3)
        self.browse_derated.grid(row = 0, column = 2)
        
        self.entry_cfg = ttk.Entry(self.frame_additional, width = 120)
        self.entry_cfg.grid(row = 1, column = 1)
        self.entry_cfg.state(['readonly'])
        self.cfgpath = ""
        self.browse_cfg = ttk.Button(self.frame_additional, text="...", command=self.select_cfg, width=3)
        self.browse_cfg.grid(row = 1, column = 2)
        
        # bus width drop-down selection
        self.frame_bits = ttk.Frame(master)
        self.frame_bits.grid(row = 2, column = 0)
        ttk.Label(self.frame_bits, text = "Select bus width:").grid(row = 0, column = 0, sticky = W)
        self.bits = StringVar()
        self.bits_menu = ttk.Combobox(self.frame_bits, textvariable = self.bits)
        self.bits_menu.grid(row = 1, column = 0)
        self.bits_menu.configure(state = 'disabled')
        self.bits_menu.bind("<<ComboboxSelected>>", self.bits_selected)
        
        # frequency drop-down selection
        self.frame_frequency = ttk.Frame(master)
        self.frame_frequency.grid(row = 3, column = 0)
        ttk.Label(self.frame_frequency, text = "Select frequency:").grid(row = 0, column = 0, sticky = W)
        self.frequency = StringVar()
        self.frequency_menu = ttk.Combobox( self.frame_frequency, textvariable = self.frequency)
        self.frequency_menu.grid(row = 1, column = 0)
        self.frequency_menu.configure(state = 'disabled')
        self.frequency_menu.bind("<<ComboboxSelected>>", self.frequency_selected)

        # axis drop-down selection
        self.frame_axis_select = ttk.Frame(master)
        self.frame_axis_select.grid(row = 4, column = 0, padx = (20,20))
        ttk.Label(self.frame_axis_select, text = "Select axis:").grid(row = 0, column = 0, sticky = W)
        self.axis = StringVar()
        self.axis_menu = ttk.Combobox(self.frame_axis_select, textvariable = self.axis)
        self.axis_menu.grid(row = 1, column = 0)
        self.axis_menu.configure(state = 'disabled')
        self.axis_menu.bind("<<ComboboxSelected>>", self.axis_selected)
        # Frame for displayed registers
        self.canvas_frame = ttk.Frame(master, width = 1000, height = 1000)
        self.canvas_frame.grid(row = 5, column = 0, sticky = "wens", fill = None)
        self.canvas_values = Canvas(self.canvas_frame, width = 1000, height = 500)
        self.canvas_values.pack(side = LEFT, fill = BOTH, expand = TRUE)
        self.frame_values = ttk.Frame(self.canvas_values)
        self.canvas_values.create_window(0, 0, window = self.frame_values, anchor = NW)
        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self.canvas_frame, orient = VERTICAL, command = self.canvas_values.yview)
        self.scrollbar.pack(side = RIGHT, fill = Y)
        self.canvas_values.config(yscrollcommand = self.scrollbar.set)
        self.frame_values.bind("<Configure>", self.frame_width)
        
        # Error box
        self.error = ttk.Entry(master, width = 143)
        self.error.grid(row = 9, column = 0, sticky = W, padx = (20,20), pady = (20,20))
        self.error.state(['disabled'])
        
        # Apply button
        self.save =  ttk.Button(master, text="Apply", command=self.save_changes, width=10)
        self.save.grid(row = 6, column = 0)

        # Addendum
        self.frame_addendum = ttk.Frame(master)
        self.frame_addendum.grid(row = 7, column = 0, sticky = W)
        ttk.Label(self.frame_addendum, text = "File name addendum:").grid(row = 0, column = 0, padx = (20,5), pady = (5,5), sticky = W)

        self.entry_addendum = ttk.Entry(self.frame_addendum, width = 30)
        self.entry_addendum.grid(row = 0, column = 1)
        
        self.checkbutton_overwrite = ttk.Checkbutton(self.frame_addendum, text = "Overwrite?")
        self.checkbutton_overwrite.grid(row = 0, column = 2, padx = (10, 0))
        self.overwrite = BooleanVar()
        self.checkbutton_overwrite.config(variable = self.overwrite, onvalue = True, offvalue = False, command = self.select_overwrite)
        
        # Export file
        self.frame_export = ttk.Frame(master)
        self.frame_export.grid(row = 8, column = 0)
        ttk.Label(self.frame_export, text = "Select export file location:").grid(row = 0, column = 0, sticky = W)

        self.entry_export = ttk.Entry(self.frame_export, width = 117)
        self.entry_export.grid(row = 1, column = 0)
        self.entry_export.state(['disabled'])
        
        self.exportpath = ""
        self.browse_export = ttk.Button(self.frame_export, text="Select Folder", command=self.select_export, width=13)
        self.browse_export.grid(row = 1, column = 1)
        
        self.export_file = ttk.Button(self.frame_export, text="Export", command=self.export_file, width=10)
        self.export_file.grid(row = 1, column = 2)
        
    def browse_file(self):
        self.inputfilepath = filedialog.askopenfilename(filetypes = (("Text files", "*.txt") , ("All files", "*.*")))
        self.entry.configure(state = 'normal')
        self.entry.delete(0, END)
        self.entry.insert(0, self.inputfilepath)
        self.entry.state(['readonly'])
        error_message(self.error, "")
        
    def load_file(self):
        if self.inputfilepath == "" or self.inputfilepath is None:
            error_message(self.error, "ERROR: No input file selected")
            return
        self.current_frequency = None
        self.current_axis = None
        self.clear_canvas()
        self.data.parse_file(self.inputfilepath, self.error)
        self.inputfile = self.inputfilepath
        self.bits_menu.set("")
        self.bits_menu.configure(state = 'readonly')
        self.bits_menu.config(values = [bits for bits in channel_select])
        self.frequency_menu.set("")
        self.frequency_menu.configure(state = 'disabled')
        self.axis_menu.set("")
        self.axis_menu.configure(state = 'disabled')
        
    def select_export(self):
        if self.overwrite.get() is True:
            error_message(self.error, "ERROR: Overwrite option selected")
        else:
            self.exportpath = filedialog.askdirectory()
            self.entry_export.configure(state = 'normal')
            self.entry_export.delete(0, END)
            self.entry_export.insert(0, self.exportpath)
            self.entry_export.state(['readonly'])
    
    def select_derated(self):
        self.deratedpath = filedialog.askopenfilename(filetypes = (("Text files", "*.txt") , ("All files", "*.*")))
        self.entry_derated.configure(state = 'normal')
        self.entry_derated.delete(0, END)
        self.entry_derated.insert(0, self.deratedpath)
        self.entry_derated.state(['readonly'])

    def select_cfg(self):
        self.cfgpath = filedialog.askopenfilename(filetypes = (("Configuration files", "*.cfg") , ("All files", "*.*")))
        self.entry_cfg.configure(state = 'normal')
        self.entry_cfg.delete(0, END)
        self.entry_cfg.insert(0, self.cfgpath)
        self.entry_cfg.state(['readonly'])
        
    def select_overwrite(self):
        if self.overwrite.get() is True:
            self.entry_addendum.delete(0, END)
            self.entry_addendum.state(['disabled'])
        else:
            self.entry_addendum.configure(state = 'normal')
    
    def export_file(self):
        if not self.overwrite.get() and not self.entry_addendum.get():
            if not self.exportpath:
                error_message(self.error, "ERROR: Addendum required if not overwriting original file")
                return
            else:
                pass
        if self.current_frequency and self.current_axis:
            self.save_changes()
            error_message(self.error, "Exporting...")
            self.data.clear(self.current_frequency, self.current_axis)
            self.data.export(self.inputfile, self.exportpath, self.deratedpath, self.cfgpath, self.entry_addendum.get(), self.error)
            self.data.display(self.frame_values, self.current_frequency, self.current_axis, self.current_bits, self.error)
        else:
            error_message(self.error, "ERROR: Select frequency/axis before exporting")
    
    def frame_width(self, event):
        self.canvas_values.configure(scrollregion = self.canvas_values.bbox("all"))
        
    def bits_selected(self, event):
        self.clear_canvas()
        self.frequency_menu.set("")
        self.frequency_menu.configure(state = 'readonly')
        self.frequency_menu.config(values = self.data.frequencies)
        self.axis_menu.set("")
        self.axis_menu.configure(state = 'disabled')
        self.current_bits = self.bits.get()
        self.current_frequency = None
        self.current_axis = None
        
    def frequency_selected(self, event):
        self.clear_canvas()
        self.axis_menu.configure(state = 'readonly')
        self.axis_menu.config(values = axes)
        self.axis_menu.set("")
        self.current_frequency = self.frequency.get()
        self.current_axis = None
            
    def axis_selected(self, event):
        self.clear_canvas()
        self.current_axis = self.axis.get()
        self.data.display(self.frame_values, self.current_frequency, self.current_axis, self.current_bits, self.error)

    def save_changes(self):
        if self.data.can_apply(self.current_frequency, self.current_axis, self.error):
            error_message(self.error, "")
            self.data.apply(self.current_frequency, self.current_axis)
            self.clear_canvas()
            self.data.display(self.frame_values, self.current_frequency, self.current_axis, self.current_bits, self.error)

    
    def clear_canvas(self):
        if self.current_axis:
            self.data.clear(self.current_frequency, self.current_axis)
        error_message(self.error, "")
        self.frame_values.destroy()
        self.canvas_values.delete("all")
        self.frame_values = ttk.Frame(self.canvas_values)
        self.canvas_values.create_window(0, 0, window = self.frame_values, anchor = NW)
        self.frame_values.bind("<Configure>", self.frame_width)
        self.canvas_values.yview_moveto(0)
        
class Data:
    ''' Contains the parsed information from DVFS table
        self.data:              dicts with parsed information from DVFS table in the order of frequency, register, then value
        self.display_registers: dicts with tree of frequency, register, axis, channel, register, field, field info/value
                                for registers in config file that tool will display in GUI
        self.cfg_dict:          dict with key as register name in cfg, and value as tuple of axis, channel, and register
                                the corresponding DVFS register can be found at in the display_registers dict
        self.training:          dict with frequency and axis keys which stores a boolean depicting whether the axis uses training 
                                registers instead for that frequency
        self.bypass:            dict with frequency and axis keys which stores whether the axis has PI Bypass enabled or not
                                which will increase the step size to 8 for field values
        self.register_mask:     dict with DVFS register name as key, and bitmask for bits that should not be changed/touched as value        
        self.frequencies:       list of frequencies found in DVFS table
    '''
    def __init__(self):
        self.data = dict()
        self.display_registers = dict()
        self.cfg_dict = dict()
        self.training = dict()
        self.bypass = dict()
        self.register_mask = dict()
        self.frequencies = list()

    def parse_file(self, inputfilepath, error):
        dictionary = dict()
        self.data.clear()
        self.display_registers.clear()
        self.cfg_dict.clear()
        self.training.clear()
        self.frequencies.clear()
        self.register_mask.clear()
        self.bypass.clear()
        
        with open(inputfilepath, 'rt') as in_file:
            for line in in_file:
                line_list = line.split(',')
                if len(line_list) > 1:
                    value = line_list[0].lstrip()
                    register = line_list[1]
                    if not register.isspace():
                        register = register.strip('/* \n')
                        dictionary[register] = value
                        if register == "PLLHUB_ENABLE_FREQ_CHANGE":    # register near end of table
                            frequency = dictionary["SDRAM frequency khz"]
                            self.frequencies.append(frequency)
                            self.data[frequency] = dict(dictionary)
                            dictionary.clear()
        try:
            frequency = self.frequencies[0]
        except IndexError:
            error_message(error, "ERROR: Invalid file")
            return
        
        # checks if unique register in config list for each processor exists
        for tegra, register in processor_register.items():
            try:
                self.data[frequency][register]
            except KeyError:
                pass
            else:
                processor = tegra
                error_message(error, "Parsed " + tegra + " DVFS Table")
        for frequency in self.data:
            # checks which frequency for these axes needs training
            dictionary = self.data[frequency]
            self.training[frequency] = dict()
            needs_training = dictionary["needs_training"]
            write_byte_training = separate_bits(4, 4, needs_training)
            write_vref_training = separate_bits(5, 5, needs_training)
            read_byte_training = separate_bits(6, 6, needs_training)
            read_vref_training = separate_bits(7, 7, needs_training)
            write_leveling = separate_bits(10, 10, needs_training)
            self.training[frequency]["OBDQ"] = True if write_byte_training else False
            self.training[frequency]["DQVREF"] = True if write_vref_training else False
            self.training[frequency]["RDQS"] = True if read_byte_training else False
            self.training[frequency]["DQIVREF"] = True if read_vref_training else False
            self.training[frequency]["WCKDQ"] = True if write_leveling else False
            # checks which frequency for these axes has PI_BYPASS enabled so step size will be 8 instead
            self.bypass[frequency] = dict()
            needs_bypass = dictionary["EMC_PMACRO_DDLL_BYPASS_0"]
            
            #if processor != "T186":
            OBCLK_bypass = separate_bits(25, 25, needs_bypass)
            OBCMD1t_bypass = separate_bits(24, 24, needs_bypass)
            WCKDQ_bypass = separate_bits(19, 19, needs_bypass)
            RDQS_bypass = separate_bits(10, 10, needs_bypass)
            OBDQS_bypass = separate_bits(9, 9, needs_bypass)
            OBDQ_bypass = separate_bits(8, 8, needs_bypass)

            #else:                
            #    OBCLK_bypass = separate_bits(17, 17, needs_bypass)
            #    OBCMD1t_bypass = separate_bits(16, 16, needs_bypass)
            #    RDQS_bypass = separate_bits(2, 2, needs_bypass)
            #    OBDQS_bypass = separate_bits(1, 1, needs_bypass)
            #    OBDQ_bypass = separate_bits(0, 0, needs_bypass)
            self.bypass[frequency]["OBCLK"] = True if OBCLK_bypass else False
            self.bypass[frequency]["OBCMD1t"] = True if OBCMD1t_bypass else False
            self.bypass[frequency]["WCKDQ"] = True if WCKDQ_bypass else False
            self.bypass[frequency]["RDQS"] = True if RDQS_bypass else False
            self.bypass[frequency]["OBDQS"] = True if OBDQS_bypass else False
            self.bypass[frequency]["OBDQ"] = True if OBDQ_bypass else False
            
#        imports config file and aremc contents
        config_file = "config" + processor
        try:
            my_module = importlib.__import__(config_file, globals(), locals(), [], 0)
        except ModuleNotFoundError:
            error_message(error, "ERROR: " + config_file + " not supported")
            return
        module_dict = my_module.__dict__
        try:
            to_import = my_module.__all__
        except AttributeError:
            to_import = [name for name in module_dict if not name.startswith('_')]
        globals().update({name: module_dict[name] for name in to_import})

#       filters through list of registers for ones we want to display/edit
        for frequency in self.frequencies:
            self.display_registers[frequency] = dict()
            bit_partition(self.data[frequency], self.cfg_dict, self.display_registers[frequency], self.register_mask)
        self.data.clear()
                            
    def display(self, frame_values, frequency, axis, bits, error):
        ''' Displays the registers, fields, and value of the axis selected
        '''
        ttk.Label(frame_values, text = "Channel").grid(row = 0, column = 0, padx = (20,20))
        ttk.Label(frame_values, text = "Register").grid(row = 0, column = 1)
        ttk.Label(frame_values, text = "Field").grid(row = 0, column = 2)
        ttk.Label(frame_values, text = "Value").grid(row = 0, column = 3)
        frame = ttk.Frame(frame_values)
        frame.grid(row = 0, column = 4)
        ttk.Label(frame_values, text = "Change").grid(row = 0, column = 5)
        step = 1
        if axis in self.bypass[frequency]:
            if self.bypass[frequency][axis]:
                step = 8

        row = 1
        if axis == "CMDVREF":
            select = ((0, 1), 2)
        if axis in self.training[frequency]:
            if self.training[frequency][axis]:
                axis = axis + " (training)"
                step = 1
        if axis in counter_specific_fields:
            select = counter_specific_fields[axis]
        elif axis == "AutocaloffsetDQTerm":
            select = ((2,), 4)
            axis = "AutocaloffsetDQ/STerm"
        elif axis == "AutocaloffsetDQSTerm":
            select = ((0,), 4)
            axis = "AutocaloffsetDQ/STerm"
        else:
            select = ((0,), 1)
        if (axis == "DQIVREF (training)") | (axis == "DQVREF (training)"):
            group = VREF_Counter(frame, step)
        else:
            group = Group_Counter(frame, step)
        if axis not in self.display_registers[frequency]:
            error_message(error,"ERROR: Axis may be unnecessary for selected frequency")
            return

        for channel in self.display_registers[frequency][axis]:
            if channel in channel_select[bits]:
                ttk.Label(frame_values, text = channel).grid(row = row, column = 0)
                for register in self.display_registers[frequency][axis][channel]:
                    ttk.Label(frame_values, text = register).grid(row = row, column = 1, padx = (5,5))
                    index = 0
                    for field, field_info in sorted(self.display_registers[frequency][axis][channel][register].items()):
                        if index % select[1] in select[0]:
                            ttk.Label(frame_values, text = field).grid(row = row, column = 2, padx = (20,20))
                            ttk.Label(frame_values, text = f"{field_info.value:#x}").grid(row = row, column = 3)
                            frame = ttk.Frame(frame_values)
                            frame.grid(row = row, column = 4)
                            total_frame = ttk.Frame(frame_values)
                            total_frame.grid(row = row, column = 5)
                            if field_info.two:
                                counter = Two_Counter(frame, total_frame, field_info)
                            else:
                                counter = Counter(frame, total_frame, field_info)
                            group.add(counter)
                            self.display_registers[frequency][axis][channel][register][field].set_counter(counter)
                            row += 1
                        index += 1
                        
    def check_axis(self, frequency, axis):
        if axis in self.training[frequency]:
            if self.training[frequency][axis]:
                axis = axis + " (training)"
        elif (axis == "AutocaloffsetDQTerm") | (axis == "AutocaloffsetDQSTerm"):
            axis = "AutocaloffsetDQ/STerm"
        return axis
                
    def can_apply(self, frequency, axis, error):
        ''' Checks if the intended modification of all values are within bounds
            of field's bit length
            Parameters:
                error: tkinter entry to display messages on
        '''
        axis = self.check_axis(frequency, axis)
        try:
            self.display_registers[frequency][axis]
        except KeyError:
            return 
        for channel in self.display_registers[frequency][axis]:
            for register in self.display_registers[frequency][axis][channel]: 
                for field, field_info in self.display_registers[frequency][axis][channel][register].items():
                    if field_info.counter is not None:
                        bits = field_info.bits
                        two = field_info.two
                        new_value = field_info.counter.get_change()
                        if within_bounds(new_value, bits, two) == False:
                            error_message(error, f"ERROR: Out of bounds, {bits:d}-bit number for {field}")
                            return False
        return True
                    
    def apply(self, frequency, axis):
        ''' Applies the changes to the values
        '''
        axis = self.check_axis(frequency, axis)
        for channel in self.display_registers[frequency][axis]:
            for register in self.display_registers[frequency][axis][channel]: 
                for field, field_info in self.display_registers[frequency][axis][channel][register].items():
                    if field_info.counter is not None:
                        new_value = field_info.counter.get_change()
                        field_info.counter.reset_value()
                        new_value = twos_complement(new_value, field_info.bits)
                        self.display_registers[frequency][axis][channel][register][field].value = new_value
                        self.display_registers[frequency][axis][channel][register][field].remove_counter()

    def clear(self, frequency, axis):
        ''' Clears the counter values
        '''
        axis = self.check_axis(frequency, axis)
        if axis not in self.display_registers[frequency]:
            return
        for channel in self.display_registers[frequency][axis]:
            for register in self.display_registers[frequency][axis][channel]: 
                for field, field_info in self.display_registers[frequency][axis][channel][register].items():
                    if field_info.counter is not None:
                        self.display_registers[frequency][axis][channel][register][field].remove_counter()
                
    def export(self, inputfilepath, outputfilepath, deratedfile, cfgfile, addendum, error, selected_frequency):
        ''' Prints new DVFS file with modifications
            Parameters:
                inputfilepath: path to DVFS table text file
                outputfilepath: path to output directory otherwise empty string
                deratedfile: path to derated file
                cfgfile: path to cfg file
                addendum: string to attach at end of original file name for new table
                error: tkinter entry to display messages on
        '''
        self.export_dvfs_file(inputfilepath, inputfilepath, outputfilepath, addendum, error)
        
        exported = True
        if deratedfile:
            exported = self.export_dvfs_file(deratedfile, inputfilepath, outputfilepath, addendum, error)

        if cfgfile:
            cfgpath = ""
            if not outputfilepath:
                cfgname = cfgfile.rsplit(".", 1)[0]
                cfgpath = cfgname + addendum + ".cfg"
            else:
                cfgname = cfgfile.rsplit("/", 1)[1].rsplit(".", 1)[0]
                cfgpath = outputfilepath + "/" + cfgname + addendum + ".cfg"
            with open(cfgfile, 'rt') as in_file:
                with tempfile.TemporaryFile(mode='wt+', delete=False) as out_file:
                    frequency = "665600"
                    for comment in in_file:
                        # checks for cfg frequency, defaulted to 204 Mhz
                        out_file.write(comment)
                        if comment.startswith("# "):
                            match = re.match(r"# Parameter file: .+\(([\d,.]+) MHz\)", comment)
                            if match:
                                frequency = str(int(float(match.group(1)) * 1000))
                                break
                        else:
                            print("Cfg frequency not matched")
                            break
                            
                  # try to update when frequency is 665.6Mhz 
                    if frequency == "665600" and self.frequency == "665600":
                        for line in in_file:
                            if line.startswith("SDRAM") or line.startswith("#@ EMC_MRW"):
                                mrw = False
                                if line.startswith("SDRAM"):
                                    line_list = line.rsplit('=', 1)
                                    value = line_list[1].strip(' ;\n')
                                    register_name = line_list[0].lstrip('SDRAM[0]. ')
                                    register_name = register_name.rstrip()
                                    if register_name.startswith("EmcMrw")or register_name.startswitch("EmcWarmBootMrwExtra"):
                                        # checks register address (MA)
                                        if separate_bits(23, 16, value) == 0xe:
                                            axis = "DQVREF"
                                            channel = '0'
                                            register_name = "EMC_MRW15_0"
                                            mrw = True
                                        elif separate_bits(23, 16, value) == 0xc:
                                            axis = "CMDVREF"
                                            channel = '0'
                                            register_name = "R0_DRAM_MR12"
                                            mrw = True
                                '''            
                                elif line.startswith("#@ EMC_MRW"):
                                    line_list = line.rsplit('=', 1)
                                    value = line_list[1].strip(' ;\n')
                                    register_name = line_list[0].rsplit('{', 1)[0]
                                    register_name = register_name.lstrip('#@ ')
                                    register_name = register_name.rstrip()
                                    if separate_bits(23, 16, value) == 0xe:
                                        axis = "DQVREF"
                                        channel = '0'
                                        register_name = "EMC_MRW15_0"
                                        mrw = True
                                    elif separate_bits(23, 16, value) == 0xc:
                                        axis = "CMDVREF"
                                        channel = '0'
                                        register_name = "R0_DRAM_MR12"
                                        mrw = True
                                    '''    
                                if register_name in self.cfg_dict:
                                    axis, channel, register_name = self.cfg_dict[register_name]
                                    mask = self.register_mask[register_name]
                                    field_values = self.display_registers[frequency][axis][channel][register_name]
                                    new_value = edit(field_values, value, mask)
                                    line = line.replace(value, f"{new_value:#0{10}x}")
                                elif mrw:
                                    mask = 0xffff0000  # remove DEV_SELECTN
                                    field_values = self.display_registers[frequency][axis][channel][register_name]
                                    new_value = edit(field_values, value, mask)
                                    line = line.replace(value, f"{new_value:#0{10}x}")
                            out_file.write(line)
                        copyfile(out_file.name, cfgpath)
                        os.remove(out_file.name)
                    else:
                        error_message(error, "ERROR: Frequency is not 665600, cfg file will not be updated")
                    
        if exported is True:
            error_message(error, "Export successful!")

    def export_dvfs_file(self, file, inpath, outpath, addendum, error):
        ''' Method to create new table for DVFS and derated because of text format similarity
        '''
        if not outpath:
            name = file.rsplit(".", 1)[0]
            path = name + addendum + ".txt"
        else:
            name = file.rsplit("/", 1)[1].rsplit(".", 1)[0]
            path = outpath + "/" + name + addendum + ".txt"
        with open(file, 'rt') as in_file:
            with tempfile.TemporaryFile(mode='wt+', delete=False) as out_file:
                for line in in_file:
                    line_list = line.split(',')
                    if len(line_list) > 1:
                        value = line_list[0].lstrip()
                        register_name = line_list[1]
                        if not register_name.isspace():
                            register_name = register_name.strip('/* \n')
                            if register_name == "SDRAM frequency khz":
                                frequency = value
                                if frequency not in self.display_registers:
                                    print(f"{frequency}Hz in derated not found in DVFS table")
                                    return False
                            register_name = register_name.split("-", 1)[0]  # removes appended info
                            register_name = register_name.split(";", 1)[0]  # removes appended info
                            register_name = register_name.rstrip("; ")
                            if register_name.startswith("R0"):
                                for axis in self.display_registers[frequency]:
                                    for channel in self.display_registers[frequency][axis]:
                                        if register_name in self.display_registers[frequency][axis][channel]:
                                            mask = self.register_mask[register_name]
                                            new_value = edit(self.display_registers[frequency][axis][channel][register_name], value, mask)
                                            line = line.replace(value, f"{new_value:#0{10}x}")
                            elif register_name.startswith("EMC"):
                                for axis in self.display_registers[frequency]:
                                    for channel in self.display_registers[frequency][axis]:
                                        if register_name in self.display_registers[frequency][axis][channel]:
                                            mask = self.register_mask[register_name]
                                            new_value = edit(self.display_registers[frequency][axis][channel][register_name], value, mask)
                                            line = line.replace(value, f"{new_value:#0{10}x}")
                    out_file.write(line)
            copyfile(out_file.name, path)
            os.remove(out_file.name)
        return True

def bit_partition(dictionary, cfg_dict, display_registers, register_mask):
    ''' uses registers_to_display list in config file to parse DVFS table into dictionaries
    '''
    
    for register, aremc_name, cfg_name, axis, twos_complement in registers_to_display:
        partition_register(dictionary, cfg_dict, display_registers, register_mask, register, aremc_name, cfg_name, axis, twos_complement)

    
def partition_register(dictionary, cfg_dict, display_registers, register_mask, register, aremc_name, cfg_name, axis, two):
    ''' Finds registers that start with register variable name and stores into
        dictionary using information from aremc file
        
        Parameters:
            dictionary:         Dictionary of registers and their values for a single frequency
            display_registers:  Dictionary of already parsed values stored in through axis, channel, register
            register_mask:      Dictionary to store mask for each register
            register:           Register name in DVFS table
            aremc_name:         Register name in aremc file
            cfg_name:           Register name in cfg file
            axis:               Axis the register belongs to
            two:                Boolean for whether value is in two's complement representation
    '''  
    matched_registers = {k:v for k, v in dictionary.items() if re.match(register, k)}
    #print(matched_registers)
    ##print(dictionary)
    ## matched_registers = {k:v for k, v in dict_item if re.match(register, k)}

    bits = dict()
    if axis not in display_registers:
        display_registers[axis] = dict()

    for specific_register, register_value in matched_registers.items():
        bits.clear()
           
        specific_register = specific_register.split("-", 1)[0] # removes appended info
        specific_register = specific_register.split(";", 1)[0] # removes appended info
        specific_register = specific_register.rstrip("; ")
        
#        uses groups from DVFS table name to generate cfg and aremc name
        register_name = re.sub(register, aremc_name, specific_register)
        cfg = re.sub(register, cfg_name, specific_register)

#        checks for channel group
        channel = re.match(register, specific_register)
        try:
            channel.group('CH')
        except IndexError:
            channel_display = ""
        else:
            channel_display =  channel.group('CH')
        if channel_display not in display_registers[axis]:
            display_registers[axis][channel_display] = dict()
        #       stores key info in cfg dict for easier lookup when retrieving corresponding register value in DVFS
        cfg_dict[cfg] = (axis, channel_display, specific_register)

        if specific_register == 'R0_DRAM_MR12':
            if specific_register not in display_registers[axis][channel_display]:        
                register_mask[specific_register] = 0xFFFFFFFF - registers['R0'][register_name]['write_mask']
                display_registers[axis][channel_display][specific_register] = dict()    

            for field in registers['R0'][register_name]['field_list']:
                num_bits = registers['R0'][register_name][field]['size']
                bit_location = registers['R0'][register_name][field]['lsb']
                field_value = (registers['R0'][register_name][field]['field'] & int(register_value, 16)) >> bit_location
                bits[field] = Field_Info(field_value, num_bits, two, bit_location)    
        else:
            if specific_register not in display_registers[axis][channel_display]:    
                register_mask[specific_register] = 0xFFFFFFFF - registers['EMC'][register_name]['write_mask']
                display_registers[axis][channel_display][specific_register] = dict()   

            for field in registers['EMC'][register_name]['field_list']:
                num_bits = registers['EMC'][register_name][field]['size']
                bit_location = registers['EMC'][register_name][field]['lsb']
                field_value = (registers['EMC'][register_name][field]['field'] & int(register_value, 16)) >> bit_location
                bits[field] = Field_Info(field_value, num_bits, two, bit_location)
            #print(specific_register, field_value)                                 
        display_registers[axis][channel_display][specific_register].update(bits)
        
def edit(values, value, mask):
    ''' Returns the new register value after replacing the bits edited by tool
        Parameters:
            values: dict with field as key and an array as value
                    array index:
                        0: value of field
                        3: lsb of field
            value:  original value of register in DVFS
            mask:   mask for bits changed by tool
    '''
    edit_value_mask = 0xFFFFFFFF - mask
    complete = 0
    for field, field_info in values.items():
        complete = complete | (field_info.value << field_info.lsb)
    complete = complete & edit_value_mask
    value = int(value, 16) & mask
    return value | complete
                
            
def separate_bits(start, end, number):
    ''' Returns a binary number specified by its msb and lsb extracted from a larger number
        Used to extract field value from a register value
        Parameters:
            start:  msb of binary number to return
            end:    lsb of binary number to return
            number: overall number to extract specific bits from
    '''
    number = int(number, 16) >> end
    exp = start-end+1
    mask = (2**exp) - 1
    number = number & mask
    return number

def twos_complement_value(value, bits):
    ''' Returns the decimal value of a two's complement number
        Parameters:
            value: two's complement number
            bits: number of bits in number
    '''
    if (value & (1 << (bits - 1))) != 0:
        value = value - (1 << bits)
    return value

def twos_complement(value, bits):
    ''' Returns two's complement form of a decimal number
        Parameters:
            value: decimal value
            bits: number of bits
    '''
    if value < 0:
        value = bin(-value)
        value = value[2:].zfill(bits)
        value = "".join('1' if x == '0' else '0' for x in value)
        value = int(value, 2) + 1
    return value
    
def within_bounds(value, bits, two):
    ''' Returns a boolean on whether the number is within bounds of bit length
        Parameters:
            value:  decimal value
            bits:   number of bits
            two:    whether two's complement
    '''
    if two:
        min_val = -(1 << (bits - 1))
        max_val = (1 << (bits - 1)) - 1
    else:
        min_val = 0
        max_val = (1 << bits) - 1
    if (value > max_val) | (value < min_val):
        return False
    else:
        return True
    
def error_message(error, text):
    ''' Displays text in a tkinter entry
        Parameters:
            error: tkinter entry
            text: text to be displayed
    '''
    error.configure(state = 'normal')
    error.delete(0, END)
    error.insert(0, f"{text}")
    error.state(['readonly'])
    
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)
   
def main():
    root = Tk()
    root.resizable(width=False, height=False)
    ## icon_path = resource_path("icon_8OB_icon.ico")
    ## root.iconbitmap("icon_8OB_icon.ico")
    root.title("Orin DVFS Table Editor")
    GUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()