# csi-extractor


## Before use
* Based on the [Nexmon CSI Extractor](https://github.com/seemoo-lab/nexmon_csi) (Raspberry Pi, Wi-Fi chip: bcm43455c0), this repository functions to save Channel State Information (CSI) data as a csv file for each TX MAC address
* Therefore, you can use this repo after installing the Nexmon CSI Extractor firmware and activating the monitor mode


## Installation
* Clone this repo to Raspberry Pi to use as extractor and install the dependencies
```
pip3 install -r requirements.txt
```

## Usage
* Run `csi_extract.py` with monitor mode enabled
```
sudo python3 csi_extract.py
```
* To stop collecting, type `s` on your keyboard
* Before starting CSI extraction, it is recommended to check whether the monitor mode is working well through a real time plot
```
sudo python3 csi_realTimeAmp.py
or
sudo python3 csi_realTimePhase.py
```
* If the real time plot does not work, there is a high possibility that there is a firmware installation error or monitor mode setting error
* The extractor configuration can be modified in `./cfg/config.py`


## Example of generated CSV file
![image](https://user-images.githubusercontent.com/51084152/178401401-8388d24a-dbd7-4c33-bf6f-8dad089624ab.png)

* Number of columns: 2 + N_subcarriers
    * `mac`: TX MAC address
    * `time`: Time the CSI was extracted
    * `N_subcarriers`: Index of each subcarrier
    
* CSI values are stored in complex type