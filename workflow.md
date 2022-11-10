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
    2. update learn_Git.md, hope to finish. Actually encountered conflict, not sure how to resolve.

  **10/30**
    1. finish io module, not it can process all supported data into a unified grid, with dimensions of time, lat, lon.
    2. resolve conflicts with different branches, use git push remote --force. Finally finished learn_git.md.

- [ ] extrapolation at a specific time, eg., optical flow method, machine learning method;
  **10/31**
    1. fetch the optical flow codes used before;
    2. preparation for machine learning by learning UNet with SEVIR data.

- [x] interpolation into a customized grid;
  **11/2-3**
    1. interpolate into a aircraft-based grid.
    2. fix the io module's bug, the 98d radar should share the same structure with other obs. sources.

  **11/4**
    1. take a day off due to the quarantine policy (without 48-hour negtive certification). [ continue the MOS pipeline, 80% done. ]
  
  **11/5**
    1. finish the interpolation module, using the last time frame for test first.

- [ ] visualization.
  **11/5**
    1. begin the ac graph module

  **11/6**
    1. take a day off, changlong sea creature exihit.

  **11/7**
    1. 


  **10/10**
  1. 收拾行李，移动接电话问题解决，语音不通畅是14pro手机的问题，联系取货地址的更改。陈老师的摘要。


1. 月底之前把流程走完
   1. 融合：近处机载、远处地基 
2. 这周把时间、空间对齐的报告写一下哦～ 


