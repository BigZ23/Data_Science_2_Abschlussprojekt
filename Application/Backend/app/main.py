from fastapi import FastAPI
from starlette.responses import RedirectResponse
from fastai.vision.all import *
import requests
import os

#Creation of the FastApi Application
app = FastAPI()

@app.get('/')
def main():
    return RedirectResponse(url='/docs/')

#simple api prediction endpoint
@app.get('/predict/')
def prediction (coordinates, zoom: int):
    #google staticmap api parameter
    url = 'https://maps.googleapis.com/maps/api/staticmap?'
    api_key = 'test'
    size = '500x500'
    maptype = 'satellite'
    #convert coordinates to image of area
    image = requests.get(url + 'center=' + coordinates + '&zoom=' + zoom + '&size=' + size + '&maptype=' + maptype + '&key=' + api_key)
    #load the model
    learner = load_learner(os.path.dirname(os.path.dirname(os.path.dirname(__file__))) + os.sep + 'Model' + os.sep + 'model.plk')
    #generate prediction on the provided image
    prediction = learner.predict(image)
    return prediction

@app.on_event('startup')
async def startup_event():
    print('Anwendung gestartet')

@app.on_event('shutdown')
async def shutdown_event():
    print('Anwendung gestoppt')