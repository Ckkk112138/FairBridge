<template>
  <teleport to="body">
    <div v-if="isVisible" class="modal-overlay">
      <div class="modal-window">
        <header class="modal-header">
          <slot name="header">Default Header</slot>
          <button class="close-btn" @click="close">✕</button>
        </header>
        <section class="modal-body">
          <slot>Default Content</slot>
        </section>
        <footer class="modal-footer">
          <slot name="footer">
            <button class="close-btn" @click="close">Close</button>
          </slot>
        </footer>
      </div>
    </div>
  </teleport>
</template>

<script>
export default {
  name: 'UploadStatusComponent',
  props: {
    isVisible: Boolean,
  },
  methods: {
    close() {
      this.$emit('update:isVisible', false);
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(2px);
}

.modal-window {
  background-color: #007BFF; /* Bright blue background */
  color: #FFFFFF; /* White text for contrast */
  border-radius: 8px;
  padding: 20px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.modal-header, .modal-footer {
  padding: 10px;
  background-color: #006FDB; /* Slightly darker blue for header and footer */
  color: #FFFFFF; /* Ensure text is white for readability */
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-body {
  padding: 20px;
  background-color: #007BFF; /* Same as modal window background */
  color: #FFFFFF; /* White text */
}

.close-btn {
  border: none;
  background: none;
  color: #FFFFFF; /* White text */
  font-size: 15px; /* Larger close button */
  cursor: pointer;
}
</style>

