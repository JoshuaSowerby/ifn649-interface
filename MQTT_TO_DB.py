import sys
#sys.path.append(r'.\secrets')
import paho.mqtt.client as mqtt
#from IP import IP
boxid=0#import
from app import *

def on_connect(client, userdata, flags, rc): #func for making connection
    print("connected to MQQT")
    print(f"Connection result: {str(rc)}")
        
    client.subscribe(f"{boxid}/outputs")
def on_message(client, userdata, msg): #func for sending message
    print(msg.topic+": "+(msg.payload).decode())#str.decode adds a b for bytes, this looks better but doesnt have as much info i guess
    input=(msg.payload).decode()#box;temp;humid;soil;light;time is expected
    print(input)#debug
    if input.count(';')==5:
        input=input.split(';')
        print(input)
        #with app context, this whole file should be in interface?
        box=input[0]
        temp=input[1]
        humid=input[2]
        soil=input[3]
        light=input[4]
        new_datum = Data(box=box, temperature=temp,humidity=humid,light=light,soil=soil)
        try:
            db.session.add(new_datum)
            db.session.commit()
            print('success')
        except:
            print("error committing")

with app.app_context():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    #IP="3.27.30.149"#AWS instance IP or "localhost"
    client.connect(IP,1883,60)

    client.loop_forever()