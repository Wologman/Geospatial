[Useful Reference for Standalone VSCode on Ubuntu](https://digital-geography.com/how-to-use-pyqgis-as-standalone-script-on-ubuntu/)

[This one specifically about importing the processing plugin](https://gis.stackexchange.com/questions/279874/using-qgis-processing-algorithms-from-pyqgis-standalone-scripts-outside-of-gui)

[Official documentation for using processing plugin from command line](https://docs.qgis.org/3.22/en/docs/user_manual/processing/standalone.html)

The key seems to be with the processing plugin.  It is accessed through a different file-path.

This one is referred to by the QGIS PYTHONPATH, from the shell in the QGIS GUI, but it does not exist: `/home/olly/.local/share/QGIS/QGIS3/profiles/default/python/plugins`

This similar looking one does: `/usr/share/qgis/python/plugins`

But neither are appearing in sys.path in vscode.  This is the root of the problem I think.

Do they get ignored after one doesn't exist?

Give up on this for the time being.  Since I've already switched to PyCharm.

