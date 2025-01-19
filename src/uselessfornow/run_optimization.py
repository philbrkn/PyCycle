import openmdao.api as om
from STOL_HBTF import MPhbtf
from HBTF import viewer


def bpr_optim_model():
    prob = om.Problem()
    prob.model = MPhbtf()

    # 1) Set up an optimizer driver
    prob.driver = om.ScipyOptimizeDriver()
    prob.driver.options["optimizer"] = "SLSQP"
    prob.driver.options["maxiter"] = 50
    prob.driver.options["debug_print"] = ["desvars", "nl_cons", "objs"]
    prob.driver.opt_settings={'Major step limit': 0.05}
    # Optionally prob.driver.opt_settings = { ... } for advanced control

    # 2) Add design variables
    # Example: HPC PR, fan PR, and T4 at design
    # HPC PR is often the product lpc.PR * hpc.PR, or you can do them individually.
    # We'll assume HPC has a single PR.  If your code is separated, adapt accordingly.
    prob.model.add_design_var("CRZ.hpc.PR", lower=6.0, upper=15.0)
    prob.model.add_design_var("CRZ.fan.PR", lower=1.2, upper=1.8)
    prob.model.add_design_var('CRZ.lpc.PR', lower=1.0, upper=4.0)
    # prob.model.add_design_var("CRZ.T4_MAX", lower=2700.0, upper=3400.0)

    # 3) Objective: Minimize TSFC at CRZ
    prob.model.add_objective("CRZ.perf.TSFC")

    # 4) Add constraints
    prob.model.add_constraint('CRZ.fan_dia.FanDia', upper=100.0, ref=100.0)

    # 5) Off-design constraints: RTO must produce required thrust
    # E.g. "RTO.Fn_target" = 22000 lbf
    # But let's say we also want T4 not to exceed 3500 R
    # or HPC exit temperature not to exceed 1300 K, etc.
    prob.model.add_constraint("RTO.perf.Fn", lower=22000.0)  # must be >= 22000
    # For HPC temp limit:
    # prob.model.add_constraint("RTO.hpc.Fl_O:tot:T", upper=1300.*1.8) # in degR
    return (prob)


def run_optimization():
    prob = bpr_optim_model()

    # 5) Setup the problem
    prob.setup()

    # 6) Set the DESIGN (CRZ) point
    prob.set_val('CRZ.fan.PR', 1.685)
    prob.set_val('CRZ.fan.eff', 0.8948)

    prob.set_val('CRZ.lpc.PR', 1.935)
    prob.set_val('CRZ.lpc.eff', 0.9243)

    prob.set_val('CRZ.hpc.PR', 9.369)
    prob.set_val('CRZ.hpc.eff', 0.8707)
    
    prob.set_val('CRZ.hpt.eff', 0.8888)
    prob.set_val('CRZ.lpt.eff', 0.8996)
    
    prob.set_val('CRZ.fc.alt', 35000., units='ft')
    prob.set_val('CRZ.fc.MN', 0.8)
    
    prob.set_val('CRZ.T4_MAX', 2857, units='degR')
    prob.set_val('CRZ.Fn_DES', 5900.0, units='lbf') 

    # prob.set_val("fan:PRdes", 1.5)  # initial guess, but we do a DV

    # Initial guesses for design balance
    prob['CRZ.balance.FAR'] = 0.025
    prob['CRZ.balance.W'] = 300.
    prob['CRZ.balance.lpt_PR'] = 4.0
    prob['CRZ.balance.hpt_PR'] = 5.0
    prob['CRZ.fc.balance.Pt'] = 5.2
    prob['CRZ.fc.balance.Tt'] = 440.0


    # 7) Set the OFF-DESIGN (RTO)
    prob.set_val("RTO.fc.alt", 0.0, units="ft")
    prob.set_val("RTO.fc.MN", 0.25)
    prob.set_val("RTO.T4_MAX", 3300.0, units="degR")

    # spool guesses, W, BPR:
    prob["RTO.balance.FAR"] = 0.03
    prob["RTO.balance.W"] = 500.0
    prob["RTO.balance.BPR"] = 6
    prob["RTO.balance.hp_Nmech"] = 18000.0
    prob["RTO.balance.lp_Nmech"] = 6000.0
    prob["RTO.hpt.PR"] = 4
    prob["RTO.lpt.PR"] = 5.0

    # 8) Solve / optimize
    prob.set_solver_print(level=1, depth=1)
    prob.run_driver()

    # 9) Print final results
    viewer(prob, "CRZ")
    viewer(prob, "RTO")

    return prob


if __name__ == "__main__":
    prob = run_optimization()
