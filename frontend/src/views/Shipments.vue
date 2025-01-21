<template>
    <div class="mt-5" :class="{ 'sidebar-open': sidebarVisible }">
        <div class="left-panel flex items-stretch">
            <div class="fixed h-screen overflow-y-scroll p-4 transition-width duration-300 ease-in-out  dark:bg-gray-900"
                :class="{
                    'w-72': !sidebarVisible, 'w-16 ml-5': sidebarVisible,
                }">
                <div class="flex justify-end p-2">
                    <div class="flex flex-col justify-between items-center">
                        <button @click="toggleSidebar" :class="{ 'hamburger-open': !sidebarVisible }"
                            class="w-8 h-8 bg-transparent border-none cursor-pointer p-0 z-1">
                            <span
                                class="block w-full h-0.5 bg-black dark:bg-white mb-2 transition-transform duration-300 transform"
                                :class="{ 'rotate-45 -translate-y-0': !sidebarVisible }"></span>
                            <span
                                class="block w-full h-0.5 bg-black dark:bg-white mb-2 transition-transform duration-300 transform"
                                :class="{ 'scale-y-0': !sidebarVisible }"></span>
                            <span
                                class="block w-full h-0.5 bg-black dark:bg-white mt-2 transition-transform duration-300 transform"
                                :class="{ '-rotate-45 -translate-y-5': !sidebarVisible }"></span>
                        </button>
                    </div>
                </div>
                <h1 class="text-4xl font mb-8 text-gray-700 dark:text-gray-200" v-if="!sidebarVisible">
                    Shipments
                </h1>


                <div class="panel h-full">
                    <div class="border rounded-lg p-4 mb-6 mt-4 relative w-full shadow-md shadow-gray-300 dark:shadow-gray-700 dark:bg-gray-900"
                        v-if="!sidebarVisible">
                        <label
                            class="block text-sm font-semibold absolute top-1 left-4 bg-white dark:bg-gray-900 text-gray-700 dark:text-gray-200 px-2 -mt-3">
                            Date
                        </label>
                        <div class="flex items-center mb-4">
                            <div class="w-full sm:w-2/3 mx-auto">
                                <select v-model="selectedDate" id="date-selector" @change="fetchDateRange"
                                    class="p-2 text-base border border-gray-300 dark:border-gray-600 rounded w-full bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 focus:outline-none focus:ring transition duration-300">
                                    <option value="today">Today</option>
                                    <option value="yesterday">Yesterday</option>
                                    <option value="last_7_days">Last 7 Days</option>
                                    <option value="last_30_days">Last 30 Days</option>
                                    <option value="this_month">This Month</option>
                                    <option value="last_month">Last Month</option>
                                    <option value="last_3_months">Last 3 Months</option>
                                    <option value="last_year">Last Year</option>
                                </select>
                            </div>
                        </div>
                        <div class="flex items-center mb-4">
                            <label for="start-date" class="w-1/3 mr-2 text-gray-700 dark:text-gray-200">Start
                                Date:</label>
                            <input type="date" id="start-date" v-model="startDate" @change="fetchData"
                                class="p-2 text-base border border-gray-300 dark:border-gray-600 rounded w-full bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 focus:ring transition duration-300">
                        </div>

                        <div class="flex items-center mb-4">
                            <label for="end-date" class="w-1/3 mr-2 text-gray-700 dark:text-gray-200">End Date:</label>
                            <input type="date" id="end-date" v-model="endDate" @change="fetchData"
                                class="p-2 text-base border border-gray-300 dark:border-gray-600 rounded w-full bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 focus:ring transition duration-300">
                        </div>
                    </div>

                    <div class="border rounded-lg p-4 mb-6 mt-4 relative w-full shadow-md shadow-gray-300 dark:shadow-gray-700 dark:bg-gray-900"
                        v-if="!sidebarVisible">
                        <label for="weight-filter"
                            class="block text-sm font-semibold absolute top-1 left-4 bg-white dark:bg-gray-900 text-gray-700 dark:text-gray-200 px-2 -mt-3">Weight</label>
                        <div class="flex items-center mb-4">
                            <div class="w-full sm:w-2/3 mx-auto">
                                <select id="weight-filter" v-model="weightsValue" @change="fetchWeights"
                                    class="focus:ring w-full rounded border border-gray-300 dark:border-gray-600 p-2 text-base bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 transition duration-300">
                                    <option value="">Select an option</option>
                                    <option value="-1">All</option>
                                    <option value="0-500">0-500</option>
                                    <option value="500-1000">500-1000</option>
                                    <option value="1000-2000">1000-2000</option>
                                    <option value="2000-5000">2000-5000</option>
                                    <option value="5000-10000">5000-10000</option>
                                    <option value="10000-">More than 10000</option>
                                </select>
                            </div>
                        </div>

                        <div class="flex items-center mb-4">
                            <label for="from-weights-value" class="w-1/3 mr-2 text-gray-700 dark:text-gray-200">From
                                weight:</label>
                            <input type="text" id="from-weights-value" v-model="fromWeightsValue" @change="fetchWeights"
                                class="p-2 text-base border border-gray-300 dark:border-gray-600 rounded w-full bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 focus:ring transition duration-300"
                                v-if="fromWeightsValue !== '-1'">
                        </div>

                        <div class="flex items-center mb-4">
                            <label for="to-weights-value" class="w-1/3 mr-2 text-gray-700 dark:text-gray-200">To
                                weight:</label>
                            <input type="text" id="to-weights-value" v-model="toWeightsValue" @change="fetchWeights"
                                class="p-2 text-base border border-gray-300 dark:border-gray-600 rounded w-full bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 focus:ring transition duration-300"
                                v-if="toWeightsValue !== '-1'">
                        </div>
                    </div>
                    <!-- <GeneralSelector
      type="dateRange"
      label="Date Range"
      :options="dateOptions"
      :selectedOption="selectedDate"
      :startDate="startDate"
      :endDate="endDate"
      @change="handleDateChange"
    /> -->
                    <!--     
    <GeneralSelector
  type="dateRange"
  label="Date Range"
  :options="dateOptions"
  :selectedOption="selectedDate"
  :startDate="startDate"
  :endDate="endDate"
  @change="fetchData"
  @update:startDate="startDate = $event"
  @update:endDate="endDate = $event"
