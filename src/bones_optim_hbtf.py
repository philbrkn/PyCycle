import sys

import numpy as np

import openmdao.api as om

import pycycle.api as pyc


class HBTF(pyc.Cycle):

    def initialize(self):
        # Initialize the model here by setting option variables such as a switch for design vs off-des cases
        self.options.declare('throttle_mode', default='T4', values=['T4', 'percent_thrust'])

        super().initialize()


    def setup(self):
        #Setup the problem by including all the relavant components here - comp, burner, turbine etc
        
        #Create any relavent short hands here:
        design = self.options['design']
        
        USE_TABULAR = False
        if USE_TABULAR: 
            self.options['thermo_method'] = 'TABULAR'
            self.options['thermo_data'] = pyc.AIR_JETA_TAB_SPEC
            FUEL_TYPE = 'FAR'
        else: 
            self.options['thermo_method'] = 'CEA'
            self.options['thermo_data'] = pyc.species_data.janaf
            FUEL_TYPE = 'Jet-A(g)'

        
        #Add subsystems to build the engine deck:
        self.add_subsystem('fc', pyc.FlightConditions())
        self.add_subsystem('inlet', pyc.Inlet())
        
        # Note variable promotion for the fan -- 
        # the LP spool speed and the fan speed are INPUTS that are promoted:
        # Note here that promotion aliases are used. Here Nmech is being aliased to LP_Nmech
        # check out: http://openmdao.org/twodocs/versions/latest/features/core_features/grouping_components/add_subsystem.html?highlight=alias
        self.add_subsystem('fan', pyc.Compressor(map_data=pyc.FanMap,
                                        bleed_names=[], map_extrap=True), promotes_inputs=[('Nmech','LP_Nmech')])
        self.add_subsystem('splitter', pyc.Splitter())
        self.add_subsystem('duct4', pyc.Duct())
        self.add_subsystem('lpc', pyc.Compressor(map_data=pyc.LPCMap,
                                        map_extrap=True),promotes_inputs=[('Nmech','LP_Nmech')])
        self.add_subsystem('duct6', pyc.Duct())
        self.add_subsystem('hpc', pyc.Compressor(map_data=pyc.HPCMap,
                                        bleed_names=['cool1','cool2','cust'], map_extrap=True),promotes_inputs=[('Nmech','HP_Nmech')])
        self.add_subsystem('bld3', pyc.BleedOut(bleed_names=['cool3','cool4']))
        self.add_subsystem('burner', pyc.Combustor(fuel_type=FUEL_TYPE))
        self.add_subsystem('hpt', pyc.Turbine(map_data=pyc.HPTMap,
                                        bleed_names=['cool3','cool4'], map_extrap=True),promotes_inputs=[('Nmech','HP_Nmech')])
        self.add_subsystem('duct11', pyc.Duct())
        self.add_subsystem('lpt', pyc.Turbine(map_data=pyc.LPTMap,
                                        bleed_names=['cool1','cool2'], map_extrap=True),promotes_inputs=[('Nmech','LP_Nmech')])
        self.add_subsystem('duct13', pyc.Duct())
        self.add_subsystem('core_nozz', pyc.Nozzle(nozzType='CV', lossCoef='Cv'))

        self.add_subsystem('byp_bld', pyc.BleedOut(bleed_names=['bypBld']))
        self.add_subsystem('duct15', pyc.Duct())
        self.add_subsystem('byp_nozz', pyc.Nozzle(nozzType='CV', lossCoef='Cv'))
        
        #Create shaft instances. Note that LP shaft has 3 ports! => no gearbox
        self.add_subsystem('lp_shaft', pyc.Shaft(num_ports=3),promotes_inputs=[('Nmech','LP_Nmech')])
        self.add_subsystem('hp_shaft', pyc.Shaft(num_ports=2),promotes_inputs=[('Nmech','HP_Nmech')])
        self.add_subsystem('perf', pyc.Performance(num_nozzles=2, num_burners=1))
        
        # FAN AREA
        self.add_subsystem('fan_dia', om.ExecComp('FanDia = 2.0*(area/(pi*(1.0-hub_tip**2.0)))**0.5',
                    area={'val':7000.0, 'units':'inch**2'},
                    hub_tip={'val':0.3125, 'units':None},
                    FanDia={'val':100.0, 'units':'inch'}))
        # Now use the explicit connect method to make connections -- connect(<from>, <to>)
        self.connect('inlet.Fl_O:stat:area', 'fan_dia.area')

        # Define the velocity ratio equation: vel_ratio = Vcore / Vbypass
        self.add_subsystem('vel_ratio_calc', om.ExecComp('vel_ratio = core_V / bypass_V',
                                                        core_V={'units': 'ft/s'},
                                                        bypass_V={'units': 'ft/s'},
                                                        vel_ratio={'units': None}))
        # Connect nozzle exit velocities to velocity ratio calculator
        self.connect('core_nozz.Fl_O:stat:V', 'vel_ratio_calc.core_V')
        self.connect('byp_nozz.Fl_O:stat:V', 'vel_ratio_calc.bypass_V')

        self.add_subsystem('opr_calc', om.ExecComp('OPR_simple = FPR*LPCPR*HPCPR',
                        FPR={'val':1.3, 'units':None},
                        LPCPR={'val':3.0, 'units':None},
                        HPCPR={'val':14.0, 'units':None},
                        OPR_simple={'val':55.0, 'units':None}))

        #Connect the inputs to perf group
        self.connect('inlet.Fl_O:tot:P', 'perf.Pt2')
        self.connect('hpc.Fl_O:tot:P', 'perf.Pt3')
        self.connect('burner.Wfuel', 'perf.Wfuel_0')
        self.connect('inlet.F_ram', 'perf.ram_drag')
        self.connect('core_nozz.Fg', 'perf.Fg_0')
        self.connect('byp_nozz.Fg', 'perf.Fg_1')

        #LP-shaft connections
        self.connect('fan.trq', 'lp_shaft.trq_0')
        self.connect('lpc.trq', 'lp_shaft.trq_1')
        self.connect('lpt.trq', 'lp_shaft.trq_2')
        #HP-shaft connections
        self.connect('hpc.trq', 'hp_shaft.trq_0')
        self.connect('hpt.trq', 'hp_shaft.trq_1')
        #Ideally expanding flow by conneting flight condition static pressure to nozzle exhaust pressure
        self.connect('fc.Fl_O:stat:P', 'core_nozz.Ps_exhaust')
        self.connect('fc.Fl_O:stat:P', 'byp_nozz.Ps_exhaust')
        
        #Create a balance component
        # Balances can be a bit confusing, here's some explanation -
        #   State Variables:
        #           (W)        Inlet mass flow rate to implictly balance thrust
        #                      LHS: perf.Fn  == RHS: Thrust requirement (set when TF is instantiated)
        #
        #           (FAR)      Fuel-air ratio to balance Tt4
        #                      LHS: burner.Fl_O:tot:T  == RHS: Tt4 target (set when TF is instantiated)
        #
        #           (lpt_PR)   LPT press ratio to balance shaft power on the low spool
        #           (hpt_PR)   HPT press ratio to balance shaft power on the high spool
        # Ref: look at the XDSM diagrams in the pyCycle paper and this:
        # http://openmdao.org/twodocs/versions/latest/features/building_blocks/components/balance_comp.html

        balance = self.add_subsystem('balance', om.BalanceComp())
        if design:
            balance.add_balance('W', units='lbm/s', eq_units='lbf')
            #Here balance.W is implicit state variable that is the OUTPUT of balance object
            self.connect('balance.W', 'fc.W') #Connect the output of balance to the relevant input
            self.connect('perf.Fn', 'balance.lhs:W')       #This statement makes perf.Fn the LHS of the balance eqn.
            self.promotes('balance', inputs=[('rhs:W', 'Fn_DES')])
            
            balance.add_balance('FAR', eq_units='degR', lower=1e-4, val=.017)
            self.connect('balance.FAR', 'burner.Fl_I:FAR')
            self.connect('burner.Fl_O:tot:T', 'balance.lhs:FAR')
            self.promotes('balance', inputs=[('rhs:FAR', 'T4_MAX')])
            
            # Note that for the following two balances the mult val is set to -1 so that the NET torque is zero
            balance.add_balance('lpt_PR', val=1.5, lower=1.001, upper=8,
                                eq_units='hp', use_mult=True, mult_val=-1)
            self.connect('balance.lpt_PR', 'lpt.PR')
            self.connect('lp_shaft.pwr_in_real', 'balance.lhs:lpt_PR')
            self.connect('lp_shaft.pwr_out_real', 'balance.rhs:lpt_PR')

            balance.add_balance('hpt_PR', val=1.5, lower=1.001, upper=8,
                                eq_units='hp', use_mult=True, mult_val=-1)
            self.connect('balance.hpt_PR', 'hpt.PR')
            self.connect('hp_shaft.pwr_in_real', 'balance.lhs:hpt_PR')
            self.connect('hp_shaft.pwr_out_real', 'balance.rhs:hpt_PR')

            # balance.add_balance('BPR', lower=2., upper=10., eq_units='inch**2')
            # self.connect('balance.BPR', 'splitter.BPR')
            # self.connect('byp_nozz.Throat:stat:area', 'balance.lhs:BPR')

        else:
            
            #In OFF-DESIGN mode we need to redefine the balances:
            #   State Variables:
            #           (W)        Inlet mass flow rate to balance core flow area
            #                      LHS: core_nozz.Throat:stat:area == Area from DESIGN calculation 
            #
            #           (FAR)      Fuel-air ratio to balance Thrust req.
            #                      LHS: perf.Fn  == RHS: Thrust requirement (set when TF is instantiated)
            #
            #           (BPR)      Bypass ratio to balance byp. noz. area
            #                      LHS: byp_nozz.Throat:stat:area == Area from DESIGN calculation
            #
            #           (lp_Nmech)   LP spool speed to balance shaft power on the low spool
            #           (hp_Nmech)   HP spool speed to balance shaft power on the high spool

            if self.options['throttle_mode'] == 'T4': 
                balance.add_balance('FAR', val=0.017, lower=1e-4, eq_units='degR')
                self.connect('balance.FAR', 'burner.Fl_I:FAR')
                self.connect('burner.Fl_O:tot:T', 'balance.lhs:FAR')
                self.promotes('balance', inputs=[('rhs:FAR', 'T4_MAX')])

            balance.add_balance('W', units='lbm/s', lower=10., upper=2000., eq_units='inch**2')
            self.connect('balance.W', 'fc.W')
            self.connect('core_nozz.Throat:stat:area', 'balance.lhs:W')

            balance.add_balance('BPR', lower=2., upper=10., eq_units='inch**2')
            self.connect('balance.BPR', 'splitter.BPR')
            self.connect('byp_nozz.Throat:stat:area', 'balance.lhs:BPR')

            # Again for the following two balances the mult val is set to -1 so that the NET torque is zero
            balance.add_balance('lp_Nmech', val=1.5, units='rpm', lower=500., eq_units='hp', use_mult=True, mult_val=-1)
            self.connect('balance.lp_Nmech', 'LP_Nmech')
            self.connect('lp_shaft.pwr_in_real', 'balance.lhs:lp_Nmech')
            self.connect('lp_shaft.pwr_out_real', 'balance.rhs:lp_Nmech')

            balance.add_balance('hp_Nmech', val=1.5, units='rpm', lower=500., eq_units='hp', use_mult=True, mult_val=-1)
            self.connect('balance.hp_Nmech', 'HP_Nmech')
            self.connect('hp_shaft.pwr_in_real', 'balance.lhs:hp_Nmech')
            self.connect('hp_shaft.pwr_out_real', 'balance.rhs:hp_Nmech')
            
            # Specify the order in which the subsystems are executed:
            
            # self.set_order(['balance', 'fc', 'inlet', 'fan', 'splitter', 'duct4', 'lpc', 'duct6', 'hpc', 'bld3', 'burner', 'hpt', 'duct11',
            #                 'lpt', 'duct13', 'core_nozz', 'byp_bld', 'duct15', 'byp_nozz', 'lp_shaft', 'hp_shaft', 'perf'])
        
        # Set up all the flow connections:
        self.pyc_connect_flow('fc.Fl_O', 'inlet.Fl_I')
        self.pyc_connect_flow('inlet.Fl_O', 'fan.Fl_I')
        self.pyc_connect_flow('fan.Fl_O', 'splitter.Fl_I')
        self.pyc_connect_flow('splitter.Fl_O1', 'duct4.Fl_I')
        self.pyc_connect_flow('duct4.Fl_O', 'lpc.Fl_I')
        self.pyc_connect_flow('lpc.Fl_O', 'duct6.Fl_I')
        self.pyc_connect_flow('duct6.Fl_O', 'hpc.Fl_I')
        self.pyc_connect_flow('hpc.Fl_O', 'bld3.Fl_I')
        self.pyc_connect_flow('bld3.Fl_O', 'burner.Fl_I')
        self.pyc_connect_flow('burner.Fl_O', 'hpt.Fl_I')
        self.pyc_connect_flow('hpt.Fl_O', 'duct11.Fl_I')
        self.pyc_connect_flow('duct11.Fl_O', 'lpt.Fl_I')
        self.pyc_connect_flow('lpt.Fl_O', 'duct13.Fl_I')
        self.pyc_connect_flow('duct13.Fl_O','core_nozz.Fl_I')
        self.pyc_connect_flow('splitter.Fl_O2', 'byp_bld.Fl_I')
        self.pyc_connect_flow('byp_bld.Fl_O', 'duct15.Fl_I')
        self.pyc_connect_flow('duct15.Fl_O', 'byp_nozz.Fl_I')

        #Bleed flows:
        self.pyc_connect_flow('hpc.cool1', 'lpt.cool1', connect_stat=False)
        self.pyc_connect_flow('hpc.cool2', 'lpt.cool2', connect_stat=False)
        self.pyc_connect_flow('bld3.cool3', 'hpt.cool3', connect_stat=False)
        self.pyc_connect_flow('bld3.cool4', 'hpt.cool4', connect_stat=False)
        
        #Specify solver settings:
        newton = self.nonlinear_solver = om.NewtonSolver()
        newton.options['atol'] = 1e-6

        # set this very small, so it never activates and we rely on atol
        newton.options['rtol'] = 1e-99 
        newton.options['iprint'] = 2
        newton.options['maxiter'] = 25
        newton.options['solve_subsystems'] = True
        newton.options['max_sub_solves'] = 1000
        newton.options['reraise_child_analysiserror'] = False
        # ls = newton.linesearch = BoundsEnforceLS()
        ls = newton.linesearch = om.ArmijoGoldsteinLS()
        ls.options['maxiter'] = 3
        ls.options['rho'] = 0.75
        ls.options['print_bound_enforce'] = False

        self.linear_solver = om.DirectSolver()

        super().setup()


