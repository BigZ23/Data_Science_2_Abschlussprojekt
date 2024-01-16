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

async function getUnique(lat, lng){
    hex_value = ['#FFFFFF', '#2F4F4F', '#556B2F', '#A0522D', '#006400', '#8B0000', '#808000', '#483D8B',
    '#778899', '#BC8F8F', '#008B8B', '#00008B', '#32CD32', '#DAA520', '#8FB88F', '#8B008B',
    '#B03060', '#FF0000', '#FF8C00', '#FFFF00', '#0000CD', '#40E0D0', '#00FF00', '#DC143C',
    '#00BFFF', '#A020F0', '#F08080', '#ADFF2F', '#DA70D6', '#FF7F50', '#FF00FF', '#F0E68C',
    '#6495ED', '#DDA0DD', '#B0E0E6', '#90EE90', '#FF1493', '#7B68EE', '#FFDAB9']
    
    // list all landuse to later classify
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
    route = "http://127.0.0.1:8000/unique/?lat=" + lat + "&lng=" + lng;
    fetch(route, { method: 'GET',  headers: { 'Accept': 'application/json' }})
    .then(response => response.json())
    .then(response => localStorage["response"] = JSON.stringify(response))
    .then(response => console.log(localStorage["response"]))
    .then(response => {
        var unique = JSON.parse(localStorage["response"]);
        for (let x = 0; x<unique.length; x++){
            var wrapper = document.getElementById("legend");    
            var classwrapper = document.createElement("div");  
            var dot = document.createElement("span");
            var text = document.createElement("span");
            dot.className = "legend_dot";
            dot.style.backgroundColor = hex_value[unique[x]];
            text.className = "legend_text";
            text.innerHTML = dictionary_landuse[unique[x]];
            classwrapper.className = "legend_item";
            classwrapper.appendChild(dot);
            classwrapper.appendChild(text);
            wrapper.appendChild(classwrapper);
        }
        
    })
    .catch((error) => { console.log(error); localStorage.removeItem("response") })

}
