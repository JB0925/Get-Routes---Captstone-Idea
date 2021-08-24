class MakeSingleMap {
    // This class generates one map with all of the different
    // route markers for each station.
    constructor() {
        this.createMap = this.createMap.bind(this);
    }

    async createMap() {
        // Collects all the data needed to create the map and
        // plot coordinates on it.
        let data = await axios.get('http://find-rides.herokuapp.com/get_routes')
        let routes = data.data;
        let {latitude, longitude} = routes[5];
        let destination_coords = routes.slice(-1)[0]
        
        L.mapquest.key = 'eAlAg70mP9dkW2BcMRHO83nzXHGmbGqo'
    
        let map = L.mapquest.map('map', {
            center: [latitude, longitude],
            layers: L.mapquest.tileLayer('map'),
            zoom: 6
        });

        L.marker([latitude, longitude], {
            icon: L.mapquest.icons.marker(),
            draggable: false
        }).bindPopup(origin).addTo(map);

        for (let i = 0; i < destination_coords.length; i++) {
            let [lat, lng] = [...destination_coords[i]]
            
            L.mapquest.directions().route({
                start: [latitude, longitude],
                end: [lat, lng],
                options: {
                    timeOverage: 25,
                    maxRoutes: 1,
                }
            });
        }

        map.addControl(L.mapquest.control());
    }
}

let mm = new MakeSingleMap()
mm.createMap()