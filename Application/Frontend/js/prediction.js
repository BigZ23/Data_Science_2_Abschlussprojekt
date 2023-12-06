async function getResult(coordinates, zoom){
    console.log(coordinates + "," + zoom)
    route = "http://127.0.0.1:8000/predict?coordinates=" + coordinates + "&zoom=" + zoom;
    fetch(route, { method: 'GET', headers: { 'Accept': 'application/json' }, })
        .then(response => console.log(response))
}