/> -->

                    <!-- Weight Selector -->


                    <div class="border rounded-lg p-4 mb-6 mt-4 relative w-full shadow-md shadow-gray-300 dark:shadow-gray-700 dark:bg-gray-900"
                        v-if="!sidebarVisible">
                        <div class="flex items-center">
                            <label for="logistic-activity-value"
                                class="w-1/3 mr-2 text-gray-700 dark:text-gray-200">Logistic Activity Value:</label>
                            <select type="text" id="logistic-activity-value" v-model="logisticActivityValue"
                                class="focus:ring w-full rounded border border-gray-300 dark:border-gray-600 p-2 text-base bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 transition duration-300">
                                <option value="outbound">Outbound</option>
                                <option value="inbound">Inbound</option>
                            </select>
                        </div>
                    </div>

                    <div class="border rounded-lg p-4 mb-6 mt-4 relative w-full shadow-md shadow-gray-300 dark:shadow-gray-700 dark:bg-gray-900"
                        v-if="!sidebarVisible">
                        <div class="flex items-center">
                            <label class="w-1/3 mr-2 text-gray-700 dark:text-gray-200" for="shipment-value">Shipment
                                Value:</label>
                            <select
                                class="focus:ring w-full rounded border border-gray-300 dark:border-gray-600 p-2 text-base bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 transition duration-300"
                                type="text" id="shipment-value" v-model="shipmentValue">
                                <option value="All">All</option>
                                <option value="Van">Freight Solutions</option>
                                <option value="Air">Specialized Logistics</option>
                                <option value="SS">ShippingSource</option>
                                <option value="Int">International</option>
                            </select>
                        </div>
                    </div>
                    <div class="border rounded-lg p-4 mb-6 mt-4 relative w-full shadow-md shadow-gray-300 dark:shadow-gray-700 dark:bg-gray-900"
                        v-if="!sidebarVisible">
                        <!-- ZIP Code Section -->
                        <div class="flex items-center">
                            <label class="w-1/3 mr-2 text-gray-700 dark:text-gray-200" for="zip-code">
                                Zip Code:
                            </label>
                            <div class="relative" ref="dropdown">
                                <div class="flex items-center">
                                    <input
                                        class="focus:ring w-full rounded border border-gray-300 dark:border-gray-600 p-2 text-base bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 transition duration-300"
                                        type="text" id="zip-code" v-model="zipCode" @input="handleInput"
                                        @focus="showDropdown" autocomplete="off" @blur="hideDropdown"
                                        @mouseout="handleMouseOut" @keyup.enter="handleEnterKey" />

                                    <ul class="z-50 p-0 rounded-md border border-black dark:border-gray-600 mt-5 absolute w-full h-[140px] top-1/2 overflow-y-scroll scrollbar-thin scrollbar-thumb-gray-200 dark:scrollbar-thumb-gray-700 scrollbar-thumb-rounded-full bg-white dark:bg-gray-800"
                                        v-show="showSuggestions">
                                        <li class="dropdownoptions border border-gray-300 dark:border-gray-600 p-2 cursor-pointer hover:bg-blue-200 dark:hover:bg-blue-600 bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200"
                                            v-for="option in filteredOptions" :key="option.value"
                                            @click="toggleOption(option)">
                                            {{ option.label }}
                                        </li>
                                    </ul>
                                </div>
                            </div>
                        </div>

                        <div class="relative inline-block ml-[-12px] pt-2">
                            <button v-for="(value, index) in selectedZipcodes" :key="index"
                                class="remove_button flex items-center justify-center relative p-2 text-base bg-transparent border-none cursor-pointer z-1 text-gray-700 dark:text-gray-200"
                                @click="removeSelectedValue(value)">
                                {{ value }} ✕
                            </button>
                        </div>
                    </div>

                    <!-- Distance Origin Value Section -->
                    <div class="border rounded-lg p-4 mb-6 mt-4 relative w-full shadow-md shadow-gray-300 dark:shadow-gray-700 dark:bg-gray-900"
                        v-if="!sidebarVisible">
                        <div class="flex items-center">
                            <label class="w-1/3 mr-2 text-gray-700 dark:text-gray-200" for="distance-origin-value">
                                Distance Origin Value:
                            </label>
                            <select
                                class="focus:ring p-2 text-base border border-gray-300 dark:border-gray-600 rounded w-full transition duration-300 flex-1 bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200"
                                id="distance-origin-value" v-model="distanceOriginValue">
                                <option value="" class="text-gray-700 dark:text-gray-200">Select...</option>
                                <option value="1" class="text-gray-700 dark:text-gray-200">0-500</option>
                                <option value="2" class="text-gray-700 dark:text-gray-200">0-1000</option>
                                <option value="3" class="text-gray-700 dark:text-gray-200">0-2000</option>
                                <option value="4" class="text-gray-700 dark:text-gray-200">0-3000</option>
                                <option value="5" class="text-gray-700 dark:text-gray-200">4000+</option>
                            </select>
                        </div>
                    </div>


                    <div class="border rounded-lg p-4 mb-6 mt-4 relative w-full shadow-md shadow-gray-300 dark:shadow-gray-700 dark:bg-gray-900"
                        v-if="!sidebarVisible">
                        <div class="flex items-center">
                            <label class="w-1/3 mr-2 text-gray-700 dark:text-gray-200" for="radius-value">Radius
                                Value:</label>
                            <select
                                class="focus:ring p-2 text-base border border-gray-300 dark:border-gray-600 rounded w-full bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 transition duration-300 flex-1"
                                type="number" id="radius-value" v-model="radiusValue">
                                <option value="50">50</option>
                                <option value="100">100</option>
                                <option value="200">200</option>
                                <option value="500">300</option>
                            </select>
                        </div>
                    </div>

                    <div class="border rounded-lg p-4 mb-6 mt-4 relative w-full shadow-md shadow-gray-300 dark:shadow-gray-700 dark:bg-gray-900 "
                        v-if="!sidebarVisible">
                        <div class="flex items-center">
                            <label class="w-1/3 mr-2 text-gray-700 dark:text-gray-200" for="stage">Stage:</label>
                            <div class="relative " ref="stageDropdown">
                                <div class="flex items-center">
                                    <input
                                        class="focus:ring p-2 text-base border border-gray-300 dark:border-gray-600 rounded w-full bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 transition duration-300 flex-1"
                                        type="text" id="stage" v-model="stageInput" autocomplete="off"
                                        @focus="showStageDropdown" @input="handleStageInput"
                                        placeholder="Select stages..." />

                                    <!-- Dropdown with checkboxes -->
                                    <ul class="z-50 p-0 rounded-md border mt-5 border-gray-300 dark:border-gray-600 absolute w-full h-[140px] top-1/2 overflow-y-scroll scrollbar-thin scrollbar-thumb-gray-400 dark:scrollbar-thumb-gray-600 scrollbar-thumb-rounded-full bg-white dark:bg-gray-800 "
                                        v-show="showStageSuggestions">
                                        <li class="dropdownoptions p-2 cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-700 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 flex items-center"
                                            v-for="([key, label]) in filteredStages" :key="key">
                                            <input type="checkbox" :id="`stage_${key}`" :value="key"
                                                v-model="selectedStages"
                                                class="form-checkbox text-blue-600 dark:text-blue-400" />
                                            <label :for="`stage_${key}`"
                                                class="ml-2 cursor-pointer text-gray-700 dark:text-gray-200">
                                                {{ label }}
                                            </label>
                                        </li>
                                    </ul>
                                </div>
                            </div>
                        </div>

                        <!-- Selected stages displayed as tags with a remove button -->
                        <div class="relative inline-block mt-2 ml-[-10px]">
                            <button v-for="(stage, index) in selectedStages" :key="index"
                                class="remove_button flex items-center justify-center relative p-2 text-base bg-gray-200 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 rounded cursor-pointer transition duration-300"
                                @click="removeSelectedStage(stage)">
                                {{ stagess[stage] }} ✕
                            </button>
                        </div>
                    </div>
                    <div class="h-48 mb-16">
                        <button
                            class="loadbutton cursor-pointer text-base rounded bg-[#2363a3] text-white transition-[background-color] duration-[0.3s] ease-[ease] m-2.5 px-4 py-2 border-[none] hover:bg-[#002956]"
                            v-if="!sidebarVisible" @click="fetchDataAndAnimate" :class="{ 'loading': loading }"
                            :style="buttonStyle">
                            <span v-if="!loading">Load</span>
                            <span v-else>Loading...</span>
                        </button>
                    </div>

                </div>
            </div>
            <ShipmentsMap :sidebarVisible="sidebarVisible" :showMap="showMap" :zoom="zoom" :center="center"
                :mapOptions="mapOptions" :url="url" :markersData="markersData" @update:center="centerUpdate"
                @update:zoom="zoomUpdate" style="padding-bottom: 50px;" />

        </div>
        <!-- <ShipmentsTable :sidebarVisible="sidebarVisible" :showTopButton="showTopButton" :sortedResults="sortedResults"
            :sortDirection="sortDirection" @sort-column="sortByColumn" @view-route="viewRoute" @select-row="selectRow"
            @update-selected-rows="updateSelectedRows" @top-function="topFunction" /> -->
        <div>
            <ShipmentsTable :sidebarVisible="sidebarVisible" :showTopButton="showTopButton"
                :sortedResults="sortedResults" :sortDirection="sortDirection" :shipmentNumber="shipmentNumber"
                @sort-column="sortByColumn" @view-route="viewRoute" @select-row="selectRow"
                @update-selected-rows="updateSelectedRows" @top-function="topFunction"
                @update-shipment-number="handleInputnumber" />
        </div>

        <button @click="topFunction" class="mybtn" title="Go to top" v-if="showTopButton">
        </button>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted,watch } from 'vue';
