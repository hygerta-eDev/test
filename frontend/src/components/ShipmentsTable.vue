<template>
  <div class="right-panel mt-[-200px] transition-width duration-300 ease-in-out" :class="{
    'ml-24 sidebar-open': sidebarVisible,
    'ml-[320px] mr-2': !sidebarVisible,
  }">
    <div class="flex flex-wrap items-center gap-2 m-4">
      <button
        class="bg-gradient-to-r from-sky-600 to-blue-500 text-white px-4 md:px-6 py-2 rounded-lg shadow-lg font-bold hover:from-sky-700 hover:to-blue-600 transition duration-300 transform hover:scale-105 dark:from-sky-500 dark:to-blue-400 dark:hover:from-sky-600 dark:hover:to-blue-500"
        @click="viewRoute" >
        View Route
      </button>


      <div
        class="border rounded-lg p-4 mb-6 mt-4 relative shadow-md shadow-gray-300 dark:shadow-gray-700 dark:border-gray-600">
        <!-- Label -->
        <label for="shipmentNumber"
          class="block text-sm font-semibold absolute top-1 left-4 bg-white px-2 -mt-3 dark:bg-gray-900 dark:text-gray-300">
          Shipment Number
        </label>

        <!-- Input and Button on the Same Line -->
        <div class="flex items-center space-x-4">
          <!-- Input Field -->
          <input type="number" id="shipmentNumber" v-model="shipmentNumber" @input="handleInputnumber"
            class="p-2 text-base border border-gray-300 rounded w-full focus:outline-none focus:ring transition duration-300 dark:bg-gray-800 dark:text-gray-200 dark:border-gray-600"
            placeholder="Enter shipment number" aria-label="Shipment Number" />

          <!-- Search Button -->
          <button @click="searchShipment"
            class="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition duration-300 whitespace-nowrap dark:bg-blue-400 dark:hover:bg-blue-500">
            Search
          </button>
        </div>
      </div>

      <div
        class="border rounded-lg p-4 mb-6 mt-4 relative shadow-md shadow-gray-300 dark:shadow-gray-700 dark:border-gray-600">
                <label for="customerMultiselect" class="block text-sm font-semibold absolute top-1 left-4 bg-white px-2 -mt-3 dark:bg-gray-900 dark:text-gray-300">Select
                  Account</label>
        <multiselect v-model="selectedCustomers" :options="uniqueCustomers" multiple placeholder="Select customers"
          track-by="Customer" label="Customer" @update:model-value="filterByCustomer"

           />

      </div>
      <!-- <div class="mb-4 z-50">
  <label for="customerDropdown" class="block text-sm font-semibold mb-1 dark:text-gray-300">Select Customer</label>
  <select
    id="customerDropdown"
    v-model="selectedCustomer"
    @change="filterByCustomer"
    class="p-2 text-base border border-gray-300 rounded w-full focus:outline-none focus:ring transition duration-300 dark:bg-gray-800 dark:text-gray-200 dark:border-gray-600"
  >
    <option value="" disabled selected>Select a Customer</option>
    <option v-for="customer in uniqueCustomers" :key="customer" :value="customer">
      {{ customer }}
    </option>
  </select>
