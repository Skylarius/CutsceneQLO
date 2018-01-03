import cx_Freeze

executables = [cx_Freeze.Executable("Cutscene_QLO.py", icon="gomezico.ico")]

cx_Freeze.setup(
    name = "CUTSCENE Q.L.O. - Quantum Leap Operation",
    version="1.1",
    options={"build_exe":{"packages":["pygame"],"include_files":["8bit.ttf","bombleft.png","bombright.png","damage1.wav","damage2.wav","explosion1.wav","explosion2.wav","laser1.wav","laser2.wav","gomezico.ico","gomezleft.png","gomezright.png","pixelParrotleft.png","pixelParrotright.png","shootleft.png","shootright.png","title.png"]}},
    description = "A game  where you shoot to your opponent and where you're awesome!",
    executables=executables
    )
