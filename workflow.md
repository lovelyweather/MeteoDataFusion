# the meteo_data_fusion projects

following is the workflow:

- [x] learning git to do the version control.
- [x] read all kinds of weather data and process into a unified format, [time, lat, lon]; 
  **10/28**: 
    1. continue the wsr98d module, automatically plot, interpolation
       - found an issue, compz is always nan, fixed by modifying 'comp_z.py, Line 124: compz = z_stack.max(axis=0).astype(z_dtype)' into **'compz = np.nanmax( z_stack,axis=0 ).astype(z_dtype)'**. 
    2. update learn_git.md. 

  **10/29**
    1. continue the wsr98d module, process into dataframe with time dimension. (2-3h)
    2. update learn_Git.md, hope to finish.(2-3h)
       1. MOS reading, organizing GBM. 

- [ ] extrapolation at a specific time, eg., optical flow method, machine learning method;
- [ ] interpolation into a customized grid;
- [ ] visualization.
