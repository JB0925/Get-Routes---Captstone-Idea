class MakeSingleMap {
    // This class generates one map with all of the different
    // route markers for each station.
    constructor() {
        this.createMap = this.createMap.bind(this);
    }

    async createMap() {
        // Collects all the data needed to create the map and
        // plot coordinates on it.
        let data = await axios.get('http://127.0.0.1:5000/get_routes')
        let routes = data.data;
        let {latitude, longitude} = routes[5];
        let address = routes.slice(-2)[0].address;
        let destination_coords = routes.slice(-1)[0]

        L.mapquest.key = 'eAlAg70mP9dkW2BcMRHO83nzXHGmbGqo'
    
        let map = L.mapquest.map('map', {
            center: [latitude, longitude],
            layers: L.mapquest.tileLayer('map'),
            zoom: 3
        });

        L.marker([latitude, longitude], {
            icon: L.mapquest.icons.marker(),
            draggable: false
        }).bindPopup(origin).addTo(map);

        for (let i = 0; i < destination_coords.length-1; i++) {
            let [lat, lng] = [...destination_coords[i]]
            let stop_type = routes[i].mode === 'bus' ? 'bus stop' : 'train station';
            let full_address = routes[i].mode === 'bus' ? `${routes[i].destination} ${stop_type} ${address}` :
                                                            `${routes[i].destination} ${stop_type}`;
            console.log(full_address)
            console.log(lat, lng)
            L.mapquest.directions().route({
                start: [latitude, longitude],
                end: routes[i].mode === 'bus' ? full_address : [lat, lng],
                options: {
                    timeOverage: 25,
                    maxRoutes: 1,
                }
            });
        }

        map.addControl(L.mapquest.control());
    }
}

mm = new MakeSingleMap()
mm.createMap()