import { latLng } from "leaflet";
import "leaflet/dist/leaflet.css";
import _ from 'lodash';
import { options as zipOptions } from '../stores/zip_codes.js';
import { stagess } from '../stores/stages.js';

import { useTableDataStore } from "../stores/table_data";
import { toast } from 'vue3-toastify';

import { api } from '@/api';
import ShipmentsTable from '@/components/ShipmentsTable.vue';
import ShipmentsMap from '@/components/ShipmentsMap.vue';
import GeneralSelector from '@/components/GeneralSelector.vue';
import { useRouter } from 'vue-router';
import { createStore } from 'vuex';

const selectedRows = ref([]);
const router = useRouter();

const selectRow = (item) => {
    const index = selectedRows.value.findIndex((row) => row.id === item.id);

    if (index === -1) {
        selectedRows.value.push(item);
    } else {
        selectedRows.value = [
            ...selectedRows.value.slice(0, index),
            ...selectedRows.value.slice(index + 1),
        ];
    }

    console.log('Selected Rows:', selectedRows.value);
};

// Function to handle routing with selected rows
// const viewRoute = () => {
//   const origins = selectedRows.value.map((row) => row.Origin_State.split(',')[0]);
//   const destinations = selectedRows.value.map((row) => row.Destination_State.split(',')[0]);
//     const order_id= selectedRows.value.map((row) => row.Ship);
//   // Combine all origins and destinations to form a comma-separated string
//   const startLocation = origins.join(',');
//   const endLocation = destinations.join(',');

