import matplotlib.pyplot as plt
import pyLTSRunner as pltsr
import numpy as np

jobdescription = "simpleRLC.json"
lidiReturnData = pltsr.handler_for_usage_test(jobdescription)


for diReturnData in lidiReturnData:
    raw = pltsr.rawRead(diReturnData["rawFile"])
    time = raw.get_axis()
    Uout = raw.get_trace('V(Uout)').get_wave()
    plt.plot(time, Uout,label = diReturnData["simRunBaseName"])


plt.legend()
plt.grid()
plt.show()