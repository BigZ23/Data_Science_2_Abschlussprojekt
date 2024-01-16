from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from fastai.vision.all import *
import requests
import os
import math
import geopandas as gpd
import matplotlib.pyplot as plt
from PIL import Image
import osmnx as ox
import shutil
import numpy as np
import warnings
import __main__


#Creation of the FastApi Application
app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://127.0.0.1:8080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# function to get the mask given an image
def get_mask(x):
    # load the numpyfile
    numpyfile = np.load(mask_path / f"{x.stem}.npz")
    # access the data stored in the compressed file format
    data = numpyfile.f.arr_0
    # close the file as to save memory
    numpyfile.close()
    # return the extracted mask
    return data

# Function for custom metric to not include non-assigned area in metric.
# Don't punish the missclassification of originaly non-assigned area and don't reward the "correct" classification of non-assigned area
# Reasoning: non-assigned area is not a real classification, but an arifact of missing data
def dice_wo_bg(input, target):

    input = (input.argmax(dim=1) != 0).float()
    target = (target.squeeze(1) != 0).float()
    return (2.0 * (input * target).sum().float() + 1e-8) / (input.sum().float() + target.sum().float() + 1e-8)
    
__main__.get_mask = get_mask
__main__.dice_wo_bg = dice_wo_bg

@app.get('/')
def main():
    return RedirectResponse(url='/docs/')