//   console.log('Start Location:', startLocation);
//   console.log('End Location:', endLocation);
//   console.log(' order_id:', order_id);

//   // Navigate to the Logicalroutes page with query parameters
//   router.push({
//     name: 'LogicalRoutes',
//     query: { startLocation, endLocation,order_id },
//   });
// };

const store = useTableDataStore();
const shipmentNumber = ref('');

const handleShipmentNumberUpdate = (newNumber) => {
    shipmentNumber.value = newNumber;
};
const handleInputnumber = () => {
    if (shipmentNumber.value.length >= 3) {
        searchShipment();
    }
};

const options = zipOptions;
const originMarkerIcon = new L.Icon.Default();
const destinationMarkerIcon = new L.Icon({
    iconUrl: 'path/to/your/destination-icon.png',
    iconSize: [32, 32],
    iconAnchor: [16, 32],
    popupAnchor: [0, -32],
});
const showSuggestions = ref(false);
const stageInput = ref('');
const showStageSuggestions = ref(false);
const selectedStages = ref([]);
const selectedZipcodes = ref([]);
const mapLoaded = ref(true);
const selected_row_ids = ref([1, 2, 3, 4]);
const startDate = ref('');
const endDate = ref('');
const weightsValue = ref('');
const fromWeightsValue = ref('');
const toWeightsValue = ref('');
const logisticActivityValue = ref('outbound');
const shipmentValue = ref('Van');
const zipCode = ref('');
const distanceOriginValue = ref('1');
const radiusValue = ref('50');
const sidebarVisible = ref(true);
const loading = ref(false);
const loadingChart = ref(false);
const buttonStyle = ref({});
const selectedDate = ref('today');
const showTopButton = ref(false);
const zoom = ref(5);
const center = ref(latLng(40.639, -90.00));
const url = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
const currentZoom = ref(3);
const currentCenter = ref(latLng(-122.4194, 37.7749));
const showParagraph = ref(false);
const mapOptions = {
    zoomSnap: 0.5
};
const showMap = ref(true);
const sortColumn = ref('');
const sortDirection = ref('asc');
const markersData = ref([]);
const shipmentdata = ref([]);
const sortedResults = ref([]);
const selectedRowss = ref([]);
const dropdown = ref(null);
const stageDropdown = ref(null);
const viewRoute = () => {
    const origins = selectedRows.value.map((row) => row.Origin_State.split(',')[0]);
    const destinations = selectedRows.value.map((row) => row.Destination_State.split(',')[0]);

    // Check if row.Ship is a string before using split
    // const order_id = selectedRows.value.map((row) => {
    //     if (typeof row.Ship === 'string') {
    //         return row.Ship.split(',')[0];  // If it's a string, split it
    //     } else {
    //         return row.Ship;  // If it's not a string, just use it as is
    //     }
    // });
    const states = selectedRows.value.map((row) => {
        return {
            originState: row.Origin_State,  // Extract the Origin_State
            destinationState: row.Destination_State  // Extract the Destination_State
        };
    });

    // Combine all origins and destinations to form a comma-separated string
    const startLocation = origins.join(',');
    const endLocation = destinations.join(',');
    console.log('Order ID:', states);

    console.log('Start Location:', startLocation);
    console.log('End Location:', endLocation);
    // console.log('Order ID:', order_id);

    // Define the parameters to be passed
    const params = {
        // order_id: order_id.join(','), // If order_id is an array, join it as a comma-separated string
        start_location: states.map((s) => s.originState).join(','),
        end_location: states.map((s) => s.destinationState).join(','),
        start_date: startDate.value,
        end_date: endDate.value,
        from_weights_value: fromWeightsValue.value,
        to_weights_value: toWeightsValue.value,
        logistic_activity_value: logisticActivityValue.value,
        shipment_value: shipmentValue.value,
        distance_origin_value: distanceOriginValue.value,
        radius_value: radiusValue.value,
        startLocation: startLocation,  // Adding start location
        endLocation: endLocation       // Adding end location
    };

    // Navigate to the LogicalRoutes page with query parameters
    router.push({
        name: 'LogicalRoutes',
        query: params,
    });
};
// docker build -t moveit_fontend_refactor .
// docker run -d -p 84:80 --name moveit_frontend_ moveit_fontend_refactor

