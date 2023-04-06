# %%
import time
import numpy as np
import pvaccess as pva
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
# from matplotlib.pyplot import plot, draw, show, ion
# ion()
# %matplotlib inline

# %%
class pvaMonitor:
    def __init__(self, fig, ax):
        self.x = 0
        self.y = 0
        self.uid = 0
        self.fig = fig
        self.ax = ax
        self.img = None
        self.data = None

    def monitor(self, pv):
        print('Got image: %d' % pv['uniqueId'])
        self.uid = pv['uniqueId']
        self.x, self.y = pv['dimension'][0]['size'], pv['dimension'][1]['size']
        self.data = pv['value'][0]['ubyteValue'].reshape((self.x, self.y))
        self.plotData()

    def plotData(self):
        print('Having issue plotting the live view, uid=%d'%self.uid)

        # self.img = self.ax.imshow(self.data, 'gray')
        # self.fig.show()
        # self.img = self.ax.imshow(self.data, 'gray') if self.img is None else self.img
        # self.img.set_data(self.data)

        return

# %%
def main(pvaChannel, pva_monitor):
    c = pva.Channel(pvaChannel)
    c.subscribe('monitor', pva_monitor.monitor)
    c.startMonitor('')
    time.sleep(100)

# %%
if __name__ == '__main__':
    fig = plt.figure()
    ax = fig.gca()
    ax.imshow(np.zeros((1024,1024)),'gray')
    ax.set_xticks([])
    ax.set_yticks([])

    plt.ion()
    plt.show()

    pvaChannel = '13SIM1:Pva1:Image'
    m = pvaMonitor(fig, ax)

    main(pvaChannel, m)

 

