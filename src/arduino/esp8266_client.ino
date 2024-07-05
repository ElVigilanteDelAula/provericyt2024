#include <Brain.h> 
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <ArduinoJson.h>

#define SSID "uwu"
#define PASSWORD "uwuuwuuwu"

int port = 80;

ESP8266WebServer server(port);

// Set up the brain parser, pass it the hardware serial object you want to listen on. 
Brain brain(Serial);

JsonDocument doc;
JsonArray uwu = doc.to<JsonArray>();


void setup() {
  Serial.begin(9600);
  WiFi.begin(SSID,PASSWORD);
  while(WiFi.status() != WL_CONNECTED){
    Serial.println("Connecting");
  delay(1000);
  }
  Serial.println("Connected to");
  Serial.println(WiFi.localIP());

  // GET METHOD
  server.on("/",HTTP_GET,sendData); // Setting the GET endpoint and callback which we define later
  
  server.begin();
} 

void loop() {
  server.handleClient();
  if (brain.update()) {
    uwu[0] = brain.readSignalQuality();
    uwu[1] = brain.readAttention();
    uwu[2] = brain.readMeditation();
    uwu[3] = brain.readDelta();
    uwu[4] = brain.readTheta();
    uwu[5] = brain.readLowAlpha();
    uwu[6] = brain.readHighAlpha();
    uwu[7] = brain.readLowBeta();
    uwu[8] = brain.readHighBeta();
    uwu[9] = brain.readLowGamma();
    uwu[10] = brain.readMidGamma();
  }
}

void sendData(){
  StaticJsonDocument<300> JSONData;
  // Use the object just like a javascript object or a python dictionary
  JSONData["data"] = uwu;
  // You can add more fields
  char data[300];
  // Converts the JSON object to String and stores it in data variable
  serializeJson(JSONData,data);
  // Set status code as 200, content type as application/json and send the data
  server.send(200,"application/json",data);
}
