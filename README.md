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

## Copyright
Splash-ML Copyright (c) 2023, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy). All rights reserved.

If you have questions about your rights to use or distribute this software, please contact Berkeley Lab's Intellectual Property Office at IPO@lbl.gov.

NOTICE. This Software was developed under funding from the U.S. Department of Energy and the U.S. Government consequently retains certain rights. As such, the U.S. Government has been granted for itself and others acting on its behalf a paid-up, nonexclusive, irrevocable, worldwide license in the Software to reproduce, distribute copies to the public, prepare derivative works, and perform publicly and display publicly, and to permit others to do so.