const filteredOptions = computed(() =>
    options.filter(option =>
        option.label.toLowerCase().includes(zipCode.value.toLowerCase())
    )
);

const filteredStages = computed(() => {
    const search = stageInput.value.toLowerCase();
    return Object.entries(stagess).filter(([key, label]) =>
        label.toLowerCase().includes(search)
    );
});

const refKeyMap = {
  startDate,
  endDate,
  weightsValue,
  fromWeightsValue,
  toWeightsValue,
  logisticActivityValue,
  shipmentValue,
  zipCode,
  distanceOriginValue,
  radiusValue,
//   selectedStages,
//   selectedZipcodes,
  selectedDate,
};
onMounted(() => {
    window.addEventListener('scroll', scrollFunction);
    scrollFunction();
    const today = new Date().toISOString().substr(0, 10);
    startDate.value = today;
    endDate.value = today;
    fromWeightsValue.value = fromWeightsValue.value;
    toWeightsValue.value = toWeightsValue.value;
    document.title = "MoveIT";
    document.addEventListener('click', handleClickOutside);
    document.addEventListener('click', handleClickOutsideStage);

    for (const [key, refValue] of Object.entries(refKeyMap)) {
    const savedValue = localStorage.getItem(key);
    if (savedValue !== null) {
      refValue.value = savedValue;
    } else {
      refValue.value = defaultValues[key] || ""; // Use default value if defined
      localStorage.setItem(key, refValue.value);
    }
  }
    window.addEventListener('beforeunload', clearLocalStorage);

});

