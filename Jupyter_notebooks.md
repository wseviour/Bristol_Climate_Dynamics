# Notes for working with Jupyter Notebooks on the BRIDGE servers

These notes are aimed at getting you up and running with using [Jupyter Notebooks](https://jupyter.org/)
on the BRIDGE servers within Geography. The end result should be a web-browser interface on your local computer
which controls Python computations on one of the servers (this happens via an `ssh` tunnel). 

First log in to one of the BRIDGE servers. In this case, we'll use Anthropocene.

```{bash}
$ ssh username@anthropocene.ggy.bris.ac.uk
```

Where `username` is here replaced with your Bristol IT username (and for the rest of this guide). 

Now we want to add a couple of lines to the `~/.bashrc` file, to ensure that the correct Python version is 
being used, and so we don't have to keep typing a lengthy command to start the Notebook. First open your `~/.bashrc` file, e.g.

```{bash}
$ nano ~/.bashrc
```

Then add the following two lines: 

```{bash}
module load anaconda/3.6-5.0.1
alias nb_serve='jupyter notebook --no-browser --port=8889'
```

Save the file and exit. Now type `bash` to re-load the new `~/.bashrc` file. 

Next we want to create a conda environment for doing our analysis. In this example we'll be analysing some output from
the Isca model, so we'll call the environment `isca_analysis`.

```{bash}
$ conda create --name isca_analysis 
$ conda activate isca_analysis
```
Remember, each time you log in to the server you'll need to type
`conda activate isca_analysis` to make sure you're in the right environment. 

Now let's install a couple of packages, [`xarray`](http://xarray.pydata.org/en/stable/) and 
[`cartopy`](http://xarray.pydata.org/en/stable/), which will be very useful. These might take a little while to install:

```{bash}
$ conda install xarray
$ conda install -c conda-forge cartopy
```
Once that is done, we are good to go. We'll start the notebook server using the alias we set up earlier:

```{bash}
$ nb_serve
```

You should get something that looks like this.

```{bash}
    Copy/paste this URL into your browser when you connect for the first time,
    to login with a token:
        http://localhost:8889/?token=b0efba1584493f08426e2a4910b6bdf0e5d35a19b0fbc873
```
The notebook is now running on the BRIDGE machine, but we need to connect to it on our local computer. 

On a Mac or Linux computer, you can type the following in to a terminal window (not the one connected to the BRIDGE server!):

```{bash}
$ ssh -N -f -L localhost:8889:localhost:8889 username@anthropocene.ggy.bris.ac.uk
```
On a Windows computer you'll need to use PuTTY. On the left hand list of options select 'SSH' and then 'Tunnels'. 
In 'source port' enter '8889', and in 'Destination' add 'localhost:8889'. Press 'Add'. Then go back to 'Session' at the top of
the left hand menu, in 'Host Name' enter 'anthropocene.ggy.bris.ac.uk'. Press 'Open' then enter your username and password.

Now in a web browser enter 'localhost:8889' in the URL box. You should be greeted with a Jupyter page asking for a token. 
Copy the token number which was printed when you set up the notebook server (i.e. the number after 'token=' in the output as above.)

You should now be logged-in and good to go. I will cover analysis in Jupyter Notebooks in a later guide. 

