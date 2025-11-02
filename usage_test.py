import matplotlib.pyplot as plt
import pyLTSRunner as pltsr


jobdescription = "myJson.json"
pltsr.handler_for_usage_test(jobdescription)




liResValues = [f"{n}" for n in [1,2,3,4]]
diUouts = {}
for resval in liResValues:
    raw = RawRead(f"{jobDesc['DIR_OUTPUT_RAW']}/R1_{resval}.raw")
    time = raw.get_axis()
    Uout = raw.get_trace('V(Uout)').get_wave()
    diUouts[resval] = Uout

    np.savez_compressed(
        f"{jobDesc['DIR_STORAGE_NPZ']}/R1_{resval}.npz",
        time=time,
        Uout=Uout,
        description=f"Data for R1_{resval} dadas")


    plt.plot(time, Uout,label = f"R1={resval}")

for n in diUouts.keys():
    print(f"R1={n}: {len(diUouts[n])} values")
# breakpoint()






plt.legend()
plt.grid()
plt.show()

for diMods in jobDesc['LIST_OF_MODIFICATIONS']:
    for mymods in diMods.keys():
        print(f"{mymods}:{diMods[mymods]}")



myRecData = np.load(f"{jobDesc['DIR_STORAGE_NPZ']}/R1_{liResValues[1]}.npz", allow_pickle=True)
breakpoint()