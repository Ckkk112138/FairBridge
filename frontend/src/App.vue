<template>
  <div class="button-container">
    <button @click="handleClick"
            class="button bg-blue-500">
      Download
    </button>
    <!-- New Upload Button -->
    <button v-if="showUploadButton" @click="handleUpload"
            class="button bg-green-500">
      Upload Crate
    </button>
    <UploadStatusComponent :isVisible="showModal" @update:isVisible="showModal = $event">
      <template #header>
        <h3>Upload Status</h3>
      </template>
      <section class="modal-body">
        <slot>{{ modalContent }}</slot>
      </section>
    </UploadStatusComponent>
  </div>
  <div>
    <DescriboCrateBuilder v-if="dataReady" :crate="crate" ref="describo"/>
    <p v-else>Loading data...(It may take a few minutes to fully load depending on the size of the data.)</p>
  </div>
</template>

<script>
import {ref, onMounted, watch, nextTick, computed} from 'vue';
import {useRoute} from "vue-router";
import DescriboCrateBuilder from "@describo/crate-builder-component/src/crate-builder/Shell.component.vue";
import UploadStatusComponent from './UploadStatusComponent.vue'; // Import the Modal Component

export default {
  name: 'App',
  components: {
    DescriboCrateBuilder,
    UploadStatusComponent // Register the Modal Component
  },
  setup() {
    const crate = ref({});
    const dataReady = ref(false);
    const describo = ref(null);
    const cm = ref(null);
    const showModal = ref(false);  // Controls visibility of the modal
    const modalContent = ref('');  // Holds content for the modal
    const showUploadButton = ref(true);

    const route = useRoute();
    const uniqueId = computed(() => route.params.uniqueId);
    console.log('Unique ID:', uniqueId.value);

    // Watch for dataReady to be true, then initialize the CrateManager
    watch(dataReady, (newVal) => {
      console.error('CrateManager initialized:', describo.value, newVal);
      if (newVal) {
        nextTick(() => {
          if (describo.value) {
            console.error('describo initialized:', describo.value, newVal);
            const describoInstance = describo.value;
            cm.value = describoInstance.cm;
            describoInstance.refresh();
          }
        });
      }
    });

    // Function to upload the crate data to the server
    const handleUpload = async () => {
      if (cm.value) {
        const crateNew = cm.value.exportCrate();
        try {
          const response = await fetch(`http://127.0.0.1:5000/store-fdo?unique_id=${uniqueId.value}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(crateNew)
          });
          const result = await response.json();
          if (response.ok) {
            modalContent.value = result.message;  // Using result.message directly for a cleaner display
            showUploadButton.value = false;
          } else {
            modalContent.value = 'Failed to save file: ' + result.message;
          }
          showModal.value = true;
        } catch (error) {
          console.error('Error uploading crate data:', error);
          modalContent.value = 'Error uploading crate data: ' + error.message;
          showModal.value = true;
        }
      } else {
        console.error('CrateManager is not initialized.');
        modalContent.value = 'CrateManager is not initialized.';
        showModal.value = true;
      }
    };


    // Function to poll the server for the processed data
    const pollForData = async () => {
      try {
        console.log('Unique ID:', uniqueId.value)
        const response = await fetch(`http://localhost:5000/is-data-ready/${uniqueId.value}`);
        const data = await response.json();
        if (data.ready) {
          await fetchCrateData();
        } else {
          setTimeout(pollForData, 2000); // Poll every 2 seconds
        }
      } catch (error) {
        console.error('Error checking if data is ready:', error);
        setTimeout(pollForData, 2000); // Retry in 2 seconds
      }
    };

    // Function to fetch the processed data from the server
    const fetchCrateData = async () => {
      try {
        const response = await fetch(`http://localhost:5000/get-processed-data/${uniqueId.value}`);
        if (response.ok) {
          const data = await response.json();
          crate.value = data;
          dataReady.value = true;
          console.error('Data Ready', dataReady.value);
        } else {
          console.error('Error fetching crate data:', response.statusText);
        }
      } catch (error) {
        console.error('Error fetching crate data:', error);
      }
    };

    // Function to download the crate data as a JSON file
    const handleClick = () => {
      if (cm.value) {
        const crateNew = cm.value.exportCrate();
        console.log(crateNew);
        downloadJSON(crateNew, 'crate-data.json');
      } else {
        console.error('CrateManager is not initialized.');
      }
    };

    const downloadJSON = (data, filename) => {
      const jsonStr = JSON.stringify(data, null, 2);
      const blob = new Blob([jsonStr], {type: 'application/json'});
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    };

    onMounted(() => {

      pollForData();
    });

    return {
      crate,
      dataReady,
      handleClick,
      handleUpload,
      describo,
      cm,
      showModal,
      modalContent,
      showUploadButton
    };
  }
};
</script>

<style scoped>
.button-container {
  position: fixed;
  bottom: 3px;
  left: 0;
  display: flex; /* Aligns buttons inline */
  gap: 10px; /* Spacing between buttons */
}

.button {
  padding: 4px 12px;
  color: white;
  border-radius: 8px;
  transition: background-color 0.3s ease-in-out;
  cursor: pointer;
}

.button:hover {
  backdrop-blur: 10px;
  opacity: 0.85;
}

.bg-blue-500 {
  background-color: #007BFF;
}

.bg-green-500 {
  background-color: #28A745;
}
</style>

