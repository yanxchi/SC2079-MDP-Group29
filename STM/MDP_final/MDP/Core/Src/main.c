/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2022 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "cmsis_os.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "oled.h"
#include "ICM20948.h"
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "ICM20948.h"
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */
/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */
/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
ADC_HandleTypeDef hadc1;
ADC_HandleTypeDef hadc2;

I2C_HandleTypeDef hi2c1;

TIM_HandleTypeDef htim1;
TIM_HandleTypeDef htim2;
TIM_HandleTypeDef htim3;
TIM_HandleTypeDef htim4;
TIM_HandleTypeDef htim6;
TIM_HandleTypeDef htim8;

UART_HandleTypeDef huart3;

/* Definitions for oledTask */
osThreadId_t oledTaskHandle;
const osThreadAttr_t oledTask_attributes = {
  .name = "oledTask",
  .stack_size = 128 * 4,
  .priority = (osPriority_t) osPriorityLow,
};
/* Definitions for commandTask */
osThreadId_t commandTaskHandle;
const osThreadAttr_t commandTask_attributes = {
  .name = "commandTask",
  .stack_size = 128 * 4,
  .priority = (osPriority_t) osPriorityNormal,
};
/* Definitions for ADCTask */
osThreadId_t ADCTaskHandle;
const osThreadAttr_t ADCTask_attributes = {
  .name = "ADCTask",
  .stack_size = 128 * 4,
  .priority = (osPriority_t) osPriorityNormal,
};
/* Definitions for moveDistTask */
osThreadId_t moveDistTaskHandle;
const osThreadAttr_t moveDistTask_attributes = {
  .name = "moveDistTask",
  .stack_size = 128 * 4,
  .priority = (osPriority_t) osPriorityNormal,
};
/* Definitions for fastestPathTask */
osThreadId_t fastestPathTaskHandle;
const osThreadAttr_t fastestPathTask_attributes = {
  .name = "fastestPathTask",
  .stack_size = 128 * 4,
  .priority = (osPriority_t) osPriorityNormal,
};
/* Definitions for buzzerTask */
osThreadId_t buzzerTaskHandle;
const osThreadAttr_t buzzerTask_attributes = {
  .name = "buzzerTask",
  .stack_size = 128 * 4,
  .priority = (osPriority_t) osPriorityNormal,
};
/* Definitions for FLTask */
osThreadId_t FLTaskHandle;
const osThreadAttr_t FLTask_attributes = {
  .name = "FLTask",
  .stack_size = 128 * 4,
  .priority = (osPriority_t) osPriorityNormal,
};
/* Definitions for FRTask */
osThreadId_t FRTaskHandle;
const osThreadAttr_t FRTask_attributes = {
  .name = "FRTask",
  .stack_size = 128 * 4,
  .priority = (osPriority_t) osPriorityNormal,
};
/* Definitions for BLTask */
osThreadId_t BLTaskHandle;
const osThreadAttr_t BLTask_attributes = {
  .name = "BLTask",
  .stack_size = 128 * 4,
  .priority = (osPriority_t) osPriorityNormal,
};
/* Definitions for BRTask */
osThreadId_t BRTaskHandle;
const osThreadAttr_t BRTask_attributes = {
  .name = "BRTask",
  .stack_size = 128 * 4,
  .priority = (osPriority_t) osPriorityNormal,
};
/* Definitions for fastestPathV2 */
osThreadId_t fastestPathV2Handle;
const osThreadAttr_t fastestPathV2_attributes = {
  .name = "fastestPathV2",
  .stack_size = 128 * 4,
  .priority = (osPriority_t) osPriorityNormal,
};
/* Definitions for batteryTask */
osThreadId_t batteryTaskHandle;
const osThreadAttr_t batteryTask_attributes = {
  .name = "batteryTask",
  .stack_size = 128 * 4,
  .priority = (osPriority_t) osPriorityNormal,
};
/* Definitions for moveDistObsTask */
osThreadId_t moveDistObsTaskHandle;
const osThreadAttr_t moveDistObsTask_attributes = {
  .name = "moveDistObsTask",
  .stack_size = 128 * 4,
  .priority = (osPriority_t) osPriorityNormal,
};
/* Definitions for SensorTask */
osThreadId_t SensorTaskHandle;
const osThreadAttr_t SensorTask_attributes = { .name = "SensorTask",
		.stack_size = 512 * 4, .priority = (osPriority_t) osPriorityNormal, };
/* Definitions for IRTask */
osThreadId_t IRTaskHandle;
const osThreadAttr_t IRTask_attributes = { .name = "IRTask", .stack_size = 128
		* 4, .priority = (osPriority_t) osPriorityLow, };
/* USER CODE BEGIN PV */
uint8_t RX_BUFFER_SIZE = 4;
uint8_t aRxBuffer[10];

typedef struct _command {
	uint8_t index;
	uint16_t val;
} Command;

uint8_t CMD_BUFFER_SIZE = 12;
typedef struct _commandQueue {
	uint8_t head;
	uint8_t tail;
	uint8_t size;
	Command buffer[12];
} CommandQueue;

CommandQueue cQueue;

Command curCmd;
uint8_t rxMsg[16];
char ch[16];

uint8_t manualMode = 0;

// PID
float targetAngle = 0;
float angleNow = 0;
uint8_t readGyroZData[2];
int16_t gyroZ;
uint16_t newDutyL, newDutyR;
uint32_t last_curTask_tick = 0;

float targetDist = 0;
uint16_t curDistTick = 0;
uint16_t targetDistTick = 0;
uint16_t dist_dL = 0;
uint16_t lastDistTick_L = 0;

typedef struct _pidConfig {
	float Kp;
	float Ki;
	float Kd;
	float ek1;
	float ekSum;
} PIDConfig;

PIDConfig pidSlow, pidTSlow, pidFast;

typedef struct _commandConfig {
	uint16_t leftDuty;
	uint16_t rightDuty;
	float servoTurnVal;
	float targetAngle;
	uint8_t direction;
} CmdConfig;

#define CONFIG_FL00 7
#define CONFIG_FR00 8
#define CONFIG_BL00 9
#define CONFIG_BR00 10

#define CONFIG_FL20 11
#define CONFIG_FR20 12
#define CONFIG_BL20 13
#define CONFIG_BR20 14

#define CONFIG_FL30 15
#define CONFIG_FR30 16
#define CONFIG_BL30 17
#define CONFIG_BR30 18

//CmdConfig cfgs[19] = {
//	{0,0,SERVO_CENTER,0, DIR_FORWARD}, // STOP
//	{1200, 1200, SERVO_CENTER, 0, DIR_FORWARD}, // FW00
//	{1200, 1200, SERVO_CENTER, 0, DIR_BACKWARD}, // BW00
//
//	{800, 1200, 50, 0, DIR_FORWARD}, // FL--
//	{1200, 800, 115, 0, DIR_FORWARD}, // FR--
//	{800, 1200, 50, 0, DIR_BACKWARD}, // BL--
//	{1200, 800, 115, 0, DIR_BACKWARD}, // BR--
//
//	{700, 1800, 50, 89, DIR_FORWARD}, // FL00
//	{1800, 400, 115 ,-87, DIR_FORWARD}, // FR00
//	{500, 1700, 50, -88, DIR_BACKWARD}, // BL00
//	{1800, 500, 115, 89, DIR_BACKWARD}, // BR00,
//
//	{800, 1800, 51.85, 89, DIR_FORWARD}, // FL20
//	{1800, 900, 115 ,-87, DIR_FORWARD}, // FR20
//	{700, 1800, 50, -89, DIR_BACKWARD}, // BL20
//	{1800, 700, 115, 89, DIR_BACKWARD}, // BR20,
//
//	{1500, 1500, 53, 87.5, DIR_FORWARD}, // FL30
//	{1500, 1500, 108, -86.5, DIR_FORWARD}, // FR30
//	{1500, 1500, 51, -87.5, DIR_BACKWARD}, // BL30
//	{1500, 1100, 115, 88, DIR_BACKWARD}, // BR30
//};
//CmdConfig cfgs[19] = {
//	{0,0,SERVO_CENTER,0, DIR_FORWARD}, // STOP
//	{1200, 1200, SERVO_CENTER, 0, DIR_FORWARD}, // FW00
//	{1200, 1200, SERVO_CENTER, 0, DIR_BACKWARD}, // BW00
//
//	{800, 1200, 50, 0, DIR_FORWARD}, // FL--
//	{1200, 1500, 115, 0, DIR_FORWARD}, // FR--
//	{800, 1200, 50, 0, DIR_BACKWARD}, // BL--
//	{1200, 800, 115, 0, DIR_BACKWARD}, // BR--
//
////	{700, 1800, 50, 89, DIR_FORWARD}, // FL00
////	{2700, 1600, 93 ,-85, DIR_FORWARD}, // FR00
////	{700, 1800, 53, -86, DIR_BACKWARD}, // BL00
////	{2700, 1600, 92, 89, DIR_BACKWARD}, // BR00,
//
//	{0, 0, 41.5, 90.7, DIR_FORWARD}, // FL00 // 90.1 //90.2 //CENTER-69 //under
//	{0, 0, 96.5 ,-85.38, DIR_FORWARD}, // FR00 // -84.9 //-84.78 //over
//	{0, 0, 41.5, -86.08, DIR_BACKWARD}, // BL00 // -86.1 //86.08 //over
//	{0, 0, 96.5, 92.5, DIR_BACKWARD}, // BR00, // 88.9 //under
//
//	{800, 1800, 51.85, 89, DIR_FORWARD}, // FL20
//	{1800, 900, 115 ,-87, DIR_FORWARD}, // FR20
//	{700, 1800, 50, -89, DIR_BACKWARD}, // BL20
//	{1800, 700, 115, 89, DIR_BACKWARD}, // BR20,
//
//	{1500, 1500, 53, 87.5, DIR_FORWARD}, // FL30
//	{1500, 1500, 108, -86.5, DIR_FORWARD}, // FR30
//	{1500, 1500, 51, -87.5, DIR_BACKWARD}, // BL30
//	{1500, 1100, 115, 88, DIR_BACKWARD}, // BR30
//};

CmdConfig cfgs[19] = {
	{0,0,SERVO_CENTER,0, DIR_FORWARD}, // STOP
	{1686.6, 2000, SERVO_CENTER, 0, DIR_FORWARD}, // FW00
	{1686.6, 1839.7, SERVO_CENTER, 0, DIR_BACKWARD}, // BW00 //{1796.4, 1854.2, SERVO_CENTER, 0, DIR_BACKWARD}, // BW00

	{800, 1200, 50, 0, DIR_FORWARD}, // FL--
	{1200, 1500, 115, 0, DIR_FORWARD}, // FR--
	{800, 1200, 50, 0, DIR_BACKWARD}, // BL--
	{1200, 800, 115, 0, DIR_BACKWARD}, // BR--

//	{700, 1800, 50, 89, DIR_FORWARD}, // FL00
//	{2700, 1600, 93 ,-85, DIR_FORWARD}, // FR00
//	{700, 1800, 53, -86, DIR_BACKWARD}, // BL00
//	{2700, 1600, 92, 89, DIR_BACKWARD}, // BR00,

	//{931, 1839.7, 46.568, 90, DIR_FORWARD}, // FL00 // 90.1 //90.2 //CENTER-69 //under //steering-35.5/38.4X41.5
	//{1839.7, 931, 91.432 ,-85.38, DIR_FORWARD}, // FR00 // -84.9 //-84.78 //over
	//{1796.4, 1854.2, 41.5, -86.08, DIR_BACKWARD}, // BL00 // -86.1 //86.08 //over
	//{1796.4, 1854.2, 96.5, 92.5, DIR_BACKWARD}, // BR00, // 88.9 //under
	//{1343.9216860203705, 1847.1742606832456, 22.53, 90.7, DIR_FORWARD},
	{1678.94, 1847.17, 44, 88.5, DIR_FORWARD},
	{1902.47, 1617.55, 98 ,-85.25, DIR_FORWARD}, // FR00 // -84.9 //-84.78 //over
	{1678.94, 1847.17, 45, -85.75, DIR_BACKWARD}, // BL00 // -86.1 //86.08 //over
	{1902.47, 1617.55, 98.75, 88.6, DIR_BACKWARD}, // BR00, // 88.9 //under //TIGHTEN

	//{800, 1800, 51.85, 88, DIR_FORWARD}, // FL20
	//{1800, 900, 115 ,-87, DIR_FORWARD}, // FR20
	{1686.6, -1839.7, SERVO_CENTER, 0, DIR_FORWARD}, // FW00
	{-1686.6, 1839.7, SERVO_CENTER, 0, DIR_BACKWARD},
	{700, 1800, 50, -89, DIR_BACKWARD}, // BL20
	{1800, 700, 115, 89, DIR_BACKWARD}, // BR20,

	{0, 2000, 53, 90, DIR_FORWARD}, // FL30
	{2000, 0, 120, -87, DIR_FORWARD}, // FR30
	{1500, 1500, 51, -87.5, DIR_BACKWARD}, // BL30
	{2000, 0, 115, 90.5, DIR_BACKWARD}, // BR30
};

