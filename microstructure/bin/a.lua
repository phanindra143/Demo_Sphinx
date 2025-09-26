-- Lua script.
p=tetview:new()
p:load_plc("U:/01_Ravi_Phanindra/Hiwi/01_Documenting_Voxsm/Sphere/10_objects_Rdius10/10_spheres.tmpSurf.smesh")
rnd=glvCreate(0, 0, 500, 500, "TetView")
p:plot(rnd)
glvWait()
