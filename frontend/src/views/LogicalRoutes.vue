
<template>
  <div>
    <div class="flex flex-col items-center space-y-4">
      <!-- Dynamic Route Inputs -->
      <div class="flex justify-center w-screen" v-for="(route, index) in routes" :key="index">
        <!-- Location Input -->
        <div>
          <label :for="'location_' + index" class="mb-2 block">Locations (Start, End):</label>
          <div class="inline-block justify-items-center items-center text-left mb-4 mr-3 p-2 border border-gray-300">
            <div class="relative flex items-center">
              <div class="border-r border-gray-300 p-2">
                <img src="../assets/letter-a.png" alt="Location" />
              </div>
              <input 
                :id="'location_' + index"  
                class="p-2 text-base w-2/3 focus:outline-none" 
                v-model="route.locations" 
                placeholder="Start1, End1, Start2, End2 (comma-separated)"
              />
            </div>
          </div>
        </div>
        <!-- See Routes Button -->
        <div>
          <button
            class="mt-10 cursor-pointer text-base rounded bg-[#2363a3] text-white transition duration-300 ease m-2.5 px-4 py-2 border-none hover:bg-[#002956]"
            @click="selectRoute(index)"
            >
            See the routes
          </button>
        </div>
      </div>
    </div>

    <!-- Map Display -->
    <div ref="map" class="h-[60vh] border overflow-hidden m-[50px] rounded-[5px] border-solid border-[#ddd] m-10"></div>

    <!-- Route Details Table -->
    <div class="m-10" v-if="selectedRouteIndex !== null && selectedRouteDetails">
  <table v-if="selectedRouteDetails" class="w-full my-4 border border-gray-300 shadow-md rounded-lg overflow-hidden">
    <thead class="bg-blue-100">
      <tr class="text-left text-sm text-gray-700">
        <th class="px-4 py-2 border-b border-gray-300">Route</th>
        <th class="px-4 py-2 border-b border-gray-300">Start</th>
        <th class="px-4 py-2 border-b border-gray-300">End</th>
        <th class="px-4 py-2 border-b border-gray-300">Distance</th>
        <th class="px-4 py-2 border-b border-gray-300">Duration</th>
      </tr>
    </thead>
    <tbody>
      <tr class="text-left text-sm text-gray-600">
        <td class="px-4 py-2 border-b border-gray-300">{{ selectedRouteIndex + 1 }}:</td>
        <td class="px-4 py-2 border-b border-gray-300">{{ selectedRouteDetails.startAddress }}</td>
        <td class="px-4 py-2 border-b border-gray-300">{{ selectedRouteDetails.endAddress }}</td>
        <td class="px-4 py-2 border-b border-gray-300">{{ selectedRouteDetails.distance }}</td>
        <td class="px-4 py-2 border-b border-gray-300">{{ selectedRouteDetails.duration }}</td>
      </tr>
    </tbody>
  </table>
  <div>
    <h2>Matching Orders</h2>
    <table v-if="matchingOrders.length>0" class="min-w-full table-auto border-collapse border border-gray-300 shadow-lg">
      <thead class="bg-gray-200">
        <tr>
          <th class="border border-gray-300 px-4 py-2">T Div</th>
          <th class="border border-gray-300 px-4 py-2">Ship</th>
          <th class="border border-gray-300 px-4 py-2">Customer</th>
          <th class="border border-gray-300 px-4 py-2">AID</th>
          <th class="border border-gray-300 px-4 py-2">Pcs</th>
          <th class="border border-gray-300 px-4 py-2">Weight</th>
          <th class="border border-gray-300 px-4 py-2">Carriers</th>
          <th class="border border-gray-300 px-4 py-2">Pickup</th>
          <th class="border border-gray-300 px-4 py-2">Delivery</th>
          <th class="border border-gray-300 px-4 py-2">Origin</th>
          <th class="border border-gray-300 px-4 py-2">Destination</th>
          <th class="border border-gray-300 px-4 py-2">Stage</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="order in matchingOrders" :key="order.Ship">
          <td class="border border-gray-300 px-4 py-2">{{ order.t_div }}</td>
          <td class="border border-gray-300 px-4 py-2">{{ order.Ship }}</td>
          <td class="border border-gray-300 px-4 py-2">{{ order.Customer }}</td>
          <td class="border border-gray-300 px-4 py-2">{{ order.AID }}</td>
          <td class="border border-gray-300 px-4 py-2">{{ order.Pcs }}</td>
          <td class="border border-gray-300 px-4 py-2">{{ order.Weight }}</td>
          <td class="border border-gray-300 px-4 py-2">{{ order.Carriers }}</td>
          <td class="border border-gray-300 px-4 py-2">{{ formatDate(order.Pickup) }}</td>
          <td class="border border-gray-300 px-4 py-2">{{ order.Deliv === '0000-00-00 00:00:00' ? '0000-00-00' : formatDate(order.Deliv) }}</td>
          <td class="border border-gray-300 px-4 py-2">{{ order.Origin_State }}</td>
          <td class="border border-gray-300 px-4 py-2">{{ order.Destination_State }}</td>
          <td class="border border-gray-300 px-4 py-2">{{ order.stage }}</td>
        </tr>
      </tbody>
    </table>
    <p v-else>No matching orders found.</p>
  </div>
