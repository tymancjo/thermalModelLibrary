# Library of standard panels


# Global imports
from thermalModelLibrary import elements as el
from thermalModelLibrary import tntPanelsSolver as tntS
from thermalModelLibrary import tntPanel as tntP

import copy


'''
The idea is to make some kind of builder for lineups
How this may work ???
What we need to define lineup?
	1. MBBs
	2. list of feeders
	3. incomer
	4. some good will ;)

'''

# List of predefined typical vbb's and MBBs 
# for panels construction
# PC1600 definition of components
PC_VBB =      [
                (el.VBB_F1G_1k6, 900, 10), 
                (el.EG_F1, 200, 4),
                (el.VBB_F1G_1k6, 200, 4), 
                (el.CT_2x40, 130, 3), 
                (el.VBB_F1G_1k6, 200, 4), 
                ]
VBB1600 = tntS.generateNodes(PC_VBB)
Lasha = copy.deepcopy(el.CT_1x100)
Lasha.rotate(0)
SMB6 = tntS.generateNodes([(Lasha,100,1),(el.SMB_6,600,8)])

# PC2000
PC_VBB =      [
                (el.VBB_F1G_2k, 900, 10), 
                (el.EG_F1, 200, 4),
                (el.VBB_F1G_2k, 200, 4), 
                (el.CT_2x40, 130, 3), 
                (el.VBB_F1G_2k, 200, 4), 
                ]
VBB2000 = tntS.generateNodes(PC_VBB)
Lasha = copy.deepcopy(el.CT_1x100)
Lasha.rotate(0)
SMB7 = tntS.generateNodes([(Lasha,100,1),(el.SMB_7,600,8)])

# PC2500
PC_VBB =      [
                (el.VBB_F2_2k5, 900, 10), 
                (el.EG_F2, 200, 4),
                (el.VBB_F2_2k5, 200, 4), 
                (el.CT_1x100, 130, 3), 
                (el.VBB_F2_2k5, 200, 4), 
                ]
VBB2500 = tntS.generateNodes(PC_VBB)
Lasha = copy.deepcopy(el.CT_1x100)
Lasha.rotate(0)
SMB12 = tntS.generateNodes([(Lasha,100,1),(el.SMB_12,800,8)])

# PC3200
PC_VBB =      [
                (el.VBB_F2_3k2, 900, 10), 
                (el.EG_F2, 200, 4),
                (el.VBB_F2_3k2, 200, 4), 
                (el.CT_2x100, 130, 3), 
                (el.VBB_F2_3k2, 200, 4), 
                ]
VBB3200 = tntS.generateNodes(PC_VBB)
Lasha = copy.deepcopy(el.CT_1x100)
Lasha.rotate(0)
SMB14 = tntS.generateNodes([(Lasha,100,1),(el.SMB_14,800,8)])

# PC4000
PC_VBB =      [
                (el.VBB_F2_4k, 900, 10), 
                (el.EG_F2_100, 200, 4),
                (el.VBB_F2_4k, 200, 4), 
                (el.CT_2x100, 130, 3), 
                (el.VBB_F2_4k, 200, 4), 
                ]
VBB4000 = tntS.generateNodes(PC_VBB)
Lasha = copy.deepcopy(el.CT_2x100)
Lasha.rotate(0)
SMB21 = tntS.generateNodes([(Lasha,100,1),(el.SMB_14,800,8)])

# PC5000
PC_VBB =      [
                (el.VBB_F3_5k, 900, 10), 
                (el.EG_F3, 200, 4),
                (el.VBB_F3_5k, 200, 4), 
                (el.CT_3x100, 130, 3), 
                (el.VBB_F3_5k, 200, 4), 
                ]
VBB5000 = tntS.generateNodes(PC_VBB)
Lasha = copy.deepcopy(el.CT_2x100)
Lasha.rotate(0)
SMB28 = tntS.generateNodes([(Lasha,100,1),(el.SMB_28,1000,8)])

# PC6000
PC_VBB =      [
                (el.VBB_F3_6k, 900, 10), 
                (el.EG_F3, 200, 4),
                (el.VBB_F3_6k, 200, 4), 
                (el.CT_3x100, 130, 3), 
                (el.VBB_F3_6k, 200, 4), 
                ]
VBB5000 = tntS.generateNodes(PC_VBB)
Lasha = copy.deepcopy(el.CT_3x100)
Lasha.rotate(0)
SMB42 = tntS.generateNodes([(Lasha,100,1),(el.SMB_42,1000,8)])




def lineup(MBB, VBBList, T0=35):
	# This function is about to generate list of panels
	# the lineup to be solved thermally
	# Inputs:
	# MBB - MBB type for entire lineup
	# VBBLIst - list of tuples:
	# 	(VBBtype, I)
	# 	where:
	# 	VBBtype - one of prepared VBB setups with ACB
	# 		like in example VBB3200 (defined above)
	# 	I - feeder current, if it's incomer set as False
	# 
	# T0 - ambient temperature default at 35C

	# Solving for currents
	# 1st finding all loads currents to set the incomer
	Iinc = 0
	for column in VBBList:
		Iinc += abs(column[1])


	
	# preparing empty list 
	Panels = []

	# looping over the delivered list
	for idx, column in enumerate(VBBList):
		
		VBB = column[0]
		
		if not column[1]:
			Load = -Iinc
		else:
			Load = column[1]

		tempPanel = tntP.PCPanel(MBB=MBB,
                     	VBB=VBB,
                     	Load=Load,
                     	Air=None,
                     	T0=T0)

		# figuring out the currents
		if idx > 0:
			tempPanel.Iin = Panels[-1].Iout

		tempPanel.Iout = tempPanel.Iin - tempPanel.I

		tempPanel.set3I(Iin=tempPanel.Iin,
            			Iout=tempPanel.Iout,
            			Ifeeder=tempPanel.I)

		Panels.append(tempPanel)
		tempPanel = None

	return Panels




