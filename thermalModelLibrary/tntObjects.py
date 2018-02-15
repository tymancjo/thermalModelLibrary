# this is the classes library for the themralModelingLibrary

class shape:
	"""docstring for shape
	this is a class that describe cubical shape of thermal analysis element
	input:
	width - width size im mm [z axis]
	height - height size in mm [y axis]
	length - length size in mm [x axis]
	"""
	def __init__(self, width=10, height=100, length=100, n=1):
		self.w = width * 1e-3  # im [m]
		self.h = height * 1e-3  # im [m]
		self.l = length * 1e-3  # im [m]
		self.n = n  # number of elements in parralel

	def xSec(self):
		return self.n * self.w * self.h

	def Area(self):
		return self.n * self.l * (2*self.w + 2*self.h)


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
		return self.shape.xSec() * self.shape.l * self.material.density

	def R(self, temperature=20):
		"""
		This function returns the DC calculated Resistance at given temperature
		Inputs:
		temperature - calculation temperature in degC
		"""	
		return self.shape.l / (self.shape.xSec() * self.material.conductivity(temperature))

	def Rth(self, temperature=20):
		"""
		This function returns the Thermal Resistance at given temperature
		Inputs:
		temperature - calculation temperature in degC
		"""	
		return self.shape.l / (self.shape.xSec() * self.material.thermalConductivity)

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
		return (self.Power(current,Telement) / (self.HTC * self.shape.Area())) + Tambient
	
	def Qconv(self, Temp, Tamb):
		"""
		Returns the heat stream transmitted via convection
		"""
		return self.shape.Area() * self.HTC * (Temp - Tamb)

	def Qrad(self, Temp, Tamb):
		"""
		Returns the heat stream transmitted via radiation
		
        thermalRadiation = stBoltzConst * barArea * emmisivity\
        * ((startTemp[i]+273.15)**4-(ambientTemp+273.15)**4)
		"""
		stBoltzConst = 5.6703e-8
		return self.shape.Area() * stBoltzConst * self.emissivity * ((Temp + 273.15)**4  - (Tamb + 273.15)**4)