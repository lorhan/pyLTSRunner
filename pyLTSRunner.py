from PyLTSpice import SimRunner, SpiceEditor, LTspice, RawRead
import matplotlib.pyplot as plt
import numpy as np




NR_CORES = 2
DIR_OUTPUT_RAW = "temp_batch3"
DIR_STORAGE_NPZ = "results_in_npz"
PATH_SPICE_MODEL = "LTSPiceModel/Draft1.asc"

def processing_data(raw_file, log_file):
    """This is the function that will process the data from simulations"""
    print("Handling the simulation data of %s, log file %s" % (raw_file, log_file))

# Configures the simulator to use and output folder. Also defines the number of parallel simulations
runner = SimRunner(output_folder=f'./{DIR_OUTPUT_RAW}', simulator=LTspice, parallel_sims=NR_CORES)

netlist = SpiceEditor(PATH_SPICE_MODEL)  # Open the Spice Model, and creates the .net
# set default arguments
netlist.set_component_value('R1', '5')  # Modifying the value of a resistor

liResValues = [f"{n}" for n in [1,2,3,4]]


for res_value in liResValues:
    netlist.set_component_value('R1', res_value)
    # overriding he automatic netlist naming
    run_netlist_file = f"R1_{res_value}.net"
    # This will launch up to 'parallel_sims' simulations in background before waiting for resources
    runner.run(netlist, run_filename=run_netlist_file, callback=processing_data)

# This will wait for the all the simulations launched before to complete.
runner.wait_completion()
# The timeout counter is reset everytime a simulation is finished.

# Sim Statistics
print('Successful/Total Simulations: ' + str(runner.okSim) + '/' + str(runner.runno))


diUouts = {}
for resval in liResValues:
    raw = RawRead(f"{DIR_OUTPUT_RAW}/R1_{resval}.raw")
    time = raw.get_axis()
    Uout = raw.get_trace('V(Uout)').get_wave()
    diUouts[resval] = Uout

    np.savez_compressed(
        f"{DIR_STORAGE_NPZ}/R1_{resval}.npz",
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


myRecData = data = np.load(f"{DIR_STORAGE_NPZ}/R1_{liResValues[1]}.npz", allow_pickle=True)
breakpoint()