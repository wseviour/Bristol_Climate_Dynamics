
# Guide to running Isca with SOCRATES on BlueCrysal Phase 4

This guide is intended to get you up-and-running with Isca and the SOCRATES
radiation code on BlueCrystal Phase 4 (BCP4). It assumes that you are starting
with a default (unmodified) user environment on BCP4. 

If you have any questions please feel free to email Will
(w.seviour@bristol.ac.uk). Also please let me know if there are any mistakes in
this guide, either by email or raising an issue on this Github page.



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

Press `Cntrl-O` to save, then `Cntrl-X` to quit nano. Then make the `Isca_work` and
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

You can also check on the job status with the command `sbatch -u $USER`. All
being well, after about 20 minutes the job should complete, and you'll find some
output files in `/mnt/storage/home/$USER/scratch/Isca_data`. :+1:


## Switching to Mars banch and adding SOCRATES

The SOCRATES radiation code is maintained by the Met Office, and so not bundled
as a part of Isca. There are also a few changes to the standard Isca code needed
in order to run Mars simulation and for compatibility with SOCRATES. The best
way to get these is to checkout my Git branch. To do so, type the following
commands:

```{bash}
(isca_env) $ git remote add Will https://github.com/wseviour/Isca
(isca_env) $ git fetch Will
(isca_env) $ git checkout -b uob_mars_dev Will/uob_mars_dev
```

Next we'll have to get the SOCRATES code. I have this on Dropbox, so you can
just download it as follows:

```{bash}
(isca_env) $ cd ~/Isca/src/atmos_param/socrates/src/
(isca_env) $ wget https://www.dropbox.com/s/q2s5jfpddrtbkh4/trunk.zip?dl=0
(isca_env) $ unzip "trunk.zip?dl=0"
(isca_env) $ rm "trunk.zip?dl=0"
```

There should now be a directory called `trunk`, which contains the SOCRATES
code.


## Running basic Mars SOCRATES

We'll now attempt to run a Mars with SOCRATES simulation. To do this, we need to
create a run script. The file `~/Isca/exp/site-specific/isca_slurm_job.sh` which
we ran earlier (for the Held-Suarez case) is an example of this. It is best
practice to make a new directory outside of the `~/Isca` directory in which to
host run scripts.

```{bash}
(isca_env) $ cd $HOME
(isca_env) $ mkdir Isca_jobs
(isca_env) $ cd Isca_jobs
(isca_env) $ nano mars_socrates.sh
```

Then copy and paste the following:

```{bash}
#!/bin/bash -l

#SBATCH --job-name=socrates_mars
#SBATCH --partition=cpu
#SBATCH --time=12:00:00
#SBATCH --nodes=1
#number of tasks ~ processes per node
#SBATCH --ntasks-per-node=16
#number of cpus (cores) per task (process)
#SBATCH --cpus-per-task=1
#SBATCH --output=slurm_%j.o

echo Running on host `hostname`
echo Time is `date`
echo Directory is `pwd`

module purge
source $HOME/.bashrc
source $GFDL_BASE/src/extra/env/bristol-bc4
source activate isca_env

$HOME/.conda/envs/isca_env/bin/python $GFDL_BASE/exp/socrates_mars/socrates_mars.py
```

Again, press `Cntrl-O` to save then `Cntrl-X` to quit nano.

To run this job then do: 

```{bash}
(isca_env) $ sbatch mars_socrates.sh
```

This sets up a simulation which lasts for 12 hours, and should produce about 36
months of output data. You can find the output in directory
`$GFDL_DATA/soc_mars_mk36_per_value70.85_none_mld_2.0_with_mola_topo/`



## Editing Isca simulation scripts

The bulk of the configuration of Isca simulations is done within the python run
scripts. There are many things that can be changed here, so I'll just mention a
few of the more common ones.

First open the run script in your favourite editor (the example uses nano, which
is simple, but I'd recommend learning something with more functionality like vi
or emacs):

```{bash}
(isca_env) $ nano ~/Isca/exp/socrates_mars/socrates_mars.py
```

On line 27 (starting `inputfiles = `) the necessary input data files are
set. These are the Mars longwave and shortwave spectral files, and the solar
spectral files needed for SOCRATES. You can find more information about these
files [here](https://simplex.giss.nasa.gov/gcm/ROCKE-3D/Spectralfiles.html), and
download additional ones [here](https://portal.nccs.nasa.gov/GISS_modelE/ROCKE-3D/).

The lines beginning `diag.add_field` determine the model diagnostics that are
saved out. To see some examples of other diagnostics that can be added look at
other examples in `Isca/exp/test_cases/`.

The parameters under `socrates_rad_nml` set the inputs to SOCRATES. These
include gas mixing ratios, solar constant, and the spectral files,

Parameters under `astronomy_nml` and `constants_nml` set many of the orbital and
planetary parameters.

Under the line `if __name__ =="__main__":` the actual simulation is set up. This
includes the experiment name. Some further parameters are listed here, such as
surface pressure (note this is in different units for different aspects of the
model!), as well as $g$.

The simulation is run in the lines beginning `exp.run`. By default, this will
run a new simulation from scratch (though it will not overwrite existing
data). It is possible to specify a restart file as follows. In doing so, you can
extend a previous simulation.

```{bash}
exp.run(1, use_restart=True, restart_file=/path/to/restart/file, num_cores=NCORES)
``

