[TOC]

# Description

This is a set of scripts and config files meant to be used to make plots of several
kinematic distributions.

## 1D plots

### comparisons between variables

For this use:

```bash
compare -q jpsi -s Bu_JpsiK_ee_eq_DPC -t Hlt2RD_BuToKpEE_MVA -c resolution -b 2 -B 2
```
where the arguments mean:

```
options:
  -h, --help            show this help message and exit
  -q {low,central,jpsi,psi2,high}, --q2bin {low,central,jpsi,psi2,high}
                        q2 bin
  -s SAMPLE, --sample SAMPLE
                        Sample
  -t {Hlt2RD_BuToKpMuMu_MVA,Hlt2RD_BuToKpEE_MVA}, --trigger {Hlt2RD_BuToKpMuMu_MVA,Hlt2RD_BuToKpEE_MVA}
                        Trigger
  -c CONFIG, --config CONFIG
                        Configuration
  -x SUBSTR, --substr SUBSTR
                        Substring that must be contained in path, e.g. magup
  -b {-1,0,1,2}, --brem {-1,0,1,2}
                        Brem category
  -B {-1,1,2,5,6,7,8}, --block {-1,1,2,5,6,7,8}
                        Block to which data belongs, -1 will put all the data together
  -r, --nomva           If used, it will remove the MVA requirement
```

The config files are stored in `rx_plotter_data/compare` and they are:

| Kind          | Description                                                                                                         |
| ------------- | ------------------------------------------------------------------------------------------------------------------- |
| resolution    | Used to compare the distribution before and after brem correction and also with L0 emulating requirements           |
| mass_smearing | Used to compare mass line shapes of $J/\psi$ and $B$ before and after smearing and of the non-brem corrected sample |

### cutflow

The `cutflow` utility will make plots of a dataset under multiple cuts, one after the other.
Use it with:

```bash
cutflow -q jpsi -s DATA* -t Hlt2RD_BuToKpEE_MVA -c cleanup
```

where `cleanup` refers to `cleanup.yaml`, a config file that shows the effect of applying cleanup
requirements (HOP, Cascade, $J/\psi$ mis ID veto). Below each config description:

| Kind    | Description                                            |
| ------- | ------------------------------------------------------ |
| vetoes  | Check effect on `B_M` original and corrected of vetoes |
| bdt     | Check effect on `B_M` original and correcte of BDT     |
| cleanup | Same as vetoes but checks effect on multiple variables |

### Block quality

One can use the same command with `block_quality`, e.g:

```bash
generic -t Hlt2RD_BuToKpMuMu_MVA -s "DATA*" -c block_quality -q jpsi
```

which will make plots showing distributions per block. These distributions pass
a tight MVA requirement and are taken from the core of the DTF B mass. Thus can be
considered background subtracted.

### Same sign shape

Plots showing effect of vetoes and MVA on SS data

```bash
cutflow -s "DATA*" -t Hlt2RD_BuToKpEE_SameSign_MVA -c vetoes -q low
cutflow -s "DATA*" -t Hlt2RD_BuToKpEE_SameSign_MVA -c vetoes -q central
cutflow -s "DATA*" -t Hlt2RD_BuToKpEE_SameSign_MVA -c vetoes -q high
```

## 2D plots

For this run:

```bash
plot_2d -C mm -q central -c mass_q2
```

where:

```
options:
  -h, --help            show this help message and exit
  -C {ee,mm}, --chanel {ee,mm}
                        Channel
  -q {low,central,jpsi,psi2,high}, --q2bin {low,central,jpsi,psi2,high}
                        q2 bin, optional
  -c {mass_q2,cmb_prc}, --config {mass_q2,cmb_prc}
                        Settings, i.e. mass_q2
  -l {10,20,30}, --loglvl {10,20,30}
                        Log level
```

This will provide plots showing

- Correlations
- Mass vs q2

## Other studies

### Leakage from $B^+\to K^+ J/\psi(\to ee)$ into central $q^2$ bin

To study the distribution after applying the smearing in the mass and using
the brem corrected vs smeared vs non smeared masses in the selection do:

```bash
leakage
```

**TODO**: This should be improved

### $q^2$ cut on different variables to get high-q2 signal region 

To study this run:

```bash
high_q2cut
```


