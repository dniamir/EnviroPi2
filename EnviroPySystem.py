from chip_systems import ProjectSystem
import smbus
import time

from chip_systems import PressureSensors
from chip_systems import TMP102
from chip_systems import TSL2591

class EnviroPy(ProjectSystem.ProjectSystem):

	def __init__(self):
		i2c_bus = smbus.SMBus(1)
		
		self.tmp102 = None
		self.bme680 = None
		self.tsl2592 = None
		
		self.SetupBme(i2c_bus)
		self.SetupTmp(i2c_bus)
		self.SetupTsl(i2c_bus)
		
	def SetupTsl(self, i2c_bus):
		self.tsl2592 = TSL2591.TSL2591(i2c_bus=i2c_bus)
		self.tsl2592.set_gain(0x05)
		self.tsl2592.set_timing(5)
		self.tsl2592.enable()
	
	def SetupTmp(self, i2c_bus):
		self.tmp102 = TMP102.TMP102(i2c_bus=i2c_bus, units='C', address=0x48)
	
	def SetupBme(self, i2c_bus):
		
		self.bme680 = PressureSensors.BME680(interface=i2c_bus)
		self.bme680.WriteRegisters('Reset', 0xB6)
		time.sleep(0.2)
		
		# Read Chip ID
		chip_id = self.bme680.ReadRegisters('Id')
		print('BME Chip ID is %i' % chip_id[0])
		
		self.bme680.WriteRegisters('osrs_h', 0b101)
		self.bme680.WriteRegisters('osrs_t', 0b101)
		self.bme680.WriteRegisters('osrs_p', 0b101)
		
		# Set IIR filter
		self.bme680.WriteRegisters('filter', 0b010)
		
		# Set Gas settings
		self.bme680.WriteRegisters('run_gas', 0b1)
		self.bme680.WriteRegisters('nb_conv', 0b0000)
		
		# Set chip mode
		self.bme680.WriteRegisters('mode', 0b01)
		
	def SetupSystem(self):
		pass

	def ReadOutputs(self):
		pass
