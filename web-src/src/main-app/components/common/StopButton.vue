<template>
  <button class="stop-btn waves-effect"
          :class="{ 'kill-mode': killEnabled }"
          :title="buttonTitle"
          @click.stop="handleClick">
    <i class="material-icons">{{ icon }}</i>
    <span v-if="killTimeout" class="timeout-badge">{{ killTimeout }}</span>
  </button>
</template>

<script>
import {axiosInstance} from '@/common/utils/axios_utils';

export default {
  name: 'StopButton',

  props: {
    executionId: {
      type: [String, Number],
      required: true
    }
  },

  data() {
    return {
      killEnabled: false,
      killTimeout: null,
      intervalId: null
    };
  },

  computed: {
    icon() {
      return this.killEnabled ? 'dangerous' : 'stop';
    },
    buttonTitle() {
      if (this.killEnabled) return 'Kill script';
      if (this.killTimeout) return `Stop (${this.killTimeout}s to kill)`;
      return 'Stop script';
    }
  },

  methods: {
    handleClick() {
      if (this.killEnabled) {
        this.killExecution();
      } else {
        this.stopExecution();
      }
    },

    stopExecution() {
      axiosInstance.post('executions/stop/' + this.executionId)
        .then(() => {
          M.toast({html: 'Stop signal sent'});
          this.startKillCountdown();
        })
        .catch(e => {
          M.toast({html: e.response?.data || 'Failed to stop script'});
        });
    },

    killExecution() {
      axiosInstance.post('executions/kill/' + this.executionId)
        .then(() => {
          M.toast({html: 'Script killed'});
          this.clearState();
          this.$emit('killed');
        })
        .catch(e => {
          M.toast({html: e.response?.data || 'Failed to kill script'});
        });
    },

    startKillCountdown() {
      this.killEnabled = false;
      this.killTimeout = 5;
      this.intervalId = setInterval(() => {
        this.tickCountdown();
      }, 1000);
    },

    tickCountdown() {
      if (this.killTimeout <= 1) {
        clearInterval(this.intervalId);
        this.intervalId = null;
        this.killEnabled = true;
        this.killTimeout = null;
      } else {
        this.killTimeout--;
      }
    },

    clearState() {
      if (this.intervalId) {
        clearInterval(this.intervalId);
        this.intervalId = null;
      }
      this.killEnabled = false;
      this.killTimeout = null;
    }
  },

  beforeDestroy() {
    this.clearState();
  }
};
</script>

<style scoped>
.stop-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  background-color: #e57373;
  color: white;
  position: relative;
  transition: background-color 0.2s ease;
}

.stop-btn:hover {
  background-color: #ef5350;
}

.stop-btn.kill-mode {
  background-color: #c62828;
}

.stop-btn.kill-mode:hover {
  background-color: #b71c1c;
}

.stop-btn i {
  font-size: 18px;
}

.timeout-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  background: #c62828;
  color: white;
  font-size: 10px;
  font-weight: bold;
  min-width: 16px;
  height: 16px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
}
</style>
