# Elements Library

# Libraries ot the tnt model
from thermalModelLibrary import tntObjects as tntO
# from thermalModelLibrary import tntSolverObj as tntS

# Defining some materials
Cu = tntO.Material(conductivity=56e6)
F1_CuACB = tntO.Material(conductivity=3.25e6, alpha=0)
F2_CuACB = tntO.Material(conductivity=4.25e6, alpha=0)
F2_100_CuACB = tntO.Material(conductivity=5.5e6, alpha=0)
F3_CuACB = tntO.Material(conductivity=9.5e6, alpha=0)

# F1 G ACBs
EG_F1 = tntO.thermalElement(
        # shape(width, height, length, number of bars in parrallel, pointing angle {0->right, 90->top, 180->left, 270-> down})
        shape = tntO.shape(20,100,200,1,-90), 
        HTC = 4,
        emissivity = 0.35,
        dP = True,
        source = 0,
        material = F1_CuACB)

# F2 ACBs
EG_F2 = tntO.thermalElement(
        # shape(width, height, length, number of bars in parrallel, pointing angle {0->right, 90->top, 180->left, 270-> down})
        shape = tntO.shape(20,100,200,1,-90), 
        HTC = 4,
        emissivity = 0.35,
        dP = True,
        source = 0,
        material = F2_CuACB)

EG_F2_100 = tntO.thermalElement(
        # shape(width, height, length, number of bars in parrallel, pointing angle {0->right, 90->top, 180->left, 270-> down})
        shape = tntO.shape(20,100,200,1,-90), 
        HTC = 4,
        emissivity = 0.35,
        dP = True,
        source = 0,
        material = F2_100_CuACB)

# Frame 3 ACBs

EG_F3 = tntO.thermalElement(
        # shape(width, height, length, number of bars in parrallel, pointing angle {0->right, 90->top, 180->left, 270-> down})
        shape = tntO.shape(20,100,200,1,-90), 
        HTC = 4.5,
        emissivity = 0.35,
        dP = True,
        source = 0,
        material = F3_CuACB)

# Horizontal Busbars Systems
SMB_6 = tntO.thermalElement(
        # shape(width, height, length, number of bars in parrallel, pointing angle {0->right, 90->top, 180->left, 270-> down})
        shape = tntO.shape(10,30,1000,2,0), 
        HTC = 6,
        emissivity = 0.35,
        dP = True,
        source = 0,
        material = Cu,
        acPower = 1.05)

SMB_7 = tntO.thermalElement(
        # shape(width, height, length, number of bars in parrallel, pointing angle {0->right, 90->top, 180->left, 270-> down})
        shape = tntO.shape(10,35,1000,2,0), 
        HTC = 5,
        emissivity = 0.35,
        dP = True,
        source = 0,
        material = Cu,
        acPower = 1.09)

SMB_12 = tntO.thermalElement(
        # shape(width, height, length, number of bars in parrallel, pointing angle {0->right, 90->top, 180->left, 270-> down})
        shape = tntO.shape(10,30,1000,4,0), 
        HTC = 4.5,
        emissivity = 0.35,
        dP = True,
        source = 0,
        material = Cu,
        acPower = 1.18)

SMB_14 = tntO.thermalElement(
        # shape(width, height, length, number of bars in parrallel, pointing angle {0->right, 90->top, 180->left, 270-> down})
        shape = tntO.shape(10,35,1000,4,0), 
        HTC = 5.25,
        emissivity = 0.35,
        dP = True,
        source = 0,
        material = Cu,
        acPower = 1.28)

SMB_21 = tntO.thermalElement(
        # shape(width, height, length, number of bars in parrallel, pointing angle {0->right, 90->top, 180->left, 270-> down})
        shape = tntO.shape(10,35,1000,6,0), 
        HTC = 4.1,
        emissivity = 0.35,
        dP = True,
        source = 0,
        material = Cu,
        acPower = 1.54)

SMB_28 = tntO.thermalElement(
        # shape(width, height, length, number of bars in parrallel, pointing angle {0->right, 90->top, 180->left, 270-> down})
        shape = tntO.shape(10,35,1000,8,0), 
        HTC = 5.5,
        emissivity = 0.35,
        dP = True,
        source = 0,
        material = Cu,
        acPower = 1.49)

SMB_42 = tntO.thermalElement(
        # shape(width, height, length, number of bars in parrallel, pointing angle {0->right, 90->top, 180->left, 270-> down})
        shape = tntO.shape(10,35,1000,12,0), 
        HTC = 4,
        emissivity = 0.35,
        dP = True,
        source = 0,
        material = Cu,
        acPower = 1.92)