</div> -->
    </div>

    <div class="flex flex-col h-[calc(100vh-200px)] overflow-hidden">

      <div class="overflow-auto">

        <table
          class="table-auto w-full  text-black border-collapse shadow-2xl border border-blue-200 rounded-lg dark:border-gray-600 dark:shadow-gray-800">
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
                Account
              </th>
              <th class="px-2 py-4 font-semibold border-r border-gray-200 whitespace-nowrap dark:text-gray-300">
                Pieces
                <button class="text-xs" @click="sortByColumn('Pcs')">
                  {{ sortDirection === 'asc' ? '▲' : '▼' }}
                </button>
              </th>
              <th class="px-2 py-4 font-semibold border-r border-gray-200 whitespace-nowrap dark:text-gray-300">
                Weight
                <button class="text-xs" @click="sortByColumn('Weight')">
                  {{ sortDirection === 'asc' ? '▲' : '▼' }}
                </button>
              </th>
              <th class="px-2 py-4 font-semibold border-r border-gray-200 whitespace-nowrap dark:text-gray-300">
                Carriers
                <button class="text-xs" @click="sortByColumn('Carriers')">
                  {{ sortDirection === 'asc' ? '▲' : '▼' }}
                </button>
              </th>
              <th class="px-2 py-4 font-semibold border-r border-gray-200 whitespace-nowrap dark:text-gray-300">
                Pickup
                <button class="text-xs" @click="sortByColumn('Pickup')">
                  {{ sortDirection === 'asc' ? '▲' : '▼' }}
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
            <template v-if="localSortedResults.length > 0" v-for="(item, index) in localSortedResults" :key="item.id">
              <tr @click="selectRow(item)"
                :class="{ 'bg-white dark:bg-gray-800': index % 2 === 0, 'bg-gray-100 dark:bg-gray-700': index % 2 !== 0 }"
                class="border-b border-gray-300 hover:bg-blue-100 transition duration-200 dark:hover:bg-gray-600">
                <td class="px-2 py-4 text-sm text-center border-r border-gray-200 whitespace-nowrap dark:text-gray-300">
                  {{ index + 1 }}
                  <input type="checkbox" v-model="selectedRowss" :value="item" @change="updateSelectedRows"
                    class="ml-2" />
                </td>
                <td
                  class="px-2 py-4 text-sm text-center border-r border-gray-200 whitespace-nowrap dark:text-gray-300 hidden sm:table-cell">
                  {{ item.t_div }}
                </td>
                <td class="px-2 py-4 text-sm text-center border-r border-gray-200 whitespace-nowrap dark:text-gray-300">
                  {{ item.Ship }}</td>
                <td class="px-2 py-4 text-sm text-center border-r border-gray-200 whitespace-nowrap dark:text-gray-300">
                  {{ item.Customer }}</td>
                <td class="px-2 py-4 text-sm text-center border-r border-gray-200 whitespace-nowrap dark:text-gray-300">
                  {{ item.Pcs }}</td>
                <td class="px-2 py-4 text-sm text-center border-r border-gray-200 whitespace-nowrap dark:text-gray-300">
                  {{ item.Weight }}
                </td>
                <td class="px-2 py-4 text-sm text-center border-r border-gray-200 whitespace-nowrap dark:text-gray-300">
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
                <td class="px-2 py-4 text-sm text-center border-r border-gray-200 whitespace-nowrap dark:text-gray-300">
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
            <template v-else>
              <tr>
                <td colspan="15" class="text-center py-4 text-gray-500 whitespace-nowrap">
                  No records found
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </div>

    <button @click="topFunction" class="mybtn transition-all duration-300 ease-in-out fixed bottom-4 right-4"
      title="Go to top" v-if="showTopButton"></button>
  </div>
</template>
<script setup>
import { ref, watch, defineProps, defineEmits, onMounted, computed } from 'vue';
import { api } from '@/api';
import { onBeforeRouteLeave } from 'vue-router';
import Multiselect from 'vue-multiselect'


const shipmentNumber = ref('');
const localSortedResults = ref([]);
const originalData = ref([]);
const selectedCustomer = ref("");
const uniqueCustomers = ref([]);
const selectedCustomers = ref([]);  // Array to hold multiple selected customers

const props = defineProps({
  sidebarVisible: Boolean,
  sortedResults: Array,
  showTopButton: Boolean,
  sortDirection: String,
  shipmentNumber: String,
});

onMounted(() => {
  fetchCustomers();

});


const fetchCustomers = () => {
  // Extract customers from sortedResults, assuming Customer is a string
  const customers = new Set(props.sortedResults.map((item) => item.Customer));
  uniqueCustomers.value = Array.from(customers).map(customer => ({ id: customer, Customer: customer }));
  console.log(uniqueCustomers.value);
};


const filterByCustomer = () => {
  if (selectedCustomers.value.length > 0) {
    // console.log("stectedcustomer", selectedCustomers.value)
    const selectedCustomerNames = selectedCustomers.value.map(c => c.Customer);

    localSortedResults.value = props.sortedResults.filter(item =>
      !selectedCustomerNames.includes(item.Customer)
    );
    // console.log("tabla", localSortedResults.value)
  } else {
    localSortedResults.value = [...props.sortedResults];
  }
};




// Watch the sortedResults to keep the localSortedResults updated
// watch(() => props.sortedResults, (newResults) => {
//   localSortedResults.value = newResults;
//   filterByCustomer();
//    // Apply filter if a customer is selected
// }, { immediate: true });
// computed(() => {
//   return localSortedResults
//     .map((item) => item.Customer)
//     .filter((customer) => customer && customer.trim() !== ""); // Ensure non-empty and valid customers
// });
watch(localSortedResults, () => {
  const customers = localSortedResults.value.map((item, index) => ({
    Customer: item.Customer, // Use the Customer name
    uniqueId: index, // Generate a unique ID based on the index
  }));
  uniqueCustomers.value = Array.from(
    new Map(customers.map((item) => [item.Customer, item])).values()
  );
  console.log('testapofiltrohen', customers.value)
});
const emit = defineEmits([
  'view-route', 'sort-column', 'select-row', 'update-selected-rows', 'top-function', 'update-shipment-number'
]);

