


problem: 
- the Area is set in on design, cruise. which is small for small thrust.
- so fails for off design high thrust. 

- can try thrust scaling, switching od/ond, chaning balancing, optimizing, constraining area somehow.


 
Set Core Velocity 20% Higher (Design Point):

To achieve the core velocity being approximately 20% higher than the bypass velocity at the design point, you need to add a specific constraint that relates these two velocities. Here's how you can do it:

Add an ExecComp: In the HBTF class's setup method (within the if design: block), add an ExecComp that calculates the ratio between core and bypass velocities:
self.add_subsystem('vel_ratio', om.ExecComp('ratio = core_V / byp_V',
                                            core_V={'val': 1000., 'units': 'ft/s'},
                                            byp_V={'val': 1000., 'units': 'ft/s'},
                                            ratio={'val': 1.2, 'units': None}))


Fan diameeter constraint too

use rolling take off t4: RTO_T4 for the engine failure?

RTO, STS, CRZ (rolling take off, sea level static, and cruise.)

i will have RTO, LDG, LHR