#simple api prediction endpoint
@app.post('/predict/')
def prediction (lat, lng):
    
    coordinates = (lat, lng)

    #linux support
    import pathlib
    user_platform = platform.system()
    if user_platform == 'Windows': pathlib.PosixPath = pathlib.WindowsPath
    else: pathlib.WindowsPath = pathlib.PosixPath
        
    # Cleanup previous request
    datanames = os.listdir(os.getcwd() + os.sep + "temp")
    for dataname in datanames:
        os.remove(os.getcwd() + os.sep + "temp" + os.sep + dataname)
    
    # Code to calculate the bounds of a given center point and zoom level on google maps (modified from here: (https://stackoverflow.com/questions/12507274/how-to-get-bounds-of-a-google-static-map))
    def latLngToPoint(mapWidth, mapHeight, lat, lng):
        x = (lng + 180) * (mapWidth / 360)

        y = ((1 - math.log(math.tan(lat * math.pi / 180) + 1 / math.cos(lat * math.pi / 180)) / math.pi) / 2) * mapHeight

        return (x, y)

    def pointToLatLng(mapWidth, mapHeight, x, y):
        lng = x / mapWidth * 360 - 180
        n = math.pi - 2 * math.pi * y / mapHeight
        lat = 180 / math.pi * math.atan(0.5 * (math.exp(n) - math.exp(-n)))


        return (lat, lng)

    def getImageBounds(lat, lng, zoom):
        picHeight = 640
        picWidth = 640


        mapHeight = 256
        mapWidth = 256


        xScale = math.pow(2, zoom) / (picWidth / mapWidth)
        yScale = math.pow(2, zoom) / (picHeight / mapWidth)


        centreX, centreY = latLngToPoint(mapWidth, mapHeight, lat, lng)


        southWestX = centreX - (mapWidth / 2) / xScale
        southWestY = centreY + (mapHeight / 2) / yScale
        SWlat, SWlng = pointToLatLng(mapWidth, mapHeight, southWestX, southWestY)


        northEastX = centreX + (mapWidth / 2) / xScale
        northEastY = centreY - (mapHeight / 2) / yScale
        NElat, NElng = pointToLatLng(mapWidth, mapHeight, northEastX, northEastY)

        return [SWlat, SWlng, NElat, NElng]    


    # list all landuse to later classify
    dictionary_landuse = [
        "not_assigned",
        "commercial",
        "construction",
        "education",
        "fairground",
        "industrial",
        "residential",
        "retail",
        "institutional",
        "aquaculture",
        "allotments",
        "farmland",
        "farmyard",
        "paddy",
        "animal_keeping",
        "flowerbed",
        "forest",
        "greenhouse_horticulture",
        "meadow",
        "orchard",
        "plant_nursery",
        "vineyard",
        "basin",
        "salt_pond",
        "brownfield",
        "cemetery",
        "depot",
        "garages",
        "grass",
        "greenfield",
        "landfill",
        "military",
        "port",
        "quarry",
        "railway",
        "recreation_ground",
        "religious",
        "village_green",
        "winter_sports",
    ]

    # map each landuse to a distinct color
    landuse_mapped_hex = {
        "not_assigned": "#FFFFFF",
        "commercial": "#2F4F4F",
        "construction": "#556B2F",
        "education": "#A0522D",
        "fairground": "#006400",
        "industrial": "#8B0000",
        "residential": "#808000",
        "retail": "#483D8B",
        "institutional": "#778899",
        "aquaculture": "#BC8F8F",
        "allotments": "#008B8B",
        "farmland": "#00008B",
        "farmyard": "#32CD32",
        "paddy": "#DAA520",
        "animal_keeping": "#8FB88F",
        "flowerbed": "#8B008B",
        "forest": "#B03060",
        "greenhouse_horticulture": "#FF0000",
        "meadow": "#FF8C00",
        "orchard": "#FFFF00",
        "plant_nursery": "#0000CD",
        "vineyard": "#40E0D0",
        "basin": "#00FF00",
        "salt_pond": "#DC143C",
        "brownfield": "#00BFFF",
        "cemetery": "#A020F0",
        "depot": "#F08080",
        "garages": "#ADFF2F",
        "grass": "#DA70D6",
        "greenfield": "#FF7F50",
        "landfill": "#FF00FF",
        "military": "#F0E68C",
        "port": "#6495ED",
        "quarry": "#DDA0DD",
        "railway": "#B0E0E6",
        "recreation_ground": "#90EE90",
        "religious": "#FF1493",
        "village_green": "#7B68EE",
        "winter_sports": "#FFDAB9",
    }

    #map each label to it's value as rgb array
    landuse_mapped_rgb = {
    0: [255, 255, 255],        # "not_assigned"
    1: [47, 79, 79],           # "commercial"
    2: [85, 107, 47],          # "construction"
    3: [160, 82, 45],          # "education"
    4: [0, 100, 0],            # "fairground"
    5: [139, 0, 0],            # "industrial"
    6: [128, 128, 0],          # "residential"
    7: [72, 61, 139],          # "retail"
    8: [119, 136, 153],        # "institutional"
    9: [188, 143, 143],        # "aquaculture"
    10: [0, 139, 139],         # "allotments"
    11: [0, 0, 139],           # "farmland"
    12: [50, 205, 50],         # "farmyard"
    13: [218, 165, 32],        # "paddy"
    14: [143, 184, 143],       # "animal_keeping"
    15: [139, 0, 139],         # "flowerbed"
    16: [176, 48, 96],         # "forest"
    17: [255, 0, 0],           # "greenhouse_horticulture"
    18: [255, 140, 0],         # "meadow"
    19: [255, 255, 0],         # "orchard"
    20: [0, 0, 205],           # "plant_nursery"
    21: [64, 224, 208],        # "vineyard"
    22: [0, 255, 0],           # "basin"
    23: [220, 20, 60],         # "salt_pond"
    24: [0, 191, 255],         # "brownfield"
    25: [160, 32, 240],        # "cemetery"
    26: [240, 128, 128],       # "depot"
    27: [173, 255, 47],        # "garages"
    28: [218, 112, 214],       # "grass"
    29: [255, 127, 80],        # "greenfield"
    30: [255, 0, 255],         # "landfill"
    31: [240, 230, 140],       # "military"
    32: [100, 149, 237],       # "port"
    33: [221, 160, 221],       # "quarry"
    34: [176, 224, 230],       # "railway"
    35: [144, 238, 144],       # "recreation_ground"
    36: [255, 20, 147],        # "religious"
    37: [123, 104, 238],       # "village_green"
    38: [255, 218, 185]        # "winter_sports"
    }

    # defining all data paths
    path = Path("Data")
    image_path = path / "Images"
    mask_path = path / "Masks"

    # Function to plot the openstreetmap data and save it as a .png
    def plot_data(coordinates, zoom=16):
        warnings.filterwarnings("ignore", message="Starting a Matplotlib GUI outside of the main thread will likely fail.", category=UserWarning)
        # get the bounding box form the given coordinates and zoom level
        south, east, north, west = getImageBounds(
            float(coordinates[0]), float(coordinates[1]), zoom
        )

        # query openstreetmap for all landuse in the boundingbox
        landuse = ox.features_from_bbox(north, south, east, west, tags={"landuse": True})

        # create a plot
        fig, ax = plt.subplots(figsize=(8, 8), dpi=104)

        # for each landuse in the queried data, color the respective area in the earlier specified color
        for type in landuse["landuse"].unique():
            # filter so wrongly labeled data doesn't cause any issues (instances of this can be seen on the openstreetmap key wiki)
            if type in dictionary_landuse:
                # filter for the currently selected landuse and plot it.
                landuse.loc[landuse["landuse"] == type].plot(
                    ax=ax,
                    color=landuse_mapped_hex[type],
                    antialiased=False,
                    edgecolor="none",
                )
        plt.xlim(east, west)
        plt.ylim(south, north)
        # turn of the axis, as to not save it in the image file
        plt.axis("off")
        # save the image file under the specified path
        fig.savefig(os.getcwd() + os.sep + "temp" + os.sep + str(coordinates[0]) + "_" + str(coordinates[1]) + "_OSM_Data" + ".png", bbox_inches="tight", pad_inches=0,)
        # close the plot to reduce memory usage
        plt.close()
        # open the image again
        rgb_converted = Image.open(os.getcwd() + os.sep + "temp" + os.sep + str(coordinates[0]) + "_" + str(coordinates[1]) + "_OSM_Data" + ".png")
        # convert it from rgba to rgb as we are not using the alpha values
        rgb_converted = rgb_converted.convert("RGB")
        # save it again
        rgb_converted.save(os.getcwd() + os.sep + "temp" + os.sep + str(coordinates[0]) + "_" + str(coordinates[1]) + "_OSM_Data" + ".png")
    
    
        
    #function to plot predicted data
    def plot_prediction(coordinates, prediction):
        warnings.filterwarnings("ignore", message="Starting a Matplotlib GUI outside of the main thread will likely fail.", category=UserWarning)
        scale = 3
        data_rgb = np.zeros((len(prediction) * scale, len(prediction) * scale, 3))
        for line in range(len(prediction)):
            for column in range(len(prediction)):
                for x in range(scale):
                    for y in range(scale):
                        data_rgb[(line * scale) + x][
                            (column * scale) + y
                        ] = landuse_mapped_rgb[prediction[line][column]]
        data_rgb = data_rgb.astype(int)
        plt.subplots(figsize=(8, 8), dpi=104)
        plt.plot(antialiased=False)
        plt.imshow(data_rgb, interpolation="none")
        # turn of the axis, as to not save it in the image file
        plt.axis("off")
        # save the image file under the specified path
        plt.savefig(os.getcwd() + os.sep + "temp" + os.sep + str(coordinates[0]) + "_" + str(coordinates[1]) + "_Prediction" + ".png", bbox_inches="tight", pad_inches=0,)
        # close the plot to reduce memory usage
        plt.close()
        # open the image again
        rgb_converted = Image.open(os.getcwd() + os.sep + "temp" + os.sep + str(coordinates[0]) + "_" + str(coordinates[1]) + "_Prediction" + ".png")
        # convert it from rgba to rgb as we are not using the alpha values
        rgb_converted = rgb_converted.convert("RGB")
        # save it again
        rgb_converted.save(os.getcwd() + os.sep + "temp" + os.sep + str(coordinates[0]) + "_" + str(coordinates[1]) + "_Prediction" + ".png")
    
    # Function to plot the openstreetmap street data and save it as a .png
    def plot_streets(coordinates, zoom=16):
        warnings.filterwarnings("ignore", message="Starting a Matplotlib GUI outside of the main thread will likely fail.", category=UserWarning)
        # get the bounding box form the given coordinates and zoom level
        south, east, north, west = getImageBounds(
            float(coordinates[0]), float(coordinates[1]), zoom
        )

        # query openstreetmap for all streets in the boundingbox
        streets = ox.features_from_bbox(north, south, east, west, tags={"highway": True})

        # create a plot
        fig, ax = plt.subplots(figsize=(8, 8), dpi=104)

        streets.plot(
                ax=ax,
                color = "#000000",
                antialiased=False,
                edgecolor="none",
                )
        
        plt.xlim(east, west)
        plt.ylim(south, north)
        # turn of the axis, as to not save it in the image file
        plt.axis("off")
        # save the image file under the specified path
        fig.savefig(os.getcwd() + os.sep + "temp" + os.sep + str(coordinates[0]) + "_" + str(coordinates[1]) + "_Street_Data" + ".png", bbox_inches="tight", pad_inches=0,)
        # close the plot to reduce memory usage
        plt.close()
        # open the image again
        rgb_converted = Image.open(os.getcwd() + os.sep + "temp" + os.sep + str(coordinates[0]) + "_" + str(coordinates[1]) + "_Street_Data" + ".png")
        # convert it from rgba to rgb as we are not using the alpha values
        rgb_converted = rgb_converted.convert("RGB")
        # save it again
        rgb_converted.save(os.getcwd() + os.sep + "temp" + os.sep + str(coordinates[0]) + "_" + str(coordinates[1]) + "_Street_Data" + ".png")
        
    #function to combine osm and predicted data
    def plot_combined(coordinates, prediction):
        warnings.filterwarnings("ignore", message="Starting a Matplotlib GUI outside of the main thread will likely fail.", category=UserWarning)
        #open all images
        osm_data = Image.open(os.getcwd() + os.sep + "temp" + os.sep + str(coordinates[0]) + "_" + str(coordinates[1]) + "_OSM_Data" + ".png")
        prediction_data = Image.open(os.getcwd() + os.sep + "temp" + os.sep + str(coordinates[0]) + "_" + str(coordinates[1]) + "_Prediction" + ".png")
        street_data = Image.open(os.getcwd() + os.sep + "temp" + os.sep + str(coordinates[0]) + "_" + str(coordinates[1]) + "_Street_Data" + ".png")
        #convert them to numpy arrays for faster processing
        osm_data = np.array(osm_data)
        prediction_data = np.array(prediction_data)
        street_data = np.array(street_data)
        #create empty "image"
        combined_array = np.zeros((len(osm_data), len(osm_data), 3))
        for line in range(len(osm_data)):
            for column in range(len(osm_data)):
                #insert blank if street is present
                if np.array_equal(street_data[line][column], [0, 0, 0]):
                    combined_array[line][column] = [255, 255, 255]
                else: 
                    #only use prediction data if osm_data didn't assign a value
                    if np.array_equal(osm_data[line][column], [255, 255, 255]):
                        combined_array[line][column] = prediction_data[line][column]
                    else:
                        combined_array[line][column] = osm_data[line][column]
                        
        combined_array = combined_array.astype(int)
        plt.subplots(figsize=(8, 8), dpi=104)
        plt.plot(antialiased=False)
        plt.imshow(combined_array, interpolation="none")
        # turn of the axis, as to not save it in the image file
        plt.axis("off")
        # save the image file under the specified path
        plt.savefig(os.getcwd() + os.sep + "temp" + os.sep + str(coordinates[0]) + "_" + str(coordinates[1]) + "_Combined" + ".png", bbox_inches="tight", pad_inches=0,)
        # close the plot to reduce memory usage
        plt.close()
        # open the image again
        rgb_converted = Image.open(os.getcwd() + os.sep + "temp" + os.sep + str(coordinates[0]) + "_" + str(coordinates[1]) + "_Combined" + ".png")
        # convert it from rgba to rgb as we are not using the alpha values
        rgb_converted = rgb_converted.convert("RGB")
        # save it again
        rgb_converted.save(os.getcwd() + os.sep + "temp" + os.sep + str(coordinates[0]) + "_" + str(coordinates[1]) + "_Combined" + ".png")

    # function to donwload images from the googlestaticmap api
    def download_images(coordinates, zoom=16):
        # define the request parameters
        url = "https://maps.googleapis.com/maps/api/staticmap?"
        api_key = "AIzaSyAnTP0O9HhzodzG1DTFhk0T9tOfcYxFfvc"
        size = "640x640"
        scale = "1"
        maptype = "satellite"

        # pose get request
        response = requests.get(url + "center=" + str(coordinates[0]) + "," + str(coordinates[1]) + "&zoom=" + str(zoom) + "&size=" + size + "&maptype=" + maptype + "&scale=" + scale + "&sensor=false" + "&key=" + api_key, stream=True,)
        # stream repsonse into file and save it
        with open(os.getcwd() + os.sep + "temp" + os.sep + str(coordinates[0]) + "_" + str(coordinates[1]) + ".png", "wb",) as out_file:
            shutil.copyfileobj(response.raw, out_file)
        # delete the repsonse arifact
        del response
        
    # Code from https://stackoverflow.com/questions/15857647/how-to-export-plots-from-matplotlib-with-transparent-background to make non-assigned white area transparent
    def white_to_transparency(img):
        x = np.asarray(img.convert('RGBA')).copy()

        x[:, :, 3] = (255 * (x[:, :, :3] != 255).any(axis=2)).astype(np.uint8)

        return Image.fromarray(x)

    def add_background(coordinates):
        warnings.filterwarnings("ignore", message="Starting a Matplotlib GUI outside of the main thread will likely fail.", category=UserWarning)
        #add background to combined mask
        plt.subplots(figsize=(8, 8), dpi=104)
        plt.plot(antialiased=True)
        plt.imshow(Image.open(os.getcwd() + os.sep + "temp" + os.sep + str(coordinates[0]) + "_" + str(coordinates[1]) + ".png"), alpha=1)
        plt.imshow(white_to_transparency(Image.open(os.getcwd() + os.sep + "temp" + os.sep + str(coordinates[0]) + "_" + str(coordinates[1]) + "_Combined" + ".png")), alpha=0.8)
        plt.axis("off")
        plt.savefig(os.getcwd() + os.sep + "temp" + os.sep + str(coordinates[0]) + "_" + str(coordinates[1]) + "_Combined_BG" + ".png", bbox_inches="tight", pad_inches=0,)
        plt.close()
    
    #download the image for the given coordinates 
    download_images(coordinates, 16)
    #plot the osm data of the given coordinates
    plot_data(coordinates, 16)
    
    #load the model    
    learn = load_learner(os.path.dirname(os.path.dirname(os.path.dirname(os.getcwd()))) + os.sep + "Model" + os.sep + "model.pkl", cpu=True,)
    #generate the prediction
    prediction = learn.predict(os.getcwd() + os.sep + "temp" + os.sep + str(coordinates[0]) + "_" + str(coordinates[1]) + ".png")
    
    #extract the data out of the returned data
    data = prediction[0]
    data = np.array(data)
        
    #plot the prediciton     
    plot_prediction(coordinates, data)
    #plot the street data
    plot_streets(coordinates)
    #combine the osm and predicted data
    plot_combined(coordinates, data)
    #add a background to the combined image
    add_background(coordinates)
    
    #cache cleanup
    datanames = os.listdir(os.getcwd() + os.sep + "cache")
    for dataname in datanames:
        os.remove(os.getcwd() + os.sep + "cache" + os.sep + dataname)

