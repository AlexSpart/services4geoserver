# Traffic Jam Detection

The detect_traffic.py script fetces the CAM collection from the geoserver DB, computes for each entry the density, and if it is too high, composes a DENM message and sends it through v2xmanager operating as a client.


## Requirements

Install this version of [v2xmanager](https://gitlab.eurecom.fr/a-team/geoserverbackend/tree/master/5gcroco/V2xManager) from source.

Install this version of [quadkeymapper](https://gitlab.eurecom.fr/a-team/geoserverbackend/tree/master/5gcroco/quadkeymapper) from source.

## Usage

run v2xmanager as client:'
```bash 
sudo v2xmanager --interface=enp0s3 --gpsd-host=localhost --gpsd-port 2947 --cam-interval 6000 --client-port-number 446 --client-address 193.55.113.48 --server-port-number 3000 --client-role 1```
```

```bash 
sudo quadkeymapper
```

```bash 
sudo python3 detect_traffic.py
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[Apache License 2.0](https://choosealicense.com/licenses/apache-2.0/)
