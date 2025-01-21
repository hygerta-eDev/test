<template>
  <div class="item">
    <!-- <div v-if="loading" class="loading-bar-container">
      <div class="loading-bar" :style="{ width: progress + '%' }"></div>
    </div> -->
    <div v-if="loading" class="progress-bar">
  <div :style="{ width: progress + '%' }" class="progress"></div>
</div>

    <div ref="myChartContainer" class="p-16 item flex mt-20 mb-6">
      <div class="flex flex-col p-10">
        <ShipmentStatCard title="Number of shipments for today" :count="orderCountToday" />
        <ShipmentStatCard title="Number of shipments in last week" :count="orderCountLasWeek" />
      </div>
      <div class="flex flex-col p-10">
        <ShipmentStatCard title="Number of shipments in last month" :count="orderCountLastMonth" />
        <ShipmentStatCard title="Number of shipments in last year" :count="orderCountLastYear" />
      </div>
      <div class="mt-10" id="piechartContainer" :style="styleOptionsforpiechart"></div>
    </div>
    <!-- Line Chart Section -->
    <div class="flex flex-row p-10">
      <div id="linechartContainer" :style="styleOptionsforLineChart"></div>
      <!-- Monthly Orders Change -->
      <div class="flex flex-row p-10 space-x-8">
        <div class="mt-12 ml-12 flex-1">
          <div class="flex shadow-md shadow-gray-800 rounded-lg mb-8 bg-[#2363a3] p-8 flex-col">
            <div class="flex items-center mb-3">
              <div class="w-10 h-10 mr-3 inline-flex items-center justify-center rounded-full text-white flex-shrink-0">

                <i :class="percentageChange > 0 ? 'fa-solid fa-arrow-trend-up' : 'fa-solid fa-arrow-trend-down'"></i>
              </div>
              <h2 class="text-white text-lg font-medium">Monthly Orders Change</h2>
            </div>
            <div class="flex flex-col justify-between flex-grow">
              <div class="leading-relaxed text-4xl text-center text-white">
                <span v-if="percentageChange !== null">
                  {{ percentageChange > 0 ? '+' : '' }}{{ percentageChange.toFixed(2) }}%
                </span>
                <span v-else>Data not available</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- Map Containers -->
    <div class=" mb-24 p-10" style="display: flex; width: 100%; height: 500px;">
      <div ref="mapContainerOrigin" class="ml-1 border-2 border-amber-300" style="flex: 1; height: 100%;"></div>
      <div class="p-3"></div>
      <div ref="mapContainerDestination" class="mr-1 border-2 border-sky-300" style="flex: 1; height: 100%;"></div>
    </div>
    <!-- Bar Charts -->
    <div class="p-10">
      <div id="barchartContainer" :style="styleOptionsforbarchart"></div>
      <div id="barchartContainer2" :style="styleOptionsforbarchart"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import ShipmentStatCard from '@/components/ShipmentStatCard.vue';
import * as CanvasJS from '@canvasjs/charts';
import * as echarts from 'echarts';
import { api } from '@/api';
const loading = ref(false);
const progress = ref(0);
const piechart = ref(null);
const barchart = ref(null);
const barchart2 = ref(null);
const orderCountLastMonth = ref(0);
const orderCountTwoMonthsAgo = ref(0);
const linechart = ref(null);
const mapChart = ref(null);
const mapChartDestination = ref(null);
const percentageChange = ref(null);
const dailyOrderCounts = ref([]);
const orderCountToday = ref(0);
const orderCountLasWeek = ref(0);
const orderCountLastYear = ref(0);
const styleOptionsforpiechart = { width: '790px', height: '360px' };
const styleOptionsforbarchart = { width: '100%', height: '600px' };
const styleOptionsforLineChart = { width: '1190px', height: '400px' };
const styleOptionsForMap = { width: '500px', height: '500px' };
const shipmentData = ref([]);
const mapContainerDestination = ref(null);
const mapContainerOrigin = ref(null);
const shipmentDataDestination = ref([]);


