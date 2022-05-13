import numpy as np
import os
import shutil
import sys
from os.path import exists
import matplotlib.pyplot as plt
from saveFig import saveFig
import constants
from math import sqrt


def writeData(data, destination, name_of_file):
    data = np.array(data)
    _destination = os.path.join(destination, name_of_file)

    if data.dtype.name[:3] == 'str':
        fmt = '%s'
    else: fmt = '%.18e'
    
    if exists(_destination):
        #print('File exists, overwrite')
        with open(_destination, "a") as f:
            np.savetxt(f, data, fmt=fmt)
    
    else: np.savetxt(_destination, data, fmt=fmt)

def write_min_N(xA, xD, min_n, destination, name_of_file):
    z = min_n.flatten(order='C')
    x = xD.flatten(order='C')
    y = xA.flatten(order='C')
    k = list(np.zeros(len(z)))
    index = 0

    for i in range(len(min_n)):
        for j in range(len(min_n)):
            index = len(xA)*i+j
            k[index] = x[index], y[index], z[index]
    
    temp_arr = np.array(k)
    writeData(data=temp_arr, destination=destination, name_of_file=name_of_file)

def read_1D_data(destination, name_of_file):
    _destination = os.path.join(destination, name_of_file)
    data = []
    for line in open(_destination, 'r'):
        lines = [i for i in line.split()]
        data.append(float(lines[0]))
    return data


def read_2D_data(destination, name_of_file):
    _destination = os.path.join(destination, name_of_file)
    X,Y = [],[]
    for line in open(_destination, 'r'):
        lines = [i for i in line.split()]
        X.append(float(lines[0]))
        Y.append(float(lines[1]))
    return X,Y

def ReadDeque(destination, name_of_file):
    _destination = os.path.join(destination, name_of_file)
    to_return = []
    for line in open(_destination, 'r'):
        lines = [i for i in line.split()]
        to_return.append( (int(float(lines[0])),int(float(lines[1])),float(lines[2]),
                        int(float(lines[3])),int(float(lines[4]))) )

    return to_return 

def compress(zip_files, destination):
    if not zip_files: return None
    if zip_files:
        shutil.make_archive(base_name=f"{destination}-zipped", format='zip')
        shutil.rmtree(path=destination)


def createDir(destination, replace_query=True):
    if replace_query:    
        try:
            os.mkdir(destination)
        except OSError as error:
            print(error)
            while True:
                query = input("Directory exists, replace it? [y/n] ")
                fl_1 = query[0].lower() 
                if query == '' or not fl_1 in ['y','n']: 
                    print('Please answer with yes or no')
                else:
                    shutil.rmtree(destination)
                    os.makedirs(destination)
                    break
            if fl_1 == 'n': sys.exit(0)
    else:
        os.makedirs(destination, exist_ok=True)

