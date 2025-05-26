#include <WiFi.h>
#include <WiFiUdp.h>

//연결할 WiFi 정보
const char* ssid = ""; //와이파이 SSID
const char* password = ""; //와이파이 비밀번호

const char* udpAddress = "";  // Raspberry Pi의 IP
const int udpPort = 5500;

WiFiUDP udp;

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nConnected to WiFi.");
  Serial.println("ESP32 IP: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // 테스트용 ESPX-TEST-CSI 라는 메시지가 포함된 패킷 전송
  const char* message = "ESPX-TEST-CSI";

  udp.beginPacket(udpAddress, udpPort);
  udp.write((const uint8_t*)message, strlen(message));
  udp.endPacket();
  delay(10); //Delay로 초당 전송할 패킷 수 조정
}

