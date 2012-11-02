# XP Airports
XP Airports is a small programm which provides navigation data from X-Plane to the user. The skript uses the earth_nav.dat file of X-Plane as data pool. The user is able to search for an airport or the ident of the navigation point. 

## Intern process
The idea to that script is very easy. A user enters a search phrase and the programm reads the navigation file and filters the right entries. Because of the small file-size there is no need for a database.

## Features (allready working)
* GUI using Tkinter
* search for an airport over an ICAO code
* search for an ident of all navigation-points
* filter for types (e.g. ILS, VOR or NDB)

## Planed features
* update of the navigation data
* integration to X-Plane programm using the python gui
* provide .exe file for windows users



## Dokumentation of the data
The navigation data file is availiable at [http://data.x-plane.com/get_data.html](http://data.x-plane.com/get_data.html "data.x-plane.com"). 

The documentation to the file format of the earth_nav.dat as pdf: [http://data.x-plane.com/file_specs/XP%20NAV810%20Spec.pdf](http://data.x-plane.com/file_specs/XP%20NAV810%20Spec.pdf "Dokumentation (pdf-file)")
