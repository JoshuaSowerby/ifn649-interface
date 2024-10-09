from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


import matplotlib.pyplot as plt 
import os 
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
        return f'<Data {self.box}, {self.timestamp}>'


####how to call function using jinja
def random(x=40):
    return np.random.randint(x)

app.jinja_env.globals.update(random=random)
#{{ random() }}
###


def create_plt(y,x):
    plt.plot(y,x)
    return plt
@app.route('/', methods=['POST', 'GET'])
def test():
    boxes = Data.query.order_by(Data.timestamp).all()
    time_axis=[]
    temp_axis=[]
    humid_axis=[]
    for box in boxes:
        time_axis+=[box.timestamp]
        temp_axis+=[box.temperature]
        humid_axis+=[box.humidity]
    '''#finish to create graphs... should also add something to choose timeframe...
    graphs=[]
    for box_num in boxes:
        box_num_query=...#all where box = box_num
        sensors={'temperature':[],'humidity':[],'light':[],'soil':[]}
        for instances in box_num_query:
            time+=instances.timestamp
            sensors['temperature']+=[instances.temperature]
            sensors['humidity']+=[instances.humidity]
            sensors['light']+=[instances.light]
            sensors['soil']+=[instances.soil]

        for sensor in sensors.keys():
            graph=f'static/box{box_num}_{sensor}.png'
            graphs+=[graph]

            plt.plot(time, sensors[sensor])
            #have plt.xlim here etc, have them set using global variable that we change through button press
            plt.savefig(graph)
            plt.close()
    '''
    """
    {% for box,graph in items%}
	<table><thead>
	  <tr>
		<td rowspan="6">Box {{box.box}}</td>
		<td> {{graph.temperature}} temperature {{box.temperature}} </td>
		<td> {{graph.humidity}} humidity {{box.humidity}} </td>
		<td> {{graph.soil}} soil {{box.soil}} </td>
		<td> {{graph.light}} light {{box.light}} </td>
		<td>input</td>
		<td>button</td>
	  </tr>
	  </thead>
	</table>
    {% endfor %}
    """
    
    """
    plt.plot(time_axis, temp_axis)
    #plt.plot(years, desired_growth)
    plt.title("test")
    plt.xlabel("time")
    plt.ylabel("temperature")
    #plt.legend(["Actual growth", "Desired growth"])
    plt.savefig('static/my_plot.png')
    """
    plot=create_plt(time_axis,temp_axis)
    plot.savefig(os.path.join('static','plot.png'))
    plot.close()
    #####example of how to prevent leakage
    plt.plot(time_axis,humid_axis)
    plt.close()
    ####
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
        return render_template('test.html', boxes = boxes, plot_url='static/plot.png')

@app.route('/do_something')
def do_something():
    print('something')
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)


'''
How would I make a button call some python script?
'''