import os
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
import tet

def main():
    np.set_printoptions(formatter={'float': lambda x: "{0:0.1f}".format(x)})
    
    max_N = 12
    omegaA, omegaD = 3, -3
    chiA, chiD = -0.5, 0.5
    coupling_lambda = 0.001
    t_max = 20

    xA = np.linspace(-4, 4, 100)
    xD = np.linspace(-4, 4, 100)

    return_query = True

    cwd = os.getcwd()
    data = f"{cwd}/data"

    coupling_dir = f"coupling-{coupling_lambda}"
    coupling_dir_path = os.path.join(data, coupling_dir)

    t_dir = f"tmax-{t_max}"
    t_dir_path = os.path.join(coupling_dir_path, t_dir)

    data_dest = os.path.join(t_dir_path, "avg_N")

    tet.data_process.createDir(data, replace=False)
    tet.data_process.createDir(coupling_dir_path, replace=False)
    tet.data_process.createDir(t_dir_path)
    tet.data_process.createDir(data_dest)

    test_data = tet.Execute(chiA=chiA, 
                            chiD=chiD, 
                            coupling_lambda=coupling_lambda, 
                            omegaA=omegaA, 
                            omegaD=omegaD, 
                            max_N=max_N, 
                            max_t=t_max, 
                            data_dir=data_dest,
                            return_data=return_query)()

    if return_query and np.ndim(test_data)>1:
        XA, XD = np.meshgrid(xA, xD)

        counter = 0
        test_z = np.zeros(len(xA)*len(xD))
        for i in enumerate(test_data): 
            test_z[i[0]] = min(i[1])
            counter += 1
        test_z = test_z.reshape(len(xA), len(xD))

        titl = f'N={max_N}, tmax = {t_max}, # points (χA, χD) = {len(xA), len(xD)}, λ={coupling_lambda}, ωA={omegaA}, ωD={omegaD}'

        figure, ax = plt.subplots(subplot_kw={"projection": "3d"}, figsize=(12,12))
        plot = ax.contour(XA, XD, test_z, cmap='rainbow', levels=50)
        ax.set_xlabel(r"$\chi_{D}$", fontsize=20)
        ax.set_ylabel(r"$\chi_{A}$", fontsize=20)
        figure.colorbar(plot)
        ax.set_title(titl, fontsize=20)
        tet.saveFig(titl+' - 3dplot', t_dir_path)

        figure2, ax2 = plt.subplots(figsize=(12,12))
        plot2 = ax2.contourf(test_z,cmap = 'rainbow',extent=[min(xD),max(xD),max(xA),min(xA)], levels=50)
        ax2.set_xlabel(r"$\chi_{D}$", fontsize=20)
        ax2.set_ylabel(r"$\chi_{A}$", fontsize=20)
        figure2.colorbar(plot2)
        ax2.set_title(titl, fontsize=20)
        tet.saveFig(titl+' - contourplot', t_dir_path)

if __name__=="__main__":
    main()