const startLoading = () => {
  // loading.value = true;
  // progress.value = 0;
  // const interval = setInterval(() => {
    if (progress.value < 80) progress.value += 10;
  //   else clearInterval(interval);
  // });
};

const stopLoading = () => {
  // const completeInterval = setInterval(() => {
    if (progress.value < 100) progress.value += 10;
  //   else {
  //     clearInterval(completeInterval);
  //     setTimeout(() => (loading.value = false));
  //   }
  // });
};

const executeWithLoading = async (fn) => {
  // startLoading();
  try {
    await fn();
  } catch (error) {
    console.error("Error during execution:", error);
  } finally {
  }
};

onMounted(async () => {
  await executeWithLoading(initCharts);
  await executeWithLoading(fetchDataAndRenderCharts);
  await executeWithLoading(initMap);
});

const initMap = async () => {
  await executeWithLoading(async () => {
    if (!mapChart.value) {
      mapChart.value = echarts.init(mapContainerOrigin.value);
    }
    if (!mapChartDestination.value) {
      mapChartDestination.value = echarts.init(mapContainerDestination.value);
    }
    await loadGeoJSON('https://raw.githubusercontent.com/shawnbot/topogram/master/data/us-states.geojson', 'origin');
    await loadGeoJSON('https://raw.githubusercontent.com/shawnbot/topogram/master/data/us-states.geojson', 'destination');
  });
};
const loadGeoJSON = async (url, type) => {
  try {
    const response = await fetch(url);
    const geojson = await response.json();
    echarts.registerMap('USA', geojson);
    await fetchShipmentData(geojson, type);
  } catch (error) {
    console.error('Error loading GeoJSON data:', error);
  }
};