onMounted(() => {
  const storedData = localStorage.getItem('tableData');
  if (storedData) {
    localSortedResults.value = JSON.parse(storedData);
    originalData.value = [...localSortedResults.value];
  }
  window.addEventListener('beforeunload', clearLocalStorage);

});
const clearLocalStorage = () => {
  localStorage.removeItem('tableData');
};

watch(
  () => props.sortedResults,
  (newVal) => {
    localSortedResults.value = [...newVal];
    originalData.value = [...newVal];
    if (newVal.length > 0) { 
      localStorage.setItem('tableData', JSON.stringify(newVal));
    }
  },
  { immediate: true }
);

onBeforeRouteLeave((to, from, next) => {
  if (localSortedResults.value.length > 0) {
    localStorage.setItem('tableData', JSON.stringify(localSortedResults.value));
  }
  next();
});

watch(
  shipmentNumber,
  (newVal) => {
    if (!newVal) {
      localSortedResults.value = [...originalData.value];
    }
  }
);

const extractUniqueCustomers = (customers) => {
  uniqueCustomers.value = customers.map(customer => ({
    id: customer.id,
    Customer: customer.Customer
  }))
}

const searchShipment = async () => {
  const storedData = localStorage.getItem('tableData');
  if (storedData) {
    localSortedResults.value = JSON.parse(storedData);
    originalData.value = [...localSortedResults.value];
  }

  if (!shipmentNumber.value) {
    localSortedResults.value = [...originalData.value];
    return;
  }

  try {
    const response = await api.get(`/search_by_t_order`, {
      params: { t_order: shipmentNumber.value },
    });
    console.log('API Response:', response.data);
    localSortedResults.value = response.data;
    originalData.value = [...response.data];
  } catch (error) {
    console.error('Error fetching shipment:', error);
    alert('Unable to fetch shipment data. Please try again.');
  }
};
const handleInputChange = () => {
  if (!shipmentNumber.value) {
    localSortedResults.value = [...originalData.value];
  } else {
    searchShipment(); 
  }
};

const selectedRowss = ref([]);
const viewRoute = () => { emit('view-route'); };
const sortByColumn = (column) => { emit('sort-column', column); };
const selectRow = (items) => {
  emit('select-row', items);
};
const updateSelectedRows = () => { emit('update-selected-rows', selectedRowss.value); };
const topFunction = () => { emit('top-function'); };
const updateShipmentNumber = (newNumber) => { emit('update-shipment-number', newNumber); };

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
<style src="vue-multiselect/dist/vue-multiselect.min.css"></style>
<style src="vue-multiselect/dist/vue-multiselect.css"></style>

<style >
.multiselect__tag-icon::after {
    content: "×";
    color: #f7f9fa !important;
    font-size: 14px;
}


</style>




<!-- <span class="multiselect__option--highlight multiselect__option" data-select="Press enter to select" data-selected="Selected" data-deselect="Press enter to remove"></span> -->



<!-- 
<template>
  <div class="right-panel mt-[-200px] transition-width duration-300 ease-in-out" :class="{
    'ml-24 sidebar-open': sidebarVisible,
    'ml-[320px] mr-2': !sidebarVisible,
  }">
    <div class="flex flex-wrap items-center gap-2 m-4">
      <button
        class="bg-gradient-to-r from-sky-600 to-blue-500 text-white px-4 md:px-6 py-2 rounded-lg shadow-lg font-bold hover:from-sky-700 hover:to-blue-600 transition duration-300 transform hover:scale-105 dark:from-sky-500 dark:to-blue-400 dark:hover:from-sky-600 dark:hover:to-blue-500"
        @click="viewRoute" v-if="sortedResults.length > 0">
        View Route
      </button>


      <div
        class="border rounded-lg p-4 mb-6 mt-4 relative shadow-md shadow-gray-300 dark:shadow-gray-700 dark:border-gray-600">
        <label for="shipmentNumber"
          class="block text-sm font-semibold absolute top-1 left-4 bg-white px-2 -mt-3 dark:bg-gray-900 dark:text-gray-300">
          Shipment Number
        </label>

        <div class="flex items-center space-x-4">
          <input type="number" id="shipmentNumber" v-model="shipmentNumber" @input="handleInputnumber"
            class="p-2 text-base border border-gray-300 rounded w-full focus:outline-none focus:ring transition duration-300 dark:bg-gray-800 dark:text-gray-200 dark:border-gray-600"
            placeholder="Enter shipment number" aria-label="Shipment Number" />

          <button @click="searchShipment"
            class="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition duration-300 whitespace-nowrap dark:bg-blue-400 dark:hover:bg-blue-500">
            Search
          </button>
        </div>
      </div>
      <div class="mb-4 z-50">
        <label for="customerMultiselect" class="block text-sm font-semibold mb-1 dark:text-gray-300">Select Customer</label>
        <multiselect 
  v-model="selectedCustomers" 
  :options="uniqueCustomers" 
  multiple 
  placeholder="Select customers" 
  track-by="id" 
  label="customer" 
