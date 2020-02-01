# simlorafs
LoRa discrete event simulator to study Spreading Factor (SF) orthogonality. This tool provides framework for simulating LoRaWAN networks. The tool keeps an transmission queue. Every event in this queue is a transmission. Every transmission has time, spreading factor, source, size, duration, and status fields. Every node generate an event according to their traffic generation rate parameter and inserts this event to simulation event queue. Initially all events are in pending state. Simulation tool then iterates and executes events, then marks events status as transmitted, interfered or under sensitivity. After all events are executed, the tool calculates network PDR, throughput and transmit energy consumption.

A command line parser is provided for interacting with the framework, this enables users to play with it without any programming or scripting. Also, an example script is provided to demonstrate usage of the framework. Python scikit-learn machine learning library is utilized for smart spreading factor schemes operations. Also, Python matplotlib library is used to generate figures.


## Acknowledgments
This work was developed as part of a Master of Science thesis at Istanbul Technical University, under the supervision of Prof. Sema Oktug.

Publications:

* T. Yatagan and S. Oktug, "Smart Spreading Factor Assignment for LoRaWANs," 2019 IEEE Symposium on Computers and Communications (ISCC), Barcelona, Spain, 2019, pp. 1-7. [![DOI](https://zenodo.org/badge/DOI/10.1109/ISCC47284.2019.8969608.svg)](https://doi.org/10.1109/ISCC47284.2019.8969608)

* T. Yatagan, "Smart Spreading Factor Assignment for LoRaWANs," M.S. thesis, Istanbul Technical University, Istanbul, Turkey, 2019. [Online]. Available: Turkish Council of Higher Education Thesis Center [No 557097](https://tez.yok.gov.tr/UlusalTezMerkezi/TezGoster?key=Mir2lXQK1dkmQ9Ige3PZbpjXYNGXhXNeBA_KevbGRLGvHRe0OPaWEuKOGMdS9yoQ).

* T. Yatagan, tugrulyatagan/simlorasf, May 2019, [Online] Available: [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3072925.svg)](https://doi.org/10.5281/zenodo.3072925).


## Installation
The simulation tool is developed and tested with Python 3.x. Python can be downloaded from official web page https://www.python.org/downloads

The simulation tool requires specific Python modules to run. All of these modules can be installed by "pip" Python package manager. A new Python module can be installed with "pip install" command. Required Python modules for the simulation tool are:

Required Python Modules:
* matplotlib
* numpy
* scipy
* scikit-learn


## Command Line Interface Usage

Command line interface examples of the simulation tool are given below:

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


## Software Architecture
Source files of the simulation tool and their primary objectives are described below:

### main.py
Command line interface of the simulator. It parses simulation inputs, executes simulation and reports simulation results.

### simulation.py
Core simulation methods and classes are defined. 'run' method is the core function that executes simulation steps.

### packet.py
LoRa related packet information classes are defined. Methods for calculating transmission duration, receive sensitivity, propagation loss and transmission energy are in this file. Also SNIR matrix and packet status enumeration types resides in this file.

### node.py
End node and gateway related classes are defined. Also, node traffic generator methods are defined.

### topology.py
LoRaWAN network topology information such as node and gateway locations are defined. Also, random topology generator method is defined.

### location.py
Location class that keeps x and y coordinate of nodes or gateways are defined.

### paper.py
An example application code for utilizing LoRa spreading factor simulation Python framework. This example script generates figures and results in the paper.

### UML Class Diagram
Relationships between these classes can be seen in UML class diagram.

![Alt text](uml_class.png?raw=true "UML class diagram")
