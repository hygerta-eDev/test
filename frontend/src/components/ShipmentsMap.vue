<!-- <template>
    <div
      class="r-panel z-0 flex-[6] h-screen ml-80"
      :class="{
        'sidebar-open': sidebarVisible,
        'ml-[90px] transition-width duration-300 ease-in-out': sidebarVisible
      }"
    >
      <div class="map w-full h-full flex-6">
        <l-map
          id="map"
          ref="map"
          v-if="showMap"
          :zoom="zoom"
          :center="center"
          :options="mapOptions"
          style="height: 80%"
          @update:center="centerUpdate"
          @update:zoom="zoomUpdate"
        >
          <l-tile-layer :url="url" />
  
          <l-polyline
            v-for="(marker, index) in markersData"
            :key="'line-' + index"
            :lat-lngs="marker.latLngs"
            :color="marker.color"
            :weight="marker.width"
          >
            <l-popup :lat-lng="marker.latLngs[0]" :content="marker.tooltip" />
          </l-polyline>
  
          <l-marker
            v-for="(item, index) in markersData"
            :key="'marker-' + index"
            :lat-lng="item.latLng"
            :content="item.tooltip"
            :state="item.Origin_State"
          >
            <l-popup :lat-lng="item.latLng">
              <div>{{ item.tooltip }}</div>
            </l-popup>
          </l-marker>
        </l-map>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, watch } from 'vue'
  import { LMap, LTileLayer, LMarker, LPolyline, LPopup, LCircle, LGeoJson } from "@vue-leaflet/vue-leaflet";

  // Define props using defineProps
  const props = defineProps({
    sidebarVisible: Boolean,
    showMap: Boolean,
    zoom: Number,
    center: Array,
    mapOptions: Object,
    url: String,
    markersData: Array,
  })
  
  // Refs for map-related properties
  const zoom = ref(props.zoom)
  const center = ref(props.center)
  const markersData = ref(props.markersData)
  
  // Update center and zoom
  const centerUpdate = (newCenter) => {
    center.value = newCenter
  }
  
  const zoomUpdate = (newZoom) => {
    zoom.value = newZoom
  }
  
  // Watchers for prop changes
  watch(() => props.zoom, (newZoom) => {
    zoom.value = newZoom
  })
  
  watch(() => props.center, (newCenter) => {
    center.value = newCenter
  })
  </script>
  
  <style scoped>
  /* Add your specific styles here */
  </style>
   -->

<template>
  <div class="r-panel flex-[6] z-0 h-screen 
     ml-80" :class="{
      'sidebar-open': sidebarVisible,
      'ml-[90px] transition-width duration-300 ease-in-out': sidebarVisible
    }">
    <div class="map w-full h-full flex-6">
      <l-map id="map" ref="map" v-if="showMap" :zoom="zoom" :center="center" :options="mapOptions" style="height: 80%"
        @update:center="centerUpdate" @update:zoom="zoomUpdate">
        <l-tile-layer :url="darkMode ? darkTileUrl : lightTileUrl" />

        <!-- Rendering Polylines -->
        <l-polyline v-for="(marker, index) in markersData" :key="'line-' + index" :lat-lngs="marker.latLngs"
          :color="marker.color" :weight="marker.width">
          <l-popup :lat-lng="marker.latLngs[0]" :content="marker.tooltip" />
        </l-polyline>

        <!-- Rendering Markers -->
        <l-marker v-for="(item, index) in markersData" :key="'marker-' + index" :lat-lng="item.latLng"
          :content="item.tooltip" :state="item.Origin_State">

          <l-popup :lat-lng="item.latLng">
            <div>{{ item.tooltip }}</div>
          </l-popup>
        </l-marker>

      </l-map>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, defineProps, defineEmits,onMounted } from 'vue';
import { LMap, LTileLayer, LMarker, LPolyline, LPopup } from "@vue-leaflet/vue-leaflet";
const darkTileUrl = "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png";
const lightTileUrl = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
const darkMode = ref(false); // Toggle based on the current theme

// Define props and emits using defineProps and defineEmits
const props = defineProps({
  sidebarVisible: Boolean,
  showMap: Boolean,
  zoom: Number,
  center: Array,
  mapOptions: Object,
  url: String,
  markersData: Array,
});

const emit = defineEmits(['update:zoom', 'update:center']);

// Local reactive state for zoom
const zoom = ref(props.zoom);
const center = ref(props.center);

// Watch for changes in props and update local state accordingly
watch(() => props.zoom, (newZoom) => {
  zoom.value = newZoom;
});

watch(() => props.center, (newCenter) => {
  center.value = newCenter;
});

// Function to handle zoom updates
const zoomUpdate = (newZoom) => {
  // Emit the zoom update to the parent component
  emit('update:zoom', newZoom);
};

// Function to handle center updates (optional, if you need to handle updates on the center)
const centerUpdate = (newCenter) => {
  emit('update:center', newCenter);
};
watch(
  () => props.markersData,
  (newMarkersData) => {
    localStorage.setItem('markersData', JSON.stringify(newMarkersData));
  },
  { deep: true } // Ensures deep watching for nested objects
);

// Load markersData from localStorage on mounted
onMounted(() => {
  const storedMarkersData = localStorage.getItem('markersData');
  if (storedMarkersData) {
    emit('update:markersData', JSON.parse(storedMarkersData));
  }
});
</script>

<style scoped>
/* Add your specific styles here */
</style>