def viewer(prob, pt, file=sys.stdout):
    """
    print a report of all the relevant cycle properties
    """

    if pt == 'DESIGN':
        MN = prob['DESIGN.fc.Fl_O:stat:MN']
        LPT_PR = prob['DESIGN.balance.lpt_PR']
        HPT_PR = prob['DESIGN.balance.hpt_PR']
        FAR = prob['DESIGN.balance.FAR']
    else:
        MN = prob[pt+'.fc.Fl_O:stat:MN']
        LPT_PR = prob[pt+'.lpt.PR']
        HPT_PR = prob[pt+'.hpt.PR']
        FAR = prob[pt+'.balance.FAR']

    summary_data = (MN, prob[pt+'.fc.alt'], prob[pt+'.inlet.Fl_O:stat:W'], prob[pt+'.perf.Fn'],
                        prob[pt+'.perf.Fg'], prob[pt+'.inlet.F_ram'], prob[pt+'.perf.OPR'],
                        prob[pt+'.perf.TSFC'], prob[pt+'.splitter.BPR'])
    # TO SOLVE DEPRECIATION WARNING    
    summary_data = tuple(x.item() for x in summary_data)

    print(file=file, flush=True)
    print(file=file, flush=True)
    print(file=file, flush=True)
    print("----------------------------------------------------------------------------", file=file, flush=True)
    print("                              POINT:", pt, file=file, flush=True)
    print("----------------------------------------------------------------------------", file=file, flush=True)
    print("                       PERFORMANCE CHARACTERISTICS", file=file, flush=True)
    print("    Mach      Alt       W      Fn      Fg    Fram     OPR     TSFC      BPR ", file=file, flush=True)
    print(" %7.5f  %7.1f %7.3f %7.1f %7.1f %7.1f %7.3f  %7.5f  %7.3f" %summary_data, file=file, flush=True)


    fs_names = ['fc.Fl_O', 'inlet.Fl_O', 'fan.Fl_O', 'splitter.Fl_O1', 'splitter.Fl_O2',
                'duct4.Fl_O', 'lpc.Fl_O', 'duct6.Fl_O', 'hpc.Fl_O', 'bld3.Fl_O', 'burner.Fl_O',
                'hpt.Fl_O', 'duct11.Fl_O', 'lpt.Fl_O', 'duct13.Fl_O', 'core_nozz.Fl_O', 'byp_bld.Fl_O',
                'duct15.Fl_O', 'byp_nozz.Fl_O']
    fs_full_names = [f'{pt}.{fs}' for fs in fs_names]
    pyc.print_flow_station(prob, fs_full_names, file=file)

    comp_names = ['fan', 'lpc', 'hpc']
    comp_full_names = [f'{pt}.{c}' for c in comp_names]
    pyc.print_compressor(prob, comp_full_names, file=file)

    pyc.print_burner(prob, [f'{pt}.burner'], file=file)

    turb_names = ['hpt', 'lpt']
    turb_full_names = [f'{pt}.{t}' for t in turb_names]
    pyc.print_turbine(prob, turb_full_names, file=file)

    noz_names = ['core_nozz', 'byp_nozz']
    noz_full_names = [f'{pt}.{n}' for n in noz_names]
    pyc.print_nozzle(prob, noz_full_names, file=file)

    shaft_names = ['hp_shaft', 'lp_shaft']
    shaft_full_names = [f'{pt}.{s}' for s in shaft_names]
    pyc.print_shaft(prob, shaft_full_names, file=file)

    bleed_names = ['hpc', 'bld3', 'byp_bld']
    bleed_full_names = [f'{pt}.{b}' for b in bleed_names]
    pyc.print_bleed(prob, bleed_full_names, file=file)


