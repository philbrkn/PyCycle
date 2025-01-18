import openmdao.api as om
from src.STOL_HBTF import MPhbtf
from src.HBTF import viewer
from flight_conditions import FLIGHT_ENV
import time
from design_parameters import BALANCE_GUESSES, OFF_DESIGN_GUESSES, TET, SIMULATION_SETTINGS

if __name__ == "__main__":
    prob = om.Problem()
    prob.model = mp_hbtf = MPhbtf()
    prob.setup()

    # --- Set Engine Settings from `design_parameters.py` ---
    for comp, value in SIMULATION_SETTINGS.items():
        units = {
            "T4_MAX": "degR",
            "Fn_DES": "lbf",
            "fc.alt": "ft",
            "LP_Nmech": "rpm",
            "HP_Nmech": "rpm"
        }.get(comp, None)

        if units:
            prob.set_val(f"DESIGN.{comp}", value, units=units)
        else:
            prob.set_val(f"DESIGN.{comp}", value)

    # --- Set Initial Guesses for Balances ---
    for param, value in BALANCE_GUESSES.items():
        prob[param] = value

    prob.set_val('OD_full_pwr.T4_MAX', TET*1.8, units='degR')
    prob.set_val('OD_part_pwr.PC', 0.8)

    # --- Set Initial Guesses for Off-Design Cases ---
    for od_pt, settings in OFF_DESIGN_GUESSES.items():
        for param, value in settings.items():
            prob[f"{od_pt}.{param}"] = value

    st = time.time()

    prob.set_solver_print(level=-1)
    prob.set_solver_print(level=2, depth=1)

    viewer_file = open("hbtf_view.out", "w")
    first_pass = True
    for MN, alt in FLIGHT_ENV:

        # NOTE: You never change the MN,alt for the
        # design point because that is a fixed reference condition.

        print("***" * 10)
        print(f"* MN: {MN}, alt: {alt}")
        print("***" * 10)

        for PC in [1, 0.9, 0.8, 0.7]:
            print(f"## PC = {PC}")
            prob["OD_part_pwr.PC"] = PC
            prob.run_model()

            if first_pass:
                viewer(prob, "DESIGN", file=viewer_file)
                first_pass = False
            viewer(prob, "OD_part_pwr", file=viewer_file)

        # run throttle back up to full power
        for PC in [1, 0.85]:
            prob["OD_part_pwr.PC"] = PC
            prob.run_model()

    print()
    print("Run time", time.time() - st)