# Verticcal Raisers
VBB_F1G_1k6 = tntO.thermalElement(
        # shape(width, height, length, number of bars in parrallel, pointing angle {0->right, 90->top, 180->left, 270-> down})
        shape = tntO.shape(10,40,1000,2,-90), 
        HTC = 5,
        emissivity = 0.35,
        dP = True,
        source = 0,
        material = Cu,
        acPower = 1.125)

VBB_F1G_2k = tntO.thermalElement(
        # shape(width, height, length, number of bars in parrallel, pointing angle {0->right, 90->top, 180->left, 270-> down})
        shape = tntO.shape(10,40,1000,3,-90), 
        HTC = 5,
        emissivity = 0.35,
        dP = True,
        source = 0,
        material = Cu,
        acPower = 1.29)

VBB_F1T_1k6 = tntO.thermalElement(
        # shape(width, height, length, number of bars in parrallel, pointing angle {0->right, 90->top, 180->left, 270-> down})
        shape = tntO.shape(10,30,1000,2,-90), 
        HTC = 6,
        emissivity = 0.35,
        dP = True,
        source = 0,
        material = Cu,
        acPower = 1.08)

VBB_F2_2k5 = tntO.thermalElement(
        # shape(width, height, length, number of bars in parrallel, pointing angle {0->right, 90->top, 180->left, 270-> down})
        shape = tntO.shape(10,40,1000,4,-90), 
        HTC = 6,
        emissivity = 0.35,
        dP = True,
        source = 0,
        material = Cu,
        acPower = 1.64)

VBB_F2_3k2 = tntO.thermalElement(
        # shape(width, height, length, number of bars in parrallel, pointing angle {0->right, 90->top, 180->left, 270-> down})
        shape = tntO.shape(10,40,1000,6,-90), 
        HTC = 6,
        emissivity = 0.35,
        dP = True,
        source = 0,
        material = Cu,
        acPower = 2.09)

VBB_F2_4k = tntO.thermalElement(
        # shape(width, height, length, number of bars in parrallel, pointing angle {0->right, 90->top, 180->left, 270-> down})
        shape = tntO.shape(10,40,1000,8,-90), 
        HTC = 5,
        emissivity = 0.35,
        dP = True,
        source = 0,
        material = Cu,
        acPower = 2.56)

VBB_F3_5k = tntO.thermalElement(
        # shape(width, height, length, number of bars in parrallel, pointing angle {0->right, 90->top, 180->left, 270-> down})
        shape = tntO.shape(10,40,1000,9,-90), 
        HTC = 5,
        emissivity = 0.35,
        dP = True,
        source = 0,
        material = Cu,
        acPower = 1.99)

VBB_F3_6k = tntO.thermalElement(
        # shape(width, height, length, number of bars in parrallel, pointing angle {0->right, 90->top, 180->left, 270-> down})
        shape = tntO.shape(10,40,1000,12,-90), 
        HTC = 6,
        emissivity = 0.35,
        dP = True,
        source = 0,
        material = Cu,
        acPower = 2.43)

#CT lashes and other like that

CT_1x100 = tntO.thermalElement(
        # shape(width, height, length, number of bars in parrallel, pointing angle {0->right, 90->top, 180->left, 270-> down})
        shape = tntO.shape(10,100,1000,1,-90), 
        HTC = 5.5,
        emissivity = 0.35,
        dP = True,
        source = 0,
        material = Cu,
        acPower = 1.41)

CT_2x100 = tntO.thermalElement(
        # shape(width, height, length, number of bars in parrallel, pointing angle {0->right, 90->top, 180->left, 270-> down})
        shape = tntO.shape(10,100,1000,2,-90), 
        HTC = 5.5,
        emissivity = 0.35,
        dP = True,
        source = 0,
        material = Cu,
        acPower = 2)

CT_3x100 = tntO.thermalElement(
        # shape(width, height, length, number of bars in parrallel, pointing angle {0->right, 90->top, 180->left, 270-> down})
        shape = tntO.shape(10,100,1000,3,-90), 
        HTC = 5.5,
        emissivity = 0.35,
        dP = True,
        source = 0,
        material = Cu,
        acPower = 2.58)

CT_4x100 = tntO.thermalElement(
        # shape(width, height, length, number of bars in parrallel, pointing angle {0->right, 90->top, 180->left, 270-> down})
        shape = tntO.shape(10,100,1000,4,-90), 
        HTC = 5.5,
        emissivity = 0.35,
        dP = True,
        source = 0,
        material = Cu,
        acPower = 3.25)

CT_2x40 = tntO.thermalElement(
        # shape(width, height, length, number of bars in parrallel, pointing angle {0->right, 90->top, 180->left, 270-> down})
        shape = tntO.shape(10,40,1000,2,-90), 
        HTC = 5.5,
        emissivity = 0.35,
        dP = True,
        source = 0,
        material = Cu,
        acPower = 1.41)