class MPhbtf(pyc.MPCycle):

    def setup(self):

        self.pyc_add_pnt('DESIGN', HBTF(thermo_method='CEA')) # Create an instace of the High Bypass ratio Turbofan

        self.set_input_defaults('DESIGN.fc.alt', 35000., units='ft')  # Typical cruise altitude
        self.set_input_defaults('DESIGN.fc.MN', 0.8)  # Typical cruise Mach number
        self.set_input_defaults('DESIGN.T4_MAX', 1600., units='degK') # Initial TET based on your notes

        # Set the default value for vel_ratio_target at the top level
        # self.set_input_defaults('DESIGN.splitter.BPR', 5.105)

        self.set_input_defaults('DESIGN.inlet.MN', 0.70)
        self.set_input_defaults('DESIGN.fan.MN', 0.45)
        self.set_input_defaults('DESIGN.splitter.MN1', 0.32)
        self.set_input_defaults('DESIGN.splitter.MN2', 0.47)
        self.set_input_defaults('DESIGN.duct4.MN', 0.33)
        self.set_input_defaults('DESIGN.lpc.MN', 0.30)
        self.set_input_defaults('DESIGN.duct6.MN', 0.35)
        self.set_input_defaults('DESIGN.hpc.MN', 0.22)
        self.set_input_defaults('DESIGN.bld3.MN', 0.29)
        self.set_input_defaults('DESIGN.burner.MN', 0.1)
        self.set_input_defaults('DESIGN.hpt.MN', 0.35)
        self.set_input_defaults('DESIGN.duct11.MN', 0.3063)
        self.set_input_defaults('DESIGN.lpt.MN', 0.39)
        self.set_input_defaults('DESIGN.duct13.MN', 0.42)
        self.set_input_defaults('DESIGN.byp_bld.MN', 0.47)
        self.set_input_defaults('DESIGN.duct15.MN', 0.49)
        self.set_input_defaults('DESIGN.LP_Nmech', 4000, units='rpm')
        self.set_input_defaults('DESIGN.HP_Nmech', 13000, units='rpm')

        # --- Set up bleed values -----
        
        self.pyc_add_cycle_param('inlet.ram_recovery', 0.9990)
        self.pyc_add_cycle_param('duct4.dPqP', 0.0048)
        self.pyc_add_cycle_param('duct6.dPqP', 0.0101)
        self.pyc_add_cycle_param('burner.dPqP', 0.0540)
        self.pyc_add_cycle_param('duct11.dPqP', 0.0051)
        self.pyc_add_cycle_param('duct13.dPqP', 0.0107)
        self.pyc_add_cycle_param('duct15.dPqP', 0.0149)
        self.pyc_add_cycle_param('core_nozz.Cv', 0.9933)
        self.pyc_add_cycle_param('byp_bld.bypBld:frac_W', 0.005)
        self.pyc_add_cycle_param('byp_nozz.Cv', 0.9939)
        self.pyc_add_cycle_param('hpc.cool1:frac_W', 0.050708)
        self.pyc_add_cycle_param('hpc.cool1:frac_P', 0.5)
        self.pyc_add_cycle_param('hpc.cool1:frac_work', 0.5)
        self.pyc_add_cycle_param('hpc.cool2:frac_W', 0.020274)
        self.pyc_add_cycle_param('hpc.cool2:frac_P', 0.55)
        self.pyc_add_cycle_param('hpc.cool2:frac_work', 0.5)
        self.pyc_add_cycle_param('bld3.cool3:frac_W', 0.067214)
        self.pyc_add_cycle_param('bld3.cool4:frac_W', 0.061256) # MAKING LOWER
        self.pyc_add_cycle_param('hpc.cust:frac_P', 0.5)
        self.pyc_add_cycle_param('hpc.cust:frac_work', 0.5)
        self.pyc_add_cycle_param('hpc.cust:frac_W', 0.0445)
        self.pyc_add_cycle_param('hpt.cool3:frac_P', 1.0)
        self.pyc_add_cycle_param('hpt.cool4:frac_P', 0.0)
        self.pyc_add_cycle_param('lpt.cool1:frac_P', 1.0)
        self.pyc_add_cycle_param('lpt.cool2:frac_P', 0.0)
        self.pyc_add_cycle_param('hp_shaft.HPX', 250.0, units='hp')

        self.od_pts = ['OD_TOfail'] #, 'OD_TO', 'OD_TOC', 'OD_LDG']

        # self.pyc_add_pnt('OD_TOfail', HBTF(design=False, thermo_method='CEA', throttle_mode='T4'))
        # self.pyc_add_pnt('OD_TO', HBTF(design=False, thermo_method='CEA', throttle_mode='T4'))
        # self.pyc_add_pnt('OD_TOC', HBTF(design=False, thermo_method='CEA', throttle_mode='T4'))
        # self.pyc_add_pnt('OD_LDG', HBTF(design=False, thermo_method='CEA', throttle_mode='T4'))
        
        # Single-engine failure during takeoff
        # self.set_input_defaults('OD_TOfail.fc.MN', 0.18)
        # self.set_input_defaults('OD_TOfail.fc.alt', 0., units='ft')
        # self.set_input_defaults('OD_TOfail.fc.dTs', 0., units='degR') # Standard day
        # self.set_input_defaults('OD_TOfail.T4_MAX', 1850., units='degK') # Allow higher TET for takeoff, based on your notes
        # Calculate thrust required for one engine to meet STOL performance after failure of another
        # self.set_input_defaults('OD_TOfail.Fn_DES', 0000.0, units='lbf') # Example - Replace with your calculation
        # self.add_constraint('OD_TOfail.perf.Fn', lower=30000.0)  # Minimum thrust constraint (example value)

        # # Takeoff (all engines operating)
        # self.set_input_defaults('OD_TO.fc.MN', 0.18)
        # self.set_input_defaults('OD_TO.fc.alt', 0., units='ft')
        # self.set_input_defaults('OD_TO.fc.dTs', 0., units='degR')
        # self.set_input_defaults('OD_TO.T4_MAX', 1850., units='degK')
        # # self.set_input_defaults('OD_TO.Fn_DES', 25000.0, units='lbf')
        # # self.add_constraint('OD_TO.perf.Fn', lower=40000.0)  # Minimum thrust constraint (example value)

        # Top-of-climb
        # self.set_input_defaults('OD_TOC.fc.MN', 0.7)
        # self.set_input_defaults('OD_TOC.fc.alt', 30000., units='ft') # Example climb altitude
        # self.set_input_defaults('OD_TOC.fc.dTs', 0., units='degR')
        # self.set_input_defaults('OD_TOC.T4_MAX', 1700., units='degK') # Reduce TET slightly from takeoff
        # # self.set_input_defaults('OD_TOC.Fn_DES', 30000.0, units='lbf')

        # # Landing
        # self.set_input_defaults('OD_LDG.fc.MN', 0.2)
        # self.set_input_defaults('OD_LDG.fc.alt', 0., units='ft')
        # self.set_input_defaults('OD_LDG.fc.dTs', 0., units='degR')
        # self.set_input_defaults('OD_LDG.T4_MAX', 1600., units='degK') # Lower TET for landing
        # # self.set_input_defaults('OD_LDG.Fn_DES', 5000.0, units='lbf')


        # self.pyc_use_default_des_od_conns()

        # # #Set up the RHS of the balances!
        # self.pyc_connect_des_od('core_nozz.Throat:stat:area','balance.rhs:W')
        # self.pyc_connect_des_od('byp_nozz.Throat:stat:area','balance.rhs:BPR')


        super().setup()


