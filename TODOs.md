### WE HAVE A VARIABLES MESS.
### WE SHOULD HAVE A FUNCTION "CLEAN UP" OR SO, THAT LET'S US REMOVE KEYS FROM THE GLOBAL DICT
### IF THEY ARE NOT USED ???
### ENCAPSULATE USER SETTINGS??!!!!

### example settings::::: here a standard dict is defined. BUT: is it the same as loading the config json file???
### WE NEED TO MAKE SURE THAT THE CONFIG DICT IS UPDATED.

# TODOS:
# ADD LOGGING?
# CREATE A FACADE ALSO FOR THE GUI ELEMENTS
# eliminate global variables; adapt file opening procedures?
# reloading of files needs to be improved
# automatical searching and loading of files
# update get_new_data
# we need to handle different
# we could enforce that dictionary keys must be present!
# check streaming button
# done - implement strategy + facade patterns for file loading
# done - we could store each button in a function and store it in the dict.
# contains keys; using keys:
# done - dict_global['gui_elements'] = ''
# done - concurrent mode so gui becomes less laggy
#
# replace printing by logging?
# no concatenate if new df is empty. -> better: check file stamps and file not read if
#
# option to open multiple file types, command line multiple json files, maybe even monitoring multiple files... :-oooooooo
#
# the normalizer from "DataReaderStrategy" works but is not helpful
# get one function
#
# to make it more robust, we need to somehow automatically check headers and rest
#
# bring config file to yaml
#
# watchdog, observer for data processing pipelines
# multifile options?
#
# done - pyproject.toml
# started - splitting in more modules
#

https://stackoverflow.com/questions/6920302/how-to-pass-arguments-to-a-button-command-in-tkinter

if commandline --test: run test generator on some file
detect or define data visualizator - e.g. tabular vs image data
additional: watchdog

what for now? refactor and restructure. Extract functions and resolve imports.
Solve the issues of the checkboxes and curves to be plotted.
replace pandas by polars?

DO NOT STREAM IF THE FILE CANNOT BE READ!

separate in dict_global (internal) and dict_user_settings?

command line arguments?

https://learn.scientific-python.org/development/guides/gha-pure/

for issues with GIT: https://graphite.dev/guides/how-to-merge-branch-to-main-in-git
