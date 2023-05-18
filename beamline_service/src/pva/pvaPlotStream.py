# %%
import time
import numpy as np
import pvaccess as pva
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
# from matplotlib.pyplot import plot, draw, show, ion
# ion()
# %matplotlib inline

# %%
class pvaMonitor:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.uid = 0
        self.fig, self.ax = plt.subplots()
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

        # # self.img = self.ax.imshow(self.data, 'gray')
        # # self.fig.show()
        # self.img = self.ax.imshow(self.data, 'gray') if self.img is None else self.img
        # self.img.set_data(self.data)
        # self.fig.show()

        return

# %%
def main(pvaChannel):
    c = pva.Channel(pvaChannel)
    m = pvaMonitor()
    c.subscribe('monitor', m.monitor)
    c.startMonitor('')
    time.sleep(100)
    return c, m

# %%
if __name__ == '__main__':
    pvaChannel = '13SIM1:Pva1:Image'
    c, m = main(pvaChannel)

 

