# Integrated CASE Assessment

This repository contains inputs for integrated PM-CAES assessment using a set of future energy system scenarios with different fractions of renewable energy supply developed by [oemof](https://github.com/znes/angus-scenarios), as well as different technical options for the power plant topology built via [TESPy](https://github.com/oemof/tespy) and subsurface storage configurations modelled in ECLIPSE simulator.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./figures/graphical-abstract_dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./figures/graphical-abstract_light.svg">
  <img alt="power plant setups">
</picture>

## Energy system dispatch model

Optimised dispatch model based on several assumptions, where three shadow electricity pricies (scenario developed within [ANGUS project](https://zenodo.org/record/3714708)), CO<sub>2</sub> emission and fuel prices  are inputs for Gurobi.  

|Scenario year|Power plant type|Renewable share [%]|Average shadow electricity price [EUR/MWh]|CO<sub>2</sub> emission price [EUR/t]|Fuel price [EUR/MWh]| Scenario reference|
|:----|:----|:----|:----|:----|:----|:----|
|2030|D-CAES|76.3|52.6|29.4|26.40|2030NEPC|
|2040|D-CAES |85.9|83.7|126.0|30.24|2040GCA|
|2050|D-CAES |100.0|88.3|150.0|43.72|2050NB|
|2030|2-AA-CAES|76.3|52.6|- |-|2030NEPC|
|2030|3-AA-CAES|76.3|52.6|-|-|2030NEPC|


<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./figures/load_profiles_dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./figures/load_profiles_light.svg">
  <img alt="power plant setups">
</picture>



## Surface power plant topology

  - __diabatic__ topology with 3-stage compression and 2-stage expansion stages including a heat recuperator to preheat the air from the storage 
 - __adiabatic__ plant with 2-stage compression and expansion stages
  - __adiabatic__ plant with 3-stage compression and expansion stages


<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./figures/power_plant_topologies_dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./figures/power_plant_topologies_light.svg">
  <img alt="power plant setups">
</picture>



Coupled power plant-geostorage parameters. The reference temperature and pressure are 273.15 K and 1.013 bar.

| Component            | Parameter                 | Value |
|:---------------------|:--------------------------|:------|
| Compressors          | nominal power                                                        | 230 MW  |
|                      | isentropic efficiency, *η*<sub>s,cmp</sub>                         | 0.92   |
|                      | isentropic efficiency control stage, *η*<sub>s,cmp,cs</sub>        | 0.85   |
|                      | pressure ratio stages 1 and 2 (diabatic, three-stage adiabatic)      | 5    |
|                      | pressure ratio at stage 1 (two-stage adiabatic)                  | 10   |
| Turbines             | nominal power                                                    | 115 MW |
|                      | isentropic efficiency, *η*<sub>s,exp</sub>                     | 0.90     |
|                      | isentropic efficiency control stage, *η*<sub>s,exp,cs</sub>    | 0.85   |
| Coolers              | temperature after cooling (diabatic)                             | 298.15 K |
|                      | temperature after cooling (adiabatic)                            | 338.15 K     |
| Generator & Motor    | efficiency, *η*<sub>(el,mech)</sub>                              | 0.97   |
| Combustion           | fuel type (diabatic)                                             | CH<sub>4</sub>   |
|                      | turbine inlet temperature                                        | 1473.15 K   |
|                      | outlet temperature (diabatic)                                    | 423.15 K   |
|                      | pressure loss                                                    | 3 %    |
| Heat exchangers      | temperature after reheating (adiabatic)                          | 573.15 K |
|                      | pressure loss                                                    | 2 %     |
| Storage              | nominal pressure compression                                     | 115 bar   |
|                      | nominal pressure expansion                                       | 110 bar    |
|                      | vertical well length, *L*                                        | 1055 m     |
|                      | vertical well number                                             | 9 / 3     |
|                      | pipe roughness, *k*<sub>s</sub>                                  | 0.04 mm     |
|                      | well diameter, *D*                                              | 0.25 m     |
|                      | horizontal well number                                           | 2 / 2     |
|                      | horizontal section length, *L*<sub>h</sub>                       | 450 m / 850 m     |
|                      | total completion length,                                         | 150 m / 150 m     |



### Plant performance


<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./figures/power_plant_performance_dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./figures/power_plant_performance_light.svg">
  <img alt="power plant capacity durining continuous chargining and discharging tests">
</picture>

*Power plant performance during continuous charging (top row: a, b, c) and discharging (bottom row: d, e, f) runs*



## Subsurface storage settings

Main geostorage parameters for scenario simulation.

| Parameter     | Value                                                            |
|---------------|--------------------------------------------------------------------|
Dry air composition  |N<sub>2</sub>/O<sub>2</sub>/Ar/CO<sub>2</sub> (0.7553/0.2314/0.0129/0.0004)
Molar mass of air  |                                        28.965 g/mol
Critical temperature  |                                     132.53 K
Critical pressure  |                                        37.86 bar
Air density at standard condition  |                        1.205 kg/m<sup>3</sup>
Initial pressure gradient  |                                0.105 bar/m
Reservoir temperature (isothermal)  |                       311 K
Permeability  |                                             700 mD
Porosity  |                                                 0.27
Residual water saturation  |                                0.15
Residual gas saturation  |                                  0
Max. relative gas permeability  |                           0.9
Max. relative water permeability  |                         1
Capillary entry pressure  |                                 0.1 bar
Pore size distribution index  |                             2
Initial air in place mass  |                                5.56 Mt
Maximum/minimum allowable BHP  |                            130 bar / 80 bar



<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./figures/geostorage_setup_dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./figures/geostorage_setup_light.svg">
  <img alt="Geostorage configuration schemes">
</picture>

*Geostorage configuration schemes for different well setups*



## Reference
- Gasanzade, F., Witte, F., Tuschy, I. and Bauer, S., 2023. Integration of geological compressed air energy storage into future energy supply systems dominated by renewable power sources. Energy Conversion and Management, 277, __doi:10.1016/j.enconman.2022.116643__ 
- TESPy Version 0.4.2 - User's Universe, __doi:10.5281/zenodo.4534878__
- National scale energy system scenarios, __doi:10.5281/zenodo.3714708__
- ECLIPSE Reservoir Simulation Software v2017.2, Schlumberger Ltd.
- LLC Gurobi Optimization. Gurobi Optimizer Reference Manual, 2021.  
