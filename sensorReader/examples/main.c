#include "main.h"

void  Handler(int signo)
{
    //System Exit
    printf("\r\nHandler:exit\r\n");
    DEV_ModuleExit();

    exit(0);
}
IMU_EN_SENSOR_TYPE enMotionSensorType;
IMU_ST_ANGLES_DATA stAngles;
IMU_ST_SENSOR_DATA stGyroRawData;
IMU_ST_SENSOR_DATA stAccelRawData;
IMU_ST_SENSOR_DATA stMagnRawData;
int main(void)
{
    // Exception handling:ctrl + c
    signal(SIGINT, Handler);
    DEV_ModuleInit();
    uint8_t light;
    BME280_Init();
    TSL2591_Init();
    LTR390_init();
    SGP40_init();
    imuInit(&enMotionSensorType);
        
    BME280_value();
    light = TSL2591_Read_Lux();
    UVS_value();
    SGP40_value();      
    imuDataGet( &stAngles, &stGyroRawData, &stAccelRawData, &stMagnRawData);
    printf("{\n\"pressure\": %.2f,\n\"pressure_unit\": \"hPa\",\n\"temperature\": %.2f,\n\"temperature_unit\": \"°C\",\n\"humidity\": %.2f,\n\"humidity_unit\": \"%\",\n\"lux\": %d,\n\"uvs\": %d,\n\"gas\": %d,\n\"roll\": %.2f,\n\"pitch\": %.2f,\n\"yaw\": %.2f,\n\"acceleration\": {\"X\": %d, \"Y\": %d, \"Z\": %d},\n\"gyroscope\": {\"X\": %d, \"Y\": %d, \"Z\": %d},\n\"magnetic\": {\"X\": %d, \"Y\": %d, \"Z\": %d}\n}\n", pres_raw[0], pres_raw[1], pres_raw[2], light, uv, gas, stAngles.fRoll, stAngles.fPitch, stAngles.fYaw, stAccelRawData.s16X, stAccelRawData.s16Y, stAccelRawData.s16Z, stGyroRawData.s16X, stGyroRawData.s16Y, stGyroRawData.s16Z, stMagnRawData.s16X, stMagnRawData.s16Y, stMagnRawData.s16Z);
    // DEV_Delay_ms(500);
    
	//System Exit
	DEV_ModuleExit();
	return 0;
	
}