class PlotResults:
    def __init__(self, const, data_path):
        self.coupling = const['coupling']
        self.max_t = const['max_t']
        self.max_n = const['max_N']
        self.omegaD = const['omegas'][0]
        self.omegaA = const['omegas'][-1]
        self.sites = const['sites']
        self.Npoints = constants.plotting_params['plotting_resolution']

        self.data_path = data_path
        self.data_dirs = [f.path for f in os.scandir(self.data_path) if f.is_dir()]
        self.iteration_path = []
        for i, d in enumerate(self.data_dirs):
            self.iteration_path.append(d)
            self.iteration_dirs = [f.path for f in os.scandir(d) if f.is_dir()]

    # ONLY WORKS IN DIMER CASE
    def plotHeatmap(self, ChiAInitial, ChiDInitial, xa_lims, xd_lims, path):

        data_path = path

        xA = np.linspace(*xa_lims, num=self.Npoints)
        xD = np.linspace(*xd_lims, num=self.Npoints)

        from tet.Execute import Execute
        data = Execute(chiA=xA, 
                       chiD=xD, 
                       coupling_lambda=self.coupling, 
                       omegaA=self.omegaA, 
                       omegaD=self.omegaD, 
                       max_N=self.max_n, 
                       max_t=self.max_t, 
                       data_dir=data_path,
                       return_data=True)()

        if np.ndim(data)>1:
            XA, XD = np.meshgrid(xA, xD)

            min_flat_data = np.zeros(len(xA)*len(xD))
            for i in enumerate(data): 
                min_flat_data[i[0]] = min(i[1])

            z = min_flat_data
            x = XD.flatten(order='C')
            y = XA.flatten(order='C')
            k = list(np.zeros(len(z)))
            for i in range(int(sqrt(len(min_flat_data)))):
                for j in range(int(sqrt(len(min_flat_data)))):
                    index = len(XA)*i+j
                    k[index] = x[index], y[index], z[index]
            
            min_n_combinations = np.array(k)

        xA_plot = min_n_combinations[:,0].reshape(self.Npoints, self.Npoints)
        xD_plot = min_n_combinations[:,1].reshape(self.Npoints, self.Npoints)
        avg_n = min_n_combinations[:,2].reshape(self.Npoints, self.Npoints)
        
        # Load Data
        a = read_1D_data(destination=data_path, name_of_file=f'x{self.sites-1}trajectory.txt')
        d = read_1D_data(destination=data_path, name_of_file=f'x{0}trajectory.txt')
        a_init = ChiAInitial
        d_init = ChiDInitial
        
        # Plot heatmaps with optimizer predictions
        titl = f'N={self.max_n}, tmax={self.max_t}, Initial (χA, χD) = {a_init, d_init},\
            λ={self.coupling}, ωA={self.omegaA}, ωD={self.omegaD}'

        x = np.array(np.array(d))
        y = np.array(np.array(a))
        figure2, ax2 = plt.subplots(figsize=(12,12))
        plot2 = ax2.contourf(xD_plot, xA_plot, avg_n, levels=50, cmap='rainbow')
        plot3 = ax2.plot(x, y, marker='o', color='black', label='Optimizer Predictions')
        u = np.diff(x)
        v = np.diff(y)
        pos_x = x[:-1] + u/2
        pos_y = y[:-1] + v/2
        norm = np.sqrt(u**2+v**2)
        ax2.quiver(pos_x, pos_y, u/norm, v/norm, angles="xy",pivot="mid")
        plot4 = ax2.scatter(d_init, a_init, color='green', edgecolors='black', s=94, label='Initial Value', zorder=3)
        ax2.set_xlabel(r"$\chi_{D}$", fontsize=20)
        ax2.set_ylabel(r"$\chi_{A}$", fontsize=20)
        figure2.colorbar(plot2)
        ax2.legend(prop={'size': 15})
        ax2.set_title(titl, fontsize=20)
        saveFig(fig_id="contour", fig_extension="png", destination=data_path)

    def plotLoss(self):
        for i in range(len(self.iteration_dirs)):
            loss_data = read_1D_data(destination=self.iteration_dirs[i], name_of_file='losses.txt')
            # Plot Loss
            fig, ax = plt.subplots()
            ax.plot(loss_data[1:])
            saveFig(fig_id="loss", fig_extension="png", destination=self.iteration_dirs[i], silent=True)
            plt.close(fig)
    
    def plotScatterChis(self):
        
        data = self.data_dirs
        opt_data = self.iteration_dirs
        optimal_vars = np.zeros((len(opt_data), self.sites+1))
        for i in range(optimal_vars.shape[0]):
            _chis = read_1D_data(destination=opt_data[i], name_of_file='optimalvars.txt')
            loss_data = read_1D_data(destination=opt_data[i], name_of_file='losses.txt')
            _loss = loss_data[-1]
            row = np.append(_chis, _loss)
            optimal_vars[i,:] = row
        
        fig = plt.figure()
        if self.sites>2:
            ax = fig.add_subplot(projection='3d')
        else:
            ax = fig.add_subplot()
        x = ax.scatter(*[optimal_vars[:,j] for j in range(optimal_vars.shape[1]-1)], c=optimal_vars[:,-1], cmap='plasma_r')
        fig.colorbar(x)
        plt.show()

    # def 

if __name__=="__main__":
    data_path = os.path.join(os.getcwd(), 'data')
    p = PlotResults(constants.loadConstants(), data_path = os.path.join(os.getcwd(), 'data'))
    p.plotScatterChis()