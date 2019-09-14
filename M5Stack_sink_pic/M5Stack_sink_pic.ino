#include <M5Stack.h>
#include <WiFi.h>
#include <WiFiMulti.h>
#include <HTTPClient.h>

//WiFi系の呪文
//#define WIFI_SSID "ssid"
//#define WIFI_PASS "password"
//#define URL "http://192.168.0.10:5000/"
//WiFiMulti wifi;
//HTTPClient http;

//カウントしないカウンター
int cnt = 1;

//画像データのUART受信箱
HardwareSerial serial_ext(2);
typedef struct {
  uint32_t length;
  uint8_t *buf;
} jpeg_data_t;
jpeg_data_t jpeg_data;
static const int RX_BUF_SIZE = 20000;
static const uint8_t packet_begin[3] = { 0xFF, 0xD8, 0xEA };

void setup() {
  M5.begin();
  M5.Lcd.setRotation(3);
  M5.Lcd.setCursor(0, 30, 4);
  M5.Lcd.println("OSS_Dev_2019");

//  setup_wifi(); Wifiセットアップ

  delay(5000);

  jpeg_data.buf = (uint8_t *) malloc(sizeof(uint8_t) * RX_BUF_SIZE);
  jpeg_data.length = 0;
  if (jpeg_data.buf == NULL) {
    Serial.println("malloc jpeg buffer 1 error");
  }

  serial_ext.begin(115200, SERIAL_8N1, 21, 22);
}

void loop() {
  M5.update();

//  UART受信、画像表示
  if (serial_ext.available()) {
    uint8_t rx_buffer[10];
    int rx_size = serial_ext.readBytes(rx_buffer, 10);
    if (rx_size == 10) {   //packet receive of packet_begin
      if ((rx_buffer[0] == packet_begin[0]) && (rx_buffer[1] == packet_begin[1]) && (rx_buffer[2] == packet_begin[2])) {
        //image size receive of packet_begin
        jpeg_data.length = (uint32_t)(rx_buffer[4] << 16) | (rx_buffer[5] << 8) | rx_buffer[6];
        int rx_size = serial_ext.readBytes(jpeg_data.buf, jpeg_data.length);

        M5.Lcd.clear();
        M5.Lcd.print(jpeg_data.length);
        Serial.println(jpeg_data.length);
        M5.Lcd.drawJpg(jpeg_data.buf, jpeg_data.length);
        
        Serial.println(String(cnt));


        // POST start
//        HTTPClient http;
//        http.begin(URL);
//        http.addHeader("Content-Type", String(cnt));
//        String requestBody = "Hello World!";
//        int httpCode = http.POST(requestBody);
//      
//        Serial.printf("Response: %d", httpCode);
//        Serial.println();
//        if (httpCode == HTTP_CODE_OK) {
//          String body = http.getString();
//          Serial.print("Response Body: ");
//          Serial.println(body);
//        }
//        http.end();
        // POST end

      }
    }
  }
//  ?
  vTaskDelay(10 / portTICK_RATE_MS);
  
}

void setup_wifi() {
   // put your setup code here, to run once:
  wifi.addAP(WIFI_SSID, WIFI_PASS);
  M5.Lcd.print("WiFi Connecting is ");
   
  while (wifi.run() != WL_CONNECTED) {
    delay(500);
    M5.Lcd.print(".");
  }
  M5.Lcd.println("OK!");
  M5.Lcd.print(WiFi.localIP());
}
