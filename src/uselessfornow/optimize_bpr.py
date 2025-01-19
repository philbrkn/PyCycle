'''
based on https://github.com/OpenMDAO/pyCycle/blob/495f3ca2f43f2d4342ddd5f98e6e4c1ae92b0eb2/example_cycles/N%2B3ref/N3_MDP_Opt.py
'''

import numpy as np
import time
import openmdao.api as om
import pycycle.api as pyc

from src.HBTF import viewer
from src.STOL_HBTF import MPhbtf  # Import your high bypass turbofan model


def BPR_Optimization_Model():
    """
    Sets up an OpenMDAO optimization problem for optimizing the Bypass Ratio (BPR)
    to minimize TSFC while maintaining thrust and fan diameter constraints.
    """
    prob = om.Problem()
    
    # -----------
    # 1) Make model
    # -----------
    prob.model = MPhbtf()

    # Optimization Driver
    prob.driver = om.ScipyOptimizeDriver()
    prob.driver.options['optimizer'] = 'SLSQP'
    prob.driver.options['debug_print'] = ['desvars', 'nl_cons', 'objs']
    prob.driver.opt_settings = {'Major step limit': 0.05}

    # Design Variables (what the optimizer changes)
    prob.model.add_design_var('DESIGN.splitter.BPR', lower=5.0, upper=12.0)  # Optimize BPR
    prob.model.add_design_var('DESIGN.fan:PRdes', lower=1.2, upper=1.7)  # Optimize fan PR
    prob.model.add_design_var('DESIGN.lpc:PRdes', lower=2.0, upper=4.0)  # Optimize LPC PR
    prob.model.add_design_var('DESIGN.hpc.PR', lower=8.0, upper=20.0)  # Optimize HPC PR

    # Objective Function (what the optimizer minimizes)
    prob.model.add_objective('DESIGN.perf.TSFC', ref0=0.4, ref=0.5)  # Minimize fuel consumption

    # Constraints (what must be satisfied)
    prob.model.add_constraint('DESIGN.perf.Fn', lower=5800.0, ref=6000.0)  # Maintain thrust
    prob.model.add_constraint('DESIGN.fan_dia.FanDia', upper=100.0, ref=100.0)  # Keep fan size reasonable

    ## SET ROLLING TAKE OFF T4 RTO_T4???

    return (prob)


if __name__ == "__main__":
    prob = BPR_Optimization_Model()
    prob.setup()

    # Set initial conditions (similar to what was done in run_simulation.py)

    prob.set_val('DESIGN.fan.PR', 1.685)
    prob.set_val('DESIGN.fan.eff', 0.8948)

    prob.set_val('DESIGN.lpc.PR', 1.935)
    prob.set_val('DESIGN.lpc.eff', 0.9243)

    prob.set_val('DESIGN.hpc.PR', 9.369)
    prob.set_val('DESIGN.hpc.eff', 0.8707)
    
    prob.set_val('DESIGN.hpt.eff', 0.8888)
    prob.set_val('DESIGN.lpt.eff', 0.8996)
    
    prob.set_val('DESIGN.fc.alt', 35000., units='ft')
    prob.set_val('DESIGN.fc.MN', 0.8)
    
    prob.set_val('DESIGN.T4_MAX', 2857, units='degR')
    prob.set_val('DESIGN.Fn_DES', 5900.0, units='lbf') 

    # Set initial guesses
    prob['DESIGN.balance.FAR'] = 0.025
    prob['DESIGN.balance.W'] = 100.
    prob['DESIGN.balance.lpt_PR'] = 4.0
    prob['DESIGN.balance.hpt_PR'] = 3.0
    prob['DESIGN.fc.balance.Pt'] = 5.2
    prob['DESIGN.fc.balance.Tt'] = 440.0

    st = time.time()
    prob.set_solver_print(level=-1)
    prob.run_driver()

    # Output Results
    viewer(prob, "DESIGN")
    print()
    print('Optimized BPR:', prob.get_val('DESIGN.splitter.BPR')[0])
    print('Optimized Fan PR:', prob.get_val('DESIGN.fan.PR')[0])
    print('Optimized LPC PR:', prob.get_val('DESIGN.lpc.PR')[0])
    print('Optimized HPC PR:', prob.get_val('DESIGN.hpc.PR')[0])
    print('TSFC:', prob.get_val('DESIGN.perf.TSFC')[0])
    print('Run time:', time.time() - st)
