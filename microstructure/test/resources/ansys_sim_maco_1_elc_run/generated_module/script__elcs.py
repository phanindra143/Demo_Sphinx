from .utils import wait_for_checkpoint_file

def run(mapdl):
    mapdl.finish()
    mapdl.run("/clear")
    mapdl.run("/filname,ELCs")
    mapdl.run("/PREP7")
    # ----------- INPUT: _________________
    mapdl.resume("WC_50spheres_0605_00ovlp", "db")
    mapdl.run("matnum_1 = 1  ")  # (WC)
    mapdl.run("matnum_2 = 2  ")  # (Co)
    # _____________________________________
    # ----------------------------------PROGRAMM----------------------
    # *** Definition material parameter ***
    mapdl.run("emod_1=650      ")  # E_modulus in 'Hauptphase'=WCin GPa
    mapdl.run("pois_1=0.22	")  # Poissonzahl Hauptphase
    mapdl.run("emod_2=210		")  # E_modulus in 'Nebenphase'= Co
    mapdl.run("pois_2=0.31   	")  # Poissonzahl Nebenphase
    # *** Parameters ***
    nifx=6
    difx=1
    # *** Attribute material to different phases ***
    # SiC:
    mapdl.mp("ex", "matnum_1", "emod_1*1e9")
    mapdl.mp("prxy", "matnum_1", "pois_1")
    # Si:
    mapdl.mp("ex", "matnum_2", "emod_2*1e9")
    mapdl.mp("prxy", "matnum_2", "pois_2")
    # poren:
    # mp,ex,10000,emod_2*1e9    1e-4
    # mp,prxy,10000,pois_2      1e-4
    mapdl.save("work", "db", "")
    di = 1
    while di < nifx:
        mapdl.run("/OUT,progress.out")
        mapdl.run("/COM,done")
        mapdl.run("/OUT")
        mapdl.parsav("all", "param1", "fem")
        mapdl.resume("work", "db", "", "", "")
        mapdl.parres("new", "param1", "fem")
        ifx = di
        # *** SET LOADS ***
        mapdl.run("/prep7		")
        mapdl.lsclear("all")  #Löscht alle vorhandenen Randbedingungen
        # Stringvariable für Koordinatenrichtungen einführen
        mapdl.run("v1='x'")
        mapdl.run("v2='y'")
        mapdl.run("v3='z'")
        # 
        if ifx % 3 == 1:
            mapdl.run("vx='x'")
            mapdl.run("vy='y'")
            mapdl.run("vz='z'")
        elif ifx % 3 == 2:
            mapdl.run("vx='z'")
            mapdl.run("vy='x'")
            mapdl.run("vz='y'")
        elif ifx % 3 == 0:
            mapdl.run("vx='y'")
            mapdl.run("vy='z'")
            mapdl.run("vz='x'")
        mapdl.run("delver=L*1/200  ")  # Längentoleranz für Selektion der Randknoten
        mapdl.allsel("all")
        mapdl.finish()
        mapdl.run("/solu")
        if_inull = 0
        if ifx < 4:
            if_inull = 1
        if if_inull == 1:
            # Innere Ebenen Verschiebung 0 setzen
            mapdl.allsel("all")
            mapdl.nsel("s", "loc", "%vx%", "0-delver", "0+delver")
            mapdl.d("all", "u%vx%", 0)
            mapdl.allsel("all")
            mapdl.nsel("s", "loc", "%vy%", "0-delver", "0+delver")
            mapdl.d("all", "u%vy%", 0)
            mapdl.allsel("all")
            mapdl.nsel("s", "LOC", "%vz%", "0-delver", "0+delver")
            mapdl.d("all", "u%vz%", 0)
            # Knoten auf den Außenebenen %vx% = L und %vy% = 0 in Richtungen senkrecht
            # zur Zugspannung koppeln (zwangsweise gleiche Verschiebung)
            mapdl.allsel("all")
            mapdl.nsel("s", "loc", "%vx%", "L-delver", "L+delver")
            mapdl.cp(2, "u%vx%", "all")
            mapdl.allsel("all")
            mapdl.nsel("s", "loc", "%vy%", "L-delver", "L+delver")
            mapdl.cp(3, "u%vy%", "all")
            mapdl.allsel("all")
        mapdl.run("delrot=(1.0e-4)*L       ")  # Shear strain
        mapdl.run("delshi=(1.5e-4)*L     ")  # Tensile strain
        # 
        if ifx >= 4:
            # simple shear auf vy=0 und vy=l Ebenen,
            # tensile strain auf vz=0 und vz=l Ebenen
            # Aussenflächen auswählen und Verschiebung setzen
            mapdl.nsel("s", "ext")
            mapdl.d("all", "u%vz%", 0)
            mapdl.nsel("r", "LOC", "%vy%", "-delver", "+delver")
            mapdl.d("all", "u%vx%", 0)
            mapdl.allsel("all")
            mapdl.nsel("s", "ext")
            mapdl.nsel("r", "LOC", "%vy%", "L-delver", "L+delver")
            mapdl.d("all", "u%vx%", "delrot")
            mapdl.allsel("all")
            mapdl.nsel("s", "ext")
            mapdl.nsel("r", "LOC", "%vx%", "-delver", "+delver")
            mapdl.d("all", "u%vy%", 0)
            mapdl.allsel("all")
            mapdl.nsel("s", "ext")
            mapdl.nsel("r", "LOC", "%vx%", "L-delver", "L+delver")
            mapdl.d("all", "u%vy%", 0)
        else: # (ifx,lt,4), also für tensile strain
            mapdl.allsel("all")
            mapdl.nsel("s", "LOC", "%vz%", "L-delver", "L+delver")
            mapdl.d("all", "u%vz%", "delshi")
        # *** SOLVE ***
        mapdl.allsel()
        mapdl.run("/status,solu")
        mapdl.eqslv("jcg", 1e-08)  #JCG solver
        mapdl.solve()
        mapdl.finish()
        mapdl.run("/post1")
        # *** SET POSTPROCESSING ***
        mapdl.allsel("all")
        mapdl.esel("s", "mat", "", 1)  #volumenanteil für mat.1 berechnen
        mapdl.etable("e_vol1", "volu", "")
        mapdl.ssum()
        mapdl.run("*get,v_mat1,ssum,0,item,e_vol1")
        mapdl.etable("e_vol1", "eras")
        mapdl.allsel("all")
        mapdl.esel("s", "mat", "", 2)  #volumenanteil für mat.9 berechnen
        mapdl.etable("e_vol9", "volu", "")
        mapdl.ssum()
        mapdl.run("*get,v_mat9,ssum,0,item,e_vol9")
        mapdl.etable("e_vol9", "eras")
        # Volumen des gesamten Würfels bestimmen (v_i) und Elementtabelle mit Volumen anlegen
        mapdl.allsel("all")
        mapdl.etable("e_vol", "volu", "")
        mapdl.etable("s_1", "s", 1)
        mapdl.smult("sv", "s_1", "e_vol")
        mapdl.ssum()
        mapdl.run("*get,v_i,ssum,0,item,e_vol")
        mapdl.run("v_ph1=v_mat1/v_i")
        mapdl.run("v_ph9=v_mat9/v_i")
        mapdl.run("*get,sv_i,ssum,0,item,sv")
        mapdl.run("f_z=sv_i/L**3                  ")  # Durchschnittliche Zugspannung
        # 
        mapdl.run("v1='x'")
        mapdl.run("v2='y'")
        mapdl.run("v3='z'")
        mapdl.run("v4='xy'")
        mapdl.run("v5='yz'")
        mapdl.run("v6='xz'")
        # 
        mapdl.run("vv1='xx'")
        mapdl.run("vv2='yy'")
        mapdl.run("vv3='zz'")
        mapdl.run("vv4='xy'")
        mapdl.run("vv5='yz'")
        mapdl.run("vv6='xz'")
        # 
        ni = 1
        while ni < 6:
            mapdl.etable("e_el%ni%", "epel", "v%ni%")
            mapdl.etable("s_el%ni%", "s", "v%ni%")
            mapdl.smult("ev_i", "e_el%ni%", "e_vol")
            mapdl.smult("sv_i", "s_el%ni%", "e_vol")
            mapdl.ssum()
            mapdl.run("*get,e_%ni%,ssum,0,item,ev_i")
            mapdl.run("*get,s_%ni%,ssum,0,item,sv_i")
            mapdl.run("vv=vv%ni%")
            mapdl.run("e_%vv%=e_%ni%/v_i")
            mapdl.run("f_%vv%=s_%ni%/v_i")
            # 
            mapdl.etable("ev_i", "eras")
            mapdl.etable("sv_i", "eras")
            i += 1
        mapdl.etable("eras")

        mapdl.run("/output,out_elc,out,,append,")
        mapdl.run("*vwrite,'ifx','fxx','fyy','fzz','fxy','fxz','fyz'")
        mapdl.run("(7A15)")
        mapdl.run("*vwrite")
        mapdl.run("/%")
        mapdl.run("*vwrite,ifx,f_xx*1e-6,f_yy*1e-6,f_zz*1e-6,f_xy*1e-6,f_xz*1e-6,f_yz*1e-6,")
        mapdl.run("(7F15.5)")
        mapdl.run("*vwrite")
        mapdl.run("/%")
        mapdl.run("*vwrite,'ifx','exx','eyy','ezz','exy','exz','eyz',")
        mapdl.run("(7A15)")
        mapdl.run("*vwrite")
        mapdl.run("/%")
        mapdl.run("*vwrite,ifx,e_xx*1000,e_yy*1000,e_zz*1000,e_xy*1000,e_xz*1000,e_yz*1000,")
        mapdl.run("(7F15.5)")
        mapdl.run("*vwrite")
        mapdl.run("/%")
        mapdl.run("/output,term")
        if ifx == 6:
            mapdl.run("/output,out_elc,out,,append,")
            mapdl.run("*vwrite,v_ph1,v_ph9,")
            mapdl.run("(7F15.5)")
            mapdl.run("*vwrite")
            mapdl.run("/%")
            mapdl.run("/output,term")
        # /%
        di += difx
        mapdl.save("sol6_elc", "db", "")
