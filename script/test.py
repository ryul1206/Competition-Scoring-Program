
import RPi.GPIO as GPIO
import time

P1 = 6

GPIO.setmode(GPIO.BCM)
GPIO.setup(P1, GPIO.IN, pull_up_down=GPIO.PUD_UP) # start
def this_sensor_pushed(id): return (GPIO.input(id))


if __name__ == "__main__":
    import sys
    while True:
        print str(time.time())+"  "+str(this_sensor_pushed(P1))
        time.sleep(0.5)
    sys.exit(app.exec_())
