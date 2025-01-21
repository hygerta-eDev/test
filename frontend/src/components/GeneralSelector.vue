<!-- <template>
    <div class="border rounded-lg p-4 mb-6 mt-4 relative w-full shadow-md shadow-gray-300">
      <label
        :for="label"
        class="block text-sm font-semibold absolute top-1 left-4 bg-white px-2 -mt-3"
      >
        {{ label }}
      </label>
  
      <div>
        <template v-if="type === 'dateRange'">
          <div class="flex items-center mb-4">
            <div class="w-full sm:w-2/3 mx-auto">
              <select
                v-model="selectedOption"
                @change="handleChange"
                class="p-2 text-base border border-gray-300 rounded w-full focus:outline-none focus:ring transition duration-300"
              >
                <option v-for="(option, key) in options" :key="key" :value="key">{{ option }}</option>
              </select>
            </div>
          </div>
  
          <div class="flex items-center mb-4">
            <label for="start-date" class="w-1/3 mr-2">Start Date:</label>
            <input
              type="date"
              id="start-date"
              v-model="startDate"
              @change="handleChange"
              class="p-2 text-base border border-gray-300 rounded w-full transition duration-300"
            />
          </div>
  
          <div class="flex items-center mb-4">
            <label for="end-date" class="w-1/3 mr-2">End Date:</label>
            <input
              type="date"
              id="end-date"
              v-model="endDate"
              @change="handleChange"
              class="p-2 text-base border border-gray-300 rounded w-full transition duration-300"
            />
          </div>
        </template>
  
        <template v-else-if="type === 'weightSelector'">
          <div class="flex items-center mb-4">
            <div class="w-full sm:w-2/3 mx-auto">
              <select
                id="weight-filter"
                v-model="selectedOption"
                @change="handleChange"
                class="focus:ring w-full rounded border border-gray-300 p-2 text-base transition duration-300"
              >
                <option v-for="(option, key) in options" :key="key" :value="key">{{ option }}</option>
              </select>
            </div>
          </div>
  
          <div class="flex items-center mb-4" v-if="selectedOption !== '-1'">
            <label for="from-value" class="w-1/3 mr-2">From:</label>
            <input
              type="text"
              id="from-value"
              v-model="fromValue"
              @change="handleChange"
              class="focus:ring p-2 text-base border border-gray-300 rounded w-full transition duration-300"
            />
          </div>
  
          <div class="flex items-center mb-4" v-if="selectedOption !== '-1'">
            <label for="to-value" class="w-1/3 mr-2">To:</label>
            <input
              type="text"
              id="to-value"
              v-model="toValue"
              @change="handleChange"
              class="focus:ring p-2 text-base border border-gray-300 rounded w-full transition duration-300"
            />
          </div>
        </template>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, watch } from "vue";
  
  // Props
  const props = defineProps({
    type: { type: String, required: true },
    label: { type: String, required: true },
    options: { type: Object, required: true },
    selectedOption: { type: String, default: "" },
    startDate: { type: String, default: "" },
    endDate: { type: String, default: "" },
    fromValue: { type: String, default: "" },
    toValue: { type: String, default: "" },
  });
  
  // Emits
  const emit = defineEmits([
    "update:selectedOption",
    "update:startDate",
    "update:endDate",
    "update:fromValue",
    "update:toValue",
    "change",
  ]);
  
  // Reactive variables
  const selectedOption = ref(props.selectedOption);
  const startDate = ref(props.startDate);
  const endDate = ref(props.endDate);
  const fromValue = ref(props.fromValue);
  const toValue = ref(props.toValue);
  
  // Watchers for two-way binding
  watch(selectedOption, (value) => emit("update:selectedOption", value));
  watch(startDate, (value) => emit("update:startDate", value));
  watch(endDate, (value) => emit("update:endDate", value));
  watch(fromValue, (value) => emit("update:fromValue", value));
  watch(toValue, (value) => emit("update:toValue", value));
  
  // Handle change event
  const handleChange = () => {
    emit("change", {
      selectedOption: selectedOption.value,
      startDate: startDate.value,
      endDate: endDate.value,
      fromValue: fromValue.value,
      toValue: toValue.value,
    });
  };
  </script>
   -->
   <template>
    <div>
      <!-- Panel Wrapper -->
      <div
        class="border rounded-lg p-4 mb-6 mt-4 relative w-full shadow-md shadow-gray-300"
        v-if="!sidebarVisible"
      >
        <!-- Date Range Selector -->
        <label
          class="block text-sm font-semibold absolute top-1 left-4 bg-white px-2 -mt-3"
          for="date-selector"
        >
          Date
        </label>
        <div class="flex items-center mb-4">
          <div class="w-full sm:w-2/3 mx-auto">
            <select
              v-model="selectedDate"
              id="date-selector"
              @change="handleDateChange"
              class="p-2 text-base border border-gray-300 rounded w-full focus:outline-none focus:ring transition duration-300"
            >
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
  
        <!-- Start Date Input -->
        <div class="flex items-center mb-4">
          <label for="start-date" class="w-1/3 mr-2">Start Date:</label>
          <input
            type="date"
            id="start-date"
            v-model="startDate"
            @change="fetchData"
            class="p-2 text-base border border-gray-300 rounded w-full transition duration-300"
          />
        </div>
  
        <!-- End Date Input -->
        <div class="flex items-center mb-4">
          <label for="end-date" class="w-1/3 mr-2">End Date:</label>
          <input
            type="date"
            id="end-date"
            v-model="endDate"
            @change="fetchData"
            class="p-2 text-base border border-gray-300 rounded w-full transition duration-300"
          />
        </div>
      </div>
  
      <!-- Weight Selector -->
      <div
        class="border rounded-lg p-4 mb-6 mt-4 relative w-full shadow-md shadow-gray-300"
        v-if="!sidebarVisible"
      >
        <label
          class="block text-sm font-semibold absolute top-1 left-4 bg-white px-2 -mt-3"
          for="weight-filter"
        >
          Weight
        </label>
        <div class="flex items-center mb-4">
          <div class="w-full sm:w-2/3 mx-auto">
            <select
              id="weight-filter"
              v-model="weightsValue"
              @change="handleWeightChange"
              class="focus:ring w-full rounded border border-gray-300 p-2 text-base transition duration-300"
            >
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
  
        <!-- From Weight Input -->
        <div class="flex items-center mb-4" v-if="weightsValue !== '-1'">
          <label for="from-weights-value" class="w-1/3 mr-2">From weight:</label>
          <input
            type="text"
            id="from-weights-value"
            v-model="fromWeightsValue"
            @change="fetchWeights"
            class="focus:ring p-2 text-base border border-gray-300 rounded w-full transition duration-300"
          />
        </div>
  
        <!-- To Weight Input -->
        <div class="flex items-center mb-4" v-if="weightsValue !== '-1'">
          <label for="to-weights-value" class="w-1/3 mr-2">To weight:</label>
          <input
            type="text"
            id="to-weights-value"
            v-model="toWeightsValue"
            @change="fetchWeights"
            class="focus:ring p-2 text-base border border-gray-300 rounded w-full transition duration-300"
          />
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue';
  import { api } from '@/api'; // Replace with your actual API
  
  // States
  const sidebarVisible = ref(false);
  const selectedDate = ref('today');
  const startDate = ref('');
  const endDate = ref('');
  const weightsValue = ref('');
  const fromWeightsValue = ref('');
  const toWeightsValue = ref('');
  
  // On mounted, set today as start and end date
  onMounted(() => {
    const today = new Date().toISOString().substr(0, 10);
    startDate.value = today;
    endDate.value = today;
  });
  
  // Methods
  const handleDateChange = async () => {
    try {
      const response = await api.get(`/date_picker_range?selected_option=${selectedDate.value}`);
      const data = response.data;
  
      startDate.value = data.start_date;
      endDate.value = data.end_date;
    } catch (error) {
      console.error('Error fetching date range:', error);
    }
  };
  
  const handleWeightChange = async () => {
    try {
      const response = await api.get(`/weights_filter?selected_weights_option=${weightsValue.value}`);
      const data = response.data;
  
      if (weightsValue.value === '-1') {
        fromWeightsValue.value = '-1';
        toWeightsValue.value = '-1';
      } else {
        const [fromWeight, toWeight] = weightsValue.value.split('-');
        fromWeightsValue.value = fromWeight || '';
        toWeightsValue.value = toWeight || '';
      }
    } catch (error) {
      console.error('Error fetching weight filter:', error);
    }
  };
  
  const fetchData = async () => {
    // This method will be triggered when either startDate or endDate changes
    console.log('Fetching data for:', startDate.value, endDate.value);
  };
  
  const fetchWeights = async () => {
    // This method will be triggered when either fromWeightsValue or toWeightsValue changes
    console.log('Fetching weights for:', fromWeightsValue.value, toWeightsValue.value);
  };
  </script>
  
  