enum TASK_TYPE{
	TASK_MOVE,
	TASK_MOVE_BACKWARD,
	TASK_FL,
	TASK_FR,
	TASK_BL,
	TASK_BR,
	TASK_ADC,
	TASK_MOVE_OBS,
	TASK_FASTESTPATH,
	TASK_FASTESTPATH_V2,
	TASK_BUZZER,
	TASK_NONE
};
enum TASK_TYPE curTask = TASK_NONE, prevTask = TASK_NONE;

enum MOVE_MODE {
	SLOW,
	FAST
};
 enum MOVE_MODE moveMode = FAST;


uint16_t obsTick_IR = 0, obsTick_IR2 = 0;

float obsDist_IR = 0, obsDist_IR2 = 0, obsDist_US = 0;
//float IR_data_raw_acc = 0, dataPoint = 0;
uint16_t dataPoint = 0, dataPoint2 = 0; uint32_t IR_data_raw_acc = 0, IR_data_raw_acc2 = 0;
float speedScale = 1;


float batteryVal;

// fastest path variable
float obs_a, x, angle_left, angle_right;
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_TIM6_Init(void);
static void MX_TIM8_Init(void);
static void MX_TIM2_Init(void);
static void MX_USART3_UART_Init(void);
static void MX_TIM1_Init(void);
static void MX_TIM3_Init(void);
static void MX_I2C1_Init(void);
static void MX_ADC1_Init(void);
static void MX_TIM4_Init(void);
static void MX_ADC2_Init(void);
void runOledTask(void *argument);
void runCmdTask(void *argument);
void runADCTask(void *argument);
void runMoveDistTask(void *argument);
void runFastestPathTask(void *argument);
void runBuzzerTask(void *argument);
void runFLTask(void *argument);
void runFRTask(void *argument);
void runBLTask(void *argument);
void runBRTask(void *argument);
void runFastestPathTask_V2(void *argument);
void runBatteryTask(void *argument);
void runMoveDistObsTask(void *argument);

/* USER CODE BEGIN PFP */
void PIDConfigInit(PIDConfig * cfg, const float Kp, const float Ki, const float Kd);
void PIDConfigReset(PIDConfig * cfg);


void StraightLineMove(const uint8_t speedMode);
void StraightLineMoveSpeedScale(const uint8_t speedMode, float * speedScale);
void RobotMoveDist(float * targetDist, const uint8_t dir, const uint8_t speedMode);
void RobotMoveDistObstacle(float * targetDist, const uint8_t speedMode);

void RobotTurn(float * targetAngle);
void RobotTurnFastest(float * targetAngle);
void sensorTask(void *argument);
void motorStop();
void StartIRTask(void *argument);
void Wait();

uint32_t IC_Val1 = 0, IC_Val2 = 0;
uint8_t Is_First_Captured = 0;
uint32_t Difference = 0;
uint16_t Distance=0;
int usFlag = 0;
uint16_t usThreshold = 40;
// ir sensor
uint16_t iDistanceL = 0;
uint16_t iDistanceR = 0;
int irFlag = 0;
int xFlag = 0;
uint16_t x1 = 0;
uint16_t irThreshold = 1500;
int irResumeFlag = 1;
uint32_t data = 0;
uint8_t directionCmd;
uint8_t moveCmd;


/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */
/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{
  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_TIM8_Init();
  MX_TIM6_Init();
  MX_TIM2_Init();
  MX_USART3_UART_Init();
  MX_TIM1_Init();
  MX_TIM3_Init();
  MX_I2C1_Init();
  MX_ADC1_Init();
  MX_TIM4_Init();
  MX_ADC2_Init();
  /* USER CODE BEGIN 2 */
  OLED_Init();

  ICM20948_init(&hi2c1,0,GYRO_FULL_SCALE_2000DPS);

  // initialise command queue
  curCmd.index = 100;
  curCmd.val = 0;

  cQueue.head = 0;
  cQueue.tail = 0;
  cQueue.size = CMD_BUFFER_SIZE;
  for (int i = 0; i < CMD_BUFFER_SIZE;i++) {
	  Command cmd;
	  cmd.index = 100;
	  cmd.val = 0;
	  cQueue.buffer[i] = cmd;
  }

  PIDConfigInit(&pidTSlow, 2.5, 0,0.8);
  PIDConfigInit(&pidSlow, 2.5, 0,0);
  PIDConfigInit(&pidFast, 1.5, 0 ,0);
//  PIDConfigInit(&pidFast, 0.75, 0.0,0);

  	HAL_UART_Receive_IT(&huart3, aRxBuffer,RX_BUFFER_SIZE);

	// servo motor turn
	HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_4);
	// motor backwheel move
	HAL_TIM_PWM_Start(&htim8, TIM_CHANNEL_1);
	HAL_TIM_PWM_Start(&htim8, TIM_CHANNEL_2);
	// encoder monitor speed and distance
	HAL_TIM_Encoder_Start(&htim2, TIM_CHANNEL_ALL);
//	HAL_TIM_Encoder_Start(&htim3, TIM_CHANNEL_ALL);

	//adjust steering
	__RESET_SERVO_TURN(&htim1);

	//htim1.Instance->CCR4 = 140; // Center wheel POS


  /* USER CODE END 2 */

  /* Init scheduler */
  osKernelInitialize();

  /* USER CODE BEGIN RTOS_MUTEX */
  /* add mutexes, ... */
  /* USER CODE END RTOS_MUTEX */

  /* USER CODE BEGIN RTOS_SEMAPHORES */
  /* add semaphores, ... */
  /* USER CODE END RTOS_SEMAPHORES */

  /* USER CODE BEGIN RTOS_TIMERS */
  /* start timers, add new ones, ... */
  /* USER CODE END RTOS_TIMERS */

  /* USER CODE BEGIN RTOS_QUEUES */
  /* add queues, ... */
  /* USER CODE END RTOS_QUEUES */

  /* Create the thread(s) */
  /* creation of oledTask */
  oledTaskHandle = osThreadNew(runOledTask, NULL, &oledTask_attributes);

  /* creation of commandTask */
  commandTaskHandle = osThreadNew(runCmdTask, NULL, &commandTask_attributes);

  /* creation of ADCTask */
  ADCTaskHandle = osThreadNew(runADCTask, NULL, &ADCTask_attributes);

  /* creation of moveDistTask */
  moveDistTaskHandle = osThreadNew(runMoveDistTask, NULL, &moveDistTask_attributes);

  /* creation of fastestPathTask */
  fastestPathTaskHandle = osThreadNew(runFastestPathTask, NULL, &fastestPathTask_attributes);

  /* creation of buzzerTask */
  buzzerTaskHandle = osThreadNew(runBuzzerTask, NULL, &buzzerTask_attributes);

  /* creation of FLTask */
  FLTaskHandle = osThreadNew(runFLTask, NULL, &FLTask_attributes);

  /* creation of FRTask */
  FRTaskHandle = osThreadNew(runFRTask, NULL, &FRTask_attributes);

  /* creation of BLTask */
  BLTaskHandle = osThreadNew(runBLTask, NULL, &BLTask_attributes);

  /* creation of BRTask */
  BRTaskHandle = osThreadNew(runBRTask, NULL, &BRTask_attributes);

  /* creation of fastestPathV2 */
  fastestPathV2Handle = osThreadNew(runFastestPathTask_V2, NULL, &fastestPathV2_attributes);

  /* creation of batteryTask */
  batteryTaskHandle = osThreadNew(runBatteryTask, NULL, &batteryTask_attributes);

  /* creation of moveDistObsTask */
  moveDistObsTaskHandle = osThreadNew(runMoveDistObsTask, NULL, &moveDistObsTask_attributes);

  SensorTaskHandle = osThreadNew(sensorTask, NULL, &SensorTask_attributes);

  IRTaskHandle = osThreadNew(StartIRTask, NULL, &IRTask_attributes);

  /* USER CODE BEGIN RTOS_THREADS */
  /* add threads, ... */
  /* USER CODE END RTOS_THREADS */

  /* USER CODE BEGIN RTOS_EVENTS */
  /* add events, ... */
  /* USER CODE END RTOS_EVENTS */

  /* Start scheduler */
  osKernelStart();

  /* We should never get here as control is now taken by the scheduler */
  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Configure the main internal regulator output voltage
  */
  __HAL_RCC_PWR_CLK_ENABLE();
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);
  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_NONE;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }
  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_HSI;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_0) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief ADC1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_ADC1_Init(void)
{

  /* USER CODE BEGIN ADC1_Init 0 */

  /* USER CODE END ADC1_Init 0 */

  ADC_ChannelConfTypeDef sConfig = {0};

  /* USER CODE BEGIN ADC1_Init 1 */

  /* USER CODE END ADC1_Init 1 */
  /** Configure the global features of the ADC (Clock, Resolution, Data Alignment and number of conversion)
  */
  hadc1.Instance = ADC1;
  hadc1.Init.ClockPrescaler = ADC_CLOCK_SYNC_PCLK_DIV2;
  hadc1.Init.Resolution = ADC_RESOLUTION_12B;
  hadc1.Init.ScanConvMode = DISABLE;
  hadc1.Init.ContinuousConvMode = DISABLE;		//this means that the ADC performs a single-channel, single-conversion mode.
  hadc1.Init.DiscontinuousConvMode = DISABLE;
  hadc1.Init.ExternalTrigConvEdge = ADC_EXTERNALTRIGCONVEDGE_NONE;
  hadc1.Init.ExternalTrigConv = ADC_SOFTWARE_START;
  hadc1.Init.DataAlign = ADC_DATAALIGN_RIGHT;
  hadc1.Init.NbrOfConversion = 1;
  hadc1.Init.DMAContinuousRequests = DISABLE;
  hadc1.Init.EOCSelection = ADC_EOC_SINGLE_CONV;
  if (HAL_ADC_Init(&hadc1) != HAL_OK)
  {
    Error_Handler();
  }
  /** Configure for the selected ADC regular channel its corresponding rank in the sequencer and its sample time.
  */
  sConfig.Channel = ADC_CHANNEL_11;
  sConfig.Rank = 1;
  sConfig.SamplingTime = ADC_SAMPLETIME_3CYCLES;
  if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN ADC1_Init 2 */

  /* USER CODE END ADC1_Init 2 */

}

