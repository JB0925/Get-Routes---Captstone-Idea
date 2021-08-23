class MapMaker {
    // This class handles the map making for the stations.
    // It is similar to the route results.js class, but
    // has some different logic that is needed to render 
    // the map.
    constructor() {
        this.makeMaps = this.makeMaps.bind(this);
        // this.defer = this.defer.bind(this);
        this.mapArray = this.mapArray.bind(this);
    }

    mapArray() {
        // An array used to loop through and add a map to each one of
        // the station results found.
        return [
            document.querySelector('#map'),
            document.querySelector('#hybrid'),
            document.querySelector('#satellite'),
            document.querySelector('#dark'),
            document.querySelector('#light')
        ];
    }
    
    async makeMaps() {
        // Gathers necessary data and uses it to render a map
        // in browser with a point to show the location of the
        // station.
        let data = await axios.get('https://find-rides.herokuapp.com/get_stations');
        console.log(data);
        let routes = data.data
        let maps = this.mapArray();

        maps.forEach((m, idx) => {
            let [origin, latitude, longitude] = routes[idx];
            L.mapquest.key = 'eAlAg70mP9dkW2BcMRHO83nzXHGmbGqo'
    
            let map = L.mapquest.map(m.id, {
                center: [latitude, longitude],
                layers: L.mapquest.tileLayer('map'),
                zoom: 12
            });

            L.marker([latitude, longitude], {
                icon: L.mapquest.icons.marker(),
                draggable: false
            }).bindPopup(origin).addTo(map);
    
            map.addControl(L.mapquest.control());
        });
    }
    
    // defer(method) {
    //     // Recursive method used to check to see if the DOM
    //     // is ready for maps to be added. If it isn't, we 
    //     // use a setTimeout to recall the method again.
    //     if (document.querySelector('#map')) {
    //         method();
    //     } else {
    //         setTimeout(function() {defer(method)},500)
    //     }
    // };
}

let loadMaps = new MapMaker()
loadMaps.makeMaps();