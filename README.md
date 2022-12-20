# Graphical User Interface Beamline 531
This project contains a prototype of the graphical user interface for Beamline 531 at the ALS.

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

The frontend interface can be accessed at: http://localhost:8022/
