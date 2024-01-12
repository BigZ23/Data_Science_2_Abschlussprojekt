async function getResult(coordinates) {
    //store the queried lat and lng to now be the default location of the homepage
    localStorage.setItem("lat", coordinates.lat());
    localStorage.setItem("lng", coordinates.lng());
    //generate post request with given lat and lng values
    route = "http://127.0.0.1:8000/predict/?lat=" + coordinates.lat() + "&lng=" + coordinates.lng();
    fetch(route, { method: 'POST',  headers: { 'Accept': 'application/json' }})
        .then(response => {
            if (!response.ok) {
                throw new Error("HTTP error! Status: ${response.status}");
            }
            // If the response is successful change website to display the result
            window.location = "result.html";
        })
        .catch((error) => { console.log(error);})
        
}