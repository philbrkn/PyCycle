import math


def calculate_cruise_thrust_req():
    # at 28k ft, M =0.74
    V = 0.74 * math.sqrt(1.4*287*230)
    rho = 0.475
    S = 353
    Cd = 0.0111
    drag = 0.5 * rho * V ** 2 * S * Cd
    # get thrust in lbf
    return drag * 0.224809


def convert_fan_area_to_diameter(area, hub_tip=0.3125):
    '''
    convert area in inches squared to diameter in inches
    using equation: FanDia = 2.0*(area/(pi*(1.0-hub_tip**2.0)))**0.5
    '''
    # convert area to meters squared
    area = area*0.00064516
    fan_dia = 2.0*(area/(math.pi*(1.0-hub_tip**2.0)))**0.5
    # convert to inches
    return fan_dia/0.0254


def convert_dia_to_fan_area(dia, units='m', hub_tip=0.3125):
    '''
    convert diameter in meters to area in inches squared
    using equation: area = pi*(dia/2.0)**2.0*(1.0-hub_tip**2.0)
    units can be meters or inches
    return area in inches squared
    '''
    if units == 'm':
        return math.pi*(dia/2.0)**2.0*(1.0-hub_tip**2.0)
    elif units == 'in':
        # convert dia to meters
        dia = dia*0.0254
        area_m2 = math.pi*(dia/2.0)**2.0*(1.0-hub_tip**2.0)
        # convert to inches squared
        return area_m2/0.00064516
    else:
        raise ValueError('units must be "m" or "in"')


def calculate_weight_from_thrust():
    Srunway = 450 # takeoff distance, meters
    Vto = 61.8  # m/s 
    mass = 353e3 # kg
    Cd = 0.03 # ASSUMING THIS, JUSTIFY
    S = 200 #  wing area, m^2
    mu = 0.03  # friction coefficient , JUSTIFY

    accel = Vto**2/(2*Srunway)
    Fnet = mass * accel
    # T = Fnet + D + Fr
    D = 0.5* 1.225* Vto**2 * Cd * S
    Fr = mu * mass * 9.81
    T = Fnet + D + Fr
    # convert Newtons to lbf
    Tlbf = T * 0.224809
    return Tlbf/4


if __name__ == "__main__":
    print(calculate_weight_from_thrust(), " lbf per engine at takeoff")

    # print(calculate_cruise_thrust_req())
    # area_from_optim = 4199.646
    # fan_dia_from_optim = convert_fan_area_to_diameter(area_from_optim)
    # pw_f117_area = convert_dia_to_fan_area(78.5, units='in')
    # print(fan_dia_from_optim)
    # print(f"change in area: {area_from_optim/ pw_f117_area - 1} ")
    # print(convert_dia_to_fan_area(86, units='in'))
    
    # inlet_area = 4199
    # inlet_diameter = math.sqrt(inlet_area / math.pi) * 2
    # print(inlet_diameter)
