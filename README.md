# Graphical User Interface Beamline 531
This is the public repository for the Advanced Light Source developmental beamline 5.3.1.

This beamline is a pilot project to study the upgrade for instrument controls and user interface from Labview (as commonly used on the ALS floor) to EPICS and bluesky.

Contact: Tanny Chavez (tanchavez@lbl.gov), Grace Luo (yluo89@lbl.gov), Wiebke Koepp (wkoepp@lbl.gov)
Beamline scientist: Antoine Wojdyla (awojdyla@lbl.gov)

## Getting Started
To get started, clone this repository:
```
$ git clone https://github.com/als-computing/beamline531.git
$ cd beamline321
```

Optional step, create a docker network "qs_net" with access to the devices in this beamline, by using [IPvlan](https://docs.docker.com/network/drivers/ipvlan/). If this network is not defined, please comment out this network in the docker-compose.yml file in this repo before moving forward.

Create an '.env' file, where you will define 'MONGO_INITDB_ROOT_USERNAME = YOUR_USERNAME' and 'MONGO_INITDB_ROOT_PASSWORD = YOUR_PASSWORD'

```
$ docker compose build
$ docker-compose up -d mongo
```

Next, we will create a new API client for this beamline. To achieve this, we will execute the following:
```
$ docker compose run beamline_api bash
$ python3 src/examples/create_api_client.py 
$ exit
```

This command will provide you a key, which should be added to the .env file as "BL_API_KEY = YOUR_KEY".

Let's now ingest a the components details, as follows:
```
$ docker-compose up -d beamline_api
$ docker compose run manager_frontend bash
$ python3 src/epics_db/atlas_to_local.py
$ exit
```

Save the UID at the output of this script as "BL_UID" in your .env file.

After this initial setup, you can start this GUI at any point by using the following command:

```
$ docker compose up
```

The frontend interface can be accessed at: http://localhost:8052/

## Copyright
Splash-ML Copyright (c) 2023, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy). All rights reserved.

If you have questions about your rights to use or distribute this software, please contact Berkeley Lab's Intellectual Property Office at IPO@lbl.gov.

NOTICE. This Software was developed under funding from the U.S. Department of Energy and the U.S. Government consequently retains certain rights. As such, the U.S. Government has been granted for itself and others acting on its behalf a paid-up, nonexclusive, irrevocable, worldwide license in the Software to reproduce, distribute copies to the public, prepare derivative works, and perform publicly and display publicly, and to permit others to do so.
