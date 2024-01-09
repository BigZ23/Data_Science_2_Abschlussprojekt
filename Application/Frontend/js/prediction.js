async function getResult(coordinates){
    localStorage.setItem("lat", coordinates.lat());
    localStorage.setItem("lng", coordinates.lat());
    route = "http://127.0.0.1:8000/predict/?lat=" + coordinates.lat() + "&lng=" + coordinates.lng();
    fetch(route, { method: 'POST', headers: { 'Accept': 'application/json' }, })
        .then(response => console.log(response))
}