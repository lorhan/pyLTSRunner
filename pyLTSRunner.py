from PyLTSpice import SimRunner, SpiceEditor, LTspice, RawRead
import matplotlib.pyplot as plt
import numpy as np

import json
from jsonschema import validate
from jsonschema.exceptions import ValidationError

import argparse

def get_validated_json_data(filepath_json):

    schema = {
        "type": "object",
        "properties": {
            "PATH_SPICE_MODEL": {"type": "string"},
            "DIR_OUTPUT_RAW": {"type": "string"},
            "DIR_STORAGE_NPZ": {"type": "string"},
            "PRL_SIMS": {"type": "integer", "minimum": 1},
        },
        "required": ["PATH_SPICE_MODEL", "DIR_OUTPUT_RAW", "DIR_STORAGE_NPZ", "PRL_SIMS"]
    }
    # Read JSON data from file
    with open(filepath_json, "r") as f:
        jobDesc = json.load(f)

    # Validate
    try:
        validate(instance=jobDesc, schema=schema)
        print("JSON is valid!")
    except ValidationError as e:
        exception_message = f"JSON validation error:{e.message}"
        raise Exception(exception_message)

    return jobDesc



def processing_data(raw_file, log_file):
    """This is the function that will process the data from simulations"""
    print("Handling the simulation data of %s, log file %s" % (raw_file, log_file))



if __name__ == "__main__":


    parser = argparse.ArgumentParser(
                    prog='pyLTSRunner',
                    description='Automates LTSpice simulations, including parallel simulations and .npz export of results',
                    epilog='By VicCos')
    parser.add_argument('-jobd', '--jobdescription', required=True, help="path tho Json file containing the job description.")
    args = parser.parse_args()



    # filepath_json = "myJson.json"
    jobDesc = get_validated_json_data(args.jobdescription)

    # Configures the simulator to use and output folder. Also defines the number of parallel simulations
    runner = SimRunner(output_folder=f'./{jobDesc["DIR_OUTPUT_RAW"]}', simulator=LTspice, parallel_sims=jobDesc["PRL_SIMS"])

    netlist = SpiceEditor(jobDesc["PATH_SPICE_MODEL"])  # Open the Spice Model, and creates the .net
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


    myRecData = data = np.load(f"{jobDesc['DIR_STORAGE_NPZ']}/R1_{liResValues[1]}.npz", allow_pickle=True)
    breakpoint()