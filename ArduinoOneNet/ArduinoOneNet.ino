//引入ESP8266.h头文件，建议使用教程中修改后的文件
#include "ESP8266.h"
#include "dht11.h"
#include "SoftwareSerial.h"

//修改
#include <Wire.h>
#include "MAX30105.h"

#include "heartRate.h"
//创建实例
MAX30105 particleSensor;
//配置ESP8266WIFI设置
#define SSID "123456abc"    //填写2.4GHz的WIFI名称，不要使用校园网
#define PASSWORD "12345678"//填写自己的WIFI密码
#define HOST_NAME "api.heclouds.com"  //API主机名称，连接到OneNET平 台，无需修改
#define DEVICE_ID "503094442"       //填写自己的OneNet设备ID
#define HOST_PORT (80)                //API端口，连接到OneNET平台，无需修改
String APIKey = "XFYcX1htR=YgtV08bPzIUgt==N0="; //与设备绑定的APIKey

#define INTERVAL_SENSOR 5000 //定义传感器采样及发送时间间隔


const byte RATE_SIZE = 4; //Increase this for more averaging. 4 is good.
byte rates[RATE_SIZE]; //Array of heart rates
byte rateSpot = 0;
long lastBeat = 0; //Time at which the last beat occurred
float beatsPerMinute;
int beatAvg;
int A=0;


//创建dht11示例

//dht11 DHT11;

//定义DHT11接入Arduino的管脚
//#define DHT11PIN 4

//定义ESP8266所连接的软串口
/*********************
 * 该实验需要使用软串口
 * Arduino上的软串口RX定义为D3,
 * 接ESP8266上的TX口,
 * Arduino上的软串口TX定义为D2,
 * 接ESP8266上的RX口.
 * D3和D2可以自定义,
 * 但接ESP8266时必须恰好相反
 *********************/
SoftwareSerial mySerial(3, 2);
ESP8266 wifi(mySerial);

void setup()
{
  mySerial.begin(115200); //初始化软串口
  Serial.begin(9600);     //初始化串口
  Serial.print("setup begin\r\n");

  //以下为ESP8266初始化的代码
  Serial.print("FW Version: ");
  Serial.println(wifi.getVersion().c_str());

  if (wifi.setOprToStation()) {
    Serial.print("to station ok\r\n");
  } else {
    Serial.print("to station err\r\n");
  }

  //ESP8266接入WIFI
  if (wifi.joinAP(SSID, PASSWORD)) {
    Serial.print("Join AP success\r\n");
    Serial.print("IP: ");
    Serial.println(wifi.getLocalIP().c_str());
  } else {
    Serial.print("Join AP failure\r\n");
  }

  //Serial.println("");
  //Serial.print("DHT11 LIBRARY VERSION: ");
  //Serial.println(DHT11LIB_VERSION);

  mySerial.println("AT+UART_CUR=9600,8,1,0,0");
  mySerial.begin(9600);
  Serial.println("setup end\r\n");


  //  连接传感器
  Serial.println("Initializing...");

  // Initialize sensor
  if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) //Use default I2C port, 400kHz speed
  {
    Serial.println("MAX30105 was not found. Please check wiring/power. ");
    while (1);
  }
  Serial.println("Place your index finger on the sensor with steady pressure.");

  particleSensor.setup(); //Configure sensor with default settings
  particleSensor.setPulseAmplitudeRed(0x0A); //Turn Red LED to low to indicate sensor is running
  particleSensor.setPulseAmplitudeGreen(0); //Turn off Green LED
}

unsigned long net_time1 = millis(); //数据上传服务器时间
void loop(){
  A=A+1;

    long irValue = particleSensor.getIR();

  if (checkForBeat(irValue) == true)
  {
    //We sensed a beat!
    long delta = millis() - lastBeat;
    lastBeat = millis();

    beatsPerMinute = 60 / (delta / 1000.0);

    if (beatsPerMinute < 255 && beatsPerMinute > 20)
    {
      rates[rateSpot++] = (byte)beatsPerMinute; //Store this reading in the array
      rateSpot %= RATE_SIZE; //Wrap variable

      //Take average of readings
      beatAvg = 0;
      for (byte x = 0 ; x < RATE_SIZE ; x++)
        beatAvg += rates[x];
      beatAvg /= RATE_SIZE;
    }
  }

  Serial.print("IR=");
  Serial.print(irValue);
  Serial.print(", BPM=");
  Serial.print(beatsPerMinute);
  Serial.print(", Avg BPM=");
  Serial.print(beatAvg);

  if (irValue < 50000)
    Serial.print(" No finger?");

  Serial.println();
    if (A>100){
      A = 1;
      if (wifi.createTCP(HOST_NAME, HOST_PORT)) { //建立TCP连接，如果失败，不能发送该数据
        Serial.print("create tcp ok\r\n");
        char buf[10];
        //拼接发送data字段字符串
        String jsonToSend = "{\"beatAvg\":";
        dtostrf(beatAvg, 1, 2, buf);
        jsonToSend += "\"" + String(buf) + "\"";
        jsonToSend += ",\"beat\":";
        dtostrf(beatsPerMinute, 1, 2, buf);
        jsonToSend += "\"" + String(buf) + "\"";
        jsonToSend += "}";
  
        //拼接POST请求字符串
        String postString = "POST /devices/";
        postString += DEVICE_ID;
        postString += "/datapoints?type=3 HTTP/1.1";
        postString += "\r\n";
        postString += "api-key:";
        postString += APIKey;
        postString += "\r\n";
        postString += "Host:api.heclouds.com\r\n";
        postString += "Connection:close\r\n";
        postString += "Content-Length:";
        postString += jsonToSend.length();
        postString += "\r\n";
        postString += "\r\n";
        postString += jsonToSend;
        postString += "\r\n";
        postString += "\r\n";
        postString += "\r\n";
  
        const char *postArray = postString.c_str(); //将str转化为char数组
  
        Serial.println(postArray);
        wifi.send((const uint8_t *)postArray, strlen(postArray)); //send发送命令，参数必须是这两种格式，尤其是(const uint8_t*)
        Serial.println("send success");
        if (wifi.releaseTCP()) { //释放TCP连接
          Serial.print("release tcp ok\r\n");
        } else {
          Serial.print("release tcp err\r\n");
        }
        postArray = NULL; //清空数组，等待下次传输数据
      } else {
        Serial.print("create tcp err\r\n");
      }
  
      Serial.println("");
      
    }
  
}
