<template>
  <div v-if="visible" class="modal-overlay" :class="overlayClass" @click.self="handleOverlayClick">
    <div class="modal-dialog" :class="modalClass" :style="modalStyle">
      <div class="modal-header" :class="headerClass">
        <slot name="header">
          <h3 v-if="title" class="modal-title">{{ title }}</h3>
        </slot>
        <button
          v-if="showCloseButton"
          class="btn-close"
          :class="closeButtonClass"
          @click="close"
          :aria-label="closeLabel"
        >
          {{ closeText }}
        </button>
      </div>

      <div class="modal-body" :class="bodyClass">
        <slot></slot>
      </div>

      <div v-if="$slots.footer" class="modal-footer" :class="footerClass">
        <slot name="footer"></slot>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'BaseModal',

  props: {
    visible: {
      type: Boolean,
      default: false,
      required: true
    },
    title: {
      type: String,
      default: ''
    },
    modalClass: {
      type: [String, Object, Array],
      default: ''
    },
    overlayClass: {
      type: [String, Object, Array],
      default: ''
    },
    headerClass: {
      type: [String, Object, Array],
      default: ''
    },
    bodyClass: {
      type: [String, Object, Array],
      default: ''
    },
    footerClass: {
      type: [String, Object, Array],
      default: ''
    },
    closeButtonClass: {
      type: [String, Object, Array],
      default: ''
    },
    modalStyle: {
      type: Object,
      default: () => ({})
    },
    showCloseButton: {
      type: Boolean,
      default: true
    },
    closeText: {
      type: String,
      default: '×'
    },
    closeLabel: {
      type: String,
      default: 'Close modal'
    },
    closeOnOverlayClick: {
      type: Boolean,
      default: true
    }
  },

  methods: {
    close() {
      this.$emit('close');
    },

    handleOverlayClick() {
      if (this.closeOnOverlayClick) {
        this.close();
      }
    }
  }
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-index-modal-overlay);
}

.modal-dialog {
  background: white;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.33);
  max-width: 90%;
  max-height: 90%;
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}

.modal-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 500;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  line-height: 1;
  cursor: pointer;
  padding: 0;
  margin-left: 1rem;
  color: #666;
  transition: color 0.2s;
}

.btn-close:hover {
  color: #000;
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #e0e0e0;
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  flex-shrink: 0;
}
</style>
