![PyTrak](https://raw.githubusercontent.com/lindemann09/pytrak/master/pytrak/pytrak_logo.png)

Python-based motion tracking software for 3D Guidance trakSTAR

*Released under the GNU General Public License (v3)*

 Oliver Lindemann <oliver.lindemann@cognitive-psychology.eu>
 
Dependencies
------------
* Python 2.7 & NumPy 1.7 or higher
* Expyriment 0.7.0 or higher
* trakSTAR Windows API (`ATC3DG.DLL` or `ATC3DG64.DLL`). The dynamic link library is needed in the Windows 
  system folder or in the `pytrak` subfolder. (see trakSTAR driver CD or ftp.ascension-tech.com)

  **Links**
  * Expyriment: http://www.expyriment.org and https://github.com/expyriment/expyriment
  * trakSTAR 2: http://www.ascension-tech.com/medical/trakSTAR.php
  * dll files (trakSTAR Windows API): ftp://ftp.ascension-tech.com/DRIVERS/MATLAB_LABVIEW_DRIVER/MATLAB%20Demo%20v5.zip

Development
-----------

https://github.com/lindemann09/pytrak/

Please [submit](https://github.com/lindemann09/pytrak/issues/new) any bugs you encounter to the Github issue tracker.

**NOTE**: So far, the Python api wrapper is experimental under Linux and has been merely tested under Windows.
