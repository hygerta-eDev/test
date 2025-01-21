<template class="dark:bg-gray-900">
  <div class=" mt-5 bg-white dark:bg-gray-900 " :class="{ 'sidebar-open ': sidebarVisible }">
    <div class="flex items-stretch bg-white dark:bg-gray-900">
      <div class="fixed h-screen overflow-y-scroll p-4  transition-width duration-300 ease-in-out dark:bg-gray-900" :class="{
        'w-72 dark:bg-gray-900 ': !sidebarVisible, 'w-16 ml-5 dark:bg-gray-900': sidebarVisible,
      }">
        <div class="flex justify-end p-2 dark:bg-gray-900">
          <div class="flex flex-col justify-between items-center">
            <button @click="toggleSidebar" :class="{ 'hamburger-open': !sidebarVisible }"
              class="w-8 h-8 bg-transparent border-none cursor-pointer p-0 z-1">
              <span class="block w-full h-0.5 bg-black dark:bg-white mb-2 transition-transform duration-300 transform"
                :class="{ 'rotate-45 -translate-y-0': !sidebarVisible }"></span>
              <span class="block w-full h-0.5 bg-black dark:bg-white mb-2 transition-transform duration-300 transform"
                :class="{ 'scale-y-0': !sidebarVisible }"></span>
              <span class="block w-full h-0.5 bg-black dark:bg-white mb-2 transition-transform duration-300 transform"
                :class="{ '-rotate-45 -translate-y-5': !sidebarVisible }"></span>
            </button>
          </div>
        </div>
        <h1 class="text-4xl font mb-8 text-gray-700 dark:text-gray-200" v-if="!sidebarVisible">
          All Shipments</h1>
        <div class="panel h-full dark:bg-gray-900">
          <div
            class="border rounded-lg p-4 mb-6 mt-4 relative w-full shadow-md shadow-gray-300 dark:shadow-gray-700 dark:bg-gray-900"
            v-if="!sidebarVisible">
            <label
              class="block text-sm font-semibold absolute top-1 left-4 bg-white dark:bg-gray-900 text-gray-700 dark:text-gray-200 px-2 -mt-3">Date</label>
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
                  <option value="last_3_months">This 3 Months</option>
                  <option value="last_year">Last Year</option>
                </select>
              </div>
            </div>
            <div class="flex items-center mb-2">
              <label for="start-date" class="w-1/3 mr-2 text-gray-700 dark:text-gray-200 ">Start Date:</label>
              <input type="date" id="start-date" v-model="startDate" @change="fetchData"
                class="p-2 text-base border border-gray-300 dark:border-gray-600 rounded w-full bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 focus:ring transition duration-300">
            </div>
            <div class="flex items-center mb-2">
              <label for="end-date" class="w-1/3 mr-2 text-gray-700 dark:text-gray-200  ">End Date:</label>
              <input type="date" id="end-date" v-model="endDate" @change="fetchData"
                class="p-2 text-base border border-gray-300 dark:border-gray-600 rounded w-full bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 focus:ring transition duration-300">
            </div>
          </div>
          <div
            class="border rounded-lg p-4 mb-6 mt-4 relative w-full shadow-md shadow-gray-300 dark:shadow-gray-700 dark:bg-gray-900"
            v-if="!sidebarVisible">
            <label for="weights-value"
              class="block text-sm font-semibold absolute top-1 left-4 bg-white dark:bg-gray-900 text-gray-700 dark:text-gray-200 px-2 -mt-3">Weight</label>
            <div class="flex items-center mb-4">
              <div class="w-full sm:w-2/3 mx-auto">
                <select id="weight-filter" v-model="weightsValue" @change="fetchWeights"
                  class="focus:ring w-full rounded border border-gray-300 dark:border-gray-600 p-2 text-base bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 transition duration-300">
                  <option value="-1">All</option>
                  <option value="0-500">0-500</option>
                  <option value="500-1000">500-1000</option>
                  <option value="1000-2000">1000-2000</option>
                  <option value="2000-5000">2000-5000</option>
                  <option value="5000-10000">5000-10000</option>
                  <option value="10000-">More than 10000</option>
                </select>
                <button v-if="weight - filter !== ''" @click="clearweight"
                  class="absolute right-[65px] top-9 transform -translate-y-1/2 mr-2">
                  X
                </button>
              </div>
            </div>
            <div class="flex items-center mb-4">
              <label for="from-weights-value" class="w-1/3 mr-2 text-gray-700 dark:text-gray-200  ">From weight:</label>
              <input type="text" id="from-weights-value" v-model="fromWeightsValue" @change="fetchWeights"
                class="p-2 text-base border border-gray-300 dark:border-gray-600 rounded w-full bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 focus:ring transition duration-300"
                v-if="fromWeightsValue !== '-1'">
            </div>
            <div class="flex items-center mb-4">
              <label for="to-weights-value" class="w-1/3 mr-2 text-gray-700 dark:text-gray-200  ">To weight:</label>
              <input type="text" id="to-weights-value" v-model="toWeightsValue" @change="fetchWeights"
                class="p-2 text-base border border-gray-300 dark:border-gray-600 rounded w-full bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 focus:ring transition duration-300"
                v-if="toWeightsValue !== '-1'">
            </div>
          </div>
          <div
            class="border rounded-lg p-4 mb-6 mt-4 relative w-full shadow-md shadow-gray-300 dark:shadow-gray-700 dark:bg-gray-900"
            v-if="!sidebarVisible">
            <div class="flex items-center">
              <label class="w-1/3 mr-2 text-gray-700 dark:text-gray-200" for="shipment-value">Shipment Value:</label>
              <div class="relative w-full">
                <select
                  class="focus:ring w-full rounded border border-gray-300 dark:border-gray-600 p-2 text-base bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 transition duration-300"
                  type="text" id="shipment-value" v-model="shipmentValue">
                  <!-- <option value="All">Select Option</option> -->
                  <option value="All">All</option>
                  <option value="Van">Freight Solutions</option>
                  <option value="Air">Specialized Logistics</option>
                  <option value="SS">ShippingSource</option>
                  <option value="Int">International</option>
                </select>
                <button v-if="shipmentValue !== ''" @click="clearSelection"
                  class="absolute right-6 top-1/2 transform -translate-y-1/2 mr-2">
                  X
                </button>
              </div>
            </div>
          </div>
          <div
            class="border rounded-lg p-4 mb-6 mt-4 relative w-full shadow-md shadow-gray-300 dark:shadow-gray-700 dark:bg-gray-900"
            v-if="!sidebarVisible">
            <div class="flex items-center">
              <label class="w-1/3 mr-2 text-gray-700 dark:text-gray-200 " for="zip-code">Zip Code:</label>
              <div class="relative" ref="dropdown">
                <div class="flex items-center">
                  <input class="p-2 text-base border border-gray-300 rounded w-full  transition duration-300  flex-1 "
                    type="text" id="zip-code" v-model="zipCode" @input="handleInput" @focus="showDropdown"
                    @blur="hideDropdown" @mouseout="handleMouseOut" />

                  <ul
                    class="list-none p-0 ml-2 absolute w-full h-300 top-1/2 overflow-y-scroll scrollbar-thin scrollbar-thumb-gray-400 scrollbar-thumb-rounded-full -200"
                    v-show="showSuggestions">
                    <li class="dropdownoptions p-2 cursor-pointer bg-opacity-85 hover:bg-gray-200"
                      v-for="option in filteredOptions" :key="option.value" @click="toggleOption(option)">
                      {{ option.label }}
                    </li>
                  </ul>
                </div>
              </div>
            </div>
            <div class="relative inline-block">
              <button v-for="(value, index) in selectedZipcodes" :key="index"
                class="remove_button flex items-center justify-center relative p-2 text-base bg-transparent border-none cursor-pointer z-1"
                @click="removeSelectedValue(value)">
                {{ value }} ✕
              </button>
            </div>
          </div>
          <div
            class="border rounded-lg p-4 mb-6 mt-4 relative w-full shadow-md shadow-gray-300 dark:shadow-gray-700 dark:bg-gray-900"
            v-if="!sidebarVisible">
            <div class="flex items-center">
              <label class="w-1/3 mr-2 text-gray-700 dark:text-gray-200" for="stage">Stage:</label>
              <div class="relative" ref="stageDropdown">
                <div class="flex items-center">
                  <input
                    class="focus:ring p-2 text-base border border-gray-300 rounded w-full transition duration-300 flex-1"
                    type="text" id="stage" v-model="stageInput" autocomplete="off" @focus="showStageDropdown"
                    @input="handleStageInput" placeholder="Select stages..." />

                  <ul
                    class="z-50 p-0 rounded-md border mt-5 border-gray-300 absolute w-full h-[120px] top-1/2 overflow-y-scroll scrollbar-thin scrollbar-thumb-gray-400 scrollbar-thumb-rounded-full bg-white"
                    v-show="showStageSuggestions">
                    <li class="dropdownoptions p-2 cursor-pointer hover:bg-gray-200 bg-white border flex items-center"
                      v-for="([key, label]) in filteredStages" :key="key">
                      <input type="checkbox" :id="`stage_${key}`" :value="key" v-model="selectedStages" />
                      <label :for="`stage_${key}`" class="ml-2 cursor-pointer">{{ label }}</label>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
            <div class="relative inline-block mt-2 ml-[-10px]">
              <button v-for="(stage, index) in selectedStages" :key="index"
                class="remove_button flex items-center justify-center relative p-2 text-base bg-transparent border-none cursor-pointer"
                @click="removeSelectedStage(stage)">
                {{ stagess[stage] }} ✕
              </button>
            </div>
          </div>

          <div
            class="border rounded-lg p-4 mb-6 mt-4 relative w-full shadow-md shadow-gray-300 dark:shadow-gray-700 dark:bg-gray-900"
            v-if="!sidebarVisible">
            <div class="flex items-center">
              <label class=" w-1/3 mr-2 text-gray-700 dark:text-gray-200 " for="loadshipment">View all
                Shipments<sup>*</sup></label>
              <select class="p-2 text-base border border-gray-300 rounded w-full  transition duration-300  flex-1"
                type="text" id="loadshipment" v-model="loadshipment" required>
                <option value="loadallshipments">Origin Shipments</option>
                <option value="loadalldestinationshipments">Destination Shipments</option>
              </select>
            </div>
          </div>
          <div class="h-36 mb-24 ">
            <button
              class="loadbutton   cursor-pointertext-base rounded bg-[#2363a3]  transition-[background-color] duration-[0.3s] ease-[ease] m-2.5 px-4 py-2 border-[none] hover: bg-[#002956];"
              v-if="!sidebarVisible" @click="loadShipments" :class="{ 'loading': loading }" :style="buttonStyle">
              <span v-if="!loading">Load</span>
              <span v-else>Loading...</span>
            </button>
          </div>

        </div>
      </div>
      <div class="r-panel flex-[6] z-0 h-screen ml-[320px] dark:bg-gray-900
     " :class="{
      'sidebar-open  transition-width duration-300 ease-in-out bg-white dark:bg-gray-900': !sidebarVisible,
      ' transition-width duration-300 ease-in-out ml-[90px] bg-white dark:bg-gray-900': sidebarVisible
    }"> <l-map id="map" ref="mapRef" v-if="showMap" :zoom="zoom" :center="center" :options="mapOptions"
          style="height: 80%" @update:center="centerUpdate" @update:zoom="zoomUpdate">
          <l-tile-layer :url="url" />

          <!-- Origin Shipments Markers -->
          <l-marker v-for="(item, index) in shipmentdata" :key="'marker-' + index" :lat-lng="item.latLng"
            :content="item.tooltip"   @click="handleMarkerClick(item.Origin_State, 'origin')"
            >
            <l-popup :content="item.tooltip"></l-popup>
          </l-marker>

          <!-- Destination Shipments Markers -->
          <l-marker v-for="(item, index) in shipmentdestinatindata" :key="'destination-marker-' + index"
            :lat-lng="item.latLng" :content="item.tooltip"   @click="handleMarkerClick(item.Destination_State, 'destination')"
            >
            <l-popup :content="item.tooltip"></l-popup>
          </l-marker>

          <l-geo-json v-if="showMap && mapLoaded" :geojson="geojson" :options="options"
            :options-style="styleFunction" />
        </l-map>

        <div class="flex flex-col h-[calc(100vh-200px)] overflow-hidden mt-5 dark:bg-gray-900">
          <div class="overflow-auto dark:bg-gray-900">
            <template v-if="apiResponseData && apiResponseData.length > 0">
              <table
                class="table-auto w-full text-black border-collapse shadow-2xl border border-blue-200 rounded-lg dark:border-gray-600 dark:shadow-gray-800">
                <thead class="bg-sky-600  text-white sticky top-0 dark:bg-sky-700">
                  <tr
                    class="text-left text-xs sm:text-sm md:text-base border-b border-solid border-gray-300 dark:border-gray-600">
                    <th class="px-2 py-4 font-semibold border-r border-gray-200 whitespace-nowrap dark:text-gray-300">
                      No.
                    </th>
                    <th class="px-2 py-4 font-semibold border-r border-gray-200 whitespace-nowrap dark:text-gray-300">
                      Div
                    </th>
                    <th class="px-2 py-4 font-semibold border-r border-gray-200 whitespace-nowrap dark:text-gray-300">
                      Shipment No.
                    </th>
                    <th class="px-2 py-4 font-semibold border-r border-gray-200 whitespace-nowrap dark:text-gray-300">
                      Customer
                    </th>
                    <th class="px-2 py-4 font-semibold border-r border-gray-200 whitespace-nowrap dark:text-gray-300">
                      Pieces
                      <button class="text-xs" @click="sortByColumn('Pcs')">
                        <!-- {{ sortDirection === 'asc' ? '▲' : '▼' }} -->
                      </button>
                    </th>
                    <th class="px-2 py-4 font-semibold border-r border-gray-200 whitespace-nowrap dark:text-gray-300">
                      Weight
                      <button class="text-xs" @click="sortByColumn('Weight')">
                        <!-- {{ sortDirection === 'asc' ? '▲' : '▼' }} -->
                      </button>
                    </th>
                    <th class="px-2 py-4 font-semibold border-r border-gray-200 whitespace-nowrap dark:text-gray-300">
                      Carriers
                      <button class="text-xs" @click="sortByColumn('Carriers')">
                        <!-- {{ sortDirection === 'asc' ? '▲' : '▼' }} -->
                      </button>
                    </th>
                    <th class="px-2 py-4 font-semibold border-r border-gray-200 whitespace-nowrap dark:text-gray-300">
                      Pickup
                      <button class="text-xs" @click="sortByColumn('Pickup')">
                        <!-- {{ sortDirection === 'asc' ? '▲' : '▼' }} -->
                      </button>
                    </th>
                    <th class="px-2 py-4 font-semibold border-r border-gray-200 whitespace-nowrap dark:text-gray-300">
                      Deliv
                    </th>
                    <th class="px-2 py-4 font-semibold border-r border-gray-200 whitespace-nowrap dark:text-gray-300">
                      Origin State
                      <button class="text-xs" @click="sortByColumn('Origin_State')">
                        {{ sortDirection === 'asc' ? '▲' : '▼' }}
                      </button>
                    </th>
                    <th class="px-2 py-4 font-semibold border-r border-gray-200 whitespace-nowrap dark:text-gray-300">
                      Zip1
                    </th>
                    <th class="px-2 py-4 font-semibold border-r border-gray-200 whitespace-nowrap dark:text-gray-300">
                      Destination State
                    </th>
                    <th class="px-2 py-4 font-semibold border-r border-gray-200 whitespace-nowrap dark:text-gray-300">
                      Zip2
                    </th>
                    <th class="px-2 py-4 font-semibold border-r border-gray-200 whitespace-nowrap dark:text-gray-300">
                      Stage
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <template v-for="(item, index) in apiResponseData" :key="item.id">
                    <tr @click="selectRow(item)"
                      :class="{ 'bg-white dark:bg-gray-800': index % 2 === 0, 'bg-gray-100 dark:bg-gray-700': index % 2 !== 0 }"
                      class="border-b border-gray-300 hover:bg-blue-100 transition duration-200 dark:hover:bg-gray-600">
                      <td
                        class="px-2 py-4 text-sm text-center border-r border-gray-200 whitespace-nowrap dark:text-gray-300">
                        {{ index + 1 }}
                        <!-- <input type="checkbox" v-model="selectedRowss" :value="item" @change="updateSelectedRows"
                          class="ml-2" /> -->
                      </td>
                      <td
                        class="px-2 py-4 text-sm text-center border-r border-gray-200 whitespace-nowrap dark:text-gray-300 hidden sm:table-cell">
                        {{ item.t_div }}
                      </td>
                      <td
                        class="px-2 py-4 text-sm text-center border-r border-gray-200 whitespace-nowrap dark:text-gray-300">
                        {{ item.Ship }}</td>
                      <td
                        class="px-2 py-4 text-sm text-center border-r border-gray-200 whitespace-nowrap dark:text-gray-300">
                        {{ item.Customer }}</td>
                      <td
                        class="px-2 py-4 text-sm text-center border-r border-gray-200 whitespace-nowrap dark:text-gray-300">
                        {{ item.Pcs }}</td>
                      <td
                        class="px-2 py-4 text-sm text-center border-r border-gray-200 whitespace-nowrap dark:text-gray-300">
                        {{ item.Weight }}
                      </td>
                      <td
                        class="px-2 py-4 text-sm text-center border-r border-gray-200 whitespace-nowrap dark:text-gray-300">
                        {{ item.Carriers }}
                      </td>
                      <td
                        class="px-2 py-4 text-sm text-center border-r border-gray-200 whitespace-nowrap dark:text-gray-300 hidden lg:table-cell">
                        {{ formatDate(item.Pickup) }}
                      </td>
                      <td
                        class="px-2 py-4 text-sm text-center border-r border-gray-200 whitespace-nowrap dark:text-gray-300 hidden lg:table-cell">
                        {{ formatDate(item.Deliv) }}
                      </td>
                      <td
                        class="px-2 py-4 text-sm text-center border-r border-gray-200 whitespace-nowrap dark:text-gray-300">
                        {{ item.Origin_State }}
                      </td>
                      <td
                        class="px-2 py-4 text-sm text-center border-r border-gray-200 whitespace-nowrap dark:text-gray-300 hidden sm:table-cell">
                        {{ item.Zip1 }}
                      </td>
                      <td class="px-2 py-4 text-sm text-center border-r whitespace-nowrap dark:text-gray-300">{{
                        item.Destination_State }}</td>
                      <td
                        class="px-2 py-4 text-sm text-center border-r border-gray-200 whitespace-nowrap dark:text-gray-300 hidden sm:table-cell">
                        {{ item.Zip2 }}
                      </td>
                      <td
                        class="px-2 py-4 text-sm text-center border-r border-gray-200 whitespace-nowrap dark:text-gray-300 hidden lg:table-cell">
                        {{ item.stage }}
                      </td>
                    </tr>
                  </template>
                </tbody>
              </table>
            </template>
            <template v-else-if="(isOrigin ? sortedResults.length : sortedResult.length) > 0">

              <table
                class="table-auto w-full text-black border-collapse shadow-2xl border border-blue-200 rounded-lg dark:border-gray-600 dark:shadow-gray-800">
                <thead class="bg-sky-600 text-white sticky top-0 dark:bg-sky-700">
                  <tr
                    class="text-left text-xs sm:text-sm md:text-base border-b border-solid border-gray-300 dark:border-gray-600">
                    <th
                      class="px-2 py-4 font-semibold border-r border-gray-200 whitespace-nowrap dark:text-gray-300  w-1/4 ">
                      No.</th>
                    <th
                      class="px-2 py-4 font-semibold border-r border-gray-200 whitespace-nowrap dark:text-gray-300 w-1/4 ">
                      {{ isOrigin ? 'Origin_State' : 'Destination_State' }}
                    </th>
                    <th
                      class="px-2 py-4 font-semibold border-r border-gray-200 whitespace-nowrap dark:text-gray-300 w-1/4 ">
                      Zip</th>
                    <th
                      class="px-2 py-4 font-semibold border-r border-gray-200 whitespace-nowrap dark:text-gray-300 w-1/4 ">
                      Shipment Count
                      <button class="text-xs"
                        @click="isOrigin ? sortByColumn('ShipmentCount') : sortByColumnDestinationdata('ShipmentCount')">
                        {{ sortDirection === 'asc' ? '▲' : '▼' }}
                      </button>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <template v-for="(item, index) in (isOrigin ? sortedResults : sortedResult)" :key="index">
                    <tr
                      class="border-b border-gray-300 hover:bg-blue-100 transition duration-200 dark:hover:bg-gray-600"
                      :class="{ 'bg-white dark:bg-gray-800': index % 2 === 0, 'bg-gray-100 dark:bg-gray-700': index % 2 !== 0 }">
                      <td
                        class="px-2 py-4 text-sm text-center border-r border-gray-200 whitespace-nowrap dark:text-gray-300 w-1/4 ">
                        {{ index + 1 }}
                      </td>
                      <td
                        class="px-2 py-4 text-sm text-center border-r border-gray-200 whitespace-nowrap dark:text-gray-300 w-1/4 ">
                        {{ isOrigin ? item.Origin_State : item.Destination_State }}
                      </td>
                      <td
                        class="px-2 py-4 text-sm text-center border-r border-gray-200 whitespace-nowrap dark:text-gray-300 w-1/4 ">
                        {{ isOrigin ? item.Zip1 : item.Zip2 }}
                      </td>
                      <td
                        class="px-2 py-4 text-sm text-center border-r border-gray-200 whitespace-nowrap dark:text-gray-300 w-1/4 ">
                        {{ item.ShipmentCount }}
                      </td>
                    </tr>
                  </template>
                </tbody>
              </table>
            </template>
            <template v-else>
              <div class="flex justify-center items-center h-full text-gray-500 dark:text-gray-400 text-lg font-medium">
                No Records Found
              </div>
            </template>
          </div>
        </div>

      </div>

    </div>
  </div>
  <button @click="topFunction" class="mybtn" title="Go to top" v-if="showTopButton">
  </button>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue';
import { latLng } from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { LMap, LTileLayer, LMarker, LPopup, LPolyline, LCircle, LGeoJson } from '@vue-leaflet/vue-leaflet';
import { stagess } from '../stores/stages.js';

import { api } from '@/api';
const topFunction = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' });
}; const scrollFunction = () => {
  const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
  showTopButton.value = scrollTop > 20;
};

const mapLoaded = ref(false);
const ShipmentCount = ref('');
const originStates = ref([]);
const OriginStates = ref([]);
const Origin_State = ref("");
const destinationStates = ref([]);
const DestinationStates = ref([]);
const Destination_State = ref("");
const startDate = ref('');
const endDate = ref('');
const weightsValue = ref(null);
const fromWeightsValue = ref(null);
const toWeightsValue = ref(null);
const logisticActivityValue = ref('outbound');
const shipmentValue = ref('All');
const zipCode = ref(null);
const stage = ref([]);
const costumStage = ref('');
const data = ref([]);
const sidebarVisible = ref(false);
const loading = ref(false);
const loadingChart = ref(false);
const buttonStyle = ref({});
const selectedDate = ref('today');
const showTopButton = ref(false);
const zoom = ref(4.5);
const center = ref(latLng(40.639, -90.00));
const url = ref("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png");
const currentZoom = ref(3);
const currentCenter = ref(latLng(-90.00, 40.639));
const showParagraph = ref(false);
const mapOptions = reactive({ zoomSnap: 0.5 });
const showMap = ref(true);
const lat = ref('');
const lng = ref('');
const sortColumn = ref('');
const sortDirection = ref('asc');
const markersData = ref([]);
const shipmentdata = ref([]);
const shipmentdestinatindata = ref([]);
const fetchedData = ref([]);
const results = ref([]);
const index = ref('');
const sortedResults = ref([]);
const sortedResult = ref([]);
const stageInput = ref('');
const selectedStages = ref([]);
const showStageSuggestions = ref(false);
const geojson = ref([]);
const stageDropdown = ref('')
const styleFunction = ref('')

