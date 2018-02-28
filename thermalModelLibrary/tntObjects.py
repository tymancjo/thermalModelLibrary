# this is the classes library for the themralModelingLibrary
import math


class shape:
	"""docstring for shape
	this is a class that describe cubical shape of thermal analysis element
	this is the basic shape

	input:
	width - width size im mm [z axis]
	height - height size in mm [y axis]
	length - length size in mm [x axis]
	"""
	def __init__(self, width=10, height=100, length=100, n=1, angle=0):
		self.w = width  # im [mm]
		self.h = height  # im [mm]
		self.l = length  # im [mm]
		self.n = n  # number of elements in parralel
		self.angle = angle * math.pi / 180  # Angle of position, 0 = flat(horizontal)

	def xSec(self):
		return self.n * self.w * 1e-3 * self.h * 1e-3

	def ConvectionArea(self):
		return self.n * self.l * 1e-3 * (2*self.w * 1e-3 + 2*self.h * 1e-3)

	def RadiationArea(self):
		return self.l * 1e-3 * (2*self.w * 1e-3 * self.n + 2*self.h * 1e-3)

	def Volume(self):
		return self.xSec() * self.l  * 1e-3

	def getR(self, conductivity):
		return self.l * 1e-3 / (self.xSec() * conductivity)

	def getPos(self):
		return {
				"x": self.l * math.cos(self.angle),
				"y": self.l * math.sin(self.angle)
				}


class pipe:
	"""docstring for shape
	this is a class that describe pipe like shape of thermal analysis element
	this is the basic shape
	
	input:
	OutDiameter - outside diameter in mm
	InDiameter - inside hole diameter in mm
	length - length size in mm [x axis]
	"""
	def __init__(self, OutDiameter=10, InDiameter=100, length=100, n=1, angle=0):
		self.fi_out = OutDiameter  # im [mm]
		self.fi_in = InDiameter  # im [mm]
		self.l = length  # im [mm]
		self.n = n  # number of elements in parralel
		self.angle = angle * math.pi / 180  # Angle of position, 0 = flat(horizontal)

	def xSec(self):
		return self.n * ( math.pi*(0.5*self.fi_out * 1e-3)**2 - math.pi*(0.5*self.fi_in * 1e-3)**2)

	def ConvectionArea(self):
		return self.n * 2 * math.pi * 0.5 * self.fi_out * 1e-3 * self.l * 1e-3

	def RadiationArea(self):
		return self.n * 2 * math.pi * 0.5 * self.fi_out * 1e-3 * self.l * 1e-3

	def Volume(self):
		return self.xSec() * self.l  * 1e-3

	def getR(self, conductivity):
		return self.l * 1e-3 / (self.xSec() * conductivity)

	def getPos(self):
		return {
				"x": self.l * math.cos(self.angle),
				"y": self.l * math.sin(self.angle)
				}


class Material:
	"""docstring for material"""
	def __init__(self, conductivity=58e6, alpha=3.9e-3, thermalConductivity=401, density=8920, Cp=385 ):
		
		self.sigma = conductivity
		self.alpha = alpha
		self.thermalConductivity = thermalConductivity
		self.density = density
		self.Cp = Cp

	def conductivity(self, temperature):
		return self.sigma / (1 + self.alpha * (temperature - 20))

		

class thermalElement:
	"""docstring for thermalElement
	this is the main component of thermal analysis
	it decribe the piece of physical object
	Inputs:
	shape - shape class object describing shape of element
	material - material calss element of the piece
	source - internal independent power generation [W]
	dP - boolean:
		if True - flowwing current create power losses
		if False - flowing current don't create power losses (whatever material)
	HTC - Heat Transfer Coeff for the convection from the external area [W/m2K]
	emmisivity - emissivity factor for the element surface
	"""
	def __init__(self, shape=shape(), material=Material(), source=0, dP=True, HTC=5, emissivity=0.35 ):
		
		self.shape = shape  # as shape class object
		self.material = material  # as material class object
		self.Q = source  # internal power generation in [W]
		self.dP = dP
		self.HTC = HTC
		self.emissivity = emissivity

	def mass(self):
		return self.shape.Volume() * self.material.density

	def R(self, temperature=20):
		"""
		This function returns the DC calculated Resistance at given temperature
		Inputs:
		temperature - calculation temperature in degC
		"""	
		return self.shape.getR(self.material.conductivity(temperature))

	def Rth(self, temperature=20):
		"""
		This function returns the Thermal Resistance at given temperature
		Inputs:
		temperature - calculation temperature in degC
		"""	
		return self.shape.getR(self.material.thermalConductivity)

	def Power(self, current=0, temperature=20):
		if self.dP:
			return self.Q + self.R(temperature) * current**2
		else:
			return self.Q

	def staticDT(self, Telement=20, current=0, Tambient=0):
		""" 
		return temperature rise wuth simple HTC convection calculation
		assuming power losses at giveb object temperature
		Telement - power losses calc temperature [degC]
		current - current value [A]
		Tambient - ambient temperature [deg C] if not zero result will be temperature in [deg C] otherwise will be rise in [K]
		"""
		return (self.Power(current,Telement) / (self.HTC * self.shape.ConvectionArea())) + Tambient
	
	def Qconv(self, Temp, Tamb):
		"""
		Returns the heat stream transmitted via convection
		"""
		return self.shape.ConvectionArea() * self.HTC * (Temp - Tamb)

	def Qrad(self, Temp, Tamb):
		"""
		Returns the heat stream transmitted via radiation
		
        thermalRadiation = stBoltzConst * barArea * emmisivity\
        * ((startTemp[i]+273.15)**4-(ambientTemp+273.15)**4)
		"""
		stBoltzConst = 5.6703e-8
		return self.shape.RadiationArea() * stBoltzConst * self.emissivity * ((Temp + 273.15)**4  - (Tamb + 273.15)**4)