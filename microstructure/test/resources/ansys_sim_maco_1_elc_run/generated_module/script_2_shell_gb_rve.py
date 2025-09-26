from .utils import wait_for_checkpoint_file

def run(mapdl):
    # 86 CMs (particles)
    # c_100001
    # c_100002
    # c_100003
    # c_100004
    # c_100005
    # c_100006
    # c_100007
    # c_100008
    # c_100009
    # c_100010
    # c_100011
    # c_100012
    # c_100013
    # c_100014
    # c_100015
    # c_100016
    # c_100017
    # c_100018
    # c_100019
    # c_100020
    # c_100021
    # c_100022
    # c_100023
    # c_100024
    # c_100025
    # c_100026
    # c_100027
    # c_100028
    # c_100029
    # c_100030
    # c_100031
    # c_100032
    # c_100033
    # c_100034
    # c_100035
    # c_100036
    # c_100037
    # c_100038
    # c_100039
    # c_100040
    # c_100041
    # c_100042
    # c_100043
    # c_100044
    # c_100045
    # c_100046
    # c_100047
    # c_100048
    # c_100049
    # c_100050
    # c_100051
    # c_100052
    # c_100053
    # c_100054
    # c_100055
    # c_100056
    # c_100057
    # c_100058
    # c_100059
    # c_100060
    # c_100061
    # c_100062
    # c_100063
    # c_100064
    # c_100065
    # c_100066
    # c_100067
    # c_100068
    # c_100069
    # c_100070
    # c_100071
    # c_100072
    # c_100073
    # c_100074
    # c_100075
    # c_100076
    # c_100077
    # c_100078
    # c_100079
    # c_100080
    # c_100081
    # c_100082
    # c_100083
    # c_100084
    # c_100085
    # c_200000
    mapdl.type(2)
    mapdl.mat(20000)  #GBs in-plane
    # c_100001
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_0','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_0.out')
    mapdl.cm("c_100001", "Elem")
    # c_100002
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_1','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_1.out')
    mapdl.cm("c_100002", "Elem")
    # c_100003
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_2','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_2.out')
    mapdl.cm("c_100003", "Elem")
    # c_100004
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_3','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_3.out')
    mapdl.cm("c_100004", "Elem")
    # c_100005
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_4','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_4.out')
    mapdl.cm("c_100005", "Elem")
    # c_100006
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_5','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_5.out')
    mapdl.cm("c_100006", "Elem")
    # c_100007
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_6','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_6.out')
    mapdl.cm("c_100007", "Elem")
    # c_100008
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_7','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_7.out')
    mapdl.cm("c_100008", "Elem")
    # c_100009
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_8','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_8.out')
    mapdl.cm("c_100009", "Elem")
    # c_100010
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_9','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_9.out')
    mapdl.cm("c_100010", "Elem")
    # c_100011
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_10','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_10.out')
    mapdl.cm("c_100011", "Elem")
    # c_100012
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_11','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_11.out')
    mapdl.cm("c_100012", "Elem")
    # c_100013
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_12','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_12.out')
    mapdl.cm("c_100013", "Elem")
    # c_100014
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_13','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_13.out')
    mapdl.cm("c_100014", "Elem")
    # c_100015
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_14','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_14.out')
    mapdl.cm("c_100015", "Elem")
    # c_100016
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_15','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_15.out')
    mapdl.cm("c_100016", "Elem")
    # c_100017
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_16','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_16.out')
    mapdl.cm("c_100017", "Elem")
    # c_100018
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_17','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_17.out')
    mapdl.cm("c_100018", "Elem")
    # c_100019
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_18','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_18.out')
    mapdl.cm("c_100019", "Elem")
    # c_100020
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_19','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_19.out')
    mapdl.cm("c_100020", "Elem")
    # c_100021
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_20','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_20.out')
    mapdl.cm("c_100021", "Elem")
    # c_100022
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_21','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_21.out')
    mapdl.cm("c_100022", "Elem")
    # c_100023
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_22','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_22.out')
    mapdl.cm("c_100023", "Elem")
    # c_100024
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_23','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_23.out')
    mapdl.cm("c_100024", "Elem")
    # c_100025
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_24','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_24.out')
    mapdl.cm("c_100025", "Elem")
    # c_100026
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_25','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_25.out')
    mapdl.cm("c_100026", "Elem")
    # c_100027
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_26','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_26.out')
    mapdl.cm("c_100027", "Elem")
    # c_100028
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_27','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_27.out')
    mapdl.cm("c_100028", "Elem")
    # c_100029
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_28','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_28.out')
    mapdl.cm("c_100029", "Elem")
    # c_100030
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_29','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_29.out')
    mapdl.cm("c_100030", "Elem")
    # c_100031
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_30','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_30.out')
    mapdl.cm("c_100031", "Elem")
    # c_100032
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_31','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_31.out')
    mapdl.cm("c_100032", "Elem")
    # c_100033
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_32','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_32.out')
    mapdl.cm("c_100033", "Elem")
    # c_100034
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_33','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_33.out')
    mapdl.cm("c_100034", "Elem")
    # c_100035
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_34','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_34.out')
    mapdl.cm("c_100035", "Elem")
    # c_100036
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_35','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_35.out')
    mapdl.cm("c_100036", "Elem")
    # c_100037
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_36','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_36.out')
    mapdl.cm("c_100037", "Elem")
    # c_100038
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_37','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_37.out')
    mapdl.cm("c_100038", "Elem")
    # c_100039
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_38','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_38.out')
    mapdl.cm("c_100039", "Elem")
    # c_100040
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_39','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_39.out')
    mapdl.cm("c_100040", "Elem")
    # c_100041
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_40','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_40.out')
    mapdl.cm("c_100041", "Elem")
    # c_100042
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_41','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_41.out')
    mapdl.cm("c_100042", "Elem")
    # c_100043
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_42','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_42.out')
    mapdl.cm("c_100043", "Elem")
    # c_100044
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_43','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_43.out')
    mapdl.cm("c_100044", "Elem")
    # c_100045
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_44','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_44.out')
    mapdl.cm("c_100045", "Elem")
    # c_100046
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_45','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_45.out')
    mapdl.cm("c_100046", "Elem")
    # c_100047
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_46','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_46.out')
    mapdl.cm("c_100047", "Elem")
    # c_100048
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_47','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_47.out')
    mapdl.cm("c_100048", "Elem")
    # c_100049
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_48','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_48.out')
    mapdl.cm("c_100049", "Elem")
    # c_100050
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_49','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_49.out')
    mapdl.cm("c_100050", "Elem")
    # c_100051
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_50','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_50.out')
    mapdl.cm("c_100051", "Elem")
    # c_100052
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_51','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_51.out')
    mapdl.cm("c_100052", "Elem")
    # c_100053
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_52','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_52.out')
    mapdl.cm("c_100053", "Elem")
    # c_100054
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_53','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_53.out')
    mapdl.cm("c_100054", "Elem")
    # c_100055
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_54','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_54.out')
    mapdl.cm("c_100055", "Elem")
    # c_100056
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_55','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_55.out')
    mapdl.cm("c_100056", "Elem")
    # c_100057
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_56','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_56.out')
    mapdl.cm("c_100057", "Elem")
    # c_100058
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_57','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_57.out')
    mapdl.cm("c_100058", "Elem")
    # c_100059
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_58','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_58.out')
    mapdl.cm("c_100059", "Elem")
    # c_100060
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_59','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_59.out')
    mapdl.cm("c_100060", "Elem")
    # c_100061
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_60','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_60.out')
    mapdl.cm("c_100061", "Elem")
    # c_100062
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_61','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_61.out')
    mapdl.cm("c_100062", "Elem")
    # c_100063
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_62','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_62.out')
    mapdl.cm("c_100063", "Elem")
    # c_100064
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_63','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_63.out')
    mapdl.cm("c_100064", "Elem")
    # c_100065
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_64','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_64.out')
    mapdl.cm("c_100065", "Elem")
    # c_100066
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_65','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_65.out')
    mapdl.cm("c_100066", "Elem")
    # c_100067
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_66','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_66.out')
    mapdl.cm("c_100067", "Elem")
    # c_100068
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_67','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_67.out')
    mapdl.cm("c_100068", "Elem")
    # c_100069
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_68','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_68.out')
    mapdl.cm("c_100069", "Elem")
    # c_100070
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_69','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_69.out')
    mapdl.cm("c_100070", "Elem")
    # c_100071
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_70','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_70.out')
    mapdl.cm("c_100071", "Elem")
    # c_100072
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_71','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_71.out')
    mapdl.cm("c_100072", "Elem")
    # c_100073
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_72','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_72.out')
    mapdl.cm("c_100073", "Elem")
    # c_100074
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_73','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_73.out')
    mapdl.cm("c_100074", "Elem")
    # c_100075
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_74','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_74.out')
    mapdl.cm("c_100075", "Elem")
    # c_100076
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_75','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_75.out')
    mapdl.cm("c_100076", "Elem")
    # c_100077
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_76','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_76.out')
    mapdl.cm("c_100077", "Elem")
    # c_100078
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_77','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_77.out')
    mapdl.cm("c_100078", "Elem")
    # c_100079
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_78','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_78.out')
    mapdl.cm("c_100079", "Elem")
    # c_100080
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_79','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_79.out')
    mapdl.cm("c_100080", "Elem")
    # c_100081
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_80','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_80.out')
    mapdl.cm("c_100081", "Elem")
    # c_100082
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_81','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_81.out')
    mapdl.cm("c_100082", "Elem")
    # c_100083
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_82','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_82.out')
    mapdl.cm("c_100083", "Elem")
    # c_100084
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_83','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_83.out')
    mapdl.cm("c_100084", "Elem")
    # c_100085
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_84','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_84.out')
    mapdl.cm("c_100085", "Elem")
    # c_200000
    mapdl.esel("none")
    mapdl.run("/input,'mymodule/elements/2_SHELL_GB_RVE_85','win',")
    wait_for_checkpoint_file(mapdl, 'done_2_SHELL_GB_RVE_85.out')
    mapdl.cm("c_200000", "Elem")
