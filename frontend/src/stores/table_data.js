// stores/tableDataStore.js
// import { defineStore } from 'pinia';

// export const useTableDataStore = defineStore('tableData', {
//     state: () => ({
//         data: [], // Holds the table data
//     }),
//     actions: {
//         setTableData(newData) {
//             this.data = newData;
//         },
//         clearTableData() {
//             this.data = [];
//         },
//     },
//     persist: true, // Optional if using a Pinia plugin for persistence
// });
import { defineStore } from 'pinia';

export const useTableDataStore = defineStore('tableData', {
    state: () => ({
        results: [], // State to hold table data
    }),
    actions: {
        setResults(data) {
            this.results = data;
        },
    },
});