/**
  * @brief ADC2 Initialization Function
  * @param None
  * @retval None
  */
static void MX_ADC2_Init(void)
{

  /* USER CODE BEGIN ADC2_Init 0 */

  /* USER CODE END ADC2_Init 0 */

  ADC_ChannelConfTypeDef sConfig = {0};

  /* USER CODE BEGIN ADC2_Init 1 */

  /* USER CODE END ADC2_Init 1 */
  /** Configure the global features of the ADC (Clock, Resolution, Data Alignment and number of conversion)
  */
  hadc2.Instance = ADC2;
  hadc2.Init.ClockPrescaler = ADC_CLOCK_SYNC_PCLK_DIV2;
  hadc2.Init.Resolution = ADC_RESOLUTION_12B;
  hadc2.Init.ScanConvMode = DISABLE;
  hadc2.Init.ContinuousConvMode = DISABLE;
  hadc2.Init.DiscontinuousConvMode = DISABLE;
  hadc2.Init.ExternalTrigConvEdge = ADC_EXTERNALTRIGCONVEDGE_NONE;
  hadc2.Init.ExternalTrigConv = ADC_SOFTWARE_START;
  hadc2.Init.DataAlign = ADC_DATAALIGN_RIGHT;
  hadc2.Init.NbrOfConversion = 1;
  hadc2.Init.DMAContinuousRequests = DISABLE;
  hadc2.Init.EOCSelection = ADC_EOC_SINGLE_CONV;
  if (HAL_ADC_Init(&hadc2) != HAL_OK)
  {
    Error_Handler();
  }
  /** Configure for the selected ADC regular channel its corresponding rank in the sequencer and its sample time.
  */
  sConfig.Channel = ADC_CHANNEL_12;
  sConfig.Rank = 1;
  sConfig.SamplingTime = ADC_SAMPLETIME_3CYCLES;
  if (HAL_ADC_ConfigChannel(&hadc2, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN ADC2_Init 2 */

  /* USER CODE END ADC2_Init 2 */

}

/**
  * @brief I2C1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_I2C1_Init(void)
{

  /* USER CODE BEGIN I2C1_Init 0 */

  /* USER CODE END I2C1_Init 0 */

  /* USER CODE BEGIN I2C1_Init 1 */

  /* USER CODE END I2C1_Init 1 */
  hi2c1.Instance = I2C1;
  hi2c1.Init.ClockSpeed = 100000;
  hi2c1.Init.DutyCycle = I2C_DUTYCYCLE_2;
  hi2c1.Init.OwnAddress1 = 0;
  hi2c1.Init.AddressingMode = I2C_ADDRESSINGMODE_7BIT;
  hi2c1.Init.DualAddressMode = I2C_DUALADDRESS_DISABLE;
  hi2c1.Init.OwnAddress2 = 0;
  hi2c1.Init.GeneralCallMode = I2C_GENERALCALL_DISABLE;
  hi2c1.Init.NoStretchMode = I2C_NOSTRETCH_DISABLE;
  if (HAL_I2C_Init(&hi2c1) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN I2C1_Init 2 */

  /* USER CODE END I2C1_Init 2 */

}

/**
  * @brief TIM1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM1_Init(void)
{

  /* USER CODE BEGIN TIM1_Init 0 */

  /* USER CODE END TIM1_Init 0 */

  TIM_ClockConfigTypeDef sClockSourceConfig = {0};
  TIM_MasterConfigTypeDef sMasterConfig = {0};
  TIM_OC_InitTypeDef sConfigOC = {0};
  TIM_BreakDeadTimeConfigTypeDef sBreakDeadTimeConfig = {0};

  /* USER CODE BEGIN TIM1_Init 1 */

  /* USER CODE END TIM1_Init 1 */
  htim1.Instance = TIM1;
  htim1.Init.Prescaler = 320;
  htim1.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim1.Init.Period = 1000;
  htim1.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim1.Init.RepetitionCounter = 0;
  htim1.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_ENABLE;
  if (HAL_TIM_Base_Init(&htim1) != HAL_OK)
  {
    Error_Handler();
  }
  sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;
  if (HAL_TIM_ConfigClockSource(&htim1, &sClockSourceConfig) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_TIM_PWM_Init(&htim1) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim1, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sConfigOC.OCMode = TIM_OCMODE_PWM1;
  sConfigOC.Pulse = 0;
  sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
  sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
  sConfigOC.OCIdleState = TIM_OCIDLESTATE_RESET;
  sConfigOC.OCNIdleState = TIM_OCNIDLESTATE_RESET;
  if (HAL_TIM_PWM_ConfigChannel(&htim1, &sConfigOC, TIM_CHANNEL_4) != HAL_OK)
  {
    Error_Handler();
  }
  sBreakDeadTimeConfig.OffStateRunMode = TIM_OSSR_DISABLE;
  sBreakDeadTimeConfig.OffStateIDLEMode = TIM_OSSI_DISABLE;
  sBreakDeadTimeConfig.LockLevel = TIM_LOCKLEVEL_OFF;
  sBreakDeadTimeConfig.DeadTime = 0;
  sBreakDeadTimeConfig.BreakState = TIM_BREAK_DISABLE;
  sBreakDeadTimeConfig.BreakPolarity = TIM_BREAKPOLARITY_HIGH;
  sBreakDeadTimeConfig.AutomaticOutput = TIM_AUTOMATICOUTPUT_DISABLE;
  if (HAL_TIMEx_ConfigBreakDeadTime(&htim1, &sBreakDeadTimeConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM1_Init 2 */

  /* USER CODE END TIM1_Init 2 */
  HAL_TIM_MspPostInit(&htim1);

}

/**
  * @brief TIM2 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM2_Init(void)
{

  /* USER CODE BEGIN TIM2_Init 0 */

  /* USER CODE END TIM2_Init 0 */

  TIM_Encoder_InitTypeDef sConfig = {0};
  TIM_MasterConfigTypeDef sMasterConfig = {0};

  /* USER CODE BEGIN TIM2_Init 1 */

  /* USER CODE END TIM2_Init 1 */
  htim2.Instance = TIM2;
  htim2.Init.Prescaler = 0;
  htim2.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim2.Init.Period = 65535;
  htim2.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim2.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  sConfig.EncoderMode = TIM_ENCODERMODE_TI12;
  sConfig.IC1Polarity = TIM_ICPOLARITY_RISING;
  sConfig.IC1Selection = TIM_ICSELECTION_DIRECTTI;
  sConfig.IC1Prescaler = TIM_ICPSC_DIV1;
  sConfig.IC1Filter = 10;
  sConfig.IC2Polarity = TIM_ICPOLARITY_RISING;
  sConfig.IC2Selection = TIM_ICSELECTION_DIRECTTI;
  sConfig.IC2Prescaler = TIM_ICPSC_DIV1;
  sConfig.IC2Filter = 10;
  if (HAL_TIM_Encoder_Init(&htim2, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim2, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM2_Init 2 */

  /* USER CODE END TIM2_Init 2 */

}

/**
  * @brief TIM3 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM3_Init(void)
{

  /* USER CODE BEGIN TIM3_Init 0 */

  /* USER CODE END TIM3_Init 0 */

  TIM_Encoder_InitTypeDef sConfig = {0};
  TIM_MasterConfigTypeDef sMasterConfig = {0};

  /* USER CODE BEGIN TIM3_Init 1 */

  /* USER CODE END TIM3_Init 1 */
  htim3.Instance = TIM3;
  htim3.Init.Prescaler = 0;
  htim3.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim3.Init.Period = 65535;
  htim3.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim3.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  sConfig.EncoderMode = TIM_ENCODERMODE_TI12;
  sConfig.IC1Polarity = TIM_ICPOLARITY_RISING;
  sConfig.IC1Selection = TIM_ICSELECTION_DIRECTTI;
  sConfig.IC1Prescaler = TIM_ICPSC_DIV1;
  sConfig.IC1Filter = 10;
  sConfig.IC2Polarity = TIM_ICPOLARITY_RISING;
  sConfig.IC2Selection = TIM_ICSELECTION_DIRECTTI;
  sConfig.IC2Prescaler = TIM_ICPSC_DIV1;
  sConfig.IC2Filter = 10;
  if (HAL_TIM_Encoder_Init(&htim3, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim3, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM3_Init 2 */

  /* USER CODE END TIM3_Init 2 */

}

/**
  * @brief TIM4 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM4_Init(void)
{

  /* USER CODE BEGIN TIM4_Init 0 */

  /* USER CODE END TIM4_Init 0 */

  TIM_MasterConfigTypeDef sMasterConfig = {0};
  TIM_IC_InitTypeDef sConfigIC = {0};

  /* USER CODE BEGIN TIM4_Init 1 */

  /* USER CODE END TIM4_Init 1 */
  htim4.Instance = TIM4;
  htim4.Init.Prescaler = 16-1;
  htim4.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim4.Init.Period = 65535;
  htim4.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim4.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  if (HAL_TIM_IC_Init(&htim4) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim4, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sConfigIC.ICPolarity = TIM_INPUTCHANNELPOLARITY_RISING;
  sConfigIC.ICSelection = TIM_ICSELECTION_DIRECTTI;
  sConfigIC.ICPrescaler = TIM_ICPSC_DIV1;
  sConfigIC.ICFilter = 0;
  if (HAL_TIM_IC_ConfigChannel(&htim4, &sConfigIC, TIM_CHANNEL_2) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_TIM_IC_ConfigChannel(&htim4, &sConfigIC, TIM_CHANNEL_1) != HAL_OK) {
  		Error_Handler();
  	}
  /* USER CODE BEGIN TIM4_Init 2 */

  /* USER CODE END TIM4_Init 2 */

}

static void MX_TIM6_Init(void)
{

  /* USER CODE BEGIN TIM6_Init 0 */

  /* USER CODE END TIM6_Init 0 */

  TIM_MasterConfigTypeDef sMasterConfig = {0};

  /* USER CODE BEGIN TIM6_Init 1 */

  /* USER CODE END TIM6_Init 1 */
  htim6.Instance = TIM6;
  htim6.Init.Prescaler = 0;
  htim6.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim6.Init.Period = 65535;
  htim6.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  if (HAL_TIM_Base_Init(&htim6) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim6, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM6_Init 2 */

  /* USER CODE END TIM6_Init 2 */

}

/**
  * @brief TIM8 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM8_Init(void)
{

  /* USER CODE BEGIN TIM8_Init 0 */

  /* USER CODE END TIM8_Init 0 */

  TIM_ClockConfigTypeDef sClockSourceConfig = {0};
  TIM_MasterConfigTypeDef sMasterConfig = {0};
  TIM_OC_InitTypeDef sConfigOC = {0};
  TIM_BreakDeadTimeConfigTypeDef sBreakDeadTimeConfig = {0};

  /* USER CODE BEGIN TIM8_Init 1 */

  /* USER CODE END TIM8_Init 1 */
  htim8.Instance = TIM8;
  htim8.Init.Prescaler = 0;
  htim8.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim8.Init.Period = 7199;
  htim8.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim8.Init.RepetitionCounter = 0;
  htim8.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  if (HAL_TIM_Base_Init(&htim8) != HAL_OK)
  {
    Error_Handler();
  }
  sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;
  if (HAL_TIM_ConfigClockSource(&htim8, &sClockSourceConfig) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_TIM_PWM_Init(&htim8) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim8, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sConfigOC.OCMode = TIM_OCMODE_PWM1;
  sConfigOC.Pulse = 0;
  sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
  sConfigOC.OCNPolarity = TIM_OCNPOLARITY_HIGH;
  sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
  sConfigOC.OCIdleState = TIM_OCIDLESTATE_RESET;
  sConfigOC.OCNIdleState = TIM_OCNIDLESTATE_RESET;
  if (HAL_TIM_PWM_ConfigChannel(&htim8, &sConfigOC, TIM_CHANNEL_1) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_TIM_PWM_ConfigChannel(&htim8, &sConfigOC, TIM_CHANNEL_2) != HAL_OK)
  {
    Error_Handler();
  }
  sBreakDeadTimeConfig.OffStateRunMode = TIM_OSSR_DISABLE;
  sBreakDeadTimeConfig.OffStateIDLEMode = TIM_OSSI_DISABLE;
  sBreakDeadTimeConfig.LockLevel = TIM_LOCKLEVEL_OFF;
  sBreakDeadTimeConfig.DeadTime = 0;
  sBreakDeadTimeConfig.BreakState = TIM_BREAK_DISABLE;
  sBreakDeadTimeConfig.BreakPolarity = TIM_BREAKPOLARITY_HIGH;
  sBreakDeadTimeConfig.AutomaticOutput = TIM_AUTOMATICOUTPUT_DISABLE;
  if (HAL_TIMEx_ConfigBreakDeadTime(&htim8, &sBreakDeadTimeConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM8_Init 2 */

  /* USER CODE END TIM8_Init 2 */

}

/**
  * @brief USART3 Initialization Function
  * @param None
  * @retval None
  */
static void MX_USART3_UART_Init(void)
{

  /* USER CODE BEGIN USART3_Init 0 */

  /* USER CODE END USART3_Init 0 */

  /* USER CODE BEGIN USART3_Init 1 */

  /* USER CODE END USART3_Init 1 */
  huart3.Instance = USART3;
  huart3.Init.BaudRate = 115200;
  huart3.Init.WordLength = UART_WORDLENGTH_8B;
  huart3.Init.StopBits = UART_STOPBITS_1;
  huart3.Init.Parity = UART_PARITY_NONE;
  huart3.Init.Mode = UART_MODE_TX_RX;
  huart3.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart3.Init.OverSampling = UART_OVERSAMPLING_16;
  if (HAL_UART_Init(&huart3) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN USART3_Init 2 */

  /* USER CODE END USART3_Init 2 */

}

/**
  * @brief GPIO Initialization Function
  * @param None
  * @retval None
  */
static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOE_CLK_ENABLE();
  __HAL_RCC_GPIOH_CLK_ENABLE();
  __HAL_RCC_GPIOC_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();
  __HAL_RCC_GPIOB_CLK_ENABLE();
  __HAL_RCC_GPIOD_CLK_ENABLE();

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOE, OLED_SCL_Pin|OLED_SDA_Pin|OLED_RST_Pin|OLED_DC_Pin
                          |LED3_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOA, AIN2_Pin|AIN1_Pin|BIN1_Pin|BIN2_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(Buzzer_GPIO_Port, Buzzer_Pin|TRI_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pin Output Level */
  	HAL_GPIO_WritePin(Trigger_GPIO_Port, Trigger_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pins : OLED_SCL_Pin OLED_SDA_Pin OLED_RST_Pin OLED_DC_Pin
                           LED3_Pin */
  GPIO_InitStruct.Pin = OLED_SCL_Pin|OLED_SDA_Pin|OLED_RST_Pin|OLED_DC_Pin
                          |LED3_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOE, &GPIO_InitStruct);

  /*Configure GPIO pins : AIN2_Pin AIN1_Pin BIN1_Pin BIN2_Pin */
  GPIO_InitStruct.Pin = AIN2_Pin|AIN1_Pin|BIN1_Pin|BIN2_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

  /*Configure GPIO pins : BUZZER_Pin TRI_Pin */
  GPIO_InitStruct.Pin = Buzzer_Pin|TRI_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);

  /*Configure GPIO pin : SW1_Pin */
  GPIO_InitStruct.Pin = USER_PB_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_IT_FALLING;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  HAL_GPIO_Init(USER_PB_GPIO_Port, &GPIO_InitStruct);

  /*Configure GPIO pin : Trigger_Pin */
  	GPIO_InitStruct.Pin = Trigger_Pin;
  	GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  	GPIO_InitStruct.Pull = GPIO_NOPULL;
  	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  	HAL_GPIO_Init(Trigger_GPIO_Port, &GPIO_InitStruct);

  /* EXTI interrupt init*/
//  HAL_NVIC_SetPriority(EXTI9_5_IRQn, 5, 0);
//  HAL_NVIC_EnableIRQ(EXTI9_5_IRQn);

}

/* USER CODE BEGIN 4 */

// HAL_UART_RxCpltCallback evoked when buffer is full
// Function process commands like stop forward and etc
// Main logic block helps to queue commands to commandqueue for processing
void HAL_UART_RxCpltCallback(UART_HandleTypeDef * huart) {
	// prevent unused argument(s) compilation warning
	HAL_UART_Transmit(&huart3, (uint8_t*) aRxBuffer, 4, 0xFFF);
	UNUSED(huart);
	int val;
	val = (aRxBuffer[2] - 48) * 10 + (aRxBuffer[3] - 48);
	if (aRxBuffer[1] >= '0' && aRxBuffer[1] <= '9') val += (aRxBuffer[1] - 48) * 100;


	manualMode = 0;

	if (aRxBuffer[0] == 'S' && aRxBuffer[1] == 'T') { // only STOP can preempt any greedy task
//		__ADD_COMMAND(cQueue, 0, 0); // stop
		__ON_TASK_END(&htim8, prevTask, curTask);
		  angleNow = 0; gyroZ = 0; // reset angle for PID
		PIDConfigReset(&pidTSlow);
		PIDConfigReset(&pidSlow);
		PIDConfigReset(&pidFast);
		curDistTick = 0;
		if (__COMMAND_QUEUE_IS_EMPTY(cQueue)) {
			__CLEAR_CURCMD(curCmd);
			__ACK_TASK_DONE(&huart3, rxMsg);
		}
		else {
			__READ_COMMAND(cQueue, curCmd, rxMsg);
		}
	}
	else if (aRxBuffer[0] == 'F' && (aRxBuffer[1] == 'W' || aRxBuffer[1] == 'S')) { //FW or FS
		manualMode = aRxBuffer[2] == '-' && aRxBuffer[3] == '-';
		moveMode = aRxBuffer[1] == 'S' ? SLOW : FAST;
		__ADD_COMMAND(cQueue, 1, val);
	}
	else if (aRxBuffer[0] == 'B' && (aRxBuffer[1] == 'W' || aRxBuffer[1] == 'S')) { //BW or BS
		manualMode = aRxBuffer[2] == '-' && aRxBuffer[3] == '-';
		moveMode = aRxBuffer[1] == 'S' ? SLOW : FAST;
		__ADD_COMMAND(cQueue, 2, val);
	}
	else if (aRxBuffer[0] == 'F' && aRxBuffer[1] == 'L') { // FL
		manualMode = aRxBuffer[2] == '-' && aRxBuffer[3] == '-';
		__ADD_COMMAND(cQueue, 3 + (manualMode ? 0 : 4), val);
	}
	else if (aRxBuffer[0] == 'F' && aRxBuffer[1] == 'R') { // FR
		manualMode = aRxBuffer[2] == '-' && aRxBuffer[3] == '-';
		__ADD_COMMAND(cQueue, 4 + (manualMode ? 0 : 4), val);
	}
	else if (aRxBuffer[0] == 'B' && aRxBuffer[1] == 'L') { // BL
		manualMode = aRxBuffer[2] == '-' && aRxBuffer[3] == '-';
		__ADD_COMMAND(cQueue, 5 + (manualMode ? 0 : 4), val);
	}
	else if (aRxBuffer[0] == 'B' && aRxBuffer[1] == 'R') { // BR
		manualMode = aRxBuffer[2] == '-' && aRxBuffer[3] == '-';
		__ADD_COMMAND(cQueue, 6 + (manualMode ? 0 : 4), val);
	}
	else if (aRxBuffer[0] == 'T' && aRxBuffer[1] == 'L') __ADD_COMMAND(cQueue, 11, val); // TL turn left max
	else if (aRxBuffer[0] == 'T' && aRxBuffer[1] == 'R') __ADD_COMMAND(cQueue, 12, val); // TR turn right max
	else if (aRxBuffer[0] == 'I' && aRxBuffer[1] == 'R') __ADD_COMMAND(cQueue, 13, val); // test IR sensor
	else if (aRxBuffer[0] == 'D' && aRxBuffer[1] == 'T') __ADD_COMMAND(cQueue, 14, val); // DT move until specified distance from obstacle
	else if (aRxBuffer[0] == 'Z' && aRxBuffer[1] == 'Z') __ADD_COMMAND(cQueue, 15, val); // ZZ buzzer
	else if (aRxBuffer[0] == 'W' && aRxBuffer[1] == 'X') __ADD_COMMAND(cQueue, 16, val); // WN fastest path
	else if (aRxBuffer[0] == 'W' && aRxBuffer[1] == 'N') __ADD_COMMAND(cQueue, 17, val); // WN fastest path v2
	else if (aRxBuffer[0] == 'A') __ADD_COMMAND(cQueue, 88, val); // anti-clockwise rotation with variable
	else if (aRxBuffer[0] == 'C') __ADD_COMMAND(cQueue, 89, val); // clockwise rotation with variable

	if (!__COMMAND_QUEUE_IS_EMPTY(cQueue)) {
		__READ_COMMAND(cQueue, curCmd, rxMsg);
	}

	// clear aRx buffer
	  __HAL_UART_FLUSH_DRREGISTER(&huart3);
	  HAL_UART_Receive_IT(&huart3, aRxBuffer, RX_BUFFER_SIZE);
	    char c1 = aRxBuffer[0];
		char c2 = aRxBuffer[1];
		// char c3 = aRxBuffer[2];
		//c1 = 'n';
		//c2 = 'w';
		char d[4];

		//d[0] = '0';
		//d[1] = '0';
		//d[2] = '3';
		if(aRxBuffer[2] == '-' && aRxBuffer[3] == '1')
			data = -1;
		else {
			memcpy(d, (void*) &aRxBuffer[2], 2);
			d[2] = '\0';

			data = (uint32_t) atoi(d);
		}

		//if (c1 == 'n') {
		//	newCmdReceived = 1;

		//}
		moveCmd = c1;
		directionCmd = c2;
		// steeringCmd = c3;
		uint8_t message1[20];

		sprintf(message1, "cmd:%c,%d", directionCmd, data);
		//OLED_ShowString(0, 10, message1);

//		HAL_UART_Transmit(&huart3, (uint8_t*) aRxBuffer, 4, 0xFFF);
//		if (aRxBuffer == "LEFT"){
//
//		} else if (aRxBuffer == "RIGHT"){
//
//		}
}

//void HAL_UART_TxCpltCallback(UART_HandleTypeDef * huart) {
//	 UNUSED(huart);
//
//	 UART_Tx_Done = 1;
//}

int clickOnce = 0;
int targetD = 5;
uint8_t tempDir = 1 ;
int8_t step = 0;
uint8_t turnMode = 2;
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin) {
	if (clickOnce) return;
	if (GPIO_Pin == USER_PB_Pin) {
		clickOnce = 1;


//		manualMode = 1;
//		moveMode = FAST;
//		__ADD_COMMAND(cQueue, 1, 90);
//		__READ_COMMAND(cQueue, curCmd, rxMsg);

		__ADD_COMMAND(cQueue, 7 + step, 0);
		__READ_COMMAND(cQueue, curCmd, rxMsg);

		step = (step + 1) % 4;
//		step = (step + 1) % 7;
//		__ADD_COMMAND(cQueue, 17, turnMode + 1);
//		__READ_COMMAND(cQueue, curCmd, rxMsg);
//		turnMode = (turnMode + 1) % 4;
//		__ADD_COMMAND(cQueue, 1, 100);
//		__READ_COMMAND(cQueue, curCmd, rxMsg);
	}

}
// ir sensor
void IR_Left_Read() {
	HAL_ADC_Start(&hadc1);
	HAL_ADC_PollForConversion(&hadc1, 10);
	iDistanceL = HAL_ADC_GetValue(&hadc1);
	HAL_ADC_Stop(&hadc1);
}

int IR_Right_Read() {
	int retval = 0;
	for (int i = 0; i < 5; i++){
		HAL_ADC_Start(&hadc2);
		HAL_ADC_PollForConversion(&hadc2, 10);
		retval += HAL_ADC_GetValue(&hadc2);
		iDistanceR = HAL_ADC_GetValue(&hadc2);
		HAL_ADC_Stop(&hadc2);
	}
	return retval/5;
}
/* USER CODE END Header_StartIRTask */
void StartIRTask(void *argument) {
	/* USER CODE BEGIN StartIRTask */
	/* Infinite loop */
	uint8_t irVal[20] = { 0 };
	for (;;) {

		sprintf(irVal, "L: %d R: %d \0", (int) iDistanceL, iDistanceR);
		//OLED_ShowString(0, 30, irVal);
		if (irResumeFlag == 1) {
			vTaskSuspend(IRTaskHandle);
		}
		IR_Left_Read();
		IR_Right_Read();

		if ((aRxBuffer[1] == 'L' && (iDistanceL <= irThreshold - 500)
				&& irFlag == 1)
				|| (aRxBuffer[1] == 'R' && (iDistanceR <= irThreshold - 500)
						&& irFlag == 1)) {
			irFlag = 0;
			motorStop();
		}

		osDelay(50);
	}
	/* USER CODE END StartIRTask */
}

void PIDConfigInit(PIDConfig * cfg, const float Kp, const float Ki, const float Kd) {
	cfg->Kp = Kp;
	cfg->Ki = Ki;
	cfg->Kd = Kd;
	cfg->ek1 = 0;
	cfg->ekSum = 0;
}

void PIDConfigReset(PIDConfig * cfg) {
	cfg->ek1 = 0;
	cfg->ekSum = 0;
}


int8_t dir = 1;
int correction = 0;
//PIDConfig curPIDConfig;

void StraightLineMove(const uint8_t speedMode) {
	__Gyro_Read_Z(&hi2c1, readGyroZData, gyroZ); // polling
	dir = __HAL_TIM_IS_TIM_COUNTING_DOWN(&htim2) ? 1 : -1; // use only one of the wheel to determine car direction
	angleNow += ((gyroZ >= -4 && gyroZ <= 11) ? 0 : gyroZ); // / GRYO_SENSITIVITY_SCALE_FACTOR_2000DPS * 0.01;

	if (speedMode == SPEED_MODE_T) __PID_SPEED_T(pidTSlow, angleNow, correction, dir, newDutyL, newDutyR);
	else if (speedMode == SPEED_MODE_2) __PID_SPEED_2(pidFast, angleNow, correction, dir, newDutyL, newDutyR);
	else if (speedMode == SPEED_MODE_1) __PID_SPEED_1(pidSlow, angleNow, correction, dir, newDutyL, newDutyR);

	__SET_MOTOR_DUTY(&htim8, newDutyL, newDutyR);
}

void StraightLineMoveSpeedScale(const uint8_t speedMode, float * speedScale) {
	__Gyro_Read_Z(&hi2c1, readGyroZData, gyroZ); // polling
	dir = __HAL_TIM_IS_TIM_COUNTING_DOWN(&htim2) ? 1 : -1; // use only one of the wheel to determine car direction
	angleNow += ((gyroZ >= -4 && gyroZ <= 11) ? 0 : gyroZ); // / GRYO_SENSITIVITY_SCALE_FACTOR_2000DPS * 0.01;
	if (speedMode == SPEED_MODE_1) __PID_SPEED_1(pidSlow, angleNow, correction, dir, newDutyL, newDutyR);
	else if (speedMode == SPEED_MODE_2) __PID_SPEED_2(pidFast, angleNow, correction, dir, newDutyL, newDutyR);

	__SET_MOTOR_DUTY(&htim8, newDutyL * (*speedScale), newDutyR * (*speedScale));
}

void RobotMoveDist(float * targetDist, const uint8_t dir, const uint8_t speedMode) {
	angleNow = 0; gyroZ = 0; // reset angle for PID
	PIDConfigReset(&pidTSlow);
	PIDConfigReset(&pidSlow);
	PIDConfigReset(&pidFast);
	curDistTick = 0;

	__GET_TARGETTICK(*targetDist, targetDistTick);

	last_curTask_tick = HAL_GetTick();
	__SET_MOTOR_DIRECTION(dir);
	__SET_ENCODER_LAST_TICK(&htim2, lastDistTick_L);
	do {
		__GET_ENCODER_TICK_DELTA(&htim2, lastDistTick_L, dist_dL);
		curDistTick += dist_dL;

		if (curDistTick >= targetDistTick) break;

		if (HAL_GetTick() - last_curTask_tick >= 10) {
			if (speedMode == SPEED_MODE_T) {
				StraightLineMove(SPEED_MODE_T);
			} else {
				speedScale = abs(curDistTick - targetDistTick) / 990; // start to slow down at last 990 ticks (15cm)
				if (speedMode == SPEED_MODE_1) speedScale = speedScale > 1 ? 1 : (speedScale < 0.75 ? 0.75 : speedScale);
				else if (speedMode == SPEED_MODE_2)speedScale = speedScale > 1 ? 1 : (speedScale < 0.4 ? 0.4 : speedScale);
				StraightLineMoveSpeedScale(speedMode, &speedScale);
			}

			last_curTask_tick = HAL_GetTick();
		}
	} while (1);
	__SET_MOTOR_DUTY(&htim8, 0, 0);
}

// RobotMoveDistObstacle must be called within a task(eg. runFastestPath) and not within an interrupt(eg. UART, EXTI)
// else osDelay won't work and TRI's timer interrupt can't be given chance to update obsDist_US
void RobotMoveDistObstacle(float * targetDist, const uint8_t speedMode) {
	angleNow = 0; gyroZ = 0;
	PIDConfigReset(&pidTSlow);
	PIDConfigReset(&pidSlow);
	PIDConfigReset(&pidFast);
//	obsDist_US = 1000;
	HAL_TIM_IC_Start_IT(&htim4, TIM_CHANNEL_2);
	last_curTask_tick = HAL_GetTick();

	do {
	  HAL_GPIO_WritePin(TRI_GPIO_Port, TRI_Pin, GPIO_PIN_SET);  // pull the TRIG pin HIGH
	  __delay_us(&htim4, 10); // wait for 10us
	  HAL_GPIO_WritePin(TRI_GPIO_Port, TRI_Pin, GPIO_PIN_RESET);  // pull the TRIG pin low
	  __HAL_TIM_ENABLE_IT(&htim4, TIM_IT_CC2);
	  osDelay(10); // give timer interrupt chance to update obsDist_US value
	  if (abs(*targetDist - Distance) < 0.1) break;
	  __SET_MOTOR_DIRECTION(Distance >= *targetDist);
	  if (HAL_GetTick() - last_curTask_tick >=20) {
//		  speedScale = 1;
		  if (speedMode == SPEED_MODE_1) {
			  speedScale = abs(Distance - *targetDist) / 15; // slow down at 15cm
			  speedScale = speedScale > 1 ? 1 : (speedScale < 0.75 ? 0.75 : speedScale);
			  StraightLineMoveSpeedScale(SPEED_MODE_1, &speedScale);
		  } else {
			  speedScale = abs(Distance - *targetDist) / 15; // slow down at 15cm
			  speedScale = speedScale > 1 ? 1 : (speedScale < 0.4 ? 0.4 : speedScale);
			  StraightLineMoveSpeedScale(SPEED_MODE_2, &speedScale);
		  }


		  last_curTask_tick = HAL_GetTick();
	  }

	} while (1);

	__SET_MOTOR_DUTY(&htim8, 0, 0);
	HAL_TIM_IC_Stop_IT(&htim4, TIM_CHANNEL_2);
}

void RobotMoveDistObstacle_IR(float * targetDist) {
	dataPoint = 0; IR_data_raw_acc = 0; obsDist_IR = 1000;
	last_curTask_tick = HAL_GetTick();
//	__PEND_CURCMD(curCmd);

	do {
		__ADC_Read_Dist(&hadc1, dataPoint, IR_data_raw_acc, obsDist_IR, obsTick_IR);
		if (*targetDist > 0 && abs(*targetDist - obsDist_IR) < 0.1) break;

		__SET_MOTOR_DIRECTION(obsDist_IR >= *targetDist);
	  if (HAL_GetTick() - last_curTask_tick >=10) {
//		  speedScale = 1;
		  speedScale = abs(obsDist_IR - *targetDist) / 15; // slow down at 15cm
		  speedScale = speedScale > 1 ? 1 : (speedScale < 0.3 ? 0.3 : speedScale);
		  StraightLineMoveSpeedScale(SPEED_MODE_2, &speedScale);

		  last_curTask_tick = HAL_GetTick();
	  }
//	  osDelay(5);
	} while (1);

//  __ON_TASK_END(&htim8, prevTask, curTask);
	__SET_MOTOR_DUTY(&htim8, 0, 0);
	HAL_ADC_Stop(&hadc1);
}

void RobotTurn(float * targetAngle) {
	angleNow = 0; gyroZ = 0;
	last_curTask_tick = HAL_GetTick();
	char message1[20];
	do {

	  if (HAL_GetTick() - last_curTask_tick >= 10) { // sample gyro every 10ms
		  __Gyro_Read_Z(&hi2c1, readGyroZData, gyroZ);
		  //if(abs(gyroZ) > 10.0f){
		  angleNow += gyroZ / GRYO_SENSITIVITY_SCALE_FACTOR_2000DPS * 0.01;
		  if (abs(angleNow - *targetAngle) < 0.01) break;
		  last_curTask_tick = HAL_GetTick();
		  //}
//		sprintf(message1, "%5.1f \n", angleNow*180/3.1415);
//		OLED_ShowString(20,30, &message1[0]);
//		OLED_Refresh_Gram();
	  }
	} while(1);
//	sprintf(message1, "%d \n", angleNow);
//	OLED_ShowString(10,15, &message1[0]);
//	OLED_Refresh_Gram();

	__SET_MOTOR_DUTY(&htim8, 0, 0);
	__RESET_SERVO_TURN(&htim1);
}

void Wait() {
	last_curTask_tick = HAL_GetTick();
	do {
	  if (HAL_GetTick() - last_curTask_tick >= 10000) { // sample gyro every 10ms
		  break;
	  }
	} while(1);
	__SET_MOTOR_DUTY(&htim8, 0, 0);
	__RESET_SERVO_TURN(&htim1);
}


void RobotTurnFastest(float * targetAngle) {
	angleNow = 0; gyroZ = 0;
	last_curTask_tick = HAL_GetTick();
	do {
	  if (HAL_GetTick() - last_curTask_tick >= 10) { // sample gyro every 10ms
		  __Gyro_Read_Z(&hi2c1, readGyroZData, gyroZ);
		  angleNow += gyroZ / GRYO_SENSITIVITY_SCALE_FACTOR_2000DPS * 0.01;
		  if (abs(angleNow - *targetAngle) < 0.01) break;
		  last_curTask_tick = HAL_GetTick();
	  }
	} while(1);
	__SET_MOTOR_DUTY(&htim8, 0, 0);
	__RESET_SERVO_TURN_FAST(&htim1);
}

void FASTESTPATH_TURN_LEFT_90() {
	targetAngle = 87.5;
	__SET_SERVO_TURN(&htim1, 50);
	__SET_MOTOR_DIRECTION(1);
	__SET_MOTOR_DUTY(&htim8, 1000, 2000);
	RobotTurn(&targetAngle);
}

void FASTESTPATH_TURN_RIGHT_90() {
	targetAngle = -86;
	__SET_SERVO_TURN(&htim1, 115);
	__SET_MOTOR_DIRECTION(1);
	__SET_MOTOR_DUTY(&htim8, 3000, 800);

	RobotTurn(&targetAngle);
}

void FASTESTPATH_TURN_RIGHT_180() {
	targetAngle = -176;
	__SET_SERVO_TURN(&htim1, 115);
	__SET_MOTOR_DIRECTION(1);
	__SET_MOTOR_DUTY(&htim8, 3000, 800);
	RobotTurn(&targetAngle);
}

void FASTESTPATH_TURN_LEFT_90X(uint8_t * turnSize) { // x3
	__SET_MOTOR_DIRECTION(1);
	switch (*turnSize) {
	case 1:
	case 3:
		targetAngle = 83;
		__SET_SERVO_TURN(&htim1, 50);
		__SET_MOTOR_DUTY(&htim8, 2000, 3500);
		break;
	case 2:
	case 4:
	default:
//		targetAngle = 85;
		targetAngle = 83;
		__SET_SERVO_TURN(&htim1, 52);
//		__SET_MOTOR_DUTY(&htim8, 2500, 2916);
		__SET_MOTOR_DUTY(&htim8, 3000, 3500);
		break;
	}
	RobotTurnFastest(&targetAngle);

}

void FASTESTPATH_TURN_LEFT_90X_RETURN(uint8_t * turnSize) {
	__SET_MOTOR_DIRECTION(1);
		switch (*turnSize) {
		case 1:
			targetAngle = 83;
			__SET_SERVO_TURN(&htim1, 50);
			__SET_MOTOR_DUTY(&htim8, 2000, 3500);
			break;
		case 3:
			targetAngle = 85;
			__SET_SERVO_TURN(&htim1, 50);
			__SET_MOTOR_DUTY(&htim8, 2000, 3500);
			break;
		case 2:
		case 4:
		default:
	//		targetAngle = 85;
			targetAngle = 79;
			__SET_SERVO_TURN(&htim1, 52);
	//		__SET_MOTOR_DUTY(&htim8, 2500, 2916);
			__SET_MOTOR_DUTY(&htim8, 3000, 3500);
			break;
		}
		RobotTurnFastest(&targetAngle);
}

//void FASTESTPATH_TURN_RIGHT_90X(const uint8_t MODE) { //x4
//	__SET_MOTOR_DIRECTION(1);
//	switch (MODE) {
//	case 1:
//		break;
//	case 2:
//		break;
//	case 3:
//	default:
//		targetAngle = -85.5;
//		__SET_SERVO_TURN(&htim1, 98);
//		__SET_MOTOR_DUTY(&htim8, 2700, 2500);
//		break;
//	}
//	RobotTurnFastest(&targetAngle);
//}

void FASTESTPATH_TURN_RIGHT_180X(uint8_t * turnSize) {
	__SET_MOTOR_DIRECTION(1);
	switch (*turnSize) {
	case 1:
	case 3:
		targetAngle = -172;
		__SET_SERVO_TURN(&htim1, 115);
		__SET_MOTOR_DUTY(&htim8, 3500, 2000);
		break;
	case 2:
	case 4:
	default:
//		targetAngle = -176;
		targetAngle = -170;
		__SET_SERVO_TURN(&htim1, 98);
//		__SET_MOTOR_DUTY(&htim8, 2700, 2500);
		__SET_MOTOR_DUTY(&htim8, 3500, 3240);
		break;
	}
	RobotTurnFastest(&targetAngle);
}
void RobotMoveUntilIROvershoot() {
  obsDist_IR = 0;
  obsDist_IR2 = 0;
  angleNow = 0; gyroZ = 0;
    last_curTask_tick = HAL_GetTick();

    do {
      __ADC_Read_Dist(&hadc1, dataPoint, IR_data_raw_acc, obsDist_IR, obsTick_IR);
      if (obsDist_IR > 20 || obsDist_IR < 0)
        {
        __ADC_Read_Dist(&hadc2, dataPoint2, IR_data_raw_acc2, obsDist_IR2, obsTick_IR2);
        if(obsDist_IR2 > 20 || obsDist_IR2<0 )
          {break;
          }
        }
      __ADC_Read_Dist(&hadc2, dataPoint2, IR_data_raw_acc2, obsDist_IR2, obsTick_IR2);
      if(obsDist_IR2 > 20 || obsDist_IR2 <0)
      {
        if(obsDist_IR > 20 || obsDist_IR <0 )break;
      }
      if (HAL_GetTick() - last_curTask_tick >= 5) {
        StraightLineMove(SPEED_MODE_2);
        last_curTask_tick = HAL_GetTick();
      }
    } while (1);

//    motorStop();
    __SET_MOTOR_DUTY(&htim8, 0, 0);
}

void RobotMoveUntilIRHit() {
	obsDist_IR = 1000;
	angleNow = 0; gyroZ = 0;
	  last_curTask_tick = HAL_GetTick();
	  do {
		  __ADC_Read_Dist(&hadc1, dataPoint, IR_data_raw_acc, obsDist_IR, obsTick_IR);
	      __ADC_Read_Dist(&hadc2, dataPoint2, IR_data_raw_acc2, obsDist_IR2, obsTick_IR2);
		  if((obsDist_IR < 25 && obsDist_IR > 0)|| (obsDist_IR2 <25 && obsDist_IR2 >0)) break;

		  if (HAL_GetTick() - last_curTask_tick >= 5) {
			  StraightLineMove(SPEED_MODE_2);
			  last_curTask_tick = HAL_GetTick();
		  }
	  } while (1);
	  __SET_MOTOR_DUTY(&htim8, 0, 0);
}
/* USER CODE END 4 */

/* USER CODE BEGIN Header_runOledTask */
/**
  * @brief  Function implementing the oledTask thread.
  * @param  argument: Not used
  * @retval None
  */
/* USER CODE END Header_runOledTask */
float angleTemp;
void runOledTask(void *argument)
{
	//RobotTurn(90);
	uint8_t message1[20], message2[20], message3[20];
  /* USER CODE BEGIN 5 */
  /* Infinite loop */
  for(;;)
  {
//	snprintf(ch, sizeof(ch), "%-3d%%", (int)batteryVal);
//	OLED_ShowString(0, 0, (char *) ch);
//	angleTemp = angleNow / GRYO_SENSITIVITY_SCALE_FACTOR_2000DPS * 0.01;
//	snprintf(ch, sizeof(ch), "angle:%-4d", (int) angleTemp);
//	OLED_ShowString(0, 8, (char *) ch);
//	OLED_ShowString(0, 12, (char *) rxMsg);
//	OLED_ShowString(0, 24, (char *) aRxBuffer);
//	snprintf(ch, sizeof(ch), "l:%-3d|r:%-3d", (int)angle_left, (int)angle_right);
//	snprintf(ch, sizeof(ch), "ir:%-5d", (int)obsDist_IR);
//	OLED_ShowString(0, 12, (char *) ch);
//	snprintf(ch, sizeof(ch), "angle:%-7d", (int)angleNow);
//	OLED_ShowString(0, 24, (char *) ch);
//	snprintf(ch, sizeof(ch), "obs_a:%-4d|x:%-4d", (int)obs_a, (int) x);
//	OLED_ShowString(0, 24, (char *) ch);
//	snprintf(ch, sizeof(ch), "US:%-4d|IR:%-4d", (int)obsDist_US, (int)obsDist_IR);
//	OLED_ShowString(0, 48, (char *) ch);
//	OLED_Refresh_Gram();
	//HAL_UART_Transmit(&huart3, (uint8_t *) "(", 7, 0xFFFF);
	sprintf(message1, "(%d)", Distance);
	HAL_UART_Transmit(&huart3, (uint8_t *) message1, 7, 0xFFFF);
	//HAL_UART_Transmit(&huart3, (uint8_t *) ")", 7, 0xFFFF);

	osDelay(1000);
  }
  /* USER CODE END 5 */
}

/* USER CODE BEGIN Header_runCmdTask */
/**
* @brief Function implementing the runCommandTask thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_runCmdTask */
void runCmdTask(void *argument)
{
  /* USER CODE BEGIN runCmdTask */
  /* Infinite loop */
  for(;;)
  {
 	  switch(curCmd.index) {
//	  	 case 0: // STOP handled in UART IRQ directly
//	  	  	  break;
	  	 case 1: //FW
	  	 case 2: //BW
	  		curTask = curCmd.index == 1 ? TASK_MOVE : TASK_MOVE_BACKWARD;
	  		__PEND_CURCMD(curCmd);
	  		 break;
	  	case 3: //FL manual

		case 4: //FR manual
		case 5: //BL manual
		case 6: //BR manual
			__SET_CMD_CONFIG(cfgs[curCmd.index], &htim8, &htim1, targetAngle);
			if (__COMMAND_QUEUE_IS_EMPTY(cQueue)) {
				__CLEAR_CURCMD(curCmd);
				__ACK_TASK_DONE(&huart3, rxMsg);

			} else __READ_COMMAND(cQueue, curCmd, rxMsg);
			__PEND_CURCMD(curCmd);
			 break;
	  	 case 7: // FL
	  		 curTask = TASK_FL;
	  		__PEND_CURCMD(curCmd);
	  		 break;
	  	 case 8: // FR
	  		curTask = TASK_FR;
	  		__PEND_CURCMD(curCmd);
	  		break;
	  	 case 9: // BL
	  		curTask = TASK_BL;
	  		__PEND_CURCMD(curCmd);
	  		break;
	  	 case 10: //BR
	  		curTask = TASK_BR;
	  		__PEND_CURCMD(curCmd);
	  		break;
	  	 case 11: // TL
	  	 case 12: // TR
	  		 __SET_SERVO_TURN_MAX(&htim1, curCmd.index - 11 ? 1 : 0);
	  		__CLEAR_CURCMD(curCmd);
			__ACK_TASK_DONE(&huart3, rxMsg);
	  		 break;
	  	 case 13: // debug IR sensor
	  		 curTask = TASK_ADC;
	  		 break;
	  	 case 14: // DT move until specified distance from obstacle
	  		  curTask = TASK_MOVE_OBS;
	  		  __PEND_CURCMD(curCmd);
	  		 break;
	  	 case 15:
	  		 curTask = TASK_BUZZER;
	  		__PEND_CURCMD(curCmd);
	  		break;
	  	 case 16:
	  		 curTask = TASK_FASTESTPATH;
	  		__PEND_CURCMD(curCmd);
	  		 break;
	  	 case 17:
	  		 curTask = TASK_FASTESTPATH_V2;
	  		__PEND_CURCMD(curCmd);
	  		 break;
	  	 case 88: // Axxx, rotate left by xxx degree
	  	 case 89: // Cxxx, rotate right by xxx degree
	  		 __SET_SERVO_TURN_MAX(&htim1, curCmd.index - 88);
	  		 __SET_MOTOR_DIRECTION(DIR_FORWARD);
	  		 if (curCmd.index == 88) {
	  			 targetAngle = curCmd.val;
	  			 __SET_MOTOR_DUTY(&htim8, 800, 1200);
	  		 } else {
	  			targetAngle = -curCmd.val;
	  			 __SET_MOTOR_DUTY(&htim8, 1200, 800);
	  		 }
	  		__PEND_CURCMD(curCmd);
	  		 RobotTurn(&targetAngle);
	  		 break;
	  	 case 99:
	  		 break;
	  	 case 100:
	  		 break;
	  	 default:
	  //		 curCmd.index = 99;
	  		 break;
	  	 }

	  osDelay(100);
  }
  /* USER CODE END runCmdTask */
}

/* USER CODE BEGIN Header_runADCTask */
/**
* @brief Function implementing the ADCTask thread.
* @param argument: Not used
* @retval None
* Greedy Task (can only preempted by UART IRQ or EXTI)
* When activate (curTask == TASK_ADC), function executes in 1MHz
*/
/* USER CODE END Header_runADCTask */
void runADCTask(void *argument)
{
  /* USER CODE BEGIN runADCTask */
	uint16_t dataPoint = 0; uint32_t IR_data_raw_acc = 0;
  /* Infinite loop */
  for(;;)
  {
	  if (curTask != TASK_ADC) osDelay(1000);
	  else {
//			dataPoint = 0; IR_data_raw_acc = 0; obsDist_IR = 1000;
//			last_curTask_tick = HAL_GetTick();
			__PEND_CURCMD(curCmd);
			targetDist = 40;
			RobotMoveDistObstacle_IR(&targetDist);
//			do {
//				__ADC_Read_Dist(&hadc1, dataPoint, IR_data_raw_acc, obsDist_IR, obsTick_IR);
//			  osDelay(5);
//			} while (1);
//
//		  __ON_TASK_END(&htim8, prevTask, curTask);
//		  HAL_ADC_Stop(&hadc1);
		  clickOnce = 0;
		  prevTask = curTask;
		  curTask = TASK_NONE;
		if (__COMMAND_QUEUE_IS_EMPTY(cQueue)) {
			__CLEAR_CURCMD(curCmd);
			__ACK_TASK_DONE(&huart3, rxMsg);

		} else __READ_COMMAND(cQueue, curCmd, rxMsg);
	  }

  }
  /* USER CODE END runADCTask */
}

/* USER CODE BEGIN Header_runMoveDistTask */
/**
* @brief Function implementing the moveDistTask thread.
* @param argument: Not used
* @retval None
* Greedy Task (can only preempted by UART IRQ or EXTI)
*/
/* USER CODE END Header_runMoveDistTask */
void runMoveDistTask(void *argument)
{
  /* USER CODE BEGIN runMoveDistTask */
  /* Infinite loop */
  for(;;)
  {
	  if (curTask != TASK_MOVE && curTask != TASK_MOVE_BACKWARD) osDelay(1000);
	  else {
		  if (manualMode) {
			angleNow = 0; gyroZ = 0; // reset angle for PID
			PIDConfigReset(&pidTSlow);
			PIDConfigReset(&pidSlow);
			PIDConfigReset(&pidFast);

			__SET_MOTOR_DIRECTION(curTask == TASK_MOVE ? DIR_FORWARD : DIR_BACKWARD);

			  __ON_TASK_END(&htim8, prevTask, curTask);
			  clickOnce = 0;

			  __CLEAR_CURCMD(curCmd);
			__ACK_TASK_DONE(&huart3, rxMsg);

			last_curTask_tick = HAL_GetTick();
			do {
				if (!manualMode) break;
				if (HAL_GetTick() - last_curTask_tick >= 10) {
					StraightLineMove(SPEED_MODE_T);
					last_curTask_tick = HAL_GetTick();
				}
//				osDelay(5); // for video demo only, give OLED chances to update
			} while (1);

		  } else {
//			  osDelay(5000); // for video demo only
			  //htim1.Instance->CCR4 = 140; // Center wheel POS
			  targetDist = (float) curCmd.val;
			  // for target distance lesser than 15, move mode must be forced to SLOW
			  if (targetDist <= 15) moveMode = SLOW;

			  if (moveMode == SLOW) {
				  RobotMoveDist(&targetDist, curTask == TASK_MOVE ? DIR_FORWARD : DIR_BACKWARD, SPEED_MODE_1);
			  } else {
				  RobotMoveDist(&targetDist, curTask == TASK_MOVE ? DIR_FORWARD : DIR_BACKWARD, SPEED_MODE_2);
			  }

			  __ON_TASK_END(&htim8, prevTask, curTask);
				  clickOnce = 0;

				if (__COMMAND_QUEUE_IS_EMPTY(cQueue)) {
					__CLEAR_CURCMD(curCmd);
					__ACK_TASK_DONE(&huart3, rxMsg);
				} else __READ_COMMAND(cQueue, curCmd, rxMsg);
		  }




	  }
  }
  /* USER CODE END runMoveDistTask */
}

/* USER CODE BEGIN Header_runFastestPathTask */
/**
* @brief Function implementing the fastestPathTask thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_runFastestPathTask */
void runFastestPathTask(void *argument) {
    /* USER CODE BEGIN runFastestPathTask */
//	RobotMoveUntilIROvershoot();
    for(;;) {
//    	RobotMoveUntilIROvershoot();
        if (curTask != TASK_FASTESTPATH) {
            osDelay(1000);
        } else {
            // Call only the RobotMoveUntilIROvershoot function
            RobotMoveUntilIROvershoot();

            // After finishing the task, clear the task and acknowledge
            prevTask = curTask;
            curTask = TASK_NONE;
            __CLEAR_CURCMD(curCmd);
            __ACK_TASK_DONE(&huart3, rxMsg);
        }

    }
    /* USER CODE END runFastestPathTask */
}

/* USER CODE BEGIN Header_runBuzzerTask */
/**
* @brief Function implementing the buzzerTask thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_runBuzzerTask */
void runBuzzerTask(void *argument)
{
  /* USER CODE BEGIN runBuzzerTask */
  /* Infinite loop */
  for(;;)
  {
	  if (curTask != TASK_BUZZER) osDelay(1000);
	  else {
		  while (curCmd.val > 0) {
			  HAL_GPIO_WritePin(Buzzer_GPIO_Port, Buzzer_Pin, GPIO_PIN_SET);
			  osDelay(100);
			  HAL_GPIO_WritePin(Buzzer_GPIO_Port, Buzzer_Pin, GPIO_PIN_RESET);
			  osDelay(100);
			  curCmd.val--;
		  }
		  prevTask = curTask;
		  curTask = TASK_NONE;
		  clickOnce = 0;


		  if (__COMMAND_QUEUE_IS_EMPTY(cQueue)) {
				__CLEAR_CURCMD(curCmd);
				__ACK_TASK_DONE(&huart3, rxMsg);
			} else __READ_COMMAND(cQueue, curCmd, rxMsg);
	  }
  }
  /* USER CODE END runBuzzerTask */
}

/* USER CODE BEGIN Header_runFLTask */
/**
* @brief Function implementing the FLTask thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_runFLTask */
void runFLTask(void *argument)
{
  /* USER CODE BEGIN runFLTask */
  /* Infinite loop */
	uint8_t message1[20], message2[20], message3[20];

  for(;;)
  {
	  if (curTask != TASK_FL) osDelay(1000);
	  else {
		  targetAngle = curCmd.val-1;
		  uint16_t leftDuty = 560;
		  uint16_t rightDuty = 2000;
		  float servoTurnVal = 53;

		              // Corrected type declaration for config
		  CmdConfig config = {leftDuty, rightDuty, servoTurnVal, targetAngle, DIR_FORWARD};

		              // Apply the configuration to the motors and steering
		  __SET_CMD_CONFIG(config, &htim8, &htim1, targetAngle);
		  RobotTurn(&targetAngle);

//		  {0, 2000, 53, 90, DIR_FORWARD}, // FL30
//		  	{2000, 0, 120, -87, DIR_FORWARD}, // FR30
//		  	{1500, 1500, 51, -87.5, DIR_BACKWARD}, // BL30
//		  	{2000, 0, 115, 90.5, DIR_BACKWARD}, // BR30
//		  osDelay(100);
//		  targetDist = 4;
//		  RobotMoveDist(&targetDist, DIR_FORWARD, SPEED_MODE_T);
		  osDelay(10);
//		  osDelay(3000); // video demo only
//		  switch(curCmd.val) {
//		  case 30: // FL30 (4x2)
//			  targetAngle = 95;
//			  __SET_CMD_CONFIG(cfgs[CONFIG_FL30], &htim8, &htim1, targetAngle);
//			  RobotTurn(&targetAngle);
//			  osDelay(100);
//			  targetDist = 4;
//			  RobotMoveDist(&targetDist, DIR_FORWARD, SPEED_MODE_T);
//			  osDelay(10);
//			  break;
//		  case 20: // FL20 (outdoor 3x1)
//			  targetDist = 4;
//			  RobotMoveDist(&targetDist, DIR_BACKWARD, SPEED_MODE_T);
//			  osDelay(10);
//			  __SET_CMD_CONFIG(cfgs[CONFIG_FL20], &htim8, &htim1, targetAngle);
//			  RobotTurn(&targetAngle);
//			  osDelay(10);
//			  targetDist = 7;
//			  RobotMoveDist(&targetDist, DIR_BACKWARD, SPEED_MODE_T);
//			  osDelay(10);
//			  break;
//		  default: // FL00 (indoor 3x1)
//			  //targetDist = 4;
//			  //RobotMoveDist(&targetDist, DIR_BACKWARD, SPEED_MODE_T);
//			  //osDelay(10);
//			  __SET_CMD_CONFIG(cfgs[CONFIG_FL00], &htim8, &htim1, targetAngle);
////			  cfgs[CONFIG_FL00].leftDuty += 100;
////			  cfgs[CONFIG_FL00].rightDuty += 100;
////			  sprintf(message2, "PWM:%d , %d", cfgs[CONFIG_FL00].leftDuty, cfgs[CONFIG_FL00].rightDuty );
////			  		OLED_ShowString(0, 30, message2);
////			  		sprintf(message3, "PWM:%d , %d", cfgs[CONFIG_FR00].leftDuty, cfgs[CONFIG_FR00].rightDuty );
////			  		OLED_ShowString(0, 50, message3);
//			  RobotTurn(&targetAngle);
//			  //Wait();
//			  osDelay(1000);
////			  targetDist = 7;
////			  RobotMoveDist(&targetDist, DIR_BACKWARD, SPEED_MODE_T);
////			  osDelay(10);
////			  targetDist = 5;
////			  RobotMoveDist(&targetDist, DIR_FORWARD, SPEED_MODE_T);
////			  osDelay(10);
//			  break;
//		  }


		  clickOnce = 0;
		  prevTask = curTask;
		  curTask = TASK_NONE;

		  if (__COMMAND_QUEUE_IS_EMPTY(cQueue)) {
				__CLEAR_CURCMD(curCmd);
				__ACK_TASK_DONE(&huart3, rxMsg);
		  } else __READ_COMMAND(cQueue, curCmd, rxMsg);
	  }
  }
  /* USER CODE END runFLTask */
}

/* USER CODE BEGIN Header_runFRTask */
/**
* @brief Function implementing the FRTask thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_runFRTask */
void runFRTask(void *argument)
{
//	float angle = 90;
//	RobotTurn(&angle);
  /* USER CODE BEGIN runFRTask */
  /* Infinite loop */
  for(;;)
  {
	  if (curTask != TASK_FR) osDelay(1000);
	  else {
//			{0, 2000, 53, 90, DIR_FORWARD}, // FL30
//			{2000, 0, 120, -87, DIR_FORWARD}, // FR30
//			{1500, 1500, 51, -87.5, DIR_BACKWARD}, // BL30
//			{2000, 0, 115, 90.5, DIR_BACKWARD}, // BR30
//		  osDelay(3000); // video demo only
		  targetAngle = curCmd.val;
		  if (targetAngle > 3){
			  targetAngle -=  3;
		  		  }
		  		  uint16_t leftDuty = 2500;
		  		  uint16_t rightDuty = 1000;
		  		  float servoTurnVal = 300;
		  		  float negatetargetAngle =  0 - targetAngle;

		  		              // Corrected type declaration for config
		  		  CmdConfig config = {leftDuty, rightDuty, servoTurnVal, negatetargetAngle, DIR_FORWARD};

		  		              // Apply the configuration to the motors and steering
		  		  __SET_CMD_CONFIG(config, &htim8, &htim1, targetAngle);
		  		  RobotTurn(&targetAngle);
//		  		  osDelay(100);
//		  		  targetDist = 4;
//		  		  RobotMoveDist(&targetDist, DIR_FORWARD, SPEED_MODE_T);
		  		  osDelay(10);


		  clickOnce = 0;
		  prevTask = curTask;
		  curTask = TASK_NONE;
		  if (__COMMAND_QUEUE_IS_EMPTY(cQueue)) {
				__CLEAR_CURCMD(curCmd);
				__ACK_TASK_DONE(&huart3, rxMsg);
		  } else __READ_COMMAND(cQueue, curCmd, rxMsg);
	  }
  }
  /* USER CODE END runFRTask */
}

/* USER CODE BEGIN Header_runBLTask */
/**
* @brief Function implementing the BLTask thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_runBLTask */
void runBLTask(void *argument)
{
  /* USER CODE BEGIN runBLTask */
  /* Infinite loop */
  for(;;)
  {
	  if (curTask != TASK_BL) osDelay(1000);
	  else {
//		  osDelay(3000); // video demo only
		  targetAngle = curCmd.val;
		  		  if (targetAngle > 2){
		  			  targetAngle -=  2;
		  		  		  }
		  		  uint16_t leftDuty = 670;
		  		  uint16_t rightDuty = 2000;
		  		  float servoTurnVal = 53;
		  		float negatetargetAngle =  0 - targetAngle;
//		  		{0, 2000, 53, 90, DIR_FORWARD}, // FL30
//		  			{2000, 0, 120, -87, DIR_FORWARD}, // FR30
//		  			{1500, 1500, 51, -87.5, DIR_BACKWARD}, // BL30
//		  			{2000, 0, 115, 90.5, DIR_BACKWARD}, // BR30

//		  		{1500, 1500, 51, -87.5, DIR_BACKWARD}, // BL30
//		  			{2000, 0, 115, 90.5, DIR_BACKWARD}, // BR30
		  		              // Corrected type declaration for config
		  		  CmdConfig config = {leftDuty, rightDuty, servoTurnVal, negatetargetAngle, DIR_BACKWARD};

		  		              // Apply the configuration to the motors and steering
		  		  __SET_CMD_CONFIG(config, &htim8, &htim1, targetAngle);
		  		  RobotTurn(&targetAngle);
//		  		  osDelay(100);
//		  		  targetDist = 4;
//		  		  RobotMoveDist(&targetDist, DIR_FORWARD, SPEED_MODE_T);
		  		  osDelay(10);


		  clickOnce = 0;
		  prevTask = curTask;
		  curTask = TASK_NONE;
		  if (__COMMAND_QUEUE_IS_EMPTY(cQueue)) {
				__CLEAR_CURCMD(curCmd);
				__ACK_TASK_DONE(&huart3, rxMsg);
		  } else __READ_COMMAND(cQueue, curCmd, rxMsg);
	  }
  }
  /* USER CODE END runBLTask */
}

/* USER CODE BEGIN Header_runBRTask */
/**
* @brief Function implementing the BRTask thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_runBRTask */
void runBRTask(void *argument)
{
  /* USER CODE BEGIN runBRTask */
  /* Infinite loop */
  for(;;)
  {
	  if (curTask != TASK_BR) osDelay(1000);
	  else {
		  //osDelay(3000); // video demo only
		  targetAngle = curCmd.val;
		  		  if (targetAngle > 2){
		  			  targetAngle -=  2;
		  		  		  }
		  		  		  uint16_t leftDuty = 2300;
		  		  		  uint16_t rightDuty = 1050;
		  		  		  float servoTurnVal = 300;
		  //		  		{1500, 1500, 51, -87.5, DIR_BACKWARD}, // BL30
		  //		  			{2000, 0, 115, 90.5, DIR_BACKWARD}, // BR30
		  		  		              // Corrected type declaration for config
		  		  		  CmdConfig config = {leftDuty, rightDuty, servoTurnVal, targetAngle, DIR_BACKWARD};

		  		  		              // Apply the configuration to the motors and steering
		  		  		  __SET_CMD_CONFIG(config, &htim8, &htim1, targetAngle);
		  		  		  RobotTurn(&targetAngle);
//		  		  		  osDelay(100);
//		  		  		  targetDist = 4;
//		  		  		  RobotMoveDist(&targetDist, DIR_FORWARD, SPEED_MODE_T);
		  		  		  osDelay(10);


		  clickOnce = 0;
		  prevTask = curTask;
		  curTask = TASK_NONE;
		  if (__COMMAND_QUEUE_IS_EMPTY(cQueue)) {
				__CLEAR_CURCMD(curCmd);
				__ACK_TASK_DONE(&huart3, rxMsg);
		  } else __READ_COMMAND(cQueue, curCmd, rxMsg);
	  }
  }
  /* USER CODE END runBRTask */
}

/* USER CODE BEGIN Header_runFastestPathTask_V2 */
/**
* @brief Function implementing the fastestPathV2 thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_runFastestPathTask_V2 */
void runFastestPathTask_V2(void *argument)
{
  /* USER CODE BEGIN runFastestPathTask_V2 */
    for(;;) {
//    	RobotMoveUntilIROvershoot();
        if (curTask != TASK_FASTESTPATH_V2) {
            osDelay(1000);
        } else {
            // Call only the RobotMoveUntilIROvershoot function
            RobotMoveUntilIRHit();

            // After finishing the task, clear the task and acknowledge
            prevTask = curTask;
            curTask = TASK_NONE;
            __CLEAR_CURCMD(curCmd);
            __ACK_TASK_DONE(&huart3, rxMsg);
        }

    }
  /* USER CODE END runFastestPathTask_V2 */
}

void HCSR04_Read(void) //Call when u want to get reading from US
{
	HAL_GPIO_WritePin(Trigger_GPIO_Port, Trigger_Pin, GPIO_PIN_SET);
	delay_us(10);
	HAL_GPIO_WritePin(Trigger_GPIO_Port, Trigger_Pin, GPIO_PIN_RESET);
	__HAL_TIM_ENABLE_IT(&htim4, TIM_IT_CC1);
}
void delay_us(uint16_t us)
{
	__HAL_TIM_SET_COUNTER(&htim4,0);  // set the counter value a 0
	while (__HAL_TIM_GET_COUNTER(&htim4) < us);  // wait for the counter to reach the us input in the parameter
}
//#define ECHO_PIN PE9
//#define ECHO_PORT PEB
void HAL_TIM_IC_CaptureCallback(TIM_HandleTypeDef *htim) {
	if (htim->Channel == HAL_TIM_ACTIVE_CHANNEL_1) {
		if (Is_First_Captured == 0) {
			IC_Val1 = HAL_TIM_ReadCapturedValue(htim, TIM_CHANNEL_1);
			Is_First_Captured = 1;
			__HAL_TIM_SET_CAPTUREPOLARITY(htim, TIM_CHANNEL_1,
					TIM_INPUTCHANNELPOLARITY_FALLING);
		} else if (Is_First_Captured == 1) {
			IC_Val2 = HAL_TIM_ReadCapturedValue(htim, TIM_CHANNEL_1);
			__HAL_TIM_SET_COUNTER(htim, 0);

			if (IC_Val2 > IC_Val1) {
				Difference = IC_Val2 - IC_Val1;
			}

			else if (IC_Val1 > IC_Val2) {
				Difference = (65535 - IC_Val1) + IC_Val2;
			}

			Distance = Difference * .0343 / 2;

			Is_First_Captured = 0;

			__HAL_TIM_SET_CAPTUREPOLARITY(htim, TIM_CHANNEL_1,
					TIM_INPUTCHANNELPOLARITY_RISING);
			__HAL_TIM_DISABLE_IT(&htim4, TIM_IT_CC1);
		}
	}
}
void sensorTask(void *argument) {
	/* USER CODE BEGIN StartUltrasonicTask */
	uint8_t usVal[20] = { 0 };
		HAL_TIM_IC_Start_IT(&htim4, TIM_CHANNEL_1);  // HC-SR04 Sensor
		/* Infinite loop */
		for (;;) {
			HCSR04_Read();
			sprintf(usVal, "Distance: %d \0", (int) Distance);
			//OLED_ShowString(0, 20, usVal);

			if (Distance <= usThreshold && usFlag == 1) {
				usFlag = 0;
				//moveCarStop();
				motorStop();
			}

			osDelay(100);
		}
		/* USER CODE END StartUltrasonicTask */

}
void setLeftPWM(uint16_t dutyCycle) {
	__HAL_TIM_SET_COMPARE(&htim8, TIM_CHANNEL_1, dutyCycle);
}

void setRightPWM(uint16_t dutyCycle) {
	__HAL_TIM_SET_COMPARE(&htim8, TIM_CHANNEL_2, dutyCycle);
}

void motorStop() {
	// ------- left motor
	HAL_GPIO_WritePin(GPIOA, BIN2_Pin, GPIO_PIN_RESET);
	HAL_GPIO_WritePin(GPIOA, BIN1_Pin, GPIO_PIN_RESET);
	// ------- right motor
	HAL_GPIO_WritePin(GPIOA, AIN2_Pin, GPIO_PIN_RESET);
	HAL_GPIO_WritePin(GPIOA, AIN1_Pin, GPIO_PIN_RESET);
	setLeftPWM(0);
	setRightPWM(0);
}

/* USER CODE BEGIN Header_runBatteryTask */
/**
* @brief Function implementing the batteryTask thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_runBatteryTask */
void runBatteryTask(void *argument)
{
  /* USER CODE BEGIN runBatteryTask */
  /* Infinite loop */
  for(;;)
  {
	HAL_ADC_Start(&hadc2);
	HAL_ADC_PollForConversion(&hadc2,20);
	batteryVal = HAL_ADC_GetValue(&hadc2) / 1421.752066 * 100;
	HAL_ADC_Stop(&hadc2);
    osDelay(30000); // check battery level every 30 seconds
  }
  /* USER CODE END runBatteryTask */
}

/* USER CODE BEGIN Header_runMoveDistObsTask */
/**
* @brief Function implementing the moveDistObsTask thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_runMoveDistObsTask */
void runMoveDistObsTask(void *argument)
{
  /* USER CODE BEGIN runMoveDistObsTask */
  /* Infinite loop */
  for(;;)
  {
	  if (curTask != TASK_MOVE_OBS) osDelay(1000);
	  else {
		  targetDist = (float) curCmd.val;
		  RobotMoveDistObstacle(&targetDist, SPEED_MODE_2);

		  __ON_TASK_END(&htim8, prevTask, curTask);
		  clickOnce = 0;

		if (__COMMAND_QUEUE_IS_EMPTY(cQueue)) {
			__CLEAR_CURCMD(curCmd);
			__ACK_TASK_DONE(&huart3, rxMsg);
		} else __READ_COMMAND(cQueue, curCmd, rxMsg);
	  }
  }
  /* USER CODE END runMoveDistObsTask */
}

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
