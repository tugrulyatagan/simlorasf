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

Example:
```
python3 main.py -r 7000 -g 3 -n 300 -s SF_Lowest -d 3600 -p 0.03 -z 65 -o 0.8 0.2 -e 76 -l log.txt -v INFO
```

Get figures and results in the paper:
```
python3 paper.py
```

## Source Code Hierarchy
### main.py
Application code

### simulation.py
TODO

### packet.py
TODO

### node.py
TODO

### topology.py
TODO

### location.py
TODO

### paper.py
TODO