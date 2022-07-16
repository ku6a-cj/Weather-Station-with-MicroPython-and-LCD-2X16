import RPi.GPIO as GPIO
from gpiozero import CPUTemperature
import time
import w1thermsensor
import requests
from datetime import datetime
from datetime import date

#set today date
current_date=date.today()

#api settings
api_key = "e3c44dc8b4dda873c34a2103267ed3fe"
base_url = "http://api.openweathermap.org/data/2.5/weather?"
city_name="Warsaw"
complete_url=base_url+"appid="+api_key + "&q=" + city_name
response=requests.get(complete_url)
p=response.json()
# Define GPIO to LCD mapping
LCD_RS = 21
LCD_E  = 20
LCD_D4 = 16
LCD_D5 = 12
LCD_D6 = 7
LCD_D7 = 8
 
if p["cod"] != "404":
    y=p["main"]
    
    current_temperature=round(y["temp"] -273, 2)
    z=p["weather"]
    m=p["wind"]
    current_pressure=y["pressure"]
    current_wind_speed=m["speed"]
    weather_description= z[0]["description"]
    
    
    print(current_date)
    print("Temperature="+ str(current_temperature) + "\n description= "+ str(weather_description) + " pressure= "+ str(current_pressure))
    
else:
    print("City not found")

#sensor temp
sensor =  w1thermsensor.W1ThermSensor()

#button pin
buttonPin = 3
 
# Define some device constants
LCD_WIDTH= 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False
 
LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
 
# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005
 
def main():
  # Main program block
  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
  GPIO.setup(LCD_E, GPIO.OUT)  # E
  GPIO.setup(LCD_RS, GPIO.OUT) # RS
  GPIO.setup(LCD_D4, GPIO.OUT) # DB4
  GPIO.setup(LCD_D5, GPIO.OUT) # DB5
  GPIO.setup(LCD_D6, GPIO.OUT) # DB6
  GPIO.setup(LCD_D7, GPIO.OUT) # DB7
  GPIO.setup(buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
  
  # Initialise display
  lcd_init()
 
  i=0
  k=0
  temp = sensor.get_temperature()
  cpu = CPUTemperature()
  print(cpu.temperature)
  
  while True:
    k+=1
    if k==30: #co 30 iteracjii nasteeepuje odswiezenie pomiaru temperatury
        temp = sensor.get_temperature()
        cpu = CPUTemperature()
        k=0
        
    buttonState=GPIO.input(buttonPin)
    
   # print("i="+str(i))
    
    if buttonState==False:
        i+=1
        time.sleep(0.3)
        
    if i==1:
        lcd_string("CJ",LCD_LINE_1)
        lcd_string("Student WAT",LCD_LINE_2)
    elif i==0:
        now=datetime.now()
        lcd_string(str(now.strftime("%H:%M:%S")),LCD_LINE_1)
        lcd_string(str(current_date),LCD_LINE_2)
    elif i==3:
        lcd_string("Weather for city",LCD_LINE_1)
        lcd_string(city_name,LCD_LINE_2) 
    elif i==2:
        lcd_string("Temp CPU:" + str(cpu.temperature) + "C", LCD_LINE_1)
        lcd_string("Temp OUT:" + str(temp) + "C", LCD_LINE_2)
    elif i==4:
        lcd_string("Temp= " + str(current_temperature) + "C", LCD_LINE_1)
        lcd_string("Pressure=" + str(current_pressure) + "hPa", LCD_LINE_2)
    elif i==5:
        lcd_string(str(weather_description), LCD_LINE_1)
        lcd_string("Wind V=" + str(current_wind_speed) + "m/s", LCD_LINE_2) 
    else:
        i=0
    
        
 
def lcd_init():
    
  # Initialise display
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)
 
def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = data
  # mode = True  for character
  #        False for command
 
  GPIO.output(LCD_RS, mode) # RS
 
  # High bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x10==0x10:
    GPIO.output(LCD_D4, True)
  if bits&0x20==0x20:
    GPIO.output(LCD_D5, True)
  if bits&0x40==0x40:
    GPIO.output(LCD_D6, True)
  if bits&0x80==0x80:
    GPIO.output(LCD_D7, True)
 
  # Toggle 'Enable' pin
  lcd_toggle_enable()
 
  # Low bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x01==0x01:
    GPIO.output(LCD_D4, True)
  if bits&0x02==0x02:
    GPIO.output(LCD_D5, True)
  if bits&0x04==0x04:
    GPIO.output(LCD_D6, True)
  if bits&0x08==0x08:
    GPIO.output(LCD_D7, True)
 
  # Toggle 'Enable' pin
  lcd_toggle_enable()
 
def lcd_toggle_enable():
  # Toggle enable
  time.sleep(E_DELAY)
  GPIO.output(LCD_E, True)
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)
  time.sleep(E_DELAY)
 
def lcd_string(message,line):
  # Send string to display
 
  message = message.ljust(LCD_WIDTH," ")
 
  lcd_byte(line, LCD_CMD)
 
  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)
 
if __name__ == '__main__':
 
  try:
    main()
  except KeyboardInterrupt:
    pass
  finally:
    lcd_byte(0x01, LCD_CMD)
    lcd_string("Goodbye!",LCD_LINE_1)
    GPIO.cleanup()
    
    
    
