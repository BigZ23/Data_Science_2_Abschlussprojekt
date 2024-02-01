# DataScience2

## Quick Start (Windows):
Download model file from https://drive.google.com/file/d/1KzhK78cQcRkj5Fay-PBw5Uw6Kw9KGhvO/view?usp=sharing and place it in `/Model/`

To launch the program on a Windows operating system, simply run the `start_program.bat`. Ensure that Python 3 is installed. The program will automatically install all required dependencies and launch both the HTML and backend servers.

## Manual Setup (Windows/Linux):

### 1. Download Modelfile:
Download model file from https://drive.google.com/file/d/1KzhK78cQcRkj5Fay-PBw5Uw6Kw9KGhvO/view?usp=sharing and place it in `/Model/`

### 2. Install Requirements:

Navigate to `/Application/Backend/` and open the console. Run the following command:

```bash
pip install -r Application/Backend/requirements.txt
```

### 3. Start the Backend Server:
Navigate to `/Application/Backend/app/` and open the console. Run:
```bash
uvicorn main:app
```
_or alternatively:_ 
```bash
python3 -m uvicorn main:app
```
### 4. Start the HTML Server:
Navigate to `/Application/` and open the console. Run:
```bash
python3 -m http.server -b 127.0.0.1 8080
```

### 5. Open the Locally Hosted Website:
Open your preferred browser and go to http://127.0.0.1:8080/.


## File Descriptions:

- **`Application/`**: Directory containing the front- and backend.
   - **`Backend/`**: Directory containing the backend server.
     - **`app/`**: Directory containing the files to run the backend server.
       - **`temp/`**: Directory containing the osm, predicted and combined images.
       - **`Backend_Test.ipynb`**: Jupyter Notebook to test code later used in the main.py.
       - **`main.py`**: Main python file to run the backend.
     - **`requirements.txt`**: Text file to automatically install all the required python libraries to run the files contained in this folder. 
   - **`Frontend/`**: Directory containing the files to run the frontend.
     - **`css/`**: Directory containing all css files used in the frontend.
       - **`buttons.css`**: Css file containig the styling of the buttons used.
       - **`globals.css`**: Css file containig the rest of the styling.
     - **`js/`**: Directory containing all javascript files used in the frontend.
       - **`prediction.js`**: Javascript file defining what happens if the user wants to start a prediction.
     - **`svg/`**: Directory containing all svg files used in the frontend.
       - **`Earth-2.6s-200px.svg`**: Svg displaying a rotating earth used as a loading animation in the frontend.
     - **`index.html`**: HTML starting page where a prediction can be started.
     - **`result.html`**: HTML page displaying the results when a prediction is made.
   - **`index.html`**: Dummyfile to set the correct scope of the html server.

- **`Model/`**: Directory containing everything to do with model training and data generation as well as the final model itself.
  - **`Data/`**: Directory containing the data used to train the model.
    - **`Images/`**: Directory containing all the images used to train the model.
    - **`Masks/`**: Directory containing all the data masks used to train the model.
  - **`Data_generation.ipynb`**: Jupyter Notebook containing the code to generate the dataset.
  - **`Dataset_analysis.ipynb`**: Jupyter Notebook containing a short analysis of the dataset.
  - **`Model.ipynb`**: Jupyter Notebook containing code to train and export the model.
  - **`requirements.txt`**: Text file to automatically install all the required python libraries to run the files contained in this folder.

- **`Capstone_Project_TOD2`**: Jupyter Notebook displaying the code in a presentable manner.

- **`README.md`**: Readme file for the whole project.
- **`start_program.bat`**: Script for starting up the program under Windows.
