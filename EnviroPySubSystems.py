import time
import numpy
from w1thermsensor import W1ThermSensor
from chip_systems import ProjectSystem
from chip_systems import ADCS
import RPi.GPIO as GPIO
import spidev

import numpy


class AquaPiTemperature(ProjectSystem.ProjectSystem):

	# Connect to Sensor
	# Assuming a single sensor is connected
	# Power is 3.3V
	# Data is connected to GPIO4 (pin 7)

	def __init__(self):
		self.temp_sensor = W1ThermSensor()
		return

	def SetupSystem(self):
		available_sensors = W1ThermSensor.get_available_sensors()
		for available_sensor in available_sensors:
			print(available_sensor)

	def ReadTemperature(self):
		temperature_degc = self.temp_sensor.get_temperature()
		return temperature_degc

	def ReadOutputs(self):
		temperature_degc = self.ReadTemperature()
		return temperature_degc


class AquaPiFluidLevel(ProjectSystem.ProjectSystem):

	def __init__(self):
		spi = spidev.SpiDev()
		spi.open(bus=0, device=0)  # bus=spi_bus, device=CS
		spi.max_speed_hz = 50000
		spi.mode = 0b00

		self.adc = ADCS.Maxim11410(interface=spi)
		self.opc = None
		self.SetupSystem()
		return

	def SetupSystem(self):

		self.adc.WriteRegisters('PD', 0b00)
		self.adc.WriteRegisters('CTRL', 0x26)
		self.adc.WriteRegisters('CAL_START', 0b00000111)

		# Filter
		self.adc.WriteRegisters('LINEF', 0x10)
		self.adc.WriteRegisters('RATE', 0x1111)

		# CNTRL
		self.adc.WriteRegisters('EXTCLK', 0b0)
		self.adc.WriteRegisters('U_BN', 0b0)
		self.adc.WriteRegisters('FORMAT', 0b0)
		self.adc.WriteRegisters('REF_SEL', 0b011)

		# MUX_CTRL0
		self.adc.WriteRegisters('AINP_SEL', 0b0001)
		self.adc.WriteRegisters('AINN_SEL', 0b0000)

		# PGA
		self.adc.WriteRegisters('SIG_PATH', 0b00)
		self.adc.WriteRegisters('GAIN', 0b000)

		# CONV
		self.adc.WriteRegisters('DEST', 0b000)
		self.adc.WriteRegisters('CONV_TYPE', 0b01)

	def TriggerSequence(self):
		self.adc.WriteRegisters(0x02, 0x3A)

	def ReadFluidLevel(self):
		# adc_lsb = self.adc.ReadRegisters('DATA0')[0]
		# self.TriggerSequence()
		# area = numpy.pi * (0.0002 / 2) ** 2
		# adc_lsb *= 1. / 2 ** 23 * 1e3 / 3.7 / area / 133.3 / 64
		adc_bits = 24
		adc_dec = 0
		n_samples = 1
		for i in range(n_samples):
			time.sleep(0.01)
			adc_lsb = self.adc.ReadRegisters('DATA0')[0]
			adc_dec += ProjectSystem.TwosComp(adc_lsb, bits=adc_bits)
		adc_dec = adc_dec / n_samples

		adc_volt_min = 0
		adc_volt_max = 3.3
		adc_lsb_max = 2 ** (adc_bits - 1)
		adc_lsb_min = 0
		# range = adc_volt_max - adc_volt_min
		adc_volts = adc_dec / adc_lsb_max * adc_volt_max

		if self.opc is None:
			self.opc = adc_volts
		adc_volts = adc_volts - self.opc
		fluid_height = (adc_volts + 0.21) / 0.04
		fluid_height = numpy.max([fluid_height, 0])
		return fluid_height

	def ReadOutputs(self):
		fluid_level_cm = self.ReadFluidLevel()
		return fluid_level_cm


class AquaPiPumpSwitches(ProjectSystem.ProjectSystem):

	def __init__(self, switch1_pin=5, switch2_pin=6, pump1_pin=15):
		self.switch1_pin = None
		self.switch2_pin = None
		self.pump1_pin = None
		self.pump1_state = 0
		self.SetupSystem(switch1_pin=switch1_pin,
						 switch2_pin=switch2_pin,
						 pump1_pin=pump1_pin)

	def SetupSystem(self, switch1_pin=5, switch2_pin=6, pump1_pin=15):
		self.switch1_pin = switch1_pin
		self.switch2_pin = switch2_pin
		self.pump1_pin = pump1_pin
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(switch1_pin, GPIO.IN)
		GPIO.setup(switch2_pin, GPIO.IN)
		GPIO.setup(pump1_pin, GPIO.OUT)

		self.pump1_state = 0

	def ReadOutputs(self):
		return self.switch1, self.switch2

	@property
	def switch1(self):
		return GPIO.input(self.switch1_pin)

	@property
	def switch2(self):
		return GPIO.input(self.switch2_pin)

	def StartInPump(self):
		GPIO.output(self.pump1_pin, 1)
		self.pump1_state = 1

	def StopInPump(self):
		GPIO.output(self.pump1_pin, 0)
		self.pump1_state = 0

	#
	# def StopInPump(self):
	# 	GPIO.output(self.pump_in_pin, GPIO.LOW)
	#
	# def StopOutPump(self):
	# 	GPIO.output(self.pump_out_pin, GPIO.LOW)