</div>

  </div>
</template>

<script>
import mapboxgl from 'mapbox-gl';
import MapboxDirections from '@mapbox/mapbox-gl-directions/dist/mapbox-gl-directions';
import { api } from '@/api';
import axios from 'axios';


export default {
  name: "Logicalroutes",
  data() {
    return {
      map: null,
      directions: null,
      routes: [{ locations: "" }],
      routeDetails: [],
      selectedRouteDetails: null, 
      selectedRouteIndex: null,  
      isMapReady: false,   
      matchingOrders: [],
      // order_id: this.$route.query.order_id,
      start_location : this.$route.query.start_location ,
      end_location : this.$route.query.end_location ,

      start_date: this.$route.query.start_date,
      end_date: this.$route.query.end_date,
      from_weights_value: this.$route.query.from_weights_value,
      to_weights_value: this.$route.query.to_weights_value,
      logistic_activity_value: this.$route.query.logistic_activity_value,
      shipment_value: this.$route.query.shipment_value,
      distance_origin_value: this.$route.query.distance_origin_value,
      radius_value: this.$route.query.radius_value,
    };
  },
  created() {
    // Handle initial query params if provided (for prefilled locations)
    if (this.$route.query.startLocation && this.$route.query.endLocation) {
      const startLocations = this.$route.query.startLocation.split(',');
      const endLocations = this.$route.query.endLocation.split(',');

      this.routes = startLocations.map((startLocation, index) => ({
        locations: `${startLocation.trim()}, ${endLocations[index] ? endLocations[index].trim() : ""}`,
      }));
    }
  },
  mounted() {
    this.loadMapbox();
    this.fetchOrders();
  },
  methods: {
    async fetchOrders() {
  try {
    const response = await api.get('/matching-orders', {
      params: {
        start_location :this.start_location,
        end_location :this.end_location,
        // order_id: this.order_id,
        start_date: this.start_date,
        end_date: this.end_date,
        from_weights_value: this.from_weights_value,
        to_weights_value: this.to_weights_value,
        logistic_activity_value: this.logistic_activity_value,
        shipment_value: this.shipment_value,
        distance_origin_value: this.distance_origin_value,
        radius_value: this.radius_value,
      },
    });

    if (response.data && response.data) {
      this.matchingOrders = response.data;
      this.addMarkersToMap();

    }
    console.log(this.matchingOrders);

  } catch (error) {
    if (
        error.response &&
        error.response.data &&
        error.response.data.detail &&
        error.response.data.detail.startsWith('Destination coordinates not found for order')
    ) {
        console.error('Error fetching route:', error.response.data.detail);

        // Get destination coordinates and details from the map
        const endLocation = this.directions.getDestination();
        console.log('End Location:', endLocation);
        async function reverseGeocode(lat, lng) {
    const response = await fetch(`https://api.mapbox.com/geocoding/v5/mapbox.places/${lng},${lat}.json?access_token=pk.eyJ1IjoiYmxlbmRpZ2FzaGkiLCJhIjoiY2w4eWV0ajRzMGcxNDNwcG5zbzlmN3o0aCJ9.7yV-xeDHbSiCKg-zlNjU7g`);
    const data = await response.json();
    return data.features[0]?.place_name || 'Unknown City';
}

        if (endLocation && endLocation.geometry && endLocation.properties) {
    const { coordinates } = endLocation.geometry;
    const [lng, lat] = coordinates;

    // Check for city information in properties or elsewhere
    const endCity = await reverseGeocode(lat, lng);


    console.log('Extracted City:', endCity);

    const newRow = {
        city: endCity,
        city_ascii: endCity,
        state_id: 'N/A', // Default if state information is unavailable
        state_name: 'N/A',
        lat: lat,
        lng: lng,
        source: 'Mapbox API',
        city_state: `${endCity}, N/A`,
    };

    console.log('New row to append:', newRow);

    // Append the data to the CSV
    await this.appendToCSV(newRow);
} else {
    console.error('Invalid end location format:', endLocation);
}

    }
}

},

// addMarkersToMap() {
//   if (!this.map) {
//     console.error('Map is not initialized.');
//     return;
//   }

//   if (!this.matchingOrders || !this.matchingOrders.length) {
//     console.warn('No matching orders to display on the map.');
//     return;
//   }

//   // Clear existing markers
//   if (this.map.markers) {
//     this.map.markers.forEach(marker => marker.remove());
//   }
//   this.map.markers = [];

//   // Function to fetch coordinates for a given state
//   const fetchCoordinatesForState = async (stateName) => {
//     if (!stateName) {
//       console.warn('State name is missing.');
//       return null;
//     }

//     try {
//       // Fetch coordinates using Mapbox Geocoding API
//       const response = await axios.get(
//         `https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURIComponent(stateName)}.json`,
//         {
//           params: {
//             access_token: 'pk.eyJ1IjoiYmxlbmRpZ2FzaGkiLCJhIjoiY2w4eWV0ajRzMGcxNDNwcG5zbzlmN3o0aCJ9.7yV-xeDHbSiCKg-zlNjU7g', // Replace with your Mapbox token
//             limit: 1,
//           },
//         }
//       );

//       const [lng, lat] = response.data.features[0]?.center || [];
//       if (lng !== undefined && lat !== undefined) {
//         console.log(`Geocoded ${stateName}:`, { lat, lng });
//         return `${lng},${lat}`;
//       } else {
//         console.warn(`No coordinates found for ${stateName}`);
//       }
//     } catch (error) {
//       console.error(`Error geocoding ${stateName}:`, error);
//     }

//     return null;
//   };

//   // Process each order
//   const processOrders = async () => {
//     for (const order of this.matchingOrders) {
//       // Fetch or retrieve origin and destination coordinates
//       const originCoordinates = order.origin_coordinates || await fetchCoordinatesForState(order.Origin_State);
//       const destinationCoordinates = order.destination_coordinates || await fetchCoordinatesForState(order.Destination_State);

//       // Add origin marker
//       if (originCoordinates) {
//         const [originLng, originLat] = originCoordinates.split(',');

//         const originMarker = new mapboxgl.Marker({ color: 'blue' }) // Blue for origin
//           .setLngLat([parseFloat(originLng), parseFloat(originLat)])
//           .setPopup(
//             new mapboxgl.Popup().setHTML(
//               `<strong>Origin:</strong> ${order.Origin_State || 'Unknown'}`
//             )
//           )
//           .addTo(this.map);

//         this.map.markers.push(originMarker); // Save markers for cleanup
//       }

//       // Add destination marker
//       if (destinationCoordinates) {
//         const [destLng, destLat] = destinationCoordinates.split(',');

//         const destinationMarker = new mapboxgl.Marker({ color: 'red' }) // Red for destination
//           .setLngLat([parseFloat(destLng), parseFloat(destLat)])
//           .setPopup(
//             new mapboxgl.Popup().setHTML(
//               `<strong>Destination:</strong> ${order.Destination_State || 'Unknown'}`
//             )
//           )
//           .addTo(this.map);

//         this.map.markers.push(destinationMarker); // Save markers for cleanup
//       }
//     }
//   };

//   processOrders();
// },

addMarkersToMap() {
    if (!this.isMapReady || !this.matchingOrders.length) return;

    // Define the left side of the map (e.g., left of the center longitude)
    const center = this.map.getCenter().lng;

    // Iterate over matchingOrders or routes to find left-turn points
    this.matchingOrders.forEach((order) => {
      // Assuming order contains turn coordinates: { lng, lat }
      const { turnCoordinates } = order;

      turnCoordinates.forEach((coord) => {
        if (coord.lng < center) {
          // Add marker for left turn
          new mapboxgl.Marker({ color: 'red' })
            .setLngLat([coord.lng, coord.lat])
            .addTo(this.map);
        }
      });
    });},
async appendToCSV(newRow) {
    try {
        const response = await fetch('http://localhost:8082/append-to-csv', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(newRow),
        });

        if (!response.ok) {
            throw new Error('Failed to append to CSV');
        }

        const data = await response.json();
        console.log('Row successfully appended:', data.message);
    } catch (error) {
        console.error('Error updating CSV:', error);
    }
},

// async appendToCSV(row) {
//   const csvFilePath = 'C:\\Users\\hygerta.hulaj\\Desktop\\MoveIT_refactor\\backend\\uscitiesdataset\\uscities_updated.csv';

//   try {
//     const response = await fetch(csvFilePath);
//     const csvText = await response.text();

//     // Parse existing CSV
//     const rows = Papa.parse(csvText, { header: true });
//     rows.data.push(row);

//     // Convert back to CSV
//     const updatedCSV = Papa.unparse(rows.data);

//     // Save the updated CSV (requires backend or FS API)
//     await fetch(csvFilePath, {
//       method: 'POST',
//       headers: {
//         'Content-Type': 'text/csv',
//       },
//       body: updatedCSV,
//     });

//     console.log('CSV updated successfully!');
//   } catch (err) {
//     console.error('Error updating CSV:', err);
//   }
// },

async resolveCoordinatesFromCSV(state) {
  try {
    // Replace with the actual path to your CSV
    
    const csvFilePath = 'C:\\Users\\hygerta.hulaj\\Desktop\\MoveIT_refactor\\backend\\uscitiesdataset\\uscities_updated.csv';

    // Fetch the CSV content
    const response = await fetch(csvFilePath);
    const csvText = await response.text();

    // Parse CSV (assuming you have a CSV parser like Papaparse)
    const rows = Papa.parse(csvText, { header: true }).data;

    // Find the first matching row for the state
    const row = rows.find((row) => row.state_name === state);

    if (row) {
      return {
        city: row.city,
        state: row.state_id,
        lat: row.lat,
        lng: row.lng,
        city_state: `${row.city}, ${row.state_id}`,
      };
    }
    return null;
  } catch (err) {
    console.error('Error resolving coordinates from CSV:', err);
    return null;
  }
},
    formatDate(dateStr) {
      const options = { year: 'numeric', month: 'short', day: 'numeric' };
      return new Date(dateStr).toLocaleDateString(undefined, options);
    },
    loadMapbox() {
      mapboxgl.accessToken = 'pk.eyJ1IjoiYmxlbmRpZ2FzaGkiLCJhIjoiY2w4eWV0ajRzMGcxNDNwcG5zbzlmN3o0aCJ9.7yV-xeDHbSiCKg-zlNjU7g';

      this.map = new mapboxgl.Map({
        container: this.$refs.map,
        style: 'mapbox://styles/mapbox/streets-v11',
        center: [-122.4194, 37.7749], 
        zoom: 5,
      });

      this.directions = new MapboxDirections({
        accessToken: mapboxgl.accessToken,
        unit: 'metric',
        profile: 'mapbox/driving',
      });

      this.map.addControl(this.directions, 'top-left');

      // Wait for the style to load before enabling interactions
      this.map.on('load', () => {
        this.isMapReady = true; // Mark the map as ready
        this.selectRoute(0); // Automatically click "See the routes" for the first route
      });
    },
    selectRoute(index) {
      if (!this.isMapReady) {
        console.warn('Map is not ready yet.');
        return;
      }

      this.selectedRouteIndex = index;
      this.selectedRouteDetails = null;

      const selectedRoute = this.routes[index];
      const [start, end] = selectedRoute.locations.split(',').map((loc) => loc.trim());

      if (start && end) {
        this.calculateRoute(start, end);
      }
    },
    calculateRoute(start, end) {
      if (!this.directions) {
        console.error('Directions control is not initialized.');
        return;
      }

      // Clear any existing routes
      this.clearPreviousRoutes();

      // Set the origin and destination for directions
      this.directions.setOrigin(start);
      this.directions.setDestination(end);

      // Fetch route information and handle the route display
      this.directions.on('route', (e) => {
        if (e.route && e.route.length > 0) {
          const routeData = e.route[0];
          console.log('Start Location:', this.directions.getOrigin().geometry.coordinates);
          console.log('End Location:', this.directions.getDestination().geometry.coordinates);
          // Push the route details into the array for display
          this.selectedRouteDetails = {
            startAddress: start,
            endAddress: end,
            distance: (routeData.distance / 1000).toFixed(2) + " km",
            duration: (routeData.duration / 60).toFixed(0) + " mins",
          };

          // Add the route to the map
          this.addRouteToMap(routeData,start,end);
        }
      });
    },
    addRouteToMap(routeData, start, end) {
      if (!this.isMapReady) {
        console.warn('Map is not ready yet.');
        return;
      }

      const sourceId = `route-source`;
      const layerId = `route-layer`;

      // Remove existing source and layer if they exist
      if (this.map.getSource(sourceId)) {
        this.map.removeSource(sourceId);
      }

      if (this.map.getLayer(layerId)) {
        this.map.removeLayer(layerId);
      }

      // Create a GeoJSON object for the route
      const routeGeoJSON = {
        type: 'FeatureCollection',
        features: [
          {
            type: 'Feature',
            geometry: {
              type: 'LineString',
              coordinates: routeData.geometry.coordinates,
            },
          },
        ],
      };

      // Add the route source
      this.map.addSource(sourceId, {
        type: 'geojson',
        data: routeGeoJSON,
      });

      // Add the route layer
      this.map.addLayer({
        id: layerId,
        type: 'line',
        source: sourceId,  // Use the same sourceId here to link source and layer
        layout: {
          'line-join': 'round',
          'line-cap': 'round',
        },
        paint: {
          'line-color': '#FF0000', // Use the same color for the selected route
          'line-width': 5,
        },
      });
      this.addLocationMarkers(start, end);  // Pass startLocation and endLocation here
  },

  addLocationMarkers(startAddress, endAddress) {

    const startPopup = new mapboxgl.Popup({ closeButton: false, closeOnClick: false })
      .setHTML(`<strong>Origin Location:</strong> ${startAddress}`)
      .setLngLat(this.directions.getOrigin().geometry.coordinates)
      .addTo(this.map);  

    const endPopup = new mapboxgl.Popup({ closeButton: false, closeOnClick: false })
      .setHTML(`<strong>Destination Location:</strong> ${endAddress}`)
      .setLngLat(this.directions.getDestination().geometry.coordinates)
      .addTo(this.map);  
},

  
    clearPreviousRoutes() {
      if (!this.isMapReady) {
        console.warn('Map is not ready yet.');
        return;
      }

      // Remove all previous route layers and sources
      const layers = this.map.getStyle().layers;
      layers.forEach((layer) => {
        if (layer.id.startsWith('route-layer')) {
          this.map.removeLayer(layer.id);
          this.map.removeSource(layer.id.replace('route-layer-', 'route-source-'));
        }
      });
    },
  },
};
</script>

<style scoped>
img {
  width: 20px;
  height: 20px;
}
.route-details {
  padding: 10px;
  border: 1px solid #ddd;
  margin: 10px;
  border-radius: 5px;
}
</style>