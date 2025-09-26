-- Lua script.
p=tetview:new()
p:load_plc("C:/Users/ravi/Desktop/mpaut/old_examples/output/10_spheres.tmpSurf.smesh")
rnd=glvCreate(0, 0, 500, 500, "TetView")
p:plot(rnd)
glvWait()
