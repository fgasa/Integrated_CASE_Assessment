
"""
@author: fgasa
"""

from CoolProp.CoolProp import PropsSI as SI
import numpy as np
import pandas as pd
import os


def get_fluid_FVF(surf_pressure, surf_temperatur, res_pressure, res_temperature, fluid):
    """
    Calculate the gas formation volume factor (pressure (double) in bar,formation temperature (double) in [K]
    return: gasFVF in Rm3/Sm3
    """
    std_Zfactor = 1
    res_Zfactor = SI('Z', 'P', res_pressure, 'T', res_temperature, fluid)

    fluid_FVF = (surf_pressure * res_temperature * res_Zfactor) / (res_pressure * surf_temperatur * std_Zfactor)

    return fluid_FVF

def get_fluid_PVTx(surf_pressure,surf_temperatur, res_temperature, fluid):

    pressure_range = np.arange(10, 202, 2)
    pressure_range = pressure_range*1e5 #in Pa for CoolProp

    temperature_range = pressure_range*0 + res_temperature

    pressure_stp = pressure_range*0 + surf_pressure
    temperature_stp = pressure_range*0 + surf_temperatur

    #fluid_Zfactor = SI('Z', 'P', pressure_range, 'T', temperature_range, fluid)
    #fluid_density = SI('D', 'P', pressure_range, 'T', temperature_range, fluid)
    fluid_viscosity = SI('V', 'P', pressure_range, 'T', temperature_range, fluid) * 1e3 # in cP
    fluid_FVF = get_fluid_FVF(pressure_stp, temperature_stp, pressure_range, temperature_range, fluid)

    print('-- MSG: Fluid density at ', pressure_stp[0]/1e5,'[bar] ', temperature_stp[0],'[K]')
    print('-- Density: ', SI('D', 'P', pressure_stp[0], 'T', temperature_stp[0], fluid), ' [kg/m3]')

    print('-----------------------------------------')
    print('-- STP condition: Ps[bar], Ts [K] ', pressure_stp[0]/1e5, temperature_stp[0])
    print('-- Pressure [bar], BG [-], viscosity [cP] ')
    print('-----------------------------------------')
    for i in range(pressure_range.shape[0]):
        print('   ', round(pressure_range[i]/1e5,0), round(fluid_FVF[i],8), round(fluid_viscosity[i],8))
    print('/')
    print('-----------------------------------------')

#read coupled simulation and return df
def read_coupled_sim(path):

    file_name = os.path.basename(path)
    dir_name = os.path.dirname(path)
    print(' File name: ', file_name)
    # print(' File directory: ', dir_name)
    df = pd.read_csv(path, sep=';', decimal = '.')

    df['charge'] = df['power_actual'] > 0
    df['discharge'] = df['power_actual'] < 0

    charge = df['power_actual'] > 0
    discharge = df['power_actual'] < 0

    df['power_output'] = -df[discharge]['power_actual']
    df['power_input'] = df[charge]['power_actual']

    df['power_output'].fillna(value=0, inplace=True)
    df['power_input'].fillna(value=0, inplace=True)

    df['massflow_output'] = -df[discharge]['massflow_actual']
    df['massflow_input'] = df[charge]['massflow_actual']

    df['massflow_output'].fillna(value=0, inplace=True)
    df['massflow_input'].fillna(value=0, inplace=True)
    df['massflow_actual_sign'] = df['massflow_input'] + df['massflow_output']
    df['total_mass'] = (df['massflow_actual_sign']).cumsum() * 3600
    
    df['heat_discharge'] = df[discharge]['heat']
    df['heat_charge'] = df[charge]['heat']
    df['heat_discharge'].fillna(value=0, inplace=True)
    df['heat_charge'].fillna(value=0, inplace=True)
    
    df['total_heat_discharge'] = (df['heat_discharge']).cumsum()
    df['total_heat_charge'] = (df['heat_charge']).cumsum()   
    
    df['total_heat'] = (df['heat']).cumsum()
   
    del discharge, charge, file_name, dir_name, path
    return df

# print allowable flow rate for compled_simulation results(csv) at different pressure levels(max/min BHP)
def print_geostorage_limit_events(temp_path, bhp_level):

    df = read_coupled_sim(temp_path)
    # print('Limit min [GWh]: ', df.loc[df['storage_pressure'] == bhp_level])
    #    power_mismathc_event = df.index.get_indexer_for((df[df['delta_power'] < 0].index))
    press_limit_event = df.index.get_indexer_for((df[df['storage_pressure'] == bhp_level].index))
    time_pressure_limit = press_limit_event[0] #time startes from December - 31 and 1 january is 1 h

    print(' MSG: Pressure limit event at \t', bhp_level, " [bar] and time [h] ", press_limit_event[0])
    print('\n MSG: Allowable mass flow rate at pressure: ', bhp_level, " [bar] and at [h] and  MFR [kg/s] ",    df['massflow_actual'].iloc[[time_pressure_limit]]) 



