Current App requirements:
I highly recommend you attempt to run this in Monty as the Renderman's and Python's setup 'should' be set up right there. (Famous last words...)
Python 2.7
PyQt4.0 or higher (Normally installed, more info here: https://sourceforge.net/projects/pyqt/)
Renderman 21 Pro Server (if Env is not set right, the settings can be updated to point to the installation of Renderman. in OSE\OSE_Modules\settings)


To Download
Download this file from my Dropbox
Then extract the zip folder.

To Run:
> cd <folder where you extracted>/OSE
> python2.7 OSE.py


Trouble Shooting:
Unable to import PyQt4 Module:
This means that you do not have Pyqt 4 installed or the path is not pointed there. You can install pyqt or if you already did, make sure your python path is set correctly.

No nodes are showing up under the "Nodes" menu:
This means that the application was unable to locate Renderman 21. If you have it installed you can check to make sure your RMANTREE env is set up right or edit
OSE\OSE_Modules\settings\path.json to point to the correct installation of Renderman. Another possibility is that you have an older version of Renderman. Currently the node importer only supports Renderman 21.0 or higher due to Pixar changing the directory structure in the new major version. 