onUnmounted(() => {
    document.removeEventListener('click', handleClickOutside);
    document.removeEventListener('click', handleClickOutsideStage);
});

watch(
  () => Object.entries(refKeyMap).map(([key, refValue]) => [key, refValue.value]),
  (newValues) => {
    for (const [key, newValue] of newValues) {
      localStorage.setItem(key, newValue);
    }
  },
  { deep: true } // Deep watch ensures nested values are tracked if necessary
);

const defaultValues = {
 today: new Date().toISOString().substr(0, 10),

  startDate: new Date().toISOString().substr(0, 10), // Set to today's date
  endDate: new Date().toISOString().substr(0, 10), // Set to today's date
  weightsValue: "",
  fromWeightsValue: "",
  toWeightsValue: "",
  logisticActivityValue: "outbound",
  shipmentValue: "Van",
  zipCode: "",
  distanceOriginValue: "1",
  radiusValue: "50",
  selectedDate:"today",
};
// const updateLocalStorage = (key, value) => {
//       localStorage.setItem(key, value);
//     };
function clearLocalStorage() {
  for (const [key, refValue] of Object.entries(refKeyMap)) {
    localStorage.removeItem(key); // Remove the key from localStorage
refValue.value = defaultValues[key] || "";  }
}

const handleEnterKey = () => {
    const validZipcode = filteredOptions.value.some(option => option.value === zipCode.value);

    if (!validZipcode && zipCode.value.trim() !== '') {
        addSelectedValue(zipCode.value);
    }

    zipCode.value = '';
    showSuggestions.value = false;
};

const handleInput = () => {
    showSuggestions.value = filteredOptions.value.length > 0;
    const validZipcode = filteredOptions.value.some(option => option.value === zipCode.value);

    if (!validZipcode && zipCode.value.trim() !== '') {
        showSuggestions.value = false;
    }
};

const addSelectedValue = (value) => {
    if (!isSelected(value) && value !== '') {
        selectedZipcodes.value.push(value);
    }
};
const isSelected = (value) => {
    return selectedZipcodes.value.includes(value);
};
const showDropdown = () => {
    if (filteredOptions.value.length > 0) {
        showSuggestions.value = true;
    }
};
const hideDropdown = () => {
    setTimeout(() => {
        showSuggestions.value = false;
    }, 200);
};
const getFilteredOptions = (input) => {
    return options.value.filter(option =>
        option.label.toLowerCase().includes(input.toLowerCase())
    );
};
const toggleOption = (option) => {
    selectedZipcodes.value.push(option.label);
    zipCode.value = '';
    showSuggestions.value = false;
};

const handleClickOutside = (event) => {
    if (dropdown.value && !dropdown.value.contains(event.target)) {
        showSuggestions.value = false;
    }
};

const handleClickOutsideStage = (event) => {
    if (stageDropdown.value && !stageDropdown.value.contains(event.target)) {
        hideStageDropdown();
    }
};
const handleStageInput = () => {

    showStageSuggestions.value = true;
};
const showStageDropdown = () => {
    showStageSuggestions.value = true;
};
const hideStageDropdown = () => {
    setTimeout(() => {
        showStageSuggestions.value = false;
    }, 150);
};

const toggleStageSelection = (stage) => {
    if (stage === " ") {
        selectedStages.value = [" "];
    } else {
        if (!selectedStages.value.includes(" ")) {
            if (!selectedStages.value.includes(stage)) {
                selectedStages.value.push(stage);
            }
        }
    }
    stageInput.value = '';
};
const selectStage = () => {
    const selectedStage = Object.keys(stagess.value).find(
        key => stagess.value[key].toLowerCase() === stageInput.value.toLowerCase()
    );

    if (selectedStage && !selectedStages.value.includes(selectedStage)) {
        selectedStages.value.push(selectedStage);
        stageInput.value = '';
        showStageSuggestions.value = false;
    }
};
const removeSelectedStage = (stage) => {

    selectedStages.value = selectedStages.value.filter(s => s !== stage);
};
// const selectRow = (item) => {
//     const index = selectedRowss.value.findIndex((row) => row.id === item.id);

