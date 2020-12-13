# EnvriPi sensor hub shield for Raspberry Pi
A Raspberry Pi shield that houses several different types of sensors
-BME280 - Bosch pressure, temperature and humidity sensor
-BME680 - Bosch pressure, humidity, temperature and VOC sensor
-TMP102 - Texas Instruments temperature sensor
-BMM150 - Bosch magnetometer
-TSL25911FN - Light intensity sensor
-ICM-20649 - Invensense 6-axis IMU (3-axis gyroscope and 3-axis accelerometer)

## Summary
This code utlizies high level functions to communicate with sensors and set their configuration for proper monitoring of an aquarium.

Unfortunately, I can't make the sub-repository for chip communication public. However that package provides a simple interface for communicating with sensors va I2C and SPI.