import matplotlib.pyplot as plt
import numpy as np


def plot_turbine_maps(
    prob,
    element_names,
    eff_vals=np.array([0, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]),
    alphas=[0],
):

    for e_name in element_names:
        comp = prob.model._get_subsystem(e_name)
        map_data = comp.options["map_data"]

        s_Wp = prob[e_name + ".s_Wp"]
        s_PR = prob[e_name + ".s_PR"]
        s_eff = prob[e_name + ".s_eff"]
        s_Np = prob[e_name + ".s_Np"]

        # Corrected meshgrid for Wp and Np
        PRmap, NpMap = np.meshgrid(map_data.PRmap, map_data.NpMap, sparse=False)
        for alpha in alphas:
            scaled_PR = (PRmap - 1.) * s_PR + 1.
            # scaled_PR = (map_data.PRmap[alpha,:,:]) * s_PR 

            plt.figure(figsize=(11, 8))

            # Ensure contour plots work with correct axis scaling
            Nc = plt.contour(map_data.WpMap[alpha,:,:]*s_Wp, scaled_PR, NpMap*s_Np,
                             colors='k', levels=np.linspace(NpMap.min(), NpMap.max(), num=10))
            
            eff = plt.contourf(map_data.WpMap[alpha,:,:]*s_Wp, scaled_PR, map_data.effMap[alpha,:,:]*s_eff, 
                               levels=eff_vals, cmap="viridis")

            plt.colorbar(eff)

            plt.plot(prob[e_name + ".Wp"], prob[e_name + ".map.scalars.PR"][0], "ko")

            plt.clabel(Nc, fontsize=9, inline=False)
            # Expand x-axis (Wp) if needed to prevent zoom-in
            plt.xlim(map_data.WpMap[alpha,:,:].min() * s_Wp * 0.8, 
                     map_data.WpMap[alpha,:,:].max() * s_Wp * 1.2)

            plt.xlabel("Wp, lbm/s")  # Fixed label
            plt.ylabel("PR (Pressure Ratio)")
            plt.title(f"Turbine Map: {e_name}")

            plt.savefig(e_name + ".pdf")
