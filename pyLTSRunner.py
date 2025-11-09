from PyLTSpice import SimRunner, SpiceEditor, LTspice, RawRead
import matplotlib.pyplot as plt
import numpy as np

import json
from jsonschema import validate
from jsonschema.exceptions import ValidationError
import shutil
import os


import argparse


#==================================================================================
def get_validated_json_data(filepath_json):

    schema = {
        "type": "object",
        "properties": {
            "PATH_SPICE_MODEL": {"type": "string"},
            "DIR_OUTPUT_RAW": {"type": "string"},
            "PRL_SIMS": {"type": "integer", "minimum": 1},
            "LIST_OF_MODIFICATIONS": {"type":"array"},
        },
        "required": ["PATH_SPICE_MODEL", "DIR_OUTPUT_RAW", "PRL_SIMS","LIST_OF_MODIFICATIONS"]
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


def sanity_check_for_netlist(netlist):

    liComps = set(netlist.get_components())
    setComps = set(liComps)
    liParams = set(netlist.get_all_parameter_names())
    setParams = set(liParams)
    
    # CHECK: you cant have multiple components with the same name
    liDuplicateComps = [i for i in setComps if liComps.count(i) > 1]
    if(len(liDuplicateComps) > 0):
        strReportError = "ERROR: you cant have multiple components with the same name."
        strReportError += f"\nHere is a list with the repeats: {liDuplicateComps}" 
        raise Exception(strReportError)
    
    # CHECK: you cant have multiple parameters with the same name
    liDuplicateParams = [i for i in setParams if liParams.count(i) > 1]
    if(len(liDuplicateParams) > 0):
        strReportError = "ERROR: you cant have multiple parameters with the same name."
        strReportError += f"\nHere is a list with the repeats: {liDuplicateParams}" 
        raise Exception(strReportError)
    
    # CHECK: you cant have repeated names among components and parameters
    setIntersecCompsParams = setComps & setParams
    if(len(setIntersecCompsParams) > 0):
        strReportError = "ERROR: you cant have names which are both a component and a parameter."
        strReportError += f"\nHere is a list with the problem-names: {setIntersecCompsParams}" 
        raise Exception(strReportError)

    print("PASSED: sanity check for netlist.")


# def sanity_check_for_list_of_modifications(liModifs):
#     # CHECK: Sanity check for modification list
#     liCompNamesInModif = []
#     liParamNamesInModif = []
#     for rawModifItem in liModifs:
#         modifItem = get_parsed_and_sanity_checked_modif_item(rawModifItem)
#         if(modifItem["type"] == "Comp"):
#             liCompNamesInModif.append(modifItem["name"])
#         else:
#             liParamNamesInModif.append(modifItem["name"])
    
#     liDuplCompNames = set([i for i in set(liCompNamesInModif) if liCompNamesInModif.count(i) > 1])
#     if(len(liDuplCompNames) > 0):
#         strReportError = "ERROR: you cant have multiple parameters with the same name."
#         strReportError += f"\nHere is a list with the repeats: {liDuplicateParams}" 
#         raise Exception(strReportError)

    

def get_parsed_and_sanity_checked_modif_item(str_raw_modif_item):
    liAux = str_raw_modif_item.split(":")
    liAux = [n.strip() for n in liAux]

    errorCheck1 = len(liAux) != 3 
    errorCheck2 = liAux[0] not in ["Comp","Param"]
    if(any([errorCheck1, errorCheck2])):
        strReportError = f"ERROR: invalid modification item: {str_raw_modif_item}."
        raise Exception(strReportError)

    return{"type":liAux[0],"name":liAux[1],"value":liAux[2]}




#==================================================================================
def processing_data(raw_file, log_file):
    """This is the function that will process the data from simulations"""
    print("Handling the simulation data of %s, log file %s" % (raw_file, log_file))


#==================================================================================
def run_simulations(jobDesc):

    # Configures the simulator to use and output folder. Also defines the number of parallel simulations
    runner = SimRunner(output_folder=f'./{jobDesc["DIR_OUTPUT_RAW"]}', simulator=LTspice, parallel_sims=jobDesc["PRL_SIMS"])

    # Open the Spice Model, and creates the .net
    netlist = SpiceEditor(jobDesc["PATH_SPICE_MODEL"])  

    
    nrModifs = len(jobDesc["LIST_OF_MODIFICATIONS"])
    nrZeroPads = int(np.ceil(np.log10(nrModifs)))
    liRunBaseNames = []
    lidiReturnData = []
    for cnt,modifData in enumerate(jobDesc["LIST_OF_MODIFICATIONS"]):
        
        for rawModifItem in modifData["ModifList"]:
            parModIt = get_parsed_and_sanity_checked_modif_item(rawModifItem)
            if(parModIt["type"] == "Comp"):
                netlist.set_component_value(parModIt["name"] , parModIt["value"] )
            else:
                netlist.set_parameter(parModIt["name"] , parModIt["value"] )

        
        simRunBaseName = f"Modif_{str(cnt).zfill(nrZeroPads)}_{modifData['ModifDescription']}"
        liRunBaseNames.append(simRunBaseName)
        # overriding he automatic netlist naming
        run_netlist_file = f"{simRunBaseName}.net"
        # This will launch up to 'parallel_sims' simulations in background before waiting for resources
        runner.run(netlist, run_filename=run_netlist_file, callback=processing_data)
        rawFile = f"{jobDesc['DIR_OUTPUT_RAW']}/{simRunBaseName}.raw"
        lidiReturnData.append({"modifData":modifData,"simRunBaseName":simRunBaseName,"rawFile":rawFile})
    # This will wait for the all the simulations launched before to complete.
    runner.wait_completion()



    # Sim Statistics
    print('Successful/Total Simulations: ' + str(runner.okSim) + '/' + str(runner.runno))
    return lidiReturnData

#==================================================================================
def rawRead(rawFile):
    return RawRead(rawFile)



#==================================================================================
def handler_for_usage_test(jobDesc_input):
        # filepath_json = "myJson.json"
    jobDesc = get_validated_json_data(jobDesc_input)
    diReturnData = run_simulations(jobDesc)
    return diReturnData

#==================================================================================
def copy_libfiles_to_ltspice_dir(dirSub, dirSym, dirLocalLibFiles):
    try:
        for file in os.listdir(dirLocalLibFiles):
            fileFullPath = os.path.abspath(os.path.join(dirLocalLibFiles, file))
            if(file.lower().endswith(".asy")):
                shutil.copy(fileFullPath, dirSym)
            elif(file.lower().endswith(".sub")):
                shutil.copy(fileFullPath, dirSub)
    except Exception as e:
        raise Exception(f"Error in copy_libraries_to_ltspice_dir:\n{e}")
    

#==================================================================================
if __name__ == "__main__":


    parser = argparse.ArgumentParser(
                    prog='pyLTSRunner',
                    description='Automates LTSpice simulations, including parallel simulations and .npz export of results',
                    epilog='By VicCos')
    parser.add_argument('-jobd', '--jobdescription', required=True, help="path tho Json file containing the job description.")
    args = parser.parse_args()



    # filepath_json = "myJson.json"
    jobDesc = get_validated_json_data(args.jobdescription)
    run_simulations(jobDesc)



    liResValues = [f"{n}" for n in [1,2,3,4]]
    diUouts = {}
    for resval in liResValues:
        raw = RawRead(f"{jobDesc['DIR_OUTPUT_RAW']}/R1_{resval}.raw")
        time = raw.get_axis()
        Uout = raw.get_trace('V(Uout)').get_wave()
        diUouts[resval] = Uout


        plt.plot(time, Uout,label = f"R1={resval}")

    for n in diUouts.keys():
        print(f"R1={n}: {len(diUouts[n])} values")
    # breakpoint()




    for diMods in jobDesc['LIST_OF_MODIFICATIONS']:
        for mymods in diMods.keys():
            print(f"{mymods}:{diMods[mymods]}")


    plt.legend()
    plt.grid()
    plt.show()

