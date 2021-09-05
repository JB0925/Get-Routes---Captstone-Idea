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
    };
};


// Adds a loading spinner in case there is lag between the form
// submission and the next page load
const addLoadingSpinner = (evt) => {
    const routeDiv = evt.target.parentElement.parentElement;
    console.log(routeDiv.className)
    
    routeDiv.innerHTML = 
    `<div class="spinner-div">
        <i class="fas fa-spinner fa-spin" id="spinner"></i>
        <p>Loading...</p>
    </div>
    `

    const spinnerDiv = document.querySelector('.spinner-div');
    spinnerDiv.style.display = 'flex';
    spinnerDiv.style.width = '100%';
    spinnerDiv.style.height = '100%';
    routeDiv.style.height = '383px';
};

let loadMaps = new MapMaker();
window.addEventListener('DOMContentLoaded', loadMaps.makeMaps);
document.addEventListener('click', addLoadingSpinner);