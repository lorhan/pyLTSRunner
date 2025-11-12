import matplotlib.pyplot as plt
import pyLTSRunner as pltsr
import numpy as np
import os


def demonstrate_library_management():
    runner = pltsr.pyLTSRunner()
    
    # Windows example
    # dirLTSpice = r"C:\Users\Nutzer\AppData\Local\LTspice\lib"
    
    # Linux (with Wine) example:
    dirLTSpice = os.path.expanduser("~/.wine/drive_c/users/victor/Documents/LTspiceXVII/lib")

    
    
    dirSub = os.path.join(dirLTSpice,"sub")
    dirSym = os.path.join(dirLTSpice,"sym")
    runner.copy_libfiles_to_ltspice_dir(dirSub, dirSym, dirLocalLibFiles="library_files")


def demonstrate_browsing_results():
    runner = pltsr.pyLTSRunner()

    pathResults = "Flyback_RawFiles"
    lidiReturnData = runner.get_results(pathResults)
    for diResultData in lidiReturnData:
        raw = runner.rawRead(diResultData["rawFile"])
        time = raw.get_axis()[::10]
        Uout = raw.get_trace("V(Uout)").get_wave()[::10]
        plt.plot(time, Uout, label = diResultData["simRunBaseName"])
    plt.grid()
    plt.legend()
    plt.show()

def demonstrate_running_simulation():
    jobdescription = "flyback.json"
    # jobdescription = "simpleRLC.json"
    runner = pltsr.pyLTSRunner()
    lidiReturnData = runner.run_simulation_from_jobfile(jobdescription)
    print(lidiReturnData)


if __name__ == "__main__":
    print("Start of demonstration")

    # demonstrate_library_management()
    
    # demonstrate_running_simulation()

    demonstrate_browsing_results()
    
    print("End of demonstration")