# generate load profile for ECLIPSE/schedule section based on disptach model result(csv file). Run without coupling, air surf desinity is 1.22
def generate_geostorage_schedule(temp_path, fluid_density=1.2232, min_bhp=80, max_bhp=130, well_number=9):

    #temp_path = str(input(' Please enter filename (with extension): '))
    #temp_path = r'..\Dispatch_A2_2030NEPC_noloss.csv'
    
    file_name = os.path.basename(temp_path)

    file_name = os.path.splitext(os.path.basename(file_name))[0] # cut file extension
    file_dir = os.path.dirname(temp_path)
    df = pd.read_csv(temp_path, sep=';', parse_dates=[0], index_col=0)
 
    power_target = df['input'] + df['output'] * -1
    df['power_target'] = power_target

    # create new column with VFR for injection and withdrawal per well
    df['VFR_input'] = df['cmp_m'] / fluid_density * 86400 / well_number #flow rate in sm3/d
    df['VFR_output'] = df['exp_m'] / fluid_density * 86400 / well_number
    df['VFR_total'] = df['VFR_input'] + df['VFR_output']

    output_file_path = '{}/WELL_SCHEDULE_' + file_name + '.INC'
    write_file = open(output_file_path.format(file_dir), "w")

    timestep = "/\nTSTEP \n 1*0.041666666666666664 /\n\n"
    injection_mode = "WCONINJE\n"
    withdrawal_mode = "WCONPROD\n"

    # generate Well names
    well_name = []
    for i in range(0, well_number): 
        well_name.append('WELL_' + str(i))
    well_name[0] = 'WELL_C'

    for i in range(len(df['power_target'])):
        # Injection mode
        if df['power_target'][i] > 0:
            write_file.write(injection_mode)
            for j in range(well_number):
                textline = str("    " + well_name[j] + " 'GAS'	'OPEN'	'RATE'   " + str(df['VFR_total'][i]) + "   1* " + max_bhp + " /\n")
                write_file.write(textline)
            write_file.write(timestep)
        
        # withdrawal mode
        if df['power_target'][i] < -1:
            write_file.write(withdrawal_mode)
            for j in range(well_number):
                textline = str("    " + well_name[j] + " 'OPEN' 'GRAT'  2*  " + str(df['VFR_total'][i]) + "  2* " + min_bhp + " /\n")
                write_file.write(textline)
            write_file.write(timestep)

        # shut-in mode, wells are in monitoring status
        if df['power_target'][i] == 0:
            write_file.write(injection_mode)
            for j in range(well_number):
                textline = str(
                    str("    " + well_name[j]) + " 'GAS'	'OPEN'	'RATE'  " + str(0.0) + "  1* " + max_bhp + " /\n")
                write_file.write(textline)
            write_file.write(timestep)
    print(' MSG: File is ready')


'-------------------------------'
def summdata(data):
    inputPower_count = 0
    outputPower_count = 0

    outputPower_sum = 0
    inputPower_sum = 0

    for n in data:
        if n > 0:
            inputPower_count += 1
        if n < 0:
            outputPower_count += 1
        if n > 0:
            inputPower_sum += n
        if n < 0:
            outputPower_sum += n

    return [ round(outputPower_sum, 2), round(inputPower_sum, 2),
             outputPower_count, inputPower_count]

# calculate physical exergy, fluid in place in kg, pressure in Pa and temperature in K
def get_physical_exergy(res_pressure, res_temperature, amb_pressure, amb_temperature, fluid, fluid_in_place):
    joule2MWh = 2.77777777778e-10
    dh = SI('H', 'P', res_pressure, 'T', res_temperature, fluid) - SI('H', 'P', amb_pressure, 'T', amb_temperature, fluid)  # Enthalpy in J/kg
    t_ds = amb_temperature * (SI('S', 'P', res_pressure, 'T', res_temperature, fluid) - SI('S', 'P', amb_pressure, 'T', amb_temperature, fluid))  # Entropy in J/kg/K
    # print('Enthalpy diff: ', dh , fluid)
    # print('Entropy diff: ', t_ds, fluid )
    
    exergy = fluid_in_place * (dh - t_ds)  # Exergy in J
    
    print(' MSG: Storage pressure in bar', res_pressure*1e-5)
    print(' MSG: Fluid physical exergy in MWh: ', exergy*joule2MWh)

    return exergy