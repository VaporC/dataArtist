If you cannot execute dataArtist.exe,

you will need to install the visual studio 215 redistributables, to be found within this folder.


Why?
---
dataArtist used <numba> for accelerating several array based routines.
Numba used <llvmlite> deliveres its own VS runtime but for some reasons I dont understand there are still external dependencies - which can be resolved by installing the redistributables. 