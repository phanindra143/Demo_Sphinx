-- Lua script.
p=tetview:new()
p:load_plc("//bay2019/home/ravi/01_Ravi_Phanindra/mpaut/examples/output/voxels.tmpSurf.smesh")
rnd=glvCreate(0, 0, 500, 500, "TetView")
p:plot(rnd)
glvWait()
