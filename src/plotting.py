import matplotlib.pyplot as plt
import numpy as np
import openmdao.api as om
import pycycle.api as pyc


def plot_turbine_maps(case, element_names, eff_vals=np.linspace(0, 1, 11)):

    for e_name in element_names:
        try:
            # Extract stored turbine map scalars from the case
            s_Wp = case.get_val(f"{e_name}.map.scalars.s_Wp")
            s_PR = case.get_val(f"{e_name}.map.scalars.s_PR")
            s_eff = case.get_val(f"{e_name}.map.scalars.s_eff")
            s_Np = case.get_val(f"{e_name}.map.scalars.s_Np")

            # Get the correct turbine map data
            if "hpt" in e_name:
                map_data = pyc.HPTMap
            elif "lpt" in e_name:
                map_data = pyc.LPTMap
            else:
                raise ValueError(f"Unknown turbine type: {e_name}")

            PRmap, NpMap = np.meshgrid(map_data.PRmap, map_data.NpMap, sparse=False)

            plt.figure(figsize=(11, 8))
            alpha = 0

            Nc = plt.contour(map_data.WpMap[alpha,:,:] * s_Wp, PRmap * s_PR, NpMap * s_Np, colors='k', levels=map_data.NpMap * s_Np)
            plt.clabel(Nc, fontsize=9, inline=False)

            eff = plt.contourf(map_data.WpMap[alpha,:,:] * s_Wp, PRmap * s_PR, map_data.effMap[alpha,:,:] * s_eff, levels=eff_vals)
            plt.clabel(eff, fontsize=9, inline=False)
            plt.colorbar(eff)

            # Plot actual operating point if data exists
            # plt.plot(case[f"{e_name}.Wp"], case[f"{e_name}.map.scalars.PR"][0], 'ko')

            plt.xlabel("Wp, lbm/s")
            plt.ylabel("PR")
            plt.title(e_name)

            plt.savefig(f"{e_name}.png")  

        except KeyError as e:
            print(f"Error: Missing key in case data for {e_name} - {e}")


def plot_compressor_maps(case, element_names, eff_vals=np.linspace(0, 1, 11), alphas=[0]):
    for e_name in element_names:
        try:
            # Extract stored variables from the case
            s_Wc = case.get_val(f"{e_name}.map.scalars.s_Wc")
            s_PR = case.get_val(f"{e_name}.map.scalars.s_PR")
            s_eff = case.get_val(f"{e_name}.map.scalars.s_eff")
            s_Nc = case.get_val(f"{e_name}.map.scalars.s_Nc")

            # Extract performance values
            # Wc_actual = case.get_val(f"{e_name}.corrinputs.Wc", None)
            # PR_actual = case.get_val(f"{e_name}.map.scaledOutput.PR", [None])[0]

            # Get compressor map data manually
            if "hpc" in e_name:
                map_data = pyc.HPCMap
            elif "lpc" in e_name:
                map_data = pyc.LPCMap
            else:
                map_data = pyc.FanMap
            RlineMap, NcMap = np.meshgrid(map_data.RlineMap, map_data.NcMap, sparse=False)

            for alpha in alphas:
                scaled_PR = (map_data.PRmap[alpha,:,:] - 1.) * s_PR + 1.

                plt.figure(figsize=(11, 8))
                Nc = plt.contour(map_data.WcMap[alpha,:,:] * s_Wc, scaled_PR, NcMap * s_Nc, colors='k', levels=map_data.NcMap * s_Nc)
                R = plt.contour(map_data.WcMap[alpha,:,:] * s_Wc, scaled_PR, RlineMap, colors='k', levels=map_data.RlineMap)
                eff = plt.contourf(map_data.WcMap[alpha,:,:] * s_Wc, scaled_PR, map_data.effMap[alpha,:,:] * s_eff, levels=eff_vals)

                plt.colorbar(eff)

                # Plot actual operating point
                plt.plot(case[f"{e_name}.Wc"], case[f"{e_name}.map.scalars.PR"][0], 'ko')

                plt.clabel(Nc, fontsize=9, inline=False)
                plt.clabel(R, fontsize=9, inline=False)

                plt.xlabel('Wc, lbm/s')
                plt.ylabel('PR')
                plt.title(e_name)

                # SAVE AS PDF FOR FINAL
                plt.savefig(f"{e_name}.png")  

        except KeyError as e:
            print(f"Error: Missing key in case data for {e_name} - {e}")


def post_map_plots(case, pt):
    """
    Plots compressor and turbine maps using a recorded OpenMDAO Case object.
    """
    comp_names = ["fan", "lpc", "hpc"]
    comp_full_names = [f'{pt}.{c}' for c in comp_names]

    plot_compressor_maps(case, comp_full_names)

    turb_names = ["hpt", "lpt"]
    turb_full_names = [f'{pt}.{t}' for t in turb_names]

    plot_turbine_maps(case, turb_full_names)


if __name__ == "__main__":
    # cr = om.CaseReader("N3ref_out/N3_opt.sql")  # Load the saved file
    # case = cr.get_case(-1)  # Retrieve the last saved iteration
    # post_map_plots(case, "TOC")  # Plot the compressor and turbine maps

    cr = om.CaseReader("optim_hbtf_out/N3_opt.sql")  # Load the saved file
    case = cr.get_case(-1)  # Retrieve the last saved iteration
    post_map_plots(case, "DESIGN")  # Plot the compressor and turbine maps
    
    # List all variables stored in the recorded case
    # outputs = case.list_outputs(out_stream=None)  # Get a list of recorded variables
    # print("Variables recorded in case:")
    # filtered_outputs = [name for name, meta in outputs if "lpt" in name or "hpt" in name]
    # # filtered_outputs = [name for name, meta in outputs if "fan" in name or "lpc" in name or "hpc" in name]

    # print("\n **Filtered Compressor Variables:**")
    # for var in filtered_outputs:
    #     print(var)

    # print(case["DESIGN.perf.TSFC"])  # Example: Access a saved variable