if __name__ == "__main__":

    import time

    prob = om.Problem()
    prob.model = mp_hbtf = MPhbtf()

    # 1) Set up an optimizer driver
    prob.driver = om.ScipyOptimizeDriver()
    prob.driver.options["optimizer"] = "SLSQP"
    prob.driver.options["maxiter"] = 20
    prob.driver.options["debug_print"] = ["desvars", "nl_cons", "objs"]
    # Optionally prob.driver.opt_settings = { ... } for advanced control

    # for component in ['DESIGN.core_nozz.ideal_flow', 'DESIGN.core_nozz.staticPs', 'DESIGN.lpt.out_stat', 'DESIGN.byp_bld.out_stat', 'DESIGN.duct13.out_stat', 'DESIGN.byp_nozz.ideal_flow']:
    #     prob.model.set_input_defaults(f'{component}.nonlinear_solver.linesearch.options["print_bound_enforce"]', True)

    # 2) Add design variables
    # Example: HPC PR, fan PR, and T4 at design
    # HPC PR is often the product lpc.PR * hpc.PR, or you can do them individually.
    # We'll assume HPC has a single PR.  If your code is separated, adapt accordingly.
    prob.model.add_design_var("DESIGN.hpc.PR", lower=7.0, upper=13.0, ref=9.5)
    prob.model.add_design_var('DESIGN.lpc.PR', lower=2.5, upper=4.0)
    prob.model.add_design_var("DESIGN.fan.PR", lower=1.4, upper=1.8)  # Fan pressure ratio
    # prob.model.add_design_var("DESIGN.splitter.BPR", lower=4.0, upper=7.0, ref=5.9)  # Bypass ratio    # prob.model.add_design_var("CRZ.T4_MAX", lower=2700.0, upper=3400.0)

    prob.model.add_objective("DESIGN.perf.TSFC", ref0=0.3, ref=0.6)

    # constraints
    # prob.model.add_constraint("OD_TOfail.perf.Fn", lower=30000., units='lbf', ref=32000)
    # prob.model.add_constraint("DESIGN.perf.Fn", lower=5000., units='lbf', ref=5000)
    prob.model.add_constraint("DESIGN.balance.FAR", lower=0.015, upper=0.03, ref=0.025)
    prob.model.add_constraint('DESIGN.fan_dia.FanDia', lower=70.0, upper=90, ref=80.0)
    # prob.model.add_constraint("OD_TOfail.perf.Fn", lower=40000.0, units='lbf')  # must be >= 22000

    recorder = om.SqliteRecorder('N3_opt.sql')
    prob.model.add_recorder(recorder)
    prob.model.recording_options['record_inputs'] = True
    prob.model.recording_options['record_outputs'] = True

    prob.setup()

    # velo ratio
    # prob.set_val('DESIGN.vel_ratio_calc.vel_ratio', 1.2)
    # prob.model.add_constraint('DESIGN.vel_ratio_calc.vel_ratio', lower=1.1, upper=1.3)

    prob.set_val('DESIGN.fc.alt', 28000., units='ft')
    prob.set_val('DESIGN.fc.MN', 0.74)

    prob.set_val('DESIGN.fan.PR', 1.5)
    prob.set_val('DESIGN.lpc.PR', 3)
    prob.set_val('DESIGN.hpc.PR', 9.5)
    prob.set_val('DESIGN.splitter.BPR', 5.9)

    prob.set_val('DESIGN.fan.eff', 0.8948)
    prob.set_val('DESIGN.lpc.eff', 0.9243)
    prob.set_val('DESIGN.hpc.eff', 0.907)

    prob.set_val('DESIGN.hpt.eff', 0.8888)
    prob.set_val('DESIGN.lpt.eff', 0.8996)

    prob.set_val('DESIGN.T4_MAX', 1600, units='degK')
    prob.set_val('DESIGN.Fn_DES', 10000.0, units='lbf')
    
    # Set initial guesses for balances
    prob['DESIGN.balance.FAR'] = 0.025
    prob['DESIGN.balance.W'] = 800.
    prob['DESIGN.balance.lpt_PR'] = 4.0
    prob['DESIGN.balance.hpt_PR'] = 6.0
    prob['DESIGN.fc.balance.Pt'] = 5.2
    prob['DESIGN.fc.balance.Tt'] = 440.0

    # prob.set_val('DESIGN.fan_dia.FanDia', 80, units='inch')

    # --- Off-Design Points ---
    # (Set values for OD_TOfail, OD_TO, OD_TOC, OD_LDG as described above)
    # prob.set_val('OD_TOfail.fc.MN', 0.18)
    # prob.set_val('OD_TOfail.fc.alt', 0.0, units='ft')
    # prob.set_val('OD_TOfail.fc.dTs', 0.0, units='degR')
    # prob.set_val('OD_TOfail.T4_MAX', 1850., units='degK')
    # prob.set_val('OD_TOfail.Fn_DES', 66000.0, units='lbf') # Example - Replace with your calculation
    # prob.model.add_constraint("OD_TOfail.perf.Fn", lower=30000.0, units='lbf')  # must be >= 22000
    # prob.model.add_constraint("OD_TOfail.Fn_DES", lower=30000.0, units='lbf')  # must be >= 22000

    # for pt in ['OD_TOfail']: #, 'OD_TO']: #, 'OD_TOC', 'OD_LDG']:
    #     # initial guesses
    #     prob[pt+'.balance.FAR'] = 0.03
    #     prob[pt+'.balance.W'] = 1500
    #     prob[pt+'.balance.BPR'] = 6
    #     prob[pt+'.balance.lp_Nmech'] = 5000 
    #     prob[pt+'.balance.hp_Nmech'] = 15000 
    #     prob[pt+'.hpt.PR'] = 3.
    #     prob[pt+'.lpt.PR'] = 2.
    #     prob[pt+'.fan.map.RlineMap'] = 2.0
    #     prob[pt+'.lpc.map.RlineMap'] = 2.0
    #     prob[pt+'.hpc.map.RlineMap'] = 2.0

    st = time.time()

    prob.set_solver_print(level=-1)
    prob.set_solver_print(level=2, depth=1)

    viewer_file = open('hbtf_view.out', 'w')
    prob.run_driver()

    # file
    date_time = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime())
    # create file:
    import os
    os.makedirs('output_data', exist_ok=True)
    viewer_file = open(f'output_data/hbtf2_{date_time}.out', 'w')
    for pt in ['DESIGN']+prob.model.od_pts:
        viewer(prob, pt, file=viewer_file)
    # print("OD_TOfail Point")
    # viewer(prob, 'OD_TOfail', file=viewer_file)

    # print("OD_TO Point")
    # viewer(prob, 'OD_TO', file=viewer_file)

    # print("OD_TOC Point")
    # viewer(prob, 'OD_TOC', file=viewer_file)

    # print("OD_LDG Point")
    # viewer(prob, 'OD_LDG', file=viewer_file)

    print()
    print("Run time", time.time() - st)