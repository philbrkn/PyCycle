import openmdao.api as om
import pycycle.api as pyc


class Efficiency(om.ExplicitComponent):
    """Component to calculate thermal, propulsive, and overall efficiencies"""

    def initialize(self):
        self.options.declare('thermo_data', default=pyc.species_data.janaf,
                            desc='Thermodynamic data to use for heat transfer calc')

    def setup(self):
        # Inputs
        self.add_input("Wfuel", val=0.0, units="lbm/s", desc="Mass flow rate of fuel")
        self.add_input("Fn", val=10000.0, units="lbf", desc="Net thrust of the engine")
        self.add_input("T4", val=1500.0, units="degK", desc="Combustor exit temperature")
        self.add_input("T3", val=800.0, units="degK", desc="Compressor exit temperature")
        self.add_input("V_aircraft", val=0.0, units="ft/s", desc="Aircraft velocity")
        self.add_input("V_jet_core", val=0.0, units="ft/s", desc="Core nozzle exit velocity")
        self.add_input("V_jet_bypass", val=0.0, units="ft/s", desc="Bypass nozzle exit velocity")
        self.add_input("W_core", val=0.0, units="lbm/s", desc="Mass flow rate in the core")
        self.add_input("W_bypass", val=0.0, units="lbm/s", desc="Mass flow rate in the bypass")
        self.add_input('cp', val=1.0, units='Btu/(lbm*degR)', desc='Specific heat at constant pressure')

        # Outputs
        self.add_output("eta_thermal", val=0.0, units=None, desc="Thermal Efficiency")
        self.add_output("eta_propulsive", val=0.0, units=None, desc="Propulsive Efficiency")
        self.add_output("eta_overall", val=0.0, units=None, desc="Overall Efficiency")

        self.declare_partials('*', '*')

    def compute(self, inputs, outputs):
        # Retrieve from options
        thermo_data = self.options["thermo_data"]

        # Calculate Thermal Efficiency
        h_fuel = thermo_data.get("h", T=298.15, units="Btu/lbm")  # Enthalpy of fuel
        outputs["eta_thermal"] =  inputs["cp"] * (inputs["T4"] - inputs["T3"]) / (h_fuel * inputs["Wfuel"] + 1.0E-12)

        # Calculate Effective Jet Velocity
        V_jet = (inputs["V_jet_core"] * inputs["W_core"] + inputs["V_jet_bypass"] * inputs["W_bypass"]) / (
            inputs["W_core"] + inputs["W_bypass"] + 1.0E-12)

        # Calculate Propulsive Efficiency
        outputs["eta_propulsive"] = (
            (2.0 * inputs["V_aircraft"]) / (V_jet + inputs["V_aircraft"] + 1.0E-12)
        )

        # Calculate Overall Efficiency
        outputs["eta_overall"] = outputs["eta_thermal"] * outputs["eta_propulsive"]
    
    def compute_partials(self, inputs, J):
        # constants
        thermo_data = self.options["thermo_data"]
        h_fuel = thermo_data.get("h", T=298.15, units="Btu/lbm")  # Enthalpy of fuel

        # inputs
        w_fuel = inputs['Wfuel']
        t_4 = inputs['T4']
        t_3 = inputs['T3']
        v_air = inputs['V_aircraft']
        v_jet_core = inputs['V_jet_core']
        v_jet_bypass = inputs['V_jet_bypass']
        w_core = inputs['W_core']
        w_bypass = inputs['W_bypass']
        cp = inputs['cp']
        
        # outputs
        eta_th = (cp * (t_4 - t_3)) / (h_fuel * w_fuel + 1.0E-12)
        v_jet = (v_jet_core * w_core + v_jet_bypass * w_bypass) / (w_core + w_bypass + 1.0E-12)
        eta_prop = (2.0 * v_air) / (v_jet + v_air + 1.0E-12)

        # thermal efficiency partials
        J['eta_thermal', 'T4'] = cp / (h_fuel * w_fuel + 1.0E-12)
        J['eta_thermal', 'T3'] = -cp / (h_fuel * w_fuel + 1.0E-12)
        J['eta_thermal', 'Wfuel'] = -(cp * (t_4 - t_3)) / (h_fuel * w_fuel**2 + 1.0E-12) * h_fuel
        J['eta_thermal', 'cp'] = (t_4 - t_3) / (h_fuel * w_fuel + 1.0E-12)

        # propulsive efficiency partials
        J['eta_propulsive', 'V_aircraft'] = 2.0 / (v_jet + v_air + 1.0E-12) - (2.0 * v_air) / (v_jet + v_air + 1.0E-12) ** 2
        J['eta_propulsive', 'V_jet_core'] = - (2.0 * v_air) / (v_jet + v_air + 1.0E-12) ** 2 * (w_core / (w_core + w_bypass + 1.0E-12))
        J['eta_propulsive', 'V_jet_bypass'] = - (2.0 * v_air) / (v_jet + v_air + 1.0E-12) ** 2 * (w_bypass / (w_core + w_bypass + 1.0E-12))
        J['eta_propulsive', 'W_core'] = - (2.0 * v_air) / (v_jet + v_air + 1.0E-12) ** 2 * (v_jet_core - v_jet) / (w_core + w_bypass + 1.0E-12)
        J['eta_propulsive', 'W_bypass'] = - (2.0 * v_air) / (v_jet + v_air + 1.0E-12) ** 2 * (v_jet_bypass - v_jet) / (w_core + w_bypass + 1.0E-12)
        

        # overall efficiency partials
        J['eta_overall', 'T4'] = eta_prop * cp / (h_fuel * w_fuel + 1.0E-12)
        J['eta_overall', 'T3'] = eta_prop * -cp / (h_fuel * w_fuel + 1.0E-12)
        J['eta_overall', 'Wfuel'] = eta_prop * -(cp * (t_4 - t_3)) / (h_fuel * w_fuel**2 + 1.0E-12) * h_fuel
        J['eta_overall', 'V_aircraft'] = eta_th * (2.0 / (v_jet + v_air + 1.0E-12) - (2.0 * v_air) / (v_jet + v_air + 1.0E-12) ** 2)
        J['eta_overall', 'V_jet_core'] = eta_th * - (2.0 * v_air) / (v_jet + v_air + 1.0E-12) ** 2 * (w_core / (w_core + w_bypass + 1.0E-12))
        J['eta_overall', 'V_jet_bypass'] = eta_th * - (2.0 * v_air) / (v_jet + v_air + 1.0E-12) ** 2 * (w_bypass / (w_core + w_bypass + 1.0E-12))
        J['eta_overall', 'W_core'] = eta_th * - (2.0 * v_air) / (v_jet + v_air + 1.0E-12) ** 2 * (v_jet_core - v_jet) / (w_core + w_bypass + 1.0E-12)
        J['eta_overall', 'W_bypass'] = eta_th * - (2.0 * v_air) / (v_jet + v_air + 1.0E-12) ** 2 * (v_jet_bypass - v_jet) / (w_core + w_bypass + 1.0E-12)
        J['eta_overall', 'cp'] = eta_prop * (t_4 - t_3) / (h_fuel * w_fuel + 1.0E-12)
