
# Guide to running Isca with SOCRATES on BlueCrysal Phase 4

This guide is intended to get you up-and-running with Isca and the SOCRATES
radiation code on BlueCrystal Phase 4 (BCP4). It assumes that you are starting
with a default (unmodified) user environment on BCP4. 

If you have any questions please feel free to email Will (w.seviour@bristol.ac.uk).



## Basic Isca model setup

First create an account on [Github](https://github.com/) (if you don't already
have one). This is free.

Now navigate to the [main Isca
repository](https://github.com/ExeClim/Isca). Click on the 'Fork' button in the
upper right hand corner.

You'll now have your own copy of the Isca code at
https://github.com/gh_username/Isca, where 'gh_username' is your Github username. 

Next we want to log in to our BCP4 account. On Linux or Mac type the following
into a terminal window:

```{bash}
$ ssh bristol_username@bc4login.acrc.bris.ac.uk
```

where 'bristol_username' is your Bristol username. Then type your Bristol
password to login. If using Windows, you'll need to use PuTTY. There is a useful
guide to this
[here](https://github.com/rgnmudhar/MSci_Project/blob/master/Handover%20Document%20for%2060%20CP%20MSci%20Project%20A1005.docx)
(click the 'download' button to download the Word Document). 

Now we want to download the contents of the newly-created Git repository. To
enable Git on BCP4, type:

```{bash}
$ module load git
```

Now you can clone the Isca repository:

```{bash}
$ git clone git@github.com:gh_username/Isca.git
$ cd Isca
```

Where 'gh_username' is again replaced by your Github username. 

Before you can run Isca, you'll need to load the Anaconda python distribution:

```{bash}
$ module load languages/anaconda3
```

Next we'll make a conda environment for Isca (this means it will have all the
right versions of the various packages on which it depends):

```{bash}
$ conda create -n isca_env python ipython
$ source activate isca_env
(isca_env) $ cd src/extra/python
(isca_env) $ pip install -r requirements.txt

Successfully installed MarkupSafe-1.0 f90nml jinja2-2.9.6 numpy-1.13.3 pandas-0.21.0 python-dateutil-2.6.1 pytz-2017.3 sh-1.12.14 six-1.11.0 xarray-0.9.6

(isca_env) $ pip install -e .
...
Successfully installed Isca
```

(Don't foget the dot after '-e'!). Finally, we'll need to update the `~/.bashrc`
file (this sets up several important system variables needed by the
model). First open the file in a text editor, such as nano.

```{bash}
nano ~/.bashrc
```

Now copy and paste in the following lines:

```{bash}
# directory of the Isca source code
export GFDL_BASE=$HOME/Isca
# "environment" configuration for bc4
export GFDL_ENV=bristol-bc4
# temporary working directory used in running the model
export GFDL_WORK=/mnt/storage/home/$USER/scratch/Isca_work
# directory for storing model output
export GFDL_DATA=/mnt/storage/home/$USER/scratch/Isca_data
```

Press Cntrl-O to save, then Cntrl-X to quit nano. Then make the `Isca_work` and
`Isca_data` directories:

```{bash}
(isca_env) $ mkdir -p /mnt/storage/home/$USER/scratch/Isca_work
(isca_env} $ mkdir -p /mnt/storage/home/$USER/scratch/Isca_data
(isca_env) $ bash
```
Now everything should be set up and we can try a test run. The following should 
compile and run 12 months of a Held-Suarez test case, at T42 resolution spread over 16 cores. 

```{bash}
(isca_env) $ cd Isca/exp/site-specific
(isca_env) $ sbatch isca_slurm_job.sh
```

This should produce a slurm file showing the progress as it compiles and runs. 
To track the progress:

```{bash}
(isca_env) $ tail -f slurm_*.o
```

All being well, after about 20 minutes the job should complete, and you'll find 
some output files in `/mnt/storage/home/$USER/scratch/Isca_data`. :+1:


## Adding SOCRATES

The SOCRATES radiation code is maintained by the Met Office, and so not bundled
as a part of Isca.

