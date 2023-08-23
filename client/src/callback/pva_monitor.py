import pvaccess as pva
import numpy as np
import json, asyncio
from datetime import datetime


# TODO: make an APIRouter for this.

# pvaMonitor constructor
class pvaMonitor:
    def __init__(self, pvaChannel:str):
        self.x = 0
        self.y = 0
        self.uid = 0
        self.channel = pva.Channel(pvaChannel)
        self.img = None
        self.pv = None
        self.received = False

    def monitor(self, pv):
        """PVA callback function. Function triggered by EPICS IOC database"""
        print('Got image uid: %d' % pv['uniqueId'])
        self.pv = pv
        self.update()

    def update(self):
        """Update the attributes of the pvaMonitor object"""
        try:
            self.uid = self.pv['uniqueId']
            self.x = self.pv['dimension'][0]['size']
            self.y = self.pv['dimension'][1]['size']
            self.img = self.pv['value'][0]['ubyteValue'].reshape((self.x, self.y))
            self.received = True
        except Exception as e:
            print(f"Unable to update pvaMonitor due to {e}")

    def subscribe(self):
        self.channel.subscribe('monitor', self.monitor)
        self.channel.startMonitor(' ')

    async def receive(self):
        """If no stream data, the process will wait and no nothing"""

        # print('before')
        while not self.received:
            # print('in receive loop')
            await asyncio.sleep(0.01)
        # print('after')

        data = {}
        img = self.img
        time_stamp = datetime.now().strftime('%m/%d/%Y, %H:%M:%S')

        if img is not None:
            data = {'img': img.tolist(), 'x': self.x, 'y': self.y, 'uid': self.uid,
                    'time_stamp': time_stamp}
        else:
            x, y = 1024, 1024
            img = np.zeros((x, y))
            data = {'img': img.tolist(), 'x':x, 'y':y,
                    'uid':0, 'time_stamp':time_stamp}

        data = json.dumps(data)
        self.received = False
        return data
