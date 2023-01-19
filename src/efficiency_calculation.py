
"""
Created on Wed Jun 12 11:40:26 2019

@author: witte
"""

import pandas as pd
import numpy as np
import sys
from matplotlib import pyplot as plt
import os
params = {
'font.sans-serif': 'Arial',
'savefig.dpi':300,
'figure.dpi':100,
'figure.figsize':(7, 4)}
plt.rcParams.update(params)


from tespy.networks import load_network
from tespy.tools.fluid_properties import h_mix_pT, s_mix_pT
import json

# fn = sys.argv[1]
# consider_thermal_input = sys.argv[2]

fn = r"..\coupled_simulation_2021-07-09\2030_output_results.csv"
consider_thermal_input = 'True'


if consider_thermal_input == 'True':
    with open('powerplant/scenario.powerplant_ctrl.json') as f:
        powerplant_data = json.load(f)
    charge_path = 'powerplant/scenario_charge_design'
    charge_model = load_network(charge_path)
    discharge_path = 'powerplant/scenario_discharge_design'
    discharge_model = load_network(discharge_path)
    charge_model.set_attr(iterinfo=False)
    discharge_model.set_attr(iterinfo=False)
    pres_design_charge = powerplant_data['charge']['pressure_nominal']
    pres_design_discharge = powerplant_data['discharge']['pressure_nominal']
    power_design_charge =  powerplant_data['charge']['power_nominal']
    power_design_discharge = powerplant_data['discharge']['power_nominal']
    charge_model.busses[powerplant_data['charge']['power_bus']].set_attr(P=None)
    discharge_model.busses[powerplant_data['discharge']['power_bus']].set_attr(P=None)

data = pd.read_csv(fn, sep=';', decimal='.')
file_name = os.path.basename(fn)

print(" File name: ", file_name)

charge = data['power_actual'] > 0
discharge = data['power_actual'] < 0

data['massflow_out'] = -data[discharge]['massflow_actual']
data['massflow_in'] = data[charge]['massflow_actual']

data['massflow_out'].fillna(value=0, inplace=True)
data['massflow_in'].fillna(value=0, inplace=True)
data['massflow'] = data['massflow_in'] + data['massflow_out']
data['total mass'] = (data['massflow']).cumsum() * 3600

data['total heat'] = (data['heat']).cumsum()
data['thermal_input'] = data[discharge]['heat']
data['thermal_input'].fillna(value=0, inplace=True)

data['power_out'] = -data[discharge]['power_actual']
data['power_in'] = data[charge]['power_actual']
data['power_out'].fillna(value=0, inplace=True)
data['power_in'].fillna(value=0, inplace=True)

fig, ax = plt.subplots(1, 1, sharex=True)
ax.plot(data.index, data['total mass'] / 1e6, color = "black")

ax.set_xlabel('Time in h')
ax.set_ylabel('Total air mass in x10$^6$ kg')
ax.grid(True, which='major', ls='--')
# ax[1].grid()
# ax[2].grid()
plt.tight_layout(pad=0.01)
# plt.show()
fig.savefig('plot_mass_'+file_name+'.png')
plt.close()

result = pd.DataFrame(
    columns=[
        'efficiency pauschal', 'power_in', 'power_out', 'thermal_input',
        'cycle_start', 'cycle_end', 'power_fraction_start',
        'power_fraction_end', 'reference_carnot_efficiency'])

# print(data.loc[36:60, ['total mass', 'power_out', 'power_in', 'thermal_input']])
if consider_thermal_input:
    carnot_data = pd.DataFrame(columns=['T_mcomb', 'Q_comb', 'S_ab', 'Q_ab'])

