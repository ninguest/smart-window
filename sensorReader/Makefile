DIR_OBJ = ./lib
DIR_BIN = ./bin
DIR_Config = ./lib/Config
DIR_TSL2591 = ./lib/TSL2591
DIR_SGP40 = ./lib/SGP40
DIR_BME280 = ./lib/BME280
DIR_LTR390 = ./lib/LTR390
DIR_ICM20948 = ./lib/ICM20948
DIR_Examples = ./examples

OBJ_C = $(wildcard ${DIR_OBJ}/*.c ${DIR_Examples}/*.c ${DIR_Config}/*.c ${DIR_TSL2591}/*.c ${DIR_SGP40}/*.c ${DIR_BME280}/*.c ${DIR_LTR390}/*.c ${DIR_ICM20948}/*.c)
OBJ_O = $(patsubst %.c,${DIR_BIN}/%.o,$(notdir ${OBJ_C}))

TARGET = main
#BIN_TARGET = ${DIR_BIN}/${TARGET}

CC = gcc

DEBUG = -g -O0 -Wall
CFLAGS += $(DEBUG)

# USELIB = USE_BCM2835_LIB
# USELIB = USE_WIRINGPI_LIB
USELIB = USE_DEV_LIB
DEBUG = -D $(USELIB) 
ifeq ($(USELIB), USE_BCM2835_LIB)
    LIB = -lbcm2835 -lm 
else ifeq ($(USELIB), USE_WIRINGPI_LIB)
    LIB = -lwiringPi -lm 
else
	LIB = -llgpio -lm 
endif

${TARGET}:${OBJ_O}
	$(CC) $(CFLAGS) $(OBJ_O) -o $@ $(LIB) -lm

${DIR_BIN}/%.o : $(DIR_Examples)/%.c
	$(CC) $(CFLAGS) -c  $< -o $@ $(LIB) -I $(DIR_OBJ) -I $(DIR_Config) -I $(DIR_TSL2591) -I $(DIR_SGP40) -I $(DIR_BME280) -I $(DIR_LTR390) -I $(DIR_ICM20948)

${DIR_BIN}/%.o : $(DIR_OBJ)/%.c
	$(CC) $(CFLAGS) -c  $< -o $@ $(LIB) -I $(DIR_Config)
    
${DIR_BIN}/%.o : $(DIR_Config)/%.c
	$(CC) $(CFLAGS) -c  $< -o $@ $(LIB)

${DIR_BIN}/%.o : $(DIR_TSL2591)/%.c
	$(CC) $(CFLAGS) -c  $< -o $@ $(LIB) -I $(DIR_Config)

${DIR_BIN}/%.o : $(DIR_SGP40)/%.c
	$(CC) $(CFLAGS) -c  $< -o $@ $(LIB) -I $(DIR_Config)

${DIR_BIN}/%.o : $(DIR_BME280)/%.c
	$(CC) $(CFLAGS) -c  $< -o $@ $(LIB) -I $(DIR_Config)

${DIR_BIN}/%.o : $(DIR_LTR390)/%.c
	$(CC) $(CFLAGS) -c  $< -o $@ $(LIB) -I $(DIR_Config)

${DIR_BIN}/%.o : $(DIR_ICM20948)/%.c
	$(CC) $(CFLAGS) -c  $< -o $@ $(LIB) -I $(DIR_Config)

clean :
	rm $(DIR_BIN)/*.* 
	rm $(TARGET) 