const fetchShipmentData = async (geojson, type) => {
  try {
    const originUrl = `/countoriginshipmentsHome`;
    const destinationUrl = `/countdestinationshipmentsHome`;

    const [originResponse, destinationResponse] = await Promise.all([
      api.get(originUrl),
      api.get(destinationUrl)
    ]);

    if (originResponse.status !== 200 || destinationResponse.status !== 200) {
      throw new Error('Error fetching shipment data');
    }

    const originData = originResponse.data.map(item => ({
      State: item.State && item.State.trim().toUpperCase(),
      ShipmentCount: item.ShipmentCount || 0,
    }));

    const originShipmentByState = originData.reduce((acc, item) => {
      if (item.State) {
        acc[item.State] = (acc[item.State] || 0) + item.ShipmentCount;
      }
      return acc;
    }, {});

    const destinationData = destinationResponse.data.map(item => ({
      State2: item.State2 && item.State2.trim().toUpperCase(),
      ShipmentCount: item.ShipmentCount || 0,
    }));

    const destinationShipmentByState = destinationData.reduce((acc, item) => {
      if (item.State2) {
        acc[item.State2] = (acc[item.State2] || 0) + item.ShipmentCount;
      }
      return acc;
    }, {});
    // progress.value = 10;

    prepareMapData(geojson, originShipmentByState, mapChart.value, '#FFEB3B', '#FF5722', '#D32F2F', 'origin');
    prepareMapData(geojson, destinationShipmentByState, mapChartDestination.value, '#E3F2FD', '#42A5F5', '#1565C0', 'destination');

  } catch (error) {
    console.error("Error fetching shipment data:", error);
  }
};
const prepareMapData = (geojson, shipmentByState, mapChartInstance, colorStart, colorMiddle, colorEnd, type) => {
  const nameAltToNameMap = geojson.features.reduce((map, feature) => {
    const nameAlt = feature.properties.name_alt.split('|')[0].trim().toUpperCase();
    map[nameAlt] = feature.properties.name;
    return map;
  }, {});
  const statesData = geojson.features.map(feature => {
    const stateNameAlt = feature.properties.name_alt.split('|')[0].trim().toUpperCase();
    const stateName = nameAltToNameMap[stateNameAlt];
    const shipmentCount = shipmentByState[stateNameAlt] || 0;
    return { name: stateName, value: shipmentCount };
  });
  const maxShipmentCount = Math.max(...statesData.map(item => item.value));
  const minShipmentCount = Math.min(...statesData.map(item => item.value));
  if (maxShipmentCount === 0) {
    statesData.forEach(state => { state.value = 1; });
  }
  renderMap(statesData, minShipmentCount, maxShipmentCount, mapChartInstance, colorStart, colorMiddle, colorEnd, type);
};
const renderMap = (statesData, minShipmentCount, maxShipmentCount, mapChartInstance, colorStart, colorMiddle, colorEnd, type) => {
  const colorRange = [colorStart, colorMiddle, colorEnd];
  const currentYear = new Date().getFullYear();
  const lastYear = currentYear - 1;
  const mapOptions = {
    title: {
      text: type === 'origin' ? `Origin Shipments (Year ${lastYear})` : `Destination Shipments (Year ${lastYear})`,
    },
    tooltip: {
      trigger: 'item',
      showDelay: 0,
      transitionDuration: 0.2,
      formatter: function (params) {
        return `${params.name}<br>Shipment Count: ${params.value}`;
      },
    },
    visualMap: {
      min: minShipmentCount,
      max: maxShipmentCount,
      text: ['High', 'Low'],
      calculable: true,
      inRange: { color: colorRange },
    },
    geo: {
      zoom: 1.6,
      map: 'USA',
      roam: true,
      itemStyle: {
        areaColor: '#E0E0E0',
        borderColor: '#FFFFFF',
      },
      emphasis: {
        label: { show: true, fontSize: 8, color: '#000' },
        itemStyle: { areaColor: '#C0C0C0' },
      },
    },
    series: [
      {
        type: 'map',
        roam: true,
        map: 'USA',
        geoIndex: 0,
        data: statesData,
      },
    ],
  };
  mapChartInstance.setOption(mapOptions);
};
const initCharts = async () => {
  await executeWithLoading(() => {
      piechart.value = new CanvasJS.Chart("piechartContainer", {
    theme: "light2",
    animationEnabled: true,
    title: { text: "All Shipments for today" },
    data: [{
      type: "doughnut",
      startAngle: 90,
      indexLabel: "{label} {y}",
      toolTipContent: "<span style='color: {color};'>{label}</span>, {y}",
      dataPoints: [],
    }],
  });

  barchart.value = new CanvasJS.Chart("barchartContainer", {
    theme: "light2",
    animationEnabled: true,
    title: { text: "Shipments in years 2022 and 2023" },
    axisY: { title: "Number of shipments", includeZero: true },
    legend: { cursor: "pointer", itemclick: toggleDataSeries },
    toolTip: { shared: true, content: toolTipFormatter },
    data: [
      { type: "column", showInLegend: true, name: "2022", color: "#4B0082", dataPoints: [] },
      { type: "column", showInLegend: true, name: "2023", color: "#81D4FA", dataPoints: [] },
    ],
  });
  barchart2.value = new CanvasJS.Chart("barchartContainer2", {
    theme: "light2",
    animationEnabled: true,
    title: { text: "Shipments in years 2023 and 2024" },
    axisY: { title: "Number of shipments", includeZero: true },
    legend: { cursor: "pointer", itemclick: toggleDataSeries2 },
    toolTip: { shared: true, content: toolTipFormatter2 },
    data: [
      { type: "column", showInLegend: true, name: "2023", color: "#fdd142", dataPoints: [] },
      { type: "column", showInLegend: true, name: "2024", color: "#04061f", dataPoints: [] },
    ],
  });
  linechart.value = new CanvasJS.Chart("linechartContainer", {
    theme: "light2",
    animationEnabled: true,
    title: {
      text: "Daily Shipments Comparison",
    },
    axisX: {
      title: "Day of the Month",
      valueFormatString: "##", // Show only day numbers (1-31)
    },
    axisY: {
      title: "Number of Shipments",
      includeZero: false,
    },
    data: [
      {
        type: "line",
        showInLegend: true,
        name: "Last Month",
        color: "#2363a3", // Color for last month
        dataPoints: [],
        toolTipContent: "{name}: <strong>{y}</strong> shipments on {x} {month} {year}", // Full date in tooltip
        toolTip: {
          contentFormatter: function (e) {
            let date = new Date(e.entries[0].dataPoint.x);
            let monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
            let month = monthNames[date.getMonth()];
            let day = date.getDate();
            let year = date.getFullYear();
            return `${e.entries[0].dataSeries.name}: <strong>${e.entries[0].dataPoint.y}</strong> shipments on ${day} ${month} ${year}`;
          }
        }
      },
      {
        type: "line",
        showInLegend: true,
        name: "Two Months Ago",
        color: "#FFA500", 
        dataPoints: [],
        toolTipContent: "{name}: <strong>{y}</strong> shipments on {x} {month} {year}", 
        toolTip: {
          contentFormatter: function (e) {
            let date = new Date(e.entries[0].dataPoint.x);
            let monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
            let month = monthNames[date.getMonth()];
            let day = date.getDate();
            let year = date.getFullYear();
            return `${e.entries[0].dataSeries.name}: <strong>${e.entries[0].dataPoint.y}</strong> shipments on ${day} ${month} ${year}`;
          }
        }
      }
    ]
  });
});

};
const fetchDataAndRenderCharts = async () => {
  try {
    await executeWithLoading(async () => {
      await Promise.all([
        fetchOrdersFortoday(),
        fetchOrdersForlastmonth(),
        fetchOrdersForlastweek(),
        fetchOrdersForlastyear(),
        fetchOrdersForLineChart(),
        fetchOrdersByState(),
        fetchOrdersByState2(),
        fetchOrdersByState3(),
        fetchOrdersByState4(),
        fetchOrdersForPieChart(),
      ]);

      calculatePercentageChange();

      if (piechart.value && barchart.value && barchart2.value) {
        piechart.value.render();
        barchart.value.render();
        barchart2.value.render();
      } else {
        console.error("Charts not initialized properly.");
      }
      
      // progress.value = 100;
    });
  } catch (error) {
    console.error("Error fetching data and rendering charts:", error);
  }
};
const fetchOrdersForPieChart = async () => {
  try {
    const today = new Date().toISOString().split('T')[0];
    const response = await api.get(`/originshipmentsfortoday?today=${today}`);
    const dataForPieChart = response.data;
    const shades = ['#e6f7ff', '#b3e0ff', '#80ccff', '#4da6ff', '#1a90ff'];
    const minValue = Math.min(...dataForPieChart.map(item => item.OrderCount));
    const maxValue = Math.max(...dataForPieChart.map(item => item.OrderCount));
    piechart.value.options.data[0].dataPoints = dataForPieChart.map((item) => ({
      label: item.Origin_State,
      y: item.OrderCount,
      color: calculateColor(item.OrderCount, minValue, maxValue, shades),
    }));
    // progress.value = 50;

  } catch (error) {
    console.error("Error fetching data for pie chart:", error);
    throw error;
  }
};
const fetchOrdersForLineChart = async () => {
  try {
    const responseLastMonth = await api.get(`/origin_shipments_for_LastMonth_Per_Day`);
    if (responseLastMonth.status !== 200) throw new Error(`Error fetching last month's data: ${responseLastMonth.statusText}`);
    const dataLastMonth = responseLastMonth.data;

    let lastMonthTotalOrders = 0;
    let lastMonthData = [];
    dataLastMonth.forEach(item => {
      const date = new Date(item.OrderDate);
      const day = date.getDate();
      const weekday = date.getDay(); // 0 = Sunday, 6 = Saturday
      if (weekday !== 0 && weekday !== 6) { // Exclude weekends
        lastMonthData.push({ x: day, y: item.OrderCount });
        lastMonthTotalOrders += item.OrderCount;
      }
    });
    orderCountLastMonth.value = lastMonthTotalOrders;

    if (linechart.value) {
      linechart.value.options.data[0].dataPoints = lastMonthData;
    }

    const responseTwoMonthsAgo = await api.get(`/origin_shipments_for_TwoMonthsAgo`);
    if (responseTwoMonthsAgo.status !== 200) throw new Error(`Error fetching two months ago data: ${responseTwoMonthsAgo.statusText}`);
    const dataTwoMonthsAgo = responseTwoMonthsAgo.data;

    let twoMonthsAgoTotalOrders = 0;
    let twoMonthsAgoData = [];
    dataTwoMonthsAgo.forEach(item => {
      const date = new Date(item.OrderDate);
      const day = date.getDate();
      const weekday = date.getDay(); // 0 = Sunday, 6 = Saturday
      if (weekday !== 0 && weekday !== 6) { // Exclude weekends
        twoMonthsAgoData.push({ x: day, y: item.OrderCount });
        twoMonthsAgoTotalOrders += item.OrderCount;
      }
    });
    orderCountTwoMonthsAgo.value = twoMonthsAgoTotalOrders;

    if (linechart.value) {
      linechart.value.options.data[1].dataPoints = twoMonthsAgoData;
    }

    calculatePercentageChange(orderCountLastMonth.value, orderCountTwoMonthsAgo.value);

    if (linechart.value) {
      linechart.value.render();
    }
  } catch (error) {
    console.error("Error fetching data for line chart:", error);
  }
};

