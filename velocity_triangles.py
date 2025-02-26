#!/usr/bin/env python3
"""
Example script to plot three velocity triangles (Stator/Nozzle, Rotor Inlet, Rotor Exit)
side-by-side, each with a simplified blade shape and labeled velocity vectors.

- Subplot 1 (index 0): Stator (or Nozzle)
- Subplot 2 (index 1): Rotor Inlet
- Subplot 3 (index 2): Rotor Exit

Author: [Your Name]
Date:   [Date]
"""

import numpy as np
import matplotlib.pyplot as plt

def draw_blade(ax, blade_type="stator"):
    """
    Draw a simplified blade shape on the given Axes 'ax'.
    'blade_type' can be 'stator' or 'rotor' to pick a shape.
    """
    if blade_type == "stator":
        # A simple curved shape for a nozzle guide vane
        x_pts = [0.0,  0.2,  0.7, 1.0, 1.2, 1.0, 0.6, 0.3, 