@app.get('/unique/')
def get_unique(lat, lng):
    coordinates = (lat, lng)
    valid_rgb = ['255255255', '477979', '8510747', '1608245', '01000', 
                '13900', '1281280', '7261139', '119136153', '188143143', 
                '0139139', '00139', '5020550', '21816532', '143184143', 
                '13900139', '1764896', '25500', '2551400', '2552550', 
                '000205', '64224208', '002550', '2202060', '0191255', 
                '16032240', '240128128', '17325547', '218112214', 
                '25512780', '2550255', '240230140', '100149237', 
                '221160221', '176224230', '144238144', '25520147', 
                '123104238', '255218185']
    
    image = Image.open(os.getcwd() + os.sep + "temp" + os.sep + str(coordinates[0]) + "_" + str(coordinates[1]) + "_Combined" + ".png")
    image_data = np.array(image)
    image_data_reshape = image_data.reshape((-1, 3))
    unique = np.unique(image_data_reshape, axis=0)
    valid_unique = []
    for element in unique:
        value = ''.join(str(x) for x in element)
        if value in valid_rgb:
            valid_unique.append(valid_rgb.index(value))
    valid_unique.sort()
    return valid_unique

@app.on_event('startup')
async def startup_event():
    print('Anwendung gestartet')

@app.on_event('shutdown')
async def shutdown_event():
    print('Anwendung gestoppt')
