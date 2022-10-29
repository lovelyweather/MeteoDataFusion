# the meteo_data_fusion projects

following is the workflow:

- [x] read all kinds of weather data and process into a unified format, [time, lat, lon]; 
  **10/28**: 
    1. continue the wsr98d module, automatically plot, interpolation
       - found an issue, compz is always nan, fixed by modifying 'comp_.py, Line 124: compz = z_stack.max(axis=0).astype(z_dtype)' into **'compz = np.nanmax( z_stack,axis=0 ).astype(z_dtype)'**. 
    2. update learn_git.md. 
- [ ] extrapolation at a specific time, eg., optical flow method, machine learning method;
- [ ] interpolation into a customized grid;
- [ ] visualization.
