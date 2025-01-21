import math


def convert_fan_area_to_diameter(area, hub_tip=0.3125):
    '''
    convert area in inches squared to diameter in meters
    using equation: FanDia = 2.0*(area/(pi*(1.0-hub_tip**2.0)))**0.5
    '''
    return 2.0*(area/(math.pi*(1.0-hub_tip**2.0)))**0.5


if __name__ == "__main__":
    print(convert_fan_area_to_diameter(5462))