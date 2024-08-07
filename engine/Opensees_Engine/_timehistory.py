import openseespy.opensees as ops    


def Timehistory(Nsteps2run,Acc_values,fsi,Nd_Rsp,Opt_File_Nme,freq,damp):
    ops.wipeAnalysis()
    fso = int(fsi/2)
    
    ops.timeSeries('Path', 11, '-dt', 1/fsi,'-values', *Acc_values)
    ops.pattern('UniformExcitation', 1, 1, '-accel', 11) 
    
    # ops.timeSeries('Path', 22, '-dt', 1/fsi,'-values', *Acc_values)
    # ops.pattern('UniformExcitation', 2, 2, '-accel', 22) 
    
    ops.timeSeries('Path', 33, '-dt', 1/fsi,'-values', *Acc_values)
    ops.pattern('UniformExcitation', 3, 1, '-accel', 33) 
    

    #  change to vel and also activate 11 timeseries 


    
    # ops.timeSeries('Path', 1, '-dt', 1/500, '-filePath',Acc_Series, '-factor',1)
    # ops.recorder('Node', '-file', Opt_File_Nme ,'-timeSeries', 33,'-dT', 1/fso,'-node', *Nd_Rsp,'-dof',1,'vel')
    ops.recorder('Node', '-file', Opt_File_Nme,'-dT', 1/fso,'-node', *Nd_Rsp,'-dof',*[1],'vel')
    # ops.recorder('Node', '- xml', Opt_File_Nme,'-dT', 1/fso,'-node', *Nd_Rsp,'-dof',*[3],'vel')
   
    dampRatio = 0.02
    ops.rayleigh(0, 0, 0,2*dampRatio/freq[0])
    # create the analysis
    ops.constraints(' Transformation')
    ops.numberer('Plain')    # renumber dof's to minimize band-width (optimization), if you want to
    ops.system('BandGeneral') # how to store and solve the system of equations in the analysis
    ops.algorithm('Linear')     # use Linear algorithm for linear analysis
    ops.integrator('Newmark', 0.5, 0.25)    # determine the next time step for an analysis
    ops.analysis('Transient')   # define type of analysis: time-dependent
    ops.analyze(int(Nsteps2run), 1/fso)     # apply time steps in analysis
    ops.remove('recorders')    



def Timehistory_loads(Nsteps2run,Acc_values,fsi,Opt_File_Nme,freq,elements):
    ops.wipeAnalysis()
    fso = int(fsi/2)
    
    # ops.timeSeries('Path', 11, '-dt', 1/fsi,'-values', *Acc_values)
    # ops.pattern('UniformExcitation', 1, 1, '-accel', 11) 
    
    ops.timeSeries('Path', 22, '-dt', 1/fsi,'-values', *Acc_values)
    ops.pattern('UniformExcitation', 2, 2, '-accel', 22) 

    ops.recorder('Element', '-file',Opt_File_Nme,'-ele',*elements,'globalForce')
   
    dampRatio = 0.02
    ops.rayleigh(0, 0, 0,2*dampRatio/freq[0])
    ops.constraints(' Transformation')
    ops.numberer('Plain')    # renumber dof's to minimize band-width (optimization), if you want to
    ops.system('BandGeneral') # how to store and solve the system of equations in the analysis
    ops.algorithm('Linear')     # use Linear algorithm for linear analysis
    ops.integrator('Newmark', 0.5, 0.25)    # determine the next time step for an analysis
    ops.analysis('Transient')   # define type of analysis: time-dependent
    ops.analyze(int(Nsteps2run), 1/fso)     # apply time steps in analysis
    ops.remove('recorders')  
    
    
def get_forces(elements, resp):
    loads = {}
    
    # Define the step size which is 2*6 = 12 columns
    step_size = 2*6
    
    for idx, ele in enumerate(elements):
        start_idx = idx * step_size
        loads[ele] = {}  
        loads[ele]['i'] = resp[:, start_idx:start_idx+6]  # Get the first 6 columns for the current element
        loads[ele]['j'] = resp[:, start_idx+6:start_idx+12]  # Get the next 6 columns
    return loads
    



    


