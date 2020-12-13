#!/usr/bin/env python3

import EnviroPySystem
import time
import numpy as np
import pandas as pd

from datetime import datetime

# Get date and time
now = datetime.now()
datetime_date = now.strftime("%d/%m/%Y")
datetime_time = now.strftime("%H:%M:%S")

sensor_hub = EnviroPySystem.EnviroPy()

bme_temp = np.array([])
bme_press = np.array([])
bme_humid = np.array([])
bme_voc = np.array([])
tmp_temp = np.array([])
tsl_lux = np.array([])
tsl_full = np.array([])
tsl_ir = np.array([])

duration = 60
start_time = time.time()
current_time = time.time()
time_elapsed = current_time - start_time

while time_elapsed < duration:
	
	time_elapsed = time.time() - start_time

	bme_outputs = sensor_hub.bme680.ReadAllOutputs()
	bme_voc_stab = sensor_hub.bme680.ReadRegisters('heat_stab_r')[0]
	bme_voc_valid = sensor_hub.bme680.ReadRegisters('gas_valid_r')[0]
	tmp_outputs = sensor_hub.tmp102.readTemperature()
	tsl_outputs = sensor_hub.tsl2592.ReadOutput()
	
	bme_temp = np.append(bme_temp, bme_outputs[0])
	bme_press = np.append(bme_press, bme_outputs[1])
	bme_humid = np.append(bme_humid, bme_outputs[2])
	
	if bme_voc_stab and bme_voc_valid and time_elapsed > 40:
		bme_voc = np.append(bme_voc, bme_outputs[3])
	
	tmp_temp = np.append(tmp_temp, tmp_outputs)
	tsl_lux = np.append(tsl_lux, tsl_outputs['lux'])
	tsl_full = np.append(tsl_full, tsl_outputs['full'])
	tsl_ir = np.append(tsl_ir, tsl_outputs['ir'])
	
	print(bme_outputs, bme_voc_stab, bme_voc_valid, tmp_outputs, tsl_outputs['lux'])
	time.sleep(0.2)
	
bme_temp = np.mean(bme_temp)
bme_press = np.mean(bme_press)
bme_humid = np.mean(bme_humid)
bme_voc = np.mean(bme_voc)
tmp_temp = np.mean(tmp_temp)
tsl_lux = np.mean(tsl_lux)
tsl_full = np.mean(tsl_full)
tsl_ir = np.mean(tsl_ir)

df = pd.DataFrame({'Date': datetime_date,
									 'Time': datetime_time,
									 'BME680 Temperature [degC]': bme_temp,
                   'BME680 Pressure [Pa]': bme_press,
                   'BME680 Humidity [%]': bme_humid,
                   'BME680 VOC': bme_voc,
                   'TMP102 Temperature [degC]': tmp_temp,
                   'TSL2591 Lux [Lux]': tsl_lux,
                   'TSL2591 Full': tsl_full,
                   'TSL2591 IR': tsl_ir,
                   }, index=[0])

try:
	df_all = pd.read_csv('enviro_data.csv')
	df_all = df_all.append(df)
	df_all.to_csv('enviro_data.csv', index=False)
except:
	df.to_csv('enviro_data.csv', index=False)