//     if (index === -1) {
//         selectedRowss.value.push(item);  // Add item to the array if it's not already selected
//     } else {
//         selectedRowss.value.splice(index, 1);  // Remove item if it's already selected
//     }

//     console.log('Selected Rows:', selectedRowss.value);
// };
// function viewRoute() {
//     const origins = state.selectedRowss.map((row) => row.Origin_State.split(',')[0]);
//     const destinations = state.selectedRowss.map((row) => row.Destination_State.split(',')[0]);
//     const startLocation = origins.join(',');
//     const endLocation = destinations.join(',');
//     router.push({
//         name: 'Logicalroutes',
//         query: { startLocation, endLocation },
//     });
// }
const getMarkerIcon = (originState) => {
    return originState === 'destination' ? destinationMarkerIcon.value : originMarkerIcon.value;
};

const handleMouseOver = () => {
    showSuggestions.value = true;
};

const removeSelectedValue = (value) => {
    const index = selectedZipcodes.value.indexOf(value);
    if (index !== -1) {
        selectedZipcodes.value.splice(index, 1);
    }
};

const fetchDateRange = async () => {
    try {
        const response = await api.get(`/date_picker_range?selected_option=${selectedDate.value}`);
        const data = response.data;

        startDate.value = data.start_date;
        endDate.value = data.end_date;
    } catch (error) {
        console.error('Error:', error);
    }
};

const fetchWeights = async () => {
    const response = await api.get(`/weights_filter?selected_weights_option=${weightsValue.value}`);
    try {
        const data = response.data;
        const selectedWeightOption = weightsValue.value;
        if (selectedWeightOption === '-1') {
            fromWeightsValue.value = '-1';
            toWeightsValue.value = '-1';
        } else {
            const [fromWeight, toWeight] = selectedWeightOption.split('-');
            fromWeightsValue.value = fromWeight || '';
            toWeightsValue.value = toWeight || '';
        }
    } catch (error) {
        console.error('Error:', error);
    }
};

const fetchData = async () => {
    shipmentdata.value = [];
    sortedResults.value = [];
    const stageQuery = selectedStages.value.join(',');

    try {
        const response = await api.get(`/get_filtered_data_for_multiple_zipcodes?zip_codes=${selectedZipcodes.value}&start_date=${startDate.value}&end_date=${endDate.value}&from_weights_value=${fromWeightsValue.value}&to_weights_value=${toWeightsValue.value}&logistic_activity_value=${logisticActivityValue.value}&shipment_value=${shipmentValue.value}&distance_origin_value=${distanceOriginValue.value}&radius_value=${radiusValue.value}&selected_row_ids=${selected_row_ids.value}&stage=${stageQuery}`);

        const results = response.data;
        console.log(results);

        sortedResults.value = convertResultsToArray(results);
        store.setResults(results);
        localStorage.setItem('tableData', JSON.stringify(results));
        if (sortedResults.value.length === 0) {
            toast.error('No records found.', {
                autoClose: 3000,
                position: toast.POSITION.TOP_RIGHT,
            });
            return;
        }
        // console.log("sorted", sortedResults);

    } catch (error) {
        console.error('Error:', error);
    }
};

