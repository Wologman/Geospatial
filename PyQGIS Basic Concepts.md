[A good starting point](https://towardsdatascience.com/how-to-use-qgis-spatial-algorithms-with-python-scripts-4bf980e39898)
[Another clue here about the PYTHONPATH variable](https://digital-geography.com/how-to-use-pyqgis-as-standalone-script-on-ubuntu/)

*You can’t import the QGIS library from your default python environment. QGIS has its version of python installed to handle all the required modules to run the software. So if you need to use the QGIS library from the python console/jupyter notebook, you need to make sure your python can find the QGIS library paths. Or you can install the QGIS library in your python environment.

What exactly would I want to use Python for with QGIS?
1. Make a QGIS plugin 
2. Make a script that can be run through the QGIS GUI built-in python console
3. Use for stand-alone back-end processing, alongside other tools, to process some data, produce new data.  The product could be the new data/analysis, or a Jupyter Notebook.

For the time-being I really only need to master (2) & (3).  For Rob's sort of work, and building up some useful helper functions I would use (2).  For exploring new topics, building up ML workflows, I might find it better to go for (3).  When I'm good at that I might want to consider 1, but I don't really have any business case for that right now.

*The question that I have been stuck on is whether (2) can be used to control the GUI with pyQT, or does that only work if it's running through the integrated terminal.  Test this with a really basic example if I can't find it online anywhere.  

*Does this even make sense?  The only reason to do this is for development, once the script is ready, it will be run through the console anyway.  Most developers are going to (1), so not much gets written about (2).

#### 1. Making a QGIS plugin
- Done through plugin builder to make the code base [here is a tutorial](http://www.qgistutorials.com/vi/docs/3/processing_python_plugin.html)
- Requires a lot of setup, to test the plugin also install plugin-reloader.
- Provides the most useful and distributable end-product

#### 2. Using an external IDE to write a script, for running in QGIS
I suspect the only thing here is to make sure the pythonpath variable is updated, for the editor and also for Pylynt and such.  It will probably not run from the editor, but need loading into the QGIS console.

#### 3. Standalone scripts from an IDE
So if the goal is to use the QGIS libraries for back-end processes, or Jupyter notebooks, there is no need to worry about Qt, or dialogue boxes and such.  In this case there are two options:

##### (Option 1) Create a Conda environment, and install QGIS libraries
Using conda, you can install the QGIS package like any other library on Python.  It should be this simple:

```bash
conda install -c conda-forge qgis
```

There are noteable downsides to this approach though, hence option (2) is preferable.
1. It is memory intensive to install QGIS for each conda environment you want to create for a new project.
2. Not all the QGIS libraries will be available.  Notably GRASS and SAGA will be missing.  So the capabilities are quite limited.   

##### (2) Map the QGIS Desktop software libraries from your Virtual Python Env
This is the instruction that shows up on the internet, as it is also the way that would be needed for creation of QGIS plugins.  This could be done in VScode with the settings, so I work with a specific  .code-worspace settings file (and .env file) as well as a specific python environment.

On Ubuntu if I go into the python shell within qgis and look up the PYTHONPATH I get this list:

```python
import sys  
print(sys.path)

>>> ['/usr/share/qgis/python', '/home/olly/.local/share/QGIS/QGIS3/profiles/default/python', '/home/olly/.local/share/QGIS/QGIS3/profiles/default/python/plugins', '/usr/share/qgis/python/plugins', '/usr/lib/python38.zip', '/usr/lib/python3.8', '/usr/lib/python3.8/lib-dynload', '/home/olly/.local/lib/python3.8/site-packages', '/usr/local/lib/python3.8/dist-packages', '/usr/lib/python3/dist-packages', '/home/olly/.local/share/QGIS/QGIS3/profiles/default/python']
```

Also if I check the interpreter being used

```python
import sys
print(sys.executable)

>>> /usr/bin/python3
```

- Before you can use the QGIS libraries and their spatial algorithms in your python script, we need to set up the PYTHONPATH and 
- Select the interpreter at `/usr/bin/python3`. I don't necessarily need a conda environment for this, in VSCode it can be stored in the workspace settings .json file (through the interpreter menue on the GUI).  I may want to use a conda environment for other reasons though, such as managaging other packages for ML for example.

So I can see a couple of things here:
1. I should be using python 3.8 
2. There are some key paths that do not appear in my IDE path.  Especially `/usr/lib/python3/dist-packages`    

Work on understanding how to use these from the IDE.

#### Library imports
When directly writing scripts in the built-in editor it doesn't seem necessary to import the QGIS libraries.  Presumably this is done by the API its self somehow.

For example this is OK, without any inport statement

```python
layers = QgsProject.instance().mapLayers() #returns a dict,
```

But say I'm trying to write a standalone script, in this case I might need to.  I imagine something like this.

```python
from qgis.core import *
```

#### Standalone Scripts
So I think this is when I use the QGIS functionality, to operate on some data, but it doesn't affect the interface its self?

#### Plugins
These are based on the QT API.  Perhaps to use those I need to add them to the python path as well.



