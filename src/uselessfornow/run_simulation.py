import openmdao.api as om
from STOL_HBTF import MPhbtf
from HBTF import viewer
import time
from simulation_inputs import (
    DESIGN_PARAMS,
    DESIGN_BALANCE_GUESSES,
    OFF_DESIGN_PARAMS,
    OFF_DESIGN_BALANCE_GUESSES,
    FLIGHT_ENV,
    TET,
)

if __name__ == "__main__":
    prob = om.Problem()
    prob.model = mp_hbtf = MPhbtf()
    prob.setup()

    # 1) Set DESIGN point numeric values
    for param, entry in DESIGN_PARAMS.items():
        val = entry["val"]
        units = entry["units"]  # might be None
        prob.set_val(f"CRZ.{param}", val, units=units)

    # 2) Set Initial Guesses for Balances
    for param, value in DESIGN_BALANCE_GUESSES.items():
        prob[param] = value

    # 3) For each off-design
    for od_pt, data in OFF_DESIGN_PARAMS.items():
        for param, entry in data.items():
            val = entry["val"]
            units = entry["units"]
            prob.set_val(f"{od_pt}.{param}", val, units=units if units else None)

    for od_pt, guesses in OFF_DESIGN_BALANCE_GUESSES.items():
        for param, entry in guesses.items():
            val = entry["val"]
            units = entry["units"]
            prob.set_val(f"{od_pt}.{param}", val, units=units if units else None)

    st = time.time()

    viewer_file = open("hbtf_view.out", "w")
    first_pass = True
    prob.set_solver_print(level=-1)
    prob.set_solver_print(level=2, depth=1)
    prob.run_model()

    for pt in ['CRZ']+prob.model.od_pts:
        viewer(prob, pt, file=viewer_file)

    # prob.run_model()
    print()
    print("Run time", time.time() - st)
    print("Bypass ratio", prob.get_val("CRZ.splitter.BPR"))
