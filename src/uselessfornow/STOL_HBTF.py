# Description: This file contains the Multi-Point Turbofan Cycle Model
import pycycle.api as pyc
import openmdao.api as om

from HBTF import HBTF
from design_parameters import (
    ENGINE_DEFAULTS,
    DEFAULT_MN_VALUES,
)


class MPhbtf(pyc.MPCycle):
    """
    Multi-point HPC Turbofan:
    * One design point: CRZ
    * Multiple off-design: RTO, LDG, LHR, etc.
    """

    def setup(self):
        # Create an instace of the High Bypass ratio Turbofan
        # Define CRZ as the Design Point
        self.pyc_add_pnt(
            "CRZ",
            HBTF(thermo_method="CEA"),
            # promotes_inputs=[
            #     ("fan.PR", "fan:PRdes"),
            #     ("lpc.PR", "lpc:PRdes"),
            #     # ("opr_calc.FPR", "fan:PRdes"),
            #     # ("opr_calc.LPCPR", "lpc:PRdes"),
            # ],
        )

        # # --- Set Engine Settings from `design_parameters.py` ---
        # for comp, value in ENGINE_DEFAULTS.items():
        #     units = {
        #         "T4_MAX": "degR",
        #         "Fn_DES": "lbf",
        #         "fc.alt": "ft",
        #         "LP_Nmech": "rpm",
        #         "HP_Nmech": "rpm",
        #     }.get(comp, None)

        #     if units:
        #         self.set_input_defaults(f"CRZ.{comp}", value, units=units)
        #     else:
        #         self.set_input_defaults(f"CRZ.{comp}", value)

        # Set Mach Numbers from `design_parameters.py`
        # for comp, mn in DEFAULT_MN_VALUES.items():
        #     if isinstance(mn, dict):  # Handling nested values like splitter
        #         if "splitter" in comp:
        #             for key, value in mn.items():
        #                 self.set_input_defaults(f"CRZ.{comp}.{key}", value)
        #         else:
        #             for key, value in mn.items():
        #                 self.set_input_defaults(f"CRZ.{key}.MN", value)
        #     else:
        #         self.set_input_defaults(f"CRZ.{comp}.MN", mn)

        self.set_input_defaults("CRZ.inlet.MN", 0.751)
        self.set_input_defaults("CRZ.fan.MN", 0.4578)
        self.set_input_defaults("CRZ.splitter.BPR", 5.105)
        self.set_input_defaults("CRZ.splitter.MN1", 0.3104)
        self.set_input_defaults("CRZ.splitter.MN2", 0.4518)
        self.set_input_defaults("CRZ.duct4.MN", 0.3121)
        self.set_input_defaults("CRZ.lpc.MN", 0.3059)
        self.set_input_defaults("CRZ.duct6.MN", 0.3563)
        self.set_input_defaults("CRZ.hpc.MN", 0.2442)
        self.set_input_defaults("CRZ.bld3.MN", 0.3000)
        self.set_input_defaults("CRZ.burner.MN", 0.1025)
        self.set_input_defaults("CRZ.hpt.MN", 0.3650)
        self.set_input_defaults("CRZ.duct11.MN", 0.3063)
        self.set_input_defaults("CRZ.lpt.MN", 0.4127)
        self.set_input_defaults("CRZ.duct13.MN", 0.4463)
        self.set_input_defaults("CRZ.byp_bld.MN", 0.4489)
        self.set_input_defaults("CRZ.duct15.MN", 0.4589)
        self.set_input_defaults("CRZ.LP_Nmech", 4666.1, units="rpm")
        self.set_input_defaults("CRZ.HP_Nmech", 14705.7, units="rpm")

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

        # Suppose inside your MPhbtf setup() you have:
        self.od_pts = ["RTO"]  # , "LDG"]  # , "LHR"]
        self.pyc_add_pnt(
            "RTO",
            HBTF(
                design=False,
                thermo_method="CEA",
                throttle_mode="T4",
            ),
        )
        self.set_input_defaults('RTO.fc.MN', 0.25)
        self.set_input_defaults('RTO.fc.alt', 0, units='ft')
        self.set_input_defaults('RTO.fc.dTs', 27.0, units='degR')
        # self.od_MNs = [0.25, 0.15, 0.6]
        # self.od_alts = [0.0, 0.0, 15000.0]
        # self.od_dTs = [27.0, 10.0, 0.0]

        # for i, pt in enumerate(self.od_pts):
        # Add this off-design point using your single-point model
        # self.pyc_add_pnt(
        #     pt,
        #     HBTF(
        #         design=False,
        #         thermo_method="CEA",
        #         throttle_mode="T4" if pt == "RTO" else "T4",
        #     ),
        # )
        # Now set the inputs for each point
        # self.set_input_defaults(f"{pt}.fc.MN", val=self.od_MNs[i])
        # self.set_input_defaults(f"{pt}.fc.alt", val=self.od_alts[i], units="ft")
        # self.set_input_defaults(f"{pt}.fc.dTs", val=self.od_dTs[i], units="degR")

        # If you want to fix FAR at RTO to achieve 22800 lbf thrust, for example:
        # self.set_input_defaults("RTO.balance.rhs:FAR", 22800.0, units="lbf")

        self.pyc_use_default_des_od_conns()

        # Set up the RHS of the balances!
        self.pyc_connect_des_od("core_nozz.Throat:stat:area", "balance.rhs:W")
        self.pyc_connect_des_od("byp_nozz.Throat:stat:area", "balance.rhs:BPR")

        # DON'T NEED TO USE:
        # self.add_subsystem('T4_ratio',
        #                     om.ExecComp('CRZ_T4 = RTO_T4*TR',
        #                                 RTO_T4={'val': 3400.0, 'units':'degR'},
        #                                 CRZ_T4={'val': 3150.0, 'units':'degR'},
        #                                 TR={'val': 0.926470588, 'units': None}), promotes_inputs=['RTO_T4',])
        # self.connect('T4_ratio.CRZ_T4', 'CRZ.balance.rhs:FAR')

        # SET UP ORDER???
        # initial_order = ["CRZ", "RTO"]  # , "LDG"]  #, "LHR"]
        # self.set_order(initial_order)

        newton = self.nonlinear_solver = om.NewtonSolver()
        newton.options["atol"] = 1e-3
        newton.options["rtol"] = 1e-3
        newton.options["iprint"] = 2
        newton.options["maxiter"] = 50
        newton.options["solve_subsystems"] = True
        newton.options["max_sub_solves"] = 10
        newton.options["err_on_non_converge"] = True
        newton.options["reraise_child_analysiserror"] = False
        newton.linesearch = om.BoundsEnforceLS()
        newton.linesearch.options["bound_enforcement"] = "scalar"
        newton.linesearch.options["iprint"] = -1

        self.linear_solver = om.DirectSolver(assemble_jac=True)

        super().setup()
