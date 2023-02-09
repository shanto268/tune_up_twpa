# TWPA TUNE UP CODE:

# Usage:

0. Take reference data (all amplifiers tuned away) using Measurement Browser through Labber
```
Counter Value (number of SA traces to consider -> used for calculating average SNR)
```

1. Take data using Measurement Browser through Labber with the following loop order (**Keep SA span the same as the above step**)
```
Counter Value (number of SA traces to consider -> used for calculating average SNR)
Power Bounds
Frequency Bounds
```

2. `$ python tune_up_twpa.py`

or ** Run on Spyder **


---



```shell
$ python tune_up_twpa.py

File Location of TWPA Data: \path\to\twpa\sweep\data.hdf5

File Location of Reference Data: \path\to\reference\data.hdf5

```


**Result**

![snr](figures/TWPA_Tune_Up_10_05_2022_170547.png)

## To Do:

- [x] Automate Use of Hyperparameters (string names, ranges, etc)
- [x] Stable High SNR Regime Finder Implementation
- [ ] Document Code
- [ ] Usage Document (works with certain order and freq, power sweeps only)

---
