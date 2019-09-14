## This Source is M5StickV MaixPy
import network, socket, time, sensor, image,lcd
from Maix import GPIO
from fpioa_manager import fm, board_info
from machine import UART
import KPU as kpu

lcd.init()
lcd.rotation(2) #Rotate the lcd 180deg

try:
    img = image.Image("boot.jpeg")
    lcd.display(img)
except:
    lcd.draw_string(lcd.width()//2-100,lcd.height()//2-4, "Error: Cannot find start.jpg", lcd.WHITE, lcd.RED)
time.sleep(1)

from Maix import I2S, GPIO
import audio
from Maix import GPIO
from fpioa_manager import *

fm.register(board_info.SPK_SD, fm.fpioa.GPIO0)
spk_sd=GPIO(GPIO.GPIO0, GPIO.OUT)
spk_sd.value(1) #Enable the SPK output

fm.register(board_info.SPK_DIN,fm.fpioa.I2S0_OUT_D1)
fm.register(board_info.SPK_BCLK,fm.fpioa.I2S0_SCLK)
fm.register(board_info.SPK_LRCLK,fm.fpioa.I2S0_WS)

wav_dev = I2S(I2S.DEVICE_0)

try:
    player = audio.Audio(path = "ding.wav")
    player.volume(100)
    wav_info = player.play_process(wav_dev)
    wav_dev.channel_config(wav_dev.CHANNEL_1, I2S.TRANSMITTER,resolution = I2S.RESOLUTION_16_BIT, align_mode = I2S.STANDARD_MODE)
    wav_dev.set_sample_rate(wav_info[1])
    while True:
        ret = player.play()
        if ret == None:
            break
        elif ret==0:
            break
    player.finish()
except:
    pass


task = kpu.load(0x300000) # Load Model File from Flash
anchor = (1.889, 2.5245, 2.9465, 3.94056, 3.99987, 5.3658, 5.155437, 6.92275, 6.718375, 9.01025)
# Anchor data is for bbox, extracted from the training sets.
kpu.init_yolo2(task, 0.5, 0.3, 5, anchor)


#M5StickV Camera Start
clock = time.clock()
lcd.init()
lcd.rotation(2) #Rotate the lcd 180deg
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.run(1)
sensor.skip_frames(time = 2000)
#M5StickV GPIO_UART
fm.register(35, fm.fpioa.UART2_TX, force=True)
fm.register(34, fm.fpioa.UART2_RX, force=True)
uart_Port = UART(UART.UART2, 115200,8,0,0, timeout=1000, read_buf_len= 4096)
#M5StickV ButtonA
but_a=GPIO(GPIO.GPIO1, GPIO.IN, GPIO.PULL_UP)

shooting_img = image.Image("shoot.jpeg")
cnt=0

while True:
    clock.tick()
    img = sensor.snapshot()
    lcd.display(img)
#   IF Button A Push Then Image Send UART
    #if but_a.value() == 0:

    img = sensor.snapshot() # Take an image from sensor
    img2 = img
    bbox = kpu.run_yolo2(task, img) # Run the detection routine
    if bbox:
        for i in bbox:
            #print(i)
            img.draw_rectangle(i.rect())
            cnt=cnt+1
            print(cnt)
            if cnt > 10:
                img_buf = img.compress(quality=70)
                img_size1 = (img.size()& 0xFF0000)>>16
                img_size2 = (img.size()& 0x00FF00)>>8
                img_size3 = (img.size()& 0x0000FF)>>0
                data_packet = bytearray([0xFF,0xD8,0xEA,0x01,img_size1,img_size2,img_size3,0x00,0x00,0x00])
                uart_Port.write(data_packet)
                uart_Port.write(img_buf)

                lcd.display(shooting_img)
                try:
                    player = audio.Audio(path = "shoot.wav")
                    player.volume(100)
                    wav_info = player.play_process(wav_dev)
                    wav_dev.channel_config(wav_dev.CHANNEL_1, I2S.TRANSMITTER,resolution = I2S.RESOLUTION_16_BIT, align_mode = I2S.STANDARD_MODE)
                    wav_dev.set_sample_rate(wav_info[1])
                    while True:
                        ret = player.play()
                        if ret == None:
                            break
                        elif ret==0:
                            break
                    player.finish()
                except:
                    pass
                img.save("get_face.jpg")

                time.sleep(1.0)
                cnt=0



#   Send UART End
uart_Port.deinit()
del uart_Port
print("finish")
