import matplotlib.pyplot as plt
import pyLTSRunner as pltsr
import numpy as np


def demonstrate_library_management():
    dirLTSpice = r"C:\Users\Nutzer\AppData\Local\LTspice\lib"
    pltsr.copy_libfiles_to_ltspice_dir(dirSub=dirLTSpice+"\sub", dirSym=dirLTSpice+"\sym", dirLocalLibFiles="library_files")


# jobdescription = "flyback.json"
# # jobdescription = "simpleRLC.json"
# lidiReturnData = pltsr.handler_for_usage_test(jobdescription)


# for diReturnData in lidiReturnData:
#     raw = pltsr.rawRead(diReturnData["rawFile"])
#     time = raw.get_axis()
#     Uout = raw.get_trace('V(Uout)').get_wave()
#     plt.plot(time, Uout,label = diReturnData["simRunBaseName"])


# plt.legend()
# plt.grid()
# plt.show()


if __name__ == "__main__":
    print("Start of demonstration")

    demonstrate_library_management()

    print("End of demonstration")