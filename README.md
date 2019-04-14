# simlorafs
LoRa simulator to study Spreading Factor (SF) orthogonality.

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.2579366.svg)](https://doi.org/10.5281/zenodo.2579366)

## Prerequisite
This tool is supposed to run with both Python 2.x and 3.x, but it is only verified with Python 3.x.

Required Python Modules:
* matplotlib
* numpy
* scipy
* scikit-learn

## Usage
Show help:
```
python3 main.py -h
```

Topology radius in meter:
```
python3 main.py -r 5000
```

Number of gateways:
```
python3 main.py -g 3
```

Number of nodes:
```
python3 main.py -n 300
```

Spreading factor assignment method:
```
python3 main.py -s SF_Lowest
```

Smart spreading factor assignment classifier:
```
python3 main.py -s SF_Smart -c DTC
```

Simulation duration in second:
```
python3 main.py -d 3600
```

Packet rate in packet per second:
```
python3 main.py -p 0.02
```

Packet size in byte:
```
python3 main.py -z 80
```

Proportions of different traffic generator type nodes:
```
python3 main.py -o 0.8 0.2
```

Random number generator seed:
```
python3 main.py -e 42
```

Events log path:
```
python3 main.py -l events.txt
```

Verbose level:
```
python3 main.py -v INFO
```

Complex example:
```
python3 main.py -r 7000 -g 3 -n 300 -s SF_Lowest -d 3600 -p 0.03 -z 65 -o 0.8 0.2 -e 76 -l log.txt -v INFO
```

Get figures and results in the paper:
```
python3 paper.py
```

## Source Code Structure
### main.py
Command line interface for simulator. This file parses simulation inputs, executes simulation and reports results.

### simulation.py
Core simulation methods and classes resides in this file. 'run' method is the core function that executes simulation steps.

### packet.py
LoRa related packet information classes resides in this file. Methods for calculating transmission's duration, sensitivity, propagation and energy methods are in this file. Also SNIR matrix and packet status enumeration types are resides in this file.

### node.py
End node and gateway related classes resides in this file. Node traffic generator methods are defined in this file.

### topology.py
LoRaWAN network topology information such as node and gateway locations are kept in the classes in this file. Also random topology generator method is resides in this file.

### location.py
Location class that keeps x and y coordinate of nodes or gateways resides in this file.

### paper.py
This is an example application code for utilizing LoRa SF simulation framework. This example file generates figures and results in the paper.

## Software Architecture
### UML Class Diagram
![Alt text](uml_class.png?raw=true "UML class diagram")