const loadshipment = ref('loadallshipments');

const toggleSidebar = () => {
  sidebarVisible.value = !sidebarVisible.value;
};
onMounted(async () => {
  try {
    loading.value = true;
    const response = await fetch("https://raw.githubusercontent.com/shawnbot/topogram/master/data/us-states.geojson");
    const data = await response.json();
    geojson.value = data; 
    mapLoaded.value = true; 
    console.log("GeoJSON Loaded:", geojson.value);
    const today = new Date().toISOString().substr(0, 10);
    startDate.value = today;
    endDate.value = today;
    fromWeightsValue.value = fromWeightsValue.value;
    toWeightsValue.value = toWeightsValue.value;
    document.title = "MoveIT";
    document.addEventListener('click', handleClickOutside);
    document.addEventListener('click', handleClickOutsideStage);
    scrollFunction();
  } catch (error) {
    console.error("Error fetching the GeoJSON data:", error);
  } finally {
    loading.value = false;
  }
});


onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
  document.removeEventListener('click', handleClickOutsideStage);
});

const showSuggestions = ref(false);
const dropdown = ref(null);

const filteredStages = computed(() => {
  const search = stageInput.value.toLowerCase();
  return Object.entries(stagess).filter(([key, label]) => label.toLowerCase().includes(search));
});
const handleClickOutside = (event) => {
  if (dropdown.value && !dropdown.value.contains(event.target)) {
    showSuggestions.value = false;
  }
};