const calculatePercentageChange = () => {
  if (orderCountLastMonth.value !== null && orderCountTwoMonthsAgo.value !== null) {
    const change = ((orderCountLastMonth.value - orderCountTwoMonthsAgo.value) / orderCountTwoMonthsAgo.value) * 100;
    percentageChange.value = change;
  } else {
    console.error("Order counts for last month or two months ago are missing.");
  }
};
const calculateColor = (value, minValue, maxValue, shades) => {
  const percentage = (value - minValue) / (maxValue - minValue);
  const index = Math.floor(percentage * (shades.length - 1));
  return shades[index];
};
const fetchData = async (apiEndpoint, index) => {
  try {
    const response = await api.get(`/${apiEndpoint}`);
    const dataForBarChart = response.data;

    if (barchart.value) {
      barchart.value.options.data[index].dataPoints = dataForBarChart.map(item => ({
        label: item.Origin_State,
        y: item.OrderCount,
      }));
    }
  // Update progress
  // progress.value = 80;


  } catch (error) {
    console.error(`Error fetching data from ${apiEndpoint}:`, error);
    throw error;
  }
};
const fetchOrdersByState = async () => {
  await fetchData('origin_shipments_for_Years_barchart?first_day_of_the_year=2022-01-01&last_day_of_the_year=2023-01-01', 0);
};
const fetchOrdersByState2 = async () => {
  await fetchData('origin_shipments_for_Years_barchart?first_day_of_the_year=2023-01-01&last_day_of_the_year=2024-01-01', 1);
};
const toolTipFormatter = (e) => {
  let content = "";
  const percentageDifference = (e.entries[1].dataPoint.y - e.entries[0].dataPoint.y) / e.entries[0].dataPoint.y;
  content += `<strong>${e.entries[0].dataPoint.label}</strong>`;
  content += ` (<span style="color: ${percentageDifference >= 0 ? "green" : "red"}"> ${percentageDifference >= 0 ? "↑" : "↓"} ${CanvasJS.formatNumber(Math.abs(percentageDifference), "#0.##%")}</span>)<br/>`;

  for (let i = 0; i < e.entries.length; i++) {
    content += `<span style="color:${e.entries[i].dataSeries.color}">${e.entries[i].dataSeries.name}</span>: <strong>${e.entries[i].dataPoint.y}</strong><br/>`;
  }
  return content;
};
const toggleDataSeries = (e) => {
  if (typeof e.dataSeries.visible === "undefined" || e.dataSeries.visible) {
    e.dataSeries.visible = false;
  } else {
    e.dataSeries.visible = true;
  }
  e.chart.render();
};
const fetchData2 = async (apiEndpoint, index) => {
  try {
    const response = await api.get(`/${apiEndpoint}`);
    const dataForBarChart2 = response.data;

    if (barchart2.value) {
      barchart2.value.options.data[index].dataPoints = dataForBarChart2.map(item => ({
        label: item.Origin_State,
        y: item.OrderCount,
      }));
    }
    // progress.value = 90;

  } catch (error) {
    console.error(`Error fetching data from ${apiEndpoint}:`, error);
    throw error;
  }
};
const fetchOrdersByState3 = async () => {
  await fetchData2('origin_shipments_for_Years_barchart?first_day_of_the_year=2023-01-01&last_day_of_the_year=2024-01-01', 0);
};
const fetchOrdersByState4 = async () => {
  await fetchData2('origin_shipments_for_Years_barchart?first_day_of_the_year=2024-01-01&last_day_of_the_year=2025-01-01', 1);
};
const toolTipFormatter2 = (e) => {
  let content = "";
  const percentageDifference = (e.entries[1].dataPoint.y - e.entries[0].dataPoint.y) / e.entries[0].dataPoint.y;
  content += `<strong>${e.entries[0].dataPoint.label}</strong>`;
  content += ` (<span style="color: ${percentageDifference >= 0 ? "green" : "red"}"> ${percentageDifference >= 0 ? "↑" : "↓"} ${CanvasJS.formatNumber(Math.abs(percentageDifference), "#0.##%")}</span>)<br/>`;

  for (let i = 0; i < e.entries.length; i++) {
    content += `<span style="color:${e.entries[i].dataSeries.color}">${e.entries[i].dataSeries.name}</span>: <strong>${e.entries[i].dataPoint.y}</strong><br/>`;
  }
  return content;
};
const toggleDataSeries2 = (e) => {
  if (typeof e.dataSeries.visible === "undefined" || e.dataSeries.visible) {
    e.dataSeries.visible = false;
  } else {
    e.dataSeries.visible = true;
  }
  e.chart.render();
};
const fetchOrdersFortoday = async () => {
  try {
    const today = new Date().toISOString().split('T')[0];
    const response = await api.get(`/origin_shipments_for_Today?today=${today}`);
    const dataFortoday = response.data;

    orderCountToday.value = dataFortoday[0]?.OrderCount;
    // progress.value = 10;

  } catch (error) {
    console.error("Error fetching data for today:", error);
    throw error;
  }
};
const fetchOrdersForlastweek = async () => {
  try {
    const response = await api.get(`/origin_shipments_for_LastWeek`);
    const dataForlastweek = response.data;

    orderCountLasWeek.value = dataForlastweek[0]?.OrderCount;
    // progress.value = 20;

  } catch (error) {
    console.error("Error fetching data for last week:", error);
    throw error;
  }
};
const fetchOrdersForlastmonth = async () => {
  try {
    const response = await api.get(`/origin_shipments_for_LastMonth`);
    const dataForlastmonth = response.data;
    orderCountLastMonth.value = dataForlastmonth[0]?.OrderCount;
    progress.value = 30;

  } catch (error) {
    console.error("Error fetching data for last month:", error);
    throw error;
  }
};
const fetchOrdersForlastyear = async () => {
  try {
    const response = await api.get(`/origin_shipments_for_LastYear`);
    const dataForlastyear = response.data;
    const totalOrderCount = dataForlastyear.reduce((sum, item) => sum + item.OrderCount, 0);
    orderCountLastYear.value = totalOrderCount;
    progress.value = 40;

  } catch (error) {
    console.error("Error fetching data for last year:", error);
    throw error;
  }
};
</script>

<style scoped>


</style>
