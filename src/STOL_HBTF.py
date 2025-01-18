# Description: This file contains the Multi-Point Turbofan Cycle Model
import pycycle.api as pyc

from src.HBTF import HBTF
from design_parameters import (
    ENGINE_DEFAULTS,
    DEFAULT_MN_VALUES,
    OFF_DESIGN_SETTINGS,
)


class MPhbtf(pyc.MPCycle):

    def setup(self):
        # Create an instace of the High Bypass ratio Turbofan
        # Define CRZ as the Design Point
        self.pyc_add_pnt("CRZ", HBTF(thermo_method="CEA"))

        # --- Set Engine Settings from `design_parameters.py` ---
        for comp, value in ENGINE_DEFAULTS.items():
            units = {
                "T4_MAX": "degR",
                "Fn_DES": "lbf",
                "fc.alt": "ft",
                "LP_Nmech": "rpm",
                "HP_Nmech": "rpm"
            }.get(comp, None)

            if units:
                self.set_input_defaults(f"CRZ.{comp}", value, units=units)
            else:
                self.set_input_defaults(f"CRZ.{comp}", value)

        # Set Mach Numbers from `design_parameters.py`
        for comp, mn in DEFAULT_MN_VALUES.items():
            if isinstance(mn, dict):  # Handling nested values like splitter
                if "splitter" in comp:
                    for key, value in mn.items():
                        self.set_input_defaults(f"CRZ.{comp}.{key}", value)
                else:
                    for key, value in mn.items():
                        self.set_input_defaults(f"CRZ.{key}.MN", value)
            else:
                self.set_input_defaults(f"CRZ.{comp}.MN", mn)

        # --- Set up bleed values -----
        # pressure drops, efficiencies, and flow coefficients
        self.pyc_add_cycle_param("inlet.ram_recovery", 0.9990)
        self.pyc_add_cycle_param("duct4.dPqP", 0.0048)
        self.pyc_add_cycle_param("duct6.dPqP", 0.0101)
        self.pyc_add_cycle_param("burner.dPqP", 0.0540)
        self.pyc_add_cycle_param("duct11.dPqP", 0.0051)
        self.pyc_add_cycle_param("duct13.dPqP", 0.0107)
        self.pyc_add_cycle_param("duct15.dPqP", 0.0149)
        self.pyc_add_cycle_param("core_nozz.Cv", 0.9933)
        self.pyc_add_cycle_param("byp_bld.bypBld:frac_W", 0.005)
        self.pyc_add_cycle_param("byp_nozz.Cv", 0.9939)
        self.pyc_add_cycle_param("hpc.cool1:frac_W", 0.050708)
        self.pyc_add_cycle_param("hpc.cool1:frac_P", 0.5)
        self.pyc_add_cycle_param("hpc.cool1:frac_work", 0.5)
        self.pyc_add_cycle_param("hpc.cool2:frac_W", 0.020274)
        self.pyc_add_cycle_param("hpc.cool2:frac_P", 0.55)
        self.pyc_add_cycle_param("hpc.cool2:frac_work", 0.5)
        self.pyc_add_cycle_param("bld3.cool3:frac_W", 0.067214)
        self.pyc_add_cycle_param("bld3.cool4:frac_W", 0.101256)
        self.pyc_add_cycle_param("hpc.cust:frac_P", 0.5)
        self.pyc_add_cycle_param("hpc.cust:frac_work", 0.5)
        self.pyc_add_cycle_param("hpc.cust:frac_W", 0.0445)
        self.pyc_add_cycle_param("hpt.cool3:frac_P", 1.0)
        self.pyc_add_cycle_param("hpt.cool4:frac_P", 0.0)
        self.pyc_add_cycle_param("lpt.cool1:frac_P", 1.0)
        self.pyc_add_cycle_param("lpt.cool2:frac_P", 0.0)
        self.pyc_add_cycle_param("hp_shaft.HPX", 250.0, units="hp")

        # --- Off-Design Performance Cases --- #
        for od_pt, settings in OFF_DESIGN_SETTINGS.items():
            self.pyc_add_pnt(od_pt, HBTF(design=False, thermo_method="CEA", throttle_mode="T4" if od_pt == "OD_full_pwr" else "percent_thrust"))
            for param, value in settings.items():
                if param == "T4_MAX" or param == "fc.dTs":
                    self.set_input_defaults(f"{od_pt}.{param}", value, units="degR")
                elif param == "fc.alt":
                    self.set_input_defaults(f"{od_pt}.{param}", value, units="ft")
                else:
                    self.set_input_defaults(f"{od_pt}.{param}", value)

        self.connect("OD_full_pwr.perf.Fn", "OD_part_pwr.Fn_max")

        self.pyc_use_default_des_od_conns()

        # Set up the RHS of the balances!
        self.pyc_connect_des_od("core_nozz.Throat:stat:area", "balance.rhs:W")
        self.pyc_connect_des_od("byp_nozz.Throat:stat:area", "balance.rhs:BPR")

        super().setup()