for offset_index in np.linspace(0, len(data) - 1, 15).astype('int'):
    data['total mass'] = data['total mass'] - data.loc[offset_index, 'total mass']
    asign = np.sign(data['total mass'])
    signchange = ((np.roll(asign, 1) - asign) != 0).astype(int)
    t_signchange = np.where(signchange.values == 1)[0][1:]
    t_before = t_signchange - 1

    mass0 = data['total mass'][t_before].values
    mass1 = data['total mass'][t_signchange].values

    zero_crossings = (0 - mass0) / (data['total mass'][t_signchange] - mass0)

    efficiency = []
    # to iterate through all cycles of the offset
    # for i in range(len(zero_crossings) - 1):
    for i in [0]:
        cycle_data = data.loc[t_signchange[0] - 1:t_signchange[-(i + 1)]]
        starting_mass = (
            cycle_data.loc[t_signchange[0] - 1, 'total mass'] +
            zero_crossings[t_signchange[0]] *
            cycle_data.loc[t_signchange[0], 'massflow'] * 3600
        )
        ending_mass = (
            cycle_data.loc[t_signchange[-(i + 1)] - 1, 'total mass'] +
            zero_crossings[t_signchange[-(i + 1)]] *
            cycle_data.loc[t_signchange[-(i + 1)], 'massflow'] * 3600
        )

        if starting_mass <= 1e-6 and ending_mass <= 1e-6:

            fig, ax = plt.subplots(3, 1,figsize= (7, 10), sharex=True)
            ax[0].plot(cycle_data.index, cycle_data['total mass'] / 1e6, color= "black")
            ax[1].plot(cycle_data.index, cycle_data['power_actual'] / 1e6, label='Power',color= "gray")
            ax[2].plot(cycle_data.index, cycle_data['total heat'] / 1e6, label='Total heat', color = "black")
            ax[1].plot(cycle_data.index, cycle_data['thermal_input'] / 1e6, label='Heat input', color = "peru")
            ax[2].set_xlabel('Time [h]')
            ax[0].set_ylabel('Total air mass in x10$^6$ kg')
            ax[1].set_ylabel('Energy flow in MW')
            ax[2].set_ylabel('Accumulated heat in MWh')
            ax[1].legend()
            ax[0].grid(True, which='major', ls='--')
            ax[1].grid(True, which='major', ls='--')
            ax[2].grid(True, which='major', ls='--')
            plt.tight_layout(pad=0.01)
            # plt.show()
            fig.savefig('plots_' + str(offset_index) + '_' + file_name +'.png')
            plt.close()

            # time is one hour!
            power_input = (
                (1 - zero_crossings[t_signchange[0]]) *
                cycle_data.loc[t_signchange[0], 'power_in'] +
                cycle_data.loc[t_signchange[0] + 1:t_signchange[-(i + 1)] -1, 'power_in'].sum() +
                zero_crossings[t_signchange[-(i + 1)]] *
                cycle_data.loc[t_signchange[-(i + 1)], 'power_in']
            )
            power_output = (
                (1 - zero_crossings[t_signchange[0]]) *
                cycle_data.loc[t_signchange[0], 'power_out'] +
                cycle_data.loc[t_signchange[0] + 1:t_signchange[-(i + 1)] -1, 'power_out'].sum() +
                zero_crossings[t_signchange[-(i + 1)]] *
                cycle_data.loc[t_signchange[-(i + 1)], 'power_out']
            )
            thermal_input = (
                (1 - zero_crossings[t_signchange[0]]) *
                cycle_data.loc[t_signchange[0], 'thermal_input'] +
                cycle_data.loc[t_signchange[0] + 1:t_signchange[-(i + 1)] -1, 'thermal_input'].sum() +
                zero_crossings[t_signchange[-(i + 1)]] *
                cycle_data.loc[t_signchange[-(i + 1)], 'thermal_input']
            )

            if consider_thermal_input == 'True':
                weights = pd.Series(dtype='float64')
                for timestamp in cycle_data[cycle_data['massflow_actual'] > 1e-3].index:
                    if timestamp == t_signchange[0]:
                        factor = (1 - zero_crossings[t_signchange[0]])
                    elif timestamp == t_signchange[-1]:
                        factor = zero_crossings[t_signchange[-1]]
                    else:
                        factor = 1

                    weights.loc[timestamp] = factor

                    if timestamp not in carnot_data.index:

                        p = cycle_data.loc[timestamp, 'storage_pressure']
                        if cycle_data.loc[timestamp, 'massflow_out'] < 0:
                            model = discharge_model
                            design_path = discharge_path
                            c_m = powerplant_data['discharge']['massflow_conn']
                            c_p = powerplant_data['discharge']['pressure_conn']
                            m = -cycle_data.loc[timestamp, 'massflow_out']
                            pres_design = pres_design_discharge
                            pow_design = power_design_discharge
                            pow_bus = powerplant_data['discharge']['power_bus']

                        elif cycle_data.loc[timestamp, 'massflow_in'] > 0:
                            model = charge_model
                            design_path = charge_path
                            c_m = powerplant_data['massflow_conn_charge']
                            c_p = powerplant_data['pressure_conn_charge']
                            m = cycle_data.loc[timestamp, 'massflow_in']
                            pres_design = pres_design_charge
                            pow_design = power_design_charge
                            pow_bus = powerplant_data['power_bus_charge']
                        model.get_conn(c_m).set_attr(m=m) #todo 1 - connections - API
                        model.get_conn(c_p).set_attr(p=p)
                        print('Timestamp: ' + str(timestamp))
                        try:
                            model.solve('offdesign', design_path=design_path)
                        except ValueError:
                            model.busses[pow_bus].set_attr(P=pow_design)
                            model.get_conn(c_m).set_attr(m=None)
                            model.get_conn(c_p).set_attr(p=pres_design)
                            model.solve('offdesign', design_path=design_path, init_path=design_path)
                            model.busses[pow_bus].set_attr(P=None)
                            m_design = model.get_conn(c_m).m.val
                            model.get_conn(c_m).set_attr(m=m_design)
                            for pres in np.linspace(pres_design, p, 4):
                                model.get_conn(c_p).set_attr(p=pres)
                                model.solve('offdesign', design_path=design_path)
                            for mass in np.linspace(m_design, m, 4):
                                model.get_conn(c_m).set_attr(m=mass)
                                model.solve('offdesign', design_path=design_path)

                        if cycle_data.loc[timestamp, 'massflow_out'] < 0:
                            carnot_data.loc[timestamp, 'Q_comb'] = model.busses[powerplant_data['discharge']['heat_bus']].P.val
                            carnot_data.loc[timestamp, 'T_mcomb'] = model.get_comp('combustion').T_mcomb

                            conn = model.get_conn('recuperator:out1_ambient:in1')
                            carnot_data.loc[timestamp, 'Q_ab'] = m * (conn.h.val_SI - h_mix_pT([0, 1e5, 0, conn.fluid.val], 298.15, force_gas=True))
                            carnot_data.loc[timestamp, 'S_ab'] = m * (conn.s.val_SI - s_mix_pT([0, 1e5, 0, conn.fluid.val], 298.15, force_gas=True))

                        elif cycle_data.loc[timestamp, 'massflow_in'] > 0:
                            carnot_data.loc[timestamp, 'Q_ab'] = model.busses[powerplant_data['charge']['heat_bus']].P.val
                            carnot_data.loc[timestamp, 'S_ab'] = (
                                model.get_comp('cooler 1').S_Q +
                                model.get_comp('cooler 2').S_Q +
                                model.get_comp('cooler 3').S_Q)
                try:
                    T_mcomb = (
                        carnot_data.loc[cycle_data.index[0]: cycle_data.index[-1], 'T_mcomb'] *
                        carnot_data.loc[cycle_data.index[0]: cycle_data.index[-1], 'Q_comb'] * weights).sum() / (
                        (carnot_data.loc[cycle_data.index[0]: cycle_data.index[-1], 'Q_comb'] * weights).sum())
                    T_mab = (
                        (carnot_data.loc[cycle_data.index[0]: cycle_data.index[-1], 'Q_ab'] * weights).sum() /
                        (carnot_data.loc[cycle_data.index[0]: cycle_data.index[-1], 'S_ab'] * weights).sum())
                    efficiency_carnot = 1 - T_mab / T_mcomb
                except:
                    efficiency_carnot = 0
            else:
                efficiency_carnot = 0

    result.loc[offset_index] = [
        power_output / (thermal_input * efficiency_carnot + power_input),
        power_input,
        power_output,
        thermal_input,
        t_signchange[0], t_signchange[-1],
        (1 - zero_crossings[t_signchange[0]]),
        zero_crossings[t_signchange[-(i + 1)]],
        efficiency_carnot
    ]

result.to_csv(fn[:-4] + '_cycle_analysis' + '.csv')
