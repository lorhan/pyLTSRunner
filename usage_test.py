import matplotlib.pyplot as plt
import pyLTSRunner as pltsr
import numpy as np
import pywt
from scipy import sparse


def demonstrate_library_management():
    runner = pltsr.pyLTSRunner()
    dirLTSpice = r"C:\Users\Nutzer\AppData\Local\LTspice\lib"
    runner.copy_libfiles_to_ltspice_dir(dirSub=dirLTSpice+"\sub", dirSym=dirLTSpice+"\sym", dirLocalLibFiles="library_files")


def demonstrate_browsing_results():
    runner = pltsr.pyLTSRunner()

    pathResults = "Flyback_RawFiles"
    lidiReturnData = runner.get_results(pathResults)
    for diResultData in lidiReturnData[0:1]:
        raw = runner.rawRead(diResultData["rawFile"])
        time = raw.get_axis()
        Uout = raw.get_trace("V(Ugate)").get_wave()



        plt.plot(time, Uout, label = diResultData["simRunBaseName"])


        # You can tune:
        # * The wavelet type ('db1', 'db4', 'sym5', 'coif3', etc.)
        # * The decomposition level (pywt.wavedec(data, wavelet, level=n))
        # * The threshold (higher = more compression, lower = better reconstruction)

        # 1️⃣ Decompose signal using DWT
        wavelet = 'db4'  # Daubechies 4 wavelet
        coeffs = pywt.wavedec(Uout, wavelet)

        # 2️⃣ Apply thresholding to compress (zero out small coefficients)
        threshold = 0.1  # adjust this to control compression strength
        coeffs_thresh = [pywt.threshold(c, threshold, mode='soft') for c in coeffs]

        # 3️⃣ Reconstruct the signal
        Uout_recov = pywt.waverec(coeffs_thresh, wavelet)[0:len(Uout)]

        # np.savez_compressed(
        #     'wavelet_compressed.npz',
        #     coeffs=coeffs_thresh,
        #     wavelet=wavelet
        # )


        # np.savez_compressed('wavelet_compressed.npz',coeffs=coeffs_thresh,wavelet=wavelet)
        sparse_coeffs = [sparse.csr_matrix(c) for c in coeffs_thresh]
        np.savez_compressed('npexport_wavelet_sparse_scipy.npz', coeffs=sparse_coeffs)
        np.savez_compressed('npexport_raw.npz', Uout=Uout)


        loaded = np.load('npexport_wavelet_sparse_scipy.npz', allow_pickle=True)
        coeffs_loaded = [c.toarray().ravel() for c in loaded['coeffs']]
        Uout_recov2 = pywt.waverec(coeffs_loaded, wavelet)[0:len(time)]



        breakpoint()


        plt.plot(time, Uout_recov2, label = "Uout_recov")


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