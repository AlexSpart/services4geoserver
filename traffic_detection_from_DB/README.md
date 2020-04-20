The detect_traffic.py script feteces the CAM collection, computes for each entry the density, and if too high, composes a DENM message and pushes it through v2x-manager operating as a client.


1) run v2xmanager as client:

    sudo v2xmanager --interface=enp0s3 --gpsd-host=localhost --gpsd-port 2947 --cam-interval 6000 --client-port-number 446 --client-address 193.55.113.48 --server-port-number 3000 --client-role 1

2) run sudo quadkeymapper

3) run detect_traffic.py
  
    sudo python3 detect_traffic.py
