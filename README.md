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

### 4. Start the HTML Server:
Navigate to `/Application/` and open the console. Run:
```bash
python3 -m http.server -b 127.0.0.1 8080
```

### 5. Open the Locally Hosted Website:
Open your preferred browser and go to http://127.0.0.1:8080/.