const fetchChartAndRender = async () => {
    mapLoaded.value = false;
    shipmentdata.value = [];
    markersData.value = [];
    // fillColor.value = []; // Uncomment if needed later

    const stageQuery = selectedStages.value.join(',');

    try {
        const response = await api.get(`/get_chart_data?zip_codes=${selectedZipcodes.value}&start_date=${startDate.value}&end_date=${endDate.value}&from_weights_value=${fromWeightsValue.value}&to_weights_value=${toWeightsValue.value}&logistic_activity_value=${logisticActivityValue.value}&shipment_value=${shipmentValue.value}&distance_origin_value=${distanceOriginValue.value}&radius_value=${radiusValue.value}&selected_row_ids=${selected_row_ids.value}&stage=${stageQuery}`);

        // Ensure the response is valid before proceeding
        if (response && response.status === 200) {
            const data = response.data;

            const zipCodes = [...new Set(data.map(item => item.zip_code))];
            const zipCodeColors = generateZipCodeColors(zipCodes); // Assume this method is defined elsewhere

            markersData.value = data.map((item) => ({
                latLngs: [
                    [item.lat[0], item.lon[0]],
                    [item.lat[1], item.lon[1]],
                ],
                color: zipCodeColors[item.zip_code] || 'blue',
                width: 3,
                tooltip: `${item.hovertext}`,
            }));
            // markersData.value = data.map((item) => {
            //     const latitudes = item.lat;
            //     const longitudes = item.lon;

            //     // Find the bounds for each item (min/max latitude and longitude)
            //     const latMin = Math.min(...latitudes);
            //     const latMax = Math.max(...latitudes);
            //     const lonMin = Math.min(...longitudes);
            //     const lonMax = Math.max(...longitudes);

            //     // Assuming you are using Leaflet or a similar mapping library:
            //     const bounds = [[latMin, lonMin], [latMax, lonMax]];
            //     console.log(bounds.value)
            //     return {
            //         latLngs: [
            //             bounds
            //         ],
            //         color: zipCodeColors[item.zip_code] || 'blue',
            //         width: 3,
            //         tooltip: `${item.hovertext}`,
            //         bounds: bounds,  // The bounds for the specific marker/region
            //     };
            // });


            loadingChart.value = false;
        } else if (response && response.status === 404) {
            showNoShipmentAlert(); // Assume this method is defined elsewhere
            throw new Error('No shipment data available');
        } else {
            throw new Error('Unexpected response status: ' + (response ? response.status : 'undefined'));
        }
    } catch (error) {
        console.error('Error fetching chart data:', error);
        loadingChart.value = false;
    }
};


const convertResultsToArray = (results) => {
    const resultArray = [];
    for (const zipCode in results) {
        resultArray.push(...results[zipCode]);
    }
    return resultArray;
};

const showNoShipmentAlert = () => {
    console.log('No shipment data available');
};

const generateZipCodeColors = (zipCodes) => {
    const zipCodeColors = {};
    zipCodes.forEach((zipCode, index) => {
        const color = generateUniqueColor(index);
        zipCodeColors[zipCode] = color;
    });
    return zipCodeColors;
};

const generateUniqueColor = (index) => {
    const colors = ['blue', '#48BF91', '#281E5D', 'orange', '#de7062'];
    return colors[index % colors.length];
};

const toggleSidebar = () => {
    sidebarVisible.value = !sidebarVisible.value;
};

const fetchDataAndAnimate = () => {
    if (!fromWeightsValue.value || !toWeightsValue.value) {
        toast.error('Please select both From and To weights before proceeding.', {
            autoClose: 3000,
            position: toast.POSITION.TOP_RIGHT,
        });
        return;
    }
    mapLoaded.value = false;
    shipmentdata.value = [];
    loading.value = true;
    fetchData();
    fetchChartAndRender();
    loading.value = false;
    buttonStyle.backgroundColor = '#7a9bbd';
    buttonStyle.transition = 'background-color 0.3s ease';

    setTimeout(() => {
        loading.value = false;
        // buttonStyle = {}; // Reset buttonStyle after animation
    }, 1000);
};

const scrollFunction = () => {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    showTopButton.value = scrollTop > 20;
};

const topFunction = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
};

const zoomUpdate = (zoom) => {
    currentZoom.value = zoom;
};

const centerUpdate = (center) => {
    currentCenter.value = center;
};

const showLongText = () => {
    showParagraph.value = !showParagraph.value;
};

const innerClick = () => {
    alert("Click!");
};
const sortByColumn = (column) => {
    if (sortColumn.value === column) {
        sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc';
    } else {
        sortColumn.value = column;
        sortDirection.value = 'asc';
    }

    sortedResults.value = _.orderBy(sortedResults.value, sortColumn.value, sortDirection.value);
};

const toggleSortDirection = () => {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc';
    sortedResults.value = _.orderBy(sortedResults.value, sortColumn.value, sortDirection.value);
};



</script>

<style scoped>
.mybtn {
    position: fixed;
    bottom: 20px;
    right: 30px;
    z-index: 99;
    font-size: 18px;
    border: none;
    outline: none;
    background-color: #2363a3;
    ;
    color: rgb(255, 255, 255);
    cursor: pointer;
    padding: 25px;
    border-radius: 60px;
    background-size: 30px;
    background-position: center;
    background-repeat: no-repeat;
    background-image: url('../assets/upload.png')
}

.mybtn:hover {
    background-color: #002956;
}

.sidebar-open .r-panel {
    flex: 6;
}

.r-panel {
    flex: 6;
}
</style>