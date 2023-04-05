# Graphical User Interface Beamline 531
This is the public repository for the Advanced Light Source developmental beamline 5.3.1.

This beamline is a pilot project to study the upgrade for instrument controls and user interface from Labview (as commonly used on the ALS floor) to EPICS and bluesky.

Contact: Tanny Chavez (tanchavez@lbl.gov), Grace Luo (yluo89@lbl.gov), Wiebke Koepp (wkoepp@lbl.gov)
Beamline scientist: Antoine Wojdyla (awojdyla@lbl.gov)

## Getting Started
Setup a python environment, as follows:

```
$ git clone https://github.com/als-computing/beamline531.git
$ cd beamline531
$ python -m venv myenv
$ source myenv/bin/activate
$ pip install -r requirements_frontend.txt
```

To start the frontend service, execute:

```
$ python client/main.py
```

The frontend interface can be accessed at: http://localhost:8052/