/>

      </div>
    
    </div>

    <div class="flex flex-col h-[calc(100vh-200px)] overflow-hidden">

      <div class="overflow-auto">
        
        <table
          class="table-auto w-full  text-black border-collapse shadow-2xl border border-blue-200 rounded-lg dark:border-gray-600 dark:shadow-gray-800">
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
                  {{ sortDirection === 'asc' ? '▲' : '▼' }}
                </button>
              </th>
              <th class="px-2 py-4 font-semibold border-r border-gray-200 whitespace-nowrap dark:text-gray-300">
                Weight
                <button class="text-xs" @click="sortByColumn('Weight')">
                  {{ sortDirection === 'asc' ? '▲' : '▼' }}
                </button>
              </th>
              <th class="px-2 py-4 font-semibold border-r border-gray-200 whitespace-nowrap dark:text-gray-300">
                Carriers
                <button class="text-xs" @click="sortByColumn('Carriers')">
                  {{ sortDirection === 'asc' ? '▲' : '▼' }}
                </button>
              </th>
              <th class="px-2 py-4 font-semibold border-r border-gray-200 whitespace-nowrap dark:text-gray-300">
                Pickup
                <button class="text-xs" @click="sortByColumn('Pickup')">
                  {{ sortDirection === 'asc' ? '▲' : '▼' }}
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
            <template v-if="localSortedResults.length > 0" v-for="(item, index) in localSortedResults" :key="item.id">
              <tr @click="selectRow(item)"
                :class="{ 'bg-white dark:bg-gray-800': index % 2 === 0, 'bg-gray-100 dark:bg-gray-700': index % 2 !== 0 }"
                class="border-b border-gray-300 hover:bg-blue-100 transition duration-200 dark:hover:bg-gray-600">
                <td class="px-2 py-4 text-sm text-center border-r border-gray-200 whitespace-nowrap dark:text-gray-300">
                  {{ index + 1 }}
                  <input type="checkbox" v-model="selectedRowss" :value="item" @change="updateSelectedRows"
                    class="ml-2" />
                </td>
                <td
                  class="px-2 py-4 text-sm text-center border-r border-gray-200 whitespace-nowrap dark:text-gray-300 hidden sm:table-cell">
                  {{ item.t_div }}
                </td>
                <td class="px-2 py-4 text-sm text-center border-r border-gray-200 whitespace-nowrap dark:text-gray-300">
                  {{ item.Ship }}</td>
                <td class="px-2 py-4 text-sm text-center border-r border-gray-200 whitespace-nowrap dark:text-gray-300">
                  {{ item.Customer }}</td>
                <td class="px-2 py-4 text-sm text-center border-r border-gray-200 whitespace-nowrap dark:text-gray-300">
                  {{ item.Pcs }}</td>
                <td class="px-2 py-4 text-sm text-center border-r border-gray-200 whitespace-nowrap dark:text-gray-300">
                  {{ item.Weight }}
                </td>
                <td class="px-2 py-4 text-sm text-center border-r border-gray-200 whitespace-nowrap dark:text-gray-300">
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
                <td class="px-2 py-4 text-sm text-center border-r border-gray-200 whitespace-nowrap dark:text-gray-300">
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
            <template v-else>
              <tr>
                <td colspan="15" class="text-center py-4 text-gray-500 whitespace-nowrap">
                  No records found
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </div>

    <button @click="topFunction" class="mybtn transition-all duration-300 ease-in-out fixed bottom-4 right-4"
      title="Go to top" v-if="showTopButton"></button>
  </div>
</template>
<script setup>
import { ref, watch, defineProps, defineEmits, onMounted } from 'vue';
import { api } from '@/api';
import { onBeforeRouteLeave } from 'vue-router';
import Multiselect from 'vue-multiselect'


