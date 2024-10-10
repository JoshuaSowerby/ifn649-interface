from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime, timedelta


import matplotlib.pyplot as plt 
import matplotlib.dates as mdates
import numpy as np 
import matplotlib 
matplotlib.use('Agg')
##the way that I am making plots is bad, but easy... remember to alwasy close plots to prevent leakage
import numpy as np

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///test.db'#3 slashes is reletive path, 4 is absolure
#app.config['SECRET_KEY']='secret'#prevent cross site request forgery
db = SQLAlchemy(app)
    


class Data(db.Model):
    #id = db.Column(db.Integer, primary_key=True)
    box =db.Column(db.Integer, nullable=False, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now, primary_key=True)
    temperature = db.Column(db.Float(200), nullable=False)
    humidity = db.Column(db.Float(200), nullable=False)
    light = db.Column(db.Float(200), nullable=False)
    soil = db.Column(db.Float(200), nullable=False)
    

    def __repr__(self):
        return f'<Box {self.box}@{self.timestamp}>'


####how to call function using jinja
def random(x=40):
    return np.random.randint(x)

app.jinja_env.globals.update(random=random)
#{{ random() }}
###



####################################
####################################
####################################
#have to use with context for this to run... this is probably bad
def generate_graphs(lower_xlim):#should change this default...
    boxes_query=Data.query.with_entities(Data.box).order_by(Data.box).distinct().all()
    boxes=[i[0] for i in boxes_query]
    graphs=[]
    for box_num in boxes:
            box_num_query=Data.query.where(Data.box==box_num).order_by(Data.timestamp).all()#...#all where box = box_num

            sensors={'temperature':[],'humidity':[],'light':[],'soil':[]}
            time=[]
            for instances in box_num_query:
                time+=[instances.timestamp]
                sensors['temperature']+=[instances.temperature]
                sensors['humidity']+=[instances.humidity]
                sensors['soil']+=[instances.soil]
                sensors['light']+=[instances.light]

            box_graphs={}
            for sensor in sensors.keys():
                plt.figure(figsize=(5, 1))#must go first

                plt.plot(time,sensors[sensor])
                #plt.xlim(),plt.xlabel(),plt.ylabel(), plt.title()#rewrite to use figure so we can change the size
                
                #how to only set lower limit for xlim
                current_xlim=plt.gca().get_xlim()
                plt.gca().set_xlim([lower_xlim, current_xlim[1]])#don't know if this is working...
                #formatting x axis
                plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H'))
                #plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))#don't use this on vely long timeframes, it takes forever

                plt_name=f'static/graphs/{box_num}_{sensor}.png'
                plt.savefig(plt_name)
                plt.close()
                box_graphs[sensor]=plt_name
            graphs+=[box_graphs]
    return graphs


'''#Todo
#use this in another file to input data...
from app import *
with app.app_context:
    new_datum = Data(box=box, temperature=temp,humidity=humid,light=light,soil=soil)
    try:
        db.session.add(new_datum)
        db.session.commit()
    except:
        print("error committing")

##change the warning value inputs to use MQTT
def publish():
    #see teensy1-output publisher.py
app.jinja_env.globals.update(publish=publish)
 '''       
####################################
####################################
####################################

####still need to finish html, only temp is done
@app.route('/update_warning/<int:box>/<string:sensor>',methods=['POST', 'GET'])
def update_warning(box,sensor):
    limit = request.form[sensor]
    print(box,sensor,limit)
    #send MQTT to topic f'{box}/{sensor}/{limit}' etc
    return redirect('/')

def create_plt(y,x):
    plt.plot(y,x)
    return plt

graph_xlim=datetime.now()-timedelta(hours=1)##this is a bad way of dealing wiht this, you should use session (cookie)
@app.route('/regen_graph/<int:xlim>')
def regen_graph(xlim):
    global graph_xlim
    if xlim == 0:       
        graph_xlim= datetime.now()-timedelta(hours=1)
    elif xlim==1:
        graph_xlim = datetime.now()-timedelta(hours=6)
    elif xlim==2:
        graph_xlim = datetime.now()-timedelta(hours=12)
    elif xlim==3:
        graph_xlim = datetime.now()-timedelta(hours=24)

    
    return redirect('/')
    

@app.route('/', methods=['POST', 'GET'])
def test():
    last_record=db.session.query(Data.box, Data.temperature, Data.humidity, Data.light, Data.soil, func.max(Data.timestamp)).group_by(Data.box).all()
    
    if request.method =='POST':
        #logic to add data
        #if any blank do not acccept?
        box = request.form['box']
        temp = request.form['temp']#id from form in html...
        humid = request.form['humid']#id from form in html...
        light = request.form['light']#id from form in html...
        soil = request.form['soil']#id from form in html...
        new_datum = Data(box=box, temperature=temp,humidity=humid,light=light,soil=soil)

        try:
            db.session.add(new_datum)
            db.session.commit()
            return redirect('/')
        except:
            return "error committing"
    else:
        boxes = Data.query.order_by(Data.timestamp).all()
        print(boxes)
        return render_template('index.html', items=zip(last_record, generate_graphs(graph_xlim)))

@app.route('/do_something')
def do_something():
    print('something')
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)


'''
How would I make a button call some python script?
'''