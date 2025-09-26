-- Lua script.
p=tetview:new()
p:load_plc("C:/Users/ravi/Desktop/mpaut/examples/output/voxels.tmpSurf.smesh")
rnd=glvCreate(0, 0, 500, 500, "TetView")
p:plot(rnd)
glvWait()
