import math


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


if __name__ == "__main__":
    print(convert_fan_area_to_diameter(4529.646))
    print(convert_dia_to_fan_area(86, units='in'))
    print(convert_dia_to_fan_area(78.5, units='in'))
