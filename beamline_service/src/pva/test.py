# %%
import time
import numpy as np
import pvaccess as pva
import matplotlib
matplotlib.use('WebAgg')
import matplotlib.pyplot as plt
from matplotlib.pyplot import plot, draw, show, ion
ion()
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
        self.newdata = False

    def monitor(self, pv):
        try:
            print('Got image: %d' % pv['uniqueId'])
            self.uid = pv['uniqueId']
            self.x, self.y = pv['dimension'][0]['size'], pv['dimension'][1]['size']
            self.data = pv['value'][0]['ubyteValue'].reshape((self.x, self.y))
            self.newdata = True
        except Exception as e:
            print('In callback function with error %s'%e)

# %%
def main(pvaChannel, pva_monitor):
    c = pva.Channel(pvaChannel)
    c.subscribe('monitor', pva_monitor.monitor)
    # c.startMonitor('')
    return c
    # time.sleep(100)

# %%
fig, ax = plt.subplots()
ax.set_xticks([])
ax.set_yticks([])

pvaChannel = '13SIM1:Pva1:Image'
m = pvaMonitor(fig, ax)
img = ax.imshow(np.zeros((1024,1024)) if m.data is None else m.data, 'inferno')
if __name__ == '__main__':
    c = main(pvaChannel, m)
    c.startMonitor('')
    img = ax.imshow(np.zeros((1024,1024)) if m.data is None else m.data, 'inferno')
    while 1:
        if m.newdata:
            img = ax.imshow(m.data)
            fig.show()
            m.newdata = False
        time.sleep(1)