const shipmentNumber = ref('');
const localSortedResults = ref([]);
const originalData = ref([]);
const selectedCustomer = ref("");
const uniqueCustomers = ref([]);
const selectedCustomers = ref([]); // Array to hold multiple selected customers
// Props
const props = defineProps({
  sidebarVisible: Boolean,
  sortedResults: Array,
  showTopButton: Boolean,
  sortDirection: String,
  shipmentNumber: String,
});

// Fetch customers once the component is mounted
onMounted(() => {
  fetchCustomers();
  
});

// Fetch unique customers
const fetchCustomers = () => {
  const customers = new Set(props.sortedResults.map((item) => item.Customer)); // Adjust if needed
  uniqueCustomers.value = Array.from(customers);
  console.log(uniqueCustomers.value); // Check if customers are being correctly populated
};


// Filter shipments based on the selected customer
// Filter shipments based on the selected customer (remove instead of show)
const filterByCustomer = () => {
  if (selectedCustomer.value) {
    localSortedResults.value = props.sortedResults.filter(item => item.Customer !== selectedCustomer.value);
  } else {
    localSortedResults.value = [...props.sortedResults]; // Reset to all results if no customer is selected
  }
};


// Watch the sortedResults to keep the localSortedResults updated
watch(() => props.sortedResults, (newResults) => {
  localSortedResults.value = newResults;
  filterByCustomer(); // Apply filter if a customer is selected
});

const emit = defineEmits([
  'view-route', 'sort-column', 'select-row', 'update-selected-rows', 'top-function', 'update-shipment-number'
]);

// First, restore data from localStorage on mount
onMounted(() => {
  const storedData = localStorage.getItem('tableData');
  if (storedData) {
    localSortedResults.value = JSON.parse(storedData);
    originalData.value = [...localSortedResults.value];
  }
  window.addEventListener('beforeunload', clearLocalStorage);

});
const clearLocalStorage = () => {
  localStorage.removeItem('tableData');
};

// Watch for changes to `sortedResults` and update localStorage accordingly
watch(
  () => props.sortedResults,
  (newVal) => {
    localSortedResults.value = [...newVal];
    originalData.value = [...newVal];
    if (newVal.length > 0) {  // Only store if data exists
      localStorage.setItem('tableData', JSON.stringify(newVal));
    }
  },
  { immediate: true }
);

// Save to localStorage when the route is left
onBeforeRouteLeave((to, from, next) => {
  if (localSortedResults.value.length > 0) {
    localStorage.setItem('tableData', JSON.stringify(localSortedResults.value));
  }
  next();
});

// Watch for changes in shipmentNumber and reset if empty
watch(
  shipmentNumber,
  (newVal) => {
    if (!newVal) {
      localSortedResults.value = [...originalData.value];
    }
  }
);

// const handleInputChange = () => {
//   if (!shipmentNumber.value) {
//     localSortedResults.value = [...originalData.value];
//   }
// };



// Search functionality for shipments
const searchShipment = async () => {
  const storedData = localStorage.getItem('tableData');
  if (storedData) {
    localSortedResults.value = JSON.parse(storedData);
    originalData.value = [...localSortedResults.value];
  }

  if (!shipmentNumber.value) {
    localSortedResults.value = [...originalData.value];
    return;
  }

  try {
    const response = await api.get(`/search_by_t_order`, {
      params: { t_order: shipmentNumber.value },
    });
    console.log('API Response:', response.data);
    localSortedResults.value = response.data;
    originalData.value = [...response.data];
  } catch (error) {
    console.error('Error fetching shipment:', error);
    alert('Unable to fetch shipment data. Please try again.');
  }
};
const handleInputChange = () => {
  if (!shipmentNumber.value) {
    localSortedResults.value = [...originalData.value]; // Reset when cleared
  } else {
    searchShipment(); // Trigger search if not empty
  }
};

// Other methods for row selection, sorting, etc.
const selectedRowss = ref([]);
const viewRoute = () => { emit('view-route'); };
const sortByColumn = (column) => { emit('sort-column', column); };
const selectRow = (items) => {
  emit('select-row', items);
};
const updateSelectedRows = () => { emit('update-selected-rows', selectedRowss.value); };
const topFunction = () => { emit('top-function'); };
const updateShipmentNumber = (newNumber) => { emit('update-shipment-number', newNumber); };

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
<style src="vue-multiselect/dist/vue-multiselect.min.css"></style>

<style scoped></style>








 -->
