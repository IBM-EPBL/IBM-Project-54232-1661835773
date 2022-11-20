import cvlib as cv
from cvlib.object_detection import draw_bbox
import cv2 , time
import numpy as np
from playsound import playsound
from flask import Flask , render_template , request,redirect
from cloudant.client import Cloudant


client = Cloudant.iam('83752889-cd2c-4ae9-8a1c-98286fc2dc8f-bluemix','FHh8N5uZqElNN8QpfHgys93ANfx_-cX_Eytq6WkULDEo', connect=True)
app=Flask(__name__)

my_database = client.create_database('my_database')


app=Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/index.html')
def home():
    return render_template("index.html")


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/afterreg', methods=['POST'])
def afterreg():
    x = [x for x in request.form.values()]
    print(x)
    data = {
        'email': x[1],  # Setting _id is optional
        'username': x[0],
        'password': x[2]
    }
    print(data)

    query = {'email': {'$eq': data['email']}}

    docs = my_database.get_query_result(query)
    print(docs)

    print(len(docs.all()))

    if (len(docs.all()) == 0):
        url = my_database.create_document(data)
        return render_template('register.html', pred="Registration Successful, please login using your details")
    else:
        return render_template('register.html', pred="You are already a member, please login using your details")


@app.route('/login')
def login():
    return render_template('Login.html')


@app.route('/afterlogin', methods=['POST'])
def afterlogin():
    user = request.form['email']
    passw = request.form['password']
   
    query = {'email': {'$eq': user}}

    docs = my_database.get_query_result(query)
    
    if (len(docs.all()) == 0):
        return render_template('Login.html', pred="The username is not found.")
    else:
        if ((user == docs[0][0]['email'] and passw == docs[0][0]['password'])):
            return redirect("/prediction")
        else:
            return render_template('Login.html', pred="Invalid email or password")


@app.route("/demo")
def demo():
    return render_template('demo.html')


@app.route('/logout')
def logout():
    return render_template('Logout.html')


@app.route("/prediction" , methods = ['GET' , 'POST'])
def predict():
    if request.method == 'POST':
        image = request.files['file']
        webcam = cv2.VideoCapture(image.filename)

        t0 = time.time()
        
        centre0 = np.zeros(2)
        isDrowning = False
        
        while True:

            status, frame = webcam.read()

            if not status:
                print("Could not read frame")
                exit()

            bbox, label, conf = cv.detect_common_objects(frame)

            if(len(bbox)>0):
                    bbox0 = bbox[0]
                    centre = [0,0]

                    centre =[(bbox0[0]+bbox0[2])/2,(bbox0[1]+bbox0[3])/2 ]

                    hmov = abs(centre[0]-centre0[0])
                    vmov = abs(centre[1]-centre0[1])

                    x=time.time()

                    threshold = 10
                    if(hmov>threshold or vmov>threshold):
                        print(x-t0, 's')
                        t0 = time.time()
                        isDrowning = False

                    else:
                        print(x-t0, 's')
                        if((time.time() - t0) > 10):
                            isDrowning = True                            
                           
                    print('bbox: ', bbox, 'centre:', centre, 'centre0:', centre0)
                    print('Is he drowning: ', isDrowning)
                    
                    centre0 = centre                   

            out = draw_bbox(frame, bbox, label, conf,isDrowning)
            cv2.imwrite('image.jpg',out)  
            
            if isDrowning:
                playsound('alarm.mp3')    
           
            cv2.imshow("Real-time object detection", out)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        webcam.release()
        cv2.destroyAllWindows()
    return render_template('prediction.html')


if __name__=="__main__":
   app.run(debug=True)
