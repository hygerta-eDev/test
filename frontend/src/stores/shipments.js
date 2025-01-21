import { createStore } from 'vuex';

const store = createStore({
  state: {
    selectedRows: [],
    shipmentNumber: '',
    selectedStages: [],
    selectedZipcodes: [],
    mapLoaded: false,
    selectedRowIds: [1, 2, 3, 4],
    startDate: '',
    endDate: '',
    weightsValue: '',
    fromWeightsValue: '',
    toWeightsValue: '',
    logisticActivityValue: 'outbound',
    shipmentValue: 'Van',
    zipCode: '',
    distanceOriginValue: '1',
    radiusValue: '50',
    sidebarVisible: true,
    loading: false,
    loadingChart: false,
    buttonStyle: {},
    selectedDate: 'today',
    showTopButton: false,
    zoom: 5,
    center: { lat: 40.639, lng: -90.00 },
    currentZoom: 3,
    currentCenter: { lat: 37.7749, lng: -122.4194 },
    showParagraph: false,
    mapOptions: { zoomSnap: 0.5 },
    showMap: true,
    sortColumn: '',
    sortDirection: 'asc',
    markersData: [],
    shipmentdata: [],
    sortedResults: [],
    selectedRowss: [],
    dropdown: null,
    stageDropdown: null,
  },
  mutations: {
    SET_SELECTED_ROWS(state, rows) {
      state.selectedRows = rows;
    },
    ADD_SELECTED_ROW(state, row) {
      const index = state.selectedRows.findIndex((r) => r.id === row.id);
      if (index === -1) {
        state.selectedRows.push(row);
      } else {
        state.selectedRows.splice(index, 1);
      }
    },
    SET_SHIPMENT_NUMBER(state, number) {
      state.shipmentNumber = number;
    },
    SET_START_DATE(state, date) {
      state.startDate = date;
    },
    SET_END_DATE(state, date) {
      state.endDate = date;
    },
    // Add more mutations for other state properties as needed.
  },
  actions: {
    updateSelectedRows({ commit }, rows) {
      commit('SET_SELECTED_ROWS', rows);
    },
    toggleSelectedRow({ commit }, row) {
      commit('ADD_SELECTED_ROW', row);
    },
    updateShipmentNumber({ commit }, number) {
      commit('SET_SHIPMENT_NUMBER', number);
    },
    // Add more actions as needed.
  },
  getters: {
    getSelectedRows: (state) => state.selectedRows,
    getShipmentNumber: (state) => state.shipmentNumber,
    getStartDate: (state) => state.startDate,
    getEndDate: (state) => state.endDate,
    // Add more getters as needed.
  },
});

export default store;