function handleClickOutsideStage(event) {
  if (stageDropdown.value && !stageDropdown.value.contains(event.target)) {
    hideStageDropdown();
  }
}

function showStageDropdown() {
  showStageSuggestions.value = true;
}

function hideStageDropdown() {
  setTimeout(() => {
    showStageSuggestions.value = false;
  }, 200);
}

function handleStageInput() {
  showStageSuggestions.value = true;
}

function toggleStageSelection(key) {
  if (!selectedStages.value.includes(key)) {
    selectedStages.value.push(key);
  }
  stageInput.value = '';
  showStageSuggestions.value = false;
}

function removeSelectedStage(stage) {
  selectedStages.value = selectedStages.value.filter(s => s !== stage);
}
function clearSelection() {
  shipmentValue.value = null;
  loadShipments();
}
function clearWeight() {
  weightsValue.value = null;
  fromWeightsValue.value = null;
  toWeightsValue.value = null;
  loadShipments();
}
function clearStage() {
  stage.value = null;
  loadShipments();
}
function checkingThenNullValue() {
  console.log('Selected Stages:', stage.value);
  if (weightsValue.value === " ") {
    weightsValue.value = null;
  };
  if (shipmentValue.value === " " && shipmentValue.value === "All") {
    shipmentValue.value = null;
  };
  if (stage.value === " ") {
    stage.value = null;
  };
}
const fetchDateRange = async () => {
  const url = `/date_picker_range?selected_option=${selectedDate.value}`;
  try {
    const response = await api.get(url);
    const data = response.data;
    startDate.value = data.start_date;
    endDate.value = data.end_date;
  } catch (error) {
    console.error('Error:', error);
  }
};
const fetchWeights = async () => {
  const url = `/weights_filter?selected_weights_option=${weightsValue.value}`;
  try {
    const response = await api.get(url);
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
const fetchAllOriginShipments = async () => {
  markersData.value = [];
  const url = `countoriginshipments?start_date=${startDate.value}&end_date=${endDate.value}` +
    (zipCode.value && zipCode.value.trim() !== '' ? `&zip_code=${zipCode.value}` : '')+
    (fromWeightsValue.value !== null ? `&from_weights_value=${fromWeightsValue.value}` : '') +
    (toWeightsValue.value !== null ? `&to_weights_value=${toWeightsValue.value}` : '') +
    (shipmentValue.value !== null ? `&shipment_value=${shipmentValue.value}` : '') +
    (selectedStages.value && selectedStages.value.length > 0
      ? selectedStages.value.map(stage => `&stage=${stage}`).join('')
      : '');
  try {
    const response = await api.get(url);
    const data = response.data;
    const shipmentData = data.map(item => ({
      latLng: [parseFloat(item.lat), parseFloat(item.lng)],
      tooltip: `
        <div>
          <i class="fas fa-info-circle"></i>
          <strong>Origin State:</strong> ${item.Origin_State}<br>
          <strong>Zip1:</strong> ${item.Zip1}<br>
          <strong>Shipment Count:</strong> ${item.ShipmentCount}
        </div>
      `,
      State: item.State,
      ShipmentCount: item.ShipmentCount,
      Zip1: item.Zip1,
      Origin_State: item.Origin_State
    }));
    const maxShipmentCount = Math.max(...shipmentData.map(item => item.ShipmentCount));
    sortedResults.value = shipmentData;
    shipmentData.forEach(item => {
      const originStateItem = {
        State: item.State,
        ShipmentCount: item.ShipmentCount,
      };
      originStates.value.push(originStateItem);
      const isMatch = geojson.value.features && Array.isArray(geojson.value.features) && geojson.value.features.some(feature => {
        const nameAlt = feature.properties.name_alt.slice(0, 2).toUpperCase();
        return nameAlt && nameAlt.includes(item.State);
      });

      if (isMatch) {
        OriginStates.value.push(originStateItem);
      }

    });
    styleFunction.value = (feature) => ({
      weight: 2,
      color: "#ECEFF1",
      opacity: 1,
      fillColor: feature.properties.fillColor,
      fillOpacity: 1
    });
    updateGeoJSONColors(maxShipmentCount);
    getColorForShipmentCount();
    shipmentdata.value = shipmentData;
    loadingChart.value = false;
  } catch (error) {
    console.error('Error fetching chart data:', error);
    loadingChart.value = false;
  }
}
function getColorForShipmentCount(shipmentCount, maxShipmentCount) {
  if (!maxShipmentCount || maxShipmentCount <= 0) {
    return '#B3E5FC'; 
  }
  const normalizedValue = shipmentCount / maxShipmentCount;

  if (normalizedValue >= 0.95) {
    return '#004B8D'; 
  } else if (normalizedValue >= 0.9) {
    return '#01579B';
  } else if (normalizedValue >= 0.85) {
    return '#01669E';
  } else if (normalizedValue >= 0.8) {
    return '#0273B2';
  } else if (normalizedValue >= 0.75) {
    return '#0277BD';
  } else if (normalizedValue >= 0.7) {
    return '#0283C8';
  } else if (normalizedValue >= 0.65) {
    return '#0288D1';
  } else if (normalizedValue >= 0.6) {
    return '#0392DA';
  } else if (normalizedValue >= 0.55) {
    return '#039BE5';
  } else if (normalizedValue >= 0.5) {
    return '#03A3EB';
  } else if (normalizedValue >= 0.45) {
    return '#03A9F4';
  } else if (normalizedValue >= 0.4) {
    return '#29B3F6';
  } else if (normalizedValue >= 0.35) {
    return '#4FBDF7';
  } else if (normalizedValue >= 0.3) {
    return '#67C8F9';
  } else if (normalizedValue >= 0.25) {
    return '#81D4FA';
  } else if (normalizedValue >= 0.2) {
    return '#9BDFFB';
  } else if (normalizedValue >= 0.15) {
    return '#B3E5FC';
  } else if (normalizedValue >= 0.1) {
    return '#CDEFFC';
  } else if (normalizedValue >= 0.05) {
    return '#E5F7FD';
  } else {
    return '#F0FBFE'; 
  }
}




function updateGeoJSONColors(maxShipmentCount) {
  if (geojson.value && Array.isArray(geojson.value.features)) {
    geojson.value.features.forEach(feature => {
      const OriginState = feature.properties.name_alt.slice(0, 2).toUpperCase();
      const matchingShipment = OriginStates.value.find(item => item.State === OriginState);
      if (matchingShipment) {
        feature.properties.fillColor = getColorForShipmentCount(matchingShipment.ShipmentCount, maxShipmentCount);
      } else {
        feature.properties.fillColor = 'grey';
      }
    });
  } else {
    console.error('GeoJSON features array is not available or is not an array:', geojson.value);
  }
}


const fetchAllDestinationShipments = async () => {
  markersData.value = [];
  const url = `countdestinationshipments?start_date=${startDate.value}&end_date=${endDate.value}` +
    (zipCode.value ? `&zip_code=${zipCode.value}` : '') +
    (fromWeightsValue.value ? `&from_weights_value=${fromWeightsValue.value}` : '') +
    (toWeightsValue.value ? `&to_weights_value=${toWeightsValue.value}` : '') +
    (shipmentValue.value ? `&shipment_value=${shipmentValue.value}` : '') +
    (selectedStages.value.length > 0
      ? selectedStages.value.map(stage => `&stage=${stage}`).join('')
      : '');
  try {
    const response = await api.get(url);
    const data = response.data;

    const shipmentDestinationData = data.map(item => ({
      latLng: [parseFloat(item.lat), parseFloat(item.lng)],
      tooltip: `
        <div>
          <strong>Destination State:</strong> ${item.Destination_State}<br>
          <strong>Zip2:</strong> ${item.Zip2}<br>
          <strong>Shipment Count:</strong> ${item.ShipmentCount}
        </div>
      `,
      State2: item.State2,
      ShipmentCount: item.ShipmentCount,
      Zip2: item.Zip2,
      Destination_State: item.Destination_State,
      Stage: item.Stage,
    }));
    const maxShipmentCount = Math.max(...shipmentDestinationData.map(item => item.ShipmentCount));

    sortedResult.value = shipmentDestinationData;
    shipmentDestinationData.forEach(item => {
      const destinationStateItem = {
        State2: item.State2,
        ShipmentCount: item.ShipmentCount,
      };

      destinationStates.value.push(destinationStateItem);
      const isMatch = geojson.value.features && Array.isArray(geojson.value.features) && geojson.value.features.some(feature => {
        const nameAlt = feature.properties.name_alt.slice(0, 2).toUpperCase();
        return nameAlt && nameAlt.includes(item.State2);
      });

      if (isMatch) {
        DestinationStates.value.push(destinationStateItem);
      }
    });

    styleFunction.value = (feature) => ({
      weight: 2,
      color: "#ECEFF1",
      opacity: 1,
      fillColor: feature.properties.fillColor,
      fillOpacity: 1
    });

    updateGeoJSONDestinationColors(maxShipmentCount);
    getColorForShipmentDestinationCount();
    shipmentdestinatindata.value = shipmentDestinationData;
    loadingChart.value = false;
  } catch (error) {
    console.error('Error fetching chart data:', error);
    loadingChart.value = false;
  }
};

const getColorForShipmentDestinationCount = (shipmentCount, maxShipmentCount) => {
  if (!maxShipmentCount || maxShipmentCount <= 0) {
    return '#c6ebd5'; // Fallback color
  }

  const normalizedValue = shipmentCount / maxShipmentCount;

  if (normalizedValue >= 0.95) {
    return '#0a5e36'; // Deepest green
  } else if (normalizedValue >= 0.9) {
    return '#0b6a3c';
  } else if (normalizedValue >= 0.85) {
    return '#0c7342';
  } else if (normalizedValue >= 0.8) {
    return '#0e7d48';
  } else if (normalizedValue >= 0.75) {
    return '#1b8a52';
  } else if (normalizedValue >= 0.7) {
    return '#209557';
  } else if (normalizedValue >= 0.65) {
    return '#239b5d';
  } else if (normalizedValue >= 0.6) {
    return '#27a263';
  } else if (normalizedValue >= 0.55) {
    return '#2cae6b';
  } else if (normalizedValue >= 0.5) {
    return '#31b571';
  } else if (normalizedValue >= 0.45) {
    return '#34be76';
  } else if (normalizedValue >= 0.4) {
    return '#49c083';
  } else if (normalizedValue >= 0.35) {
    return '#59c88b';
  } else if (normalizedValue >= 0.3) {
    return '#69cf93';
  } else if (normalizedValue >= 0.25) {
    return '#79d2a0';
  } else if (normalizedValue >= 0.2) {
    return '#8eddb1';
  } else if (normalizedValue >= 0.15) {
    return '#a1debb';
  } else if (normalizedValue >= 0.1) {
    return '#b3e5c7';
  } else if (normalizedValue >= 0.05) {
    return '#c6ebd5';
  } else {
    return '#e0f5e5'; // Lightest green
  }
};


const updateGeoJSONDestinationColors = (maxShipmentCount) => {
  if (geojson.value && Array.isArray(geojson.value.features)) {
    geojson.value.features.forEach((feature) => {
      const DestinationState = feature.properties.name_alt.slice(0, 2).toUpperCase();
      const matchingShipment = DestinationStates.value.find(item => item.State2 === DestinationState);

      if (matchingShipment) {
        feature.properties.fillColor = getColorForShipmentDestinationCount(matchingShipment.ShipmentCount,maxShipmentCount);
        // console.log(`DestinationState: ${DestinationState}, fillColor: ${feature.properties.fillColor}`);
      } else {
        feature.properties.fillColor = 'grey';
      }
    });
  } else {
    console.error('GeoJSON features array is not available or is not an array:', geojson.value);
  }
};

const loadAllDestinationShipments = () => {
  mapLoaded.value = true;
  shipmentdestinatindata.value = [];
  apiResponseData.value = null;
  shipmentdata.value = [];
  DestinationStates.value = [];
  markersData.value = [];
  fetchAllDestinationShipments();
  updateGeoJSONDestinationColors();
};

const loadallshipments = () => {
  results.value = [];
  apiResponseData.value = null;
  mapLoaded.value = true;
  shipmentdata.value = [];
  shipmentdestinatindata.value = [];
  OriginStates.value = [];
  markersData.value = [];
  fetchAllOriginShipments();
  updateGeoJSONColors();
};

const apiResponseData = ref(null);

// // Function to handle marker click
// const handleMarkerClick = async (state) => {
//   try {
//     // console.log('State passed:', state); // Log for debugging
//     const stateAbbreviation = state.split(',').pop().trim();
//     const response = await api.get(`/search_by_state_and_date?state=${stateAbbreviation}&start_date=${startDate.value}&end_date=${endDate.value}`);
//     // console.log('API response:', response.data);
//     processApiResponse(response.data);
//   } catch (error) {
//     console.error('Error fetching data for state:', state, error);
//   }
// };
const handleMarkerClick = async (state, type) => {
  try {
    const stateAbbreviation = state.split(',').pop().trim();
    let endpoint = '';
    if (type === 'origin') {
      endpoint = `/search_by_origin_state_and_date?state=${stateAbbreviation}&start_date=${startDate.value}&end_date=${endDate.value}`+
 
    (fromWeightsValue.value !== null ? `&from_weights_value=${fromWeightsValue.value}` : '') +
    (toWeightsValue.value !== null ? `&to_weights_value=${toWeightsValue.value}` : '') +
    (shipmentValue.value !== null ? `&shipment_value=${shipmentValue.value}` : '') +
    (selectedStages.value && selectedStages.value.length > 0
      ? selectedStages.value.map(stage => `&stage=${stage}`).join('')
      : '');
    } else if (type === 'destination') {
      endpoint = `/search_by_destination_state_and_date?state=${stateAbbreviation}&start_date=${startDate.value}&end_date=${endDate.value}` +
 
    (fromWeightsValue.value !== null ? `&from_weights_value=${fromWeightsValue.value}` : '') +
    (toWeightsValue.value !== null ? `&to_weights_value=${toWeightsValue.value}` : '') +
    (shipmentValue.value !== null ? `&shipment_value=${shipmentValue.value}` : '') +
    (selectedStages.value && selectedStages.value.length > 0
      ? selectedStages.value.map(stage => `&stage=${stage}`).join('')
      : '');
    }
    const response = await api.get(endpoint);

    processApiResponse(response.data);
  } catch (error) {
    console.error(`Error fetching data for ${type} state:`, state, error);
  }
};
const processApiResponse = (data) => {
  apiResponseData.value = data; 
  // console.log('Processing response data:', data);
};

const loadShipments = async () => {
  loading.value = true;
  try {
    if (loadshipment.value === 'loadallshipments') {
      await loadallshipments();
      isOrigin.value = true; 
    } else if (loadshipment.value === 'loadalldestinationshipments') {
      await loadAllDestinationShipments();
      isOrigin.value = false; 
    } else {
      console.warn('No valid shipment load option selected');
    }
  } catch (error) {
    console.error('Error loading shipments:', error);
  } finally {
    loading.value = false;
  }
};
const isOrigin = ref(true); 
const sortByColumn = (column) => {
  if (sortColumn.value === column) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortColumn.value = column;
    sortDirection.value = 'asc';
  }

  sortedResults.value = shipmentdata.value.slice().sort((a, b) => {
    const aValue = parseFloat(a[column]);
    const bValue = parseFloat(b[column]);

    if (sortDirection.value === 'asc') {
      return aValue - bValue;
    } else {
      return bValue - aValue;
    }
  });
};

const sortByColumnDestinationdata = (column) => {
  if (sortColumn.value === column) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortColumn.value = column;
    sortDirection.value = 'asc';
  }

  sortedResult.value = shipmentdestinatindata.value.slice().sort((a, b) => {
    const aValue = parseFloat(a[column]);
    const bValue = parseFloat(b[column]);

    if (sortDirection.value === 'asc') {
      return aValue - bValue;
    } else {
      return bValue - aValue;
    }
  });
};
const formatDate = (date) => {
  if (date === '0000-00-00 00:00:00') {
    return '0000-00-00';
  }

  if (date) {
    const d = new Date(date);
    const year = d.getFullYear();
    const month = (d.getMonth() + 1).toString().padStart(2, '0');
    const day = d.getDate().toString().padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  return '';
};
</script>

<!-- <script setup>
import { ref, reactive, onMounted, onBeforeUnmount, watch, computed } from 'vue';
import { latLng } from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { LMap, LTileLayer, LMarker, LPopup, LPolyline, LCircle, LGeoJson } from '@vue-leaflet/vue-leaflet';

import { api } from '@/api';

const stagess = reactive({
  " ": "All",
  BPR: "BPR",
  HOLD: "HOLD",
  OPS: "OPS",
  PACK: "PACK",
  PCKD: "PCKD",
  PEND: "PEND",
  QNEW: "QNEW",
  QOLD: "QOLD",
  QT: "QT",
  QUOT: "QUOT",
  QXLD: "QXLD",
  SRVY: "SRVY",
  STOR: "STOR",
  TRAN: "TRAN",
  XLD: "XLD"
});


const mapLoaded = ref(false);

const shipmentCount = ref(''); 
const originStates = ref([]); 
const OriginStates = ref([]); 

const styleFunction = {
  fillColor: 'blue',
  weight: 2,
  opacity: 1,
  color: 'white',
  fillOpacity: 0.7,
};

const originState = ref(''); 
const destinationStates = ref([]); 
const destinationState = ref(''); 
const startDate = ref('');
const endDate = ref('');
const weightsValue = ref(null); 
const fromWeightsValue = ref(null); 
const toWeightsValue = ref(null); 
const logisticActivityValue = ref('outbound'); 
const shipmentValue = ref('All'); 
const zipCode = ref(null); 
const selectedStages = ref([]);
const data = ref([]); 
const sidebarVisible = ref(false);
const showMap = ref(true);
const loadshipment = ref('loadallshipments');
const loading = ref(false); 
const loadingChart = ref(false); 
const selectedDate = ref('today'); 
const zoom = ref(7); 
const center = ref(latLng(40.639, -90.0)); 
const url = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
const currentZoom = ref(11.5); 
const currentCenter = ref(latLng(-90.0, 40.639)); 
const markersData = ref([]); 
const shipmentData = ref([]); 
const sortedResults = ref([]);
const sortedResult = ref([]);

const stageInput = ref(''); 
const showStageSuggestions = ref(false);
const showTopButton = ref(false);
const DestinationStates = ref([]);

const mapOptions = {
  zoomControl: true,
  attributionControl: false,
};

const geojson = ref(null); // Initially null
// const loading = ref(false);

// Fetch GeoJSON data
onMounted(async () => {
  try {
    loading.value = true;
    const response = await fetch("https://raw.githubusercontent.com/shawnbot/topogram/master/data/us-states.geojson");
    const data = await response.json();
    geojson.value = data; // Assign the fetched data
    mapLoaded.value = true; // Update mapLoaded once data is fetched
    console.log("GeoJSON Loaded:", geojson.value); 
  } catch (error) {
    console.error("Error fetching the GeoJSON data:", error);
  } finally {
    loading.value = false;
  }
});


// Watch for geojson changes
watch(geojson, (newVal) => {
  if (newVal) {
    console.log("GeoJSON Changed:", newVal);
    // Perform operations that depend on geojson being loaded
    updateGeoJSONColors();
    updateGeoJSONDestinationColors();
  }
});

const filteredStages = computed(() =>
  Object.entries(stagess).filter(([key, label]) =>
    label.toLowerCase().includes(stageInput.value.toLowerCase())
  )
);

// onMounted lifecycle hook
onMounted(() => {
  window.addEventListener('scroll', scrollFunction);
  scrollFunction();
  const today = new Date().toISOString().substr(0, 10);
  startDate.value = today;
  endDate.value = today;
  fromWeightsValue.value = fromWeightsValue.value;
  toWeightsValue.value = toWeightsValue.value;
  document.addEventListener('click', handleClickOutsideStage);
//   loadShipments();

});

// Function to handle click outside of the stage dropdown
const handleClickOutsideStage = (event)  => {
  if (!event.target.closest('.stage-dropdown')) {
    hideStageDropdown();
  }
};
// Function to handle click outside of any element

// Function to toggle stage selection
function toggleStageSelection(key) {
  if (!selectedStages.value.includes(key)) {
    selectedStages.value.push(key);
  }
  stageInput.value = '';
  hideStageDropdown();
}

// Function to remove selected stage
function removeSelectedStage(stage) {
  selectedStages.value = selectedStages.value.filter(s => s !== stage);
}

// Function to show the stage dropdown
function showStageDropdown() {
  showStageSuggestions.value = true;
}

// Function to hide the stage dropdown
function hideStageDropdown() {
  setTimeout(() => {
    showStageSuggestions.value = false;
  }, 200);
}

// Function to handle stage input
function handleStageInput() {
  showStageSuggestions.value = true;
}

// Clear selections
const clearSelection = () => {
  shipmentValue.value = null;
  loadShipments();
};

// Clear weight values
const clearWeight = () => {
  weightsValue.value = null;
  fromWeightsValue.value = null;
  toWeightsValue.value = null;
  loadShipments();
};

// Clear stage
const clearStage = () => {
  stageInput.value = null;
  loadShipments();
};

// Checking and nullifying empty values
const checkingThenNullValue = () => {
  console.log('Selected Stages:', selectedStages.value);
  if (weightsValue.value === " ") {
    weightsValue.value = null;
  }
  if (shipmentValue.value === " " || shipmentValue.value === "All") {
    shipmentValue.value = null;
  }
  if (stageInput.value === " ") {
    stageInput.value = null;
  }
};


const fetchDateRange = async () => {
  const url = `/date_picker_range?selected_option=${selectedDate.value}`;
  try {
    const response = await api.get(url);
    const data = response.data; // Axios automatically parses the JSON response
    startDate.value = data.start_date;
    endDate.value = data.end_date;
  } catch (error) {
    console.error('Error:', error);
  }
};


// Fetch Weights
const fetchWeights = async () => {
  const url = `/weights_filter?selected_weights_option=${weightsValue.value}`;
  try {
    const response = await api.get(url);
    const data = response.data; 
    // const data = await response.json();
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

// Fetch All Origin Shipments
const fetchAllOriginShipments = async () => {
  markersData.value = [];
  const url = `countoriginshipments?start_date=${startDate.value}&end_date=${endDate.value}` +
    (zipCode.value !== null ? `&zip_code=${zipCode.value}` : '') +
    (fromWeightsValue.value !== null ? `&from_weights_value=${fromWeightsValue.value}` : '') +
    (toWeightsValue.value !== null ? `&to_weights_value=${toWeightsValue.value}` : '') +
    (shipmentValue.value !== null ? `&shipment_value=${shipmentValue.value}` : '') +
    (selectedStages.value && selectedStages.value.length > 0
      ? selectedStages.value.map(stage => `&stage=${stage}`).join('')
      : '');
  try {
    const response = await api.get(url);
    // const data = await response.json();
    const data = response.data; 
    const shipmentData = data.map(item => ({
      latLng: [parseFloat(item.lat), parseFloat(item.lng)],
      tooltip: `
        <div>
          <i class="fas fa-info-circle"></i>
          <strong>Origin State:</strong> ${item.Origin_State}<br>
          <strong>Zip1:</strong> ${item.Zip1}<br>
          <strong>Shipment Count:</strong> ${item.ShipmentCount}
        </div>
      `,
      State: item.State,
      ShipmentCount: item.ShipmentCount,
      Zip1: item.Zip1,
      Origin_State: item.Origin_State
    }));
    sortedResults.value = shipmentData;
    shipmentData.forEach(item => {
      const originStateItem = {
        State: item.State,
        ShipmentCount: item.ShipmentCount
      };
      originStates.value.push(originStateItem);

      const isMatch = geojson.value.features.some(feature => {
        const nameAlt = feature.properties.name_alt.slice(0, 2).toUpperCase();
        return nameAlt && nameAlt.includes(item.State);
      });

      if (isMatch) {
        OriginStates.value.push(originStateItem);
      }
    });
    updateGeoJSONColors();
    getColorForShipmentCount();
    loadingChart.value = false;
  } catch (error) {
    console.error('Error fetching chart data:', error);
    loadingChart.value = false;
  }
};


// Update GeoJSON Colors
// const updateGeoJSONColors = () => {
//   geojson.value.features.forEach((feature) => {
//     const OriginState = feature.properties.name_alt.slice(0, 2).toUpperCase();
//     const matchingShipment = OriginStates.value.find(item => item.State === OriginState);
//     if (matchingShipment) {
//       feature.properties.fillColor = getColorForShipmentCount(matchingShipment.ShipmentCount);
//     } else {
//       feature.properties.fillColor = 'grey';
//     }
//   });
// };
const fetchAllDestinationShipments = async () => {
    markersData.value = [];
    const url = `countdestinationshipments?start_date=${startDate.value}&end_date=${endDate.value}` +
        (zipCode.value ? `&zip_code=${zipCode.value}` : '') +
        (fromWeightsValue.value ? `&from_weights_value=${fromWeightsValue.value}` : '') +
        (toWeightsValue.value ? `&to_weights_value=${toWeightsValue.value}` : '') +
        (shipmentValue.value ? `&shipment_value=${shipmentValue.value}` : '') +
        (selectedStages.value.length > 0
            ? selectedStages.value.map(stage => `&stage=${stage}`).join('')
            : '');
    try {
        const response = await api.get(url);
        const data = response.data;
        const shipmentdestinatindata = data.map(item => ({
            latLng: [parseFloat(item.lat), parseFloat(item.lng)],
            tooltip: `
                <div>
                    <strong>Destination State:</strong> ${item.Destination_State}<br>
                    <strong>Zip2:</strong> ${item.Zip2}<br>
                    <strong>Shipment Count:</strong> ${item.ShipmentCount}
                </div>
            `,
            State2: item.State2,
            ShipmentCount: item.ShipmentCount,
            Zip2: item.Zip2,
            Destination_State: item.Destination_State,
            Stage: item.Stage
        }));
        sortedResult.value = shipmentdestinatindata;

        // Check if geojson is valid
        if (geojson.value?.features && Array.isArray(geojson.value.features)) {
            shipmentdestinatindata.forEach(item => {
                const destinationStateItem = {
                    State2: item.State2,
                    ShipmentCount: item.ShipmentCount,
                };
                destinationStates.value.push(destinationStateItem);
                const isMatch = geojson.value.features.some(feature => {
                    const nameAlt = feature.properties?.name_alt?.slice(0, 2).toUpperCase();
                    return nameAlt && nameAlt.includes(item.State2);
                });
                if (isMatch) {
                    DestinationStates.value.push(destinationStateItem);
                }
            });
        } else {
            console.error('Invalid geojson structure');
        }

        styleFunction.value = (feature) => ({
            weight: 2,
            color: "#ECEFF1",
            opacity: 1,
            fillColor: feature.properties?.fillColor || "#FFFFFF",
            fillOpacity: 1
        });


        updateGeoJSONDestinationColors();
        shipmentdestinatindata.value = shipmentdestinatindata;
        loadingChart.value = false;
    } catch (error) {
        console.error('Error fetching chart data:', error);
        loadingChart.value = false;
    }
};


const getColorForShipmentCount = (ShipmentCount) => {
    if (ShipmentCount >= 2000) return '#01579B';
    if (ShipmentCount >= 1000) return '#0277BD';
    if (ShipmentCount >= 500) return ' #0288D1';
    if (ShipmentCount >= 250) return '#039BE5';
    if (ShipmentCount >= 100) return '#03A9F4';
    if (ShipmentCount >= 50) return '#29B6F6';
    if (ShipmentCount >= 25) return '#4FC3F7';
    if (ShipmentCount >= 10) return '#81D4FA';
    return '#B3E5FC';
};

const updateGeoJSONColors = () => {
  geojson.value.features.forEach((feature) => {
    const stateCode = feature.properties.name_alt.slice(0, 2).toUpperCase();
    const matchingShipment = OriginStates.value.find(item => item.State === stateCode);
    feature.properties.style = {
      fillColor: matchingShipment
        ? getColorForShipmentCount(matchingShipment.ShipmentCount)
        : 'grey',
      weight: 1,
      color: 'black',
      fillOpacity: 0.7,
    };
  });
};



const updateGeoJSONDestinationColors = () => {
    console.log("Updating GeoJSON Destination Colors...");

  // Ensure geojson.value is defined and has features
  if (geojson.value && geojson.value.features && Array.isArray(geojson.value.features)) {
    geojson.value.features.forEach((feature) => {
      const destinationState = feature.properties.name_alt.slice(0, 2).toUpperCase();
      const matchingShipment = DestinationStates.value.find(item => item.State2 === destinationState);
      
      if (matchingShipment) {
        feature.properties.fillColor = getColorForShipmentDestinationCount(matchingShipment.ShipmentCount);
      } else {
        feature.properties.fillColor = 'grey';
      }
    });
  } else {
    console.error("GeoJSON or GeoJSON features are missing or invalid.");
  }
};

const getColorForShipmentDestinationCount = (ShipmentCount) => {
    if (ShipmentCount >= 2000) return '#0b6a3c';
    if (ShipmentCount >= 1000) return '#1b8a52';
    if (ShipmentCount >= 500) return ' #239b5d';
    if (ShipmentCount >= 250) return '#2cae6b';
    if (ShipmentCount >= 100) return '#34be76';
    if (ShipmentCount >= 50) return '#59c88b';
    if (ShipmentCount >= 25) return '#73d199';
    if (ShipmentCount >= 10) return '#8ae3ad';
    return '#9de8b9';
};
console.log('GeoJSON:', geojson.value);

// const loadalldestinationshipments = () => {
//     mapLoaded.value = true;
//     shipmentdestinatindata.value = [];
//     shipmentdata.value = [];
//     DestinationStates.value = [];
//     markersData.value = [];
//     fillColor.value = [];
//     fetchalldestinationshipments();
//     updateGeoJSONDestinationColors();
// };

// const loadallshipments = () => {
//     sortedResults.value = [];
//     mapLoaded.value = true;
//     shipmentdata.value = [];
//     shipmentdestinatindata.value = [];
//     OriginStates.value = [];
//     markersData.value = [];
//     fillColor.value = [];
//     fetchalloriginshipments();
//     updateGeoJSONColors();
// };
const loadalldestinationshipments = async () => {
  mapLoaded.value = true;
  shipmentdestinatindata.value = [];
  shipmentdata.value = [];
  DestinationStates.value = [];
  markersData.value = [];
  fillColor.value = [];
  await fetchalldestinationshipments();  // Make sure this function is defined
  updateGeoJSONDestinationColors();  // Make sure this function is defined
};

// Function to load origin shipments
const loadallshipments = async () => {
  results.value = [];
  mapLoaded.value = true;
  shipmentdata.value = [];
  shipmentdestinatindata.value = [];
  OriginStates.value = [];
  markersData.value = [];
  fillColor.value = [];
  await fetchalloriginshipments();  // Make sure this function is defined
  updateGeoJSONColors();  // Make sure this function is defined
};

// Function to load shipments based on `loadshipment` value
const loadShipments = async () => {
  // Set loading to true
  loading.value = true;

  try {
    if (loadshipment.value === 'loadallshipments') {
      // Fetch all origin and destination shipments
      await fetchAllOriginShipments();
    } else if (loadshipment.value === 'loadalldestinationshipments') {
      // Fetch only destination shipments
      await fetchAllDestinationShipments();
    }
    
    loading.value = false; // Set loading to false once data is fetched
  } catch (error) {
    console.error('Error loading shipments:', error);
    loading.value = false; // Ensure loading is false even on error
  }
};

const toggleSidebar = () => {
    sidebarVisible.value = !sidebarVisible.value;
};

const scrollFunction = () => {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    showTopButton.value = scrollTop > 20;
};

const topFunction = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
};

watch(() => window, () => {
    window.addEventListener('scroll', scrollFunction);
});

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

    sortedResults.value = shipmentdata.value.slice().sort((a, b) => {
        const aValue = parseFloat(a[column]);
        const bValue = parseFloat(b[column]);

        if (sortDirection.value === 'asc') {
            return aValue - bValue;
        } else {
            return bValue - aValue;
        }
    });
};

const sortByColumnDestinationdata = (column) => {
    if (sortColumn.value === column) {
        sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc';
    } else {
        sortColumn.value = column;
        sortDirection.value = 'asc';
    }

    sortedResult.value = shipmentdestinatindata.value.slice().sort((a, b) => {
        const aValue = parseFloat(a[column]);
        const bValue = parseFloat(b[column]);

        if (sortDirection.value === 'asc') {
            return aValue - bValue;
        } else {
            return bValue - aValue;
        }
    });
};


// onMounted(() => {
//   console.log("Map Loaded", showMap, geojson, shipmentdata, shipmentdestinatindata);
// });
</script> -->

<style scoped>
/* .sidebar-open .side-panel {
    width: 4%;
  } */
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

/* .map{
    width: 100%;
    height: 100%;
    flex: 6;
  
  } */
/* .sidebar-open .r-panel {
    flex: 6;
  } */
/* .r-panel{
    flex: 6;
  } */
.small-button {
  font-size: 0.5rem;
  padding: 0.1rem;
}

sup {
  color: red;
}
</style>