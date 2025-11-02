import matplotlib.pyplot as plt
import pyLTSRunner as pltsr
import numpy as np

jobdescription = "simpleRLC.json"
diJobSimData = pltsr.handler_for_usage_test(jobdescription)



for runBaseName in diJobSimData["liRunBaseNames"]:
    npzFile = f"{diJobSimData['jobDesc']['DIR_STORAGE_NPZ']}/{runBaseName}.npz"
    myRecData = np.load(npzFile, allow_pickle=True)
    plt.plot(myRecData["time_s"]*1000, myRecData["Uout_V"], label = runBaseName)
    

plt.ylabel(r'$U_{out}$ in V')
plt.xlabel(r'Time in s')
plt.legend()
plt.grid()
plt.show()

# liResValues = [f"{n}" for n in [1,2,3,4]]
# diUouts = {}
# for resval in liResValues:
#     raw = RawRead(f"{jobDesc['DIR_OUTPUT_RAW']}/R1_{resval}.raw")
#     time = raw.get_axis()
#     Uout = raw.get_trace('V(Uout)').get_wave()
#     diUouts[resval] = Uout

#     np.savez_compressed(
#         f"{jobDesc['DIR_STORAGE_NPZ']}/R1_{resval}.npz",
#         time=time,
#         Uout=Uout,
#         description=f"Data for R1_{resval} dadas")


#     plt.plot(time, Uout,label = f"R1={resval}")

# for n in diUouts.keys():
#     print(f"R1={n}: {len(diUouts[n])} values")
# # breakpoint()






# plt.legend()
# plt.grid()
# plt.show()

# for diMods in jobDesc['LIST_OF_MODIFICATIONS']:
#     for mymods in diMods.keys():
#         print(f"{mymods}:{diMods[mymods]}")



# myRecData = np.load(f"{jobDesc['DIR_STORAGE_NPZ']}/R1_{liResValues[1]}.npz", allow_pickle=True)
# breakpoint()