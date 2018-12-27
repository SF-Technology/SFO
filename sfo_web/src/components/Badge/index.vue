<template>
  <div class="my-badge">
    <slot></slot>
    <span class="my-badge__content"
          v-show="!hidden && (content || content === 0 || isDot)"
          v-text="content"
          :class="{ 'is-fixed': $slots.default, 'is-dot': isDot }"></span>
  </div>
</template>

<script>
    export default {
      name: "badge",
      props: {
        value: {},
        max: Number,
        isDot: Boolean,
        hidden: Boolean
      },
      computed: {
        content() {
          if (this.isDot) return;

          const value = this.value;
          const max = this.max;

          if (typeof value === 'number' && typeof max === 'number') {
            return max < value ? `${max}+` : value;
          }

          return value;
        }
      }
    }
</script>

<style scoped>
  .my-badge {
    display: inline-block;
    position: relative;
  }
  .my-badge__content {
    background-color:#f56c6c;
    border-radius:10px;
    color:#fff;
    display:inline-block;
    font-size:12px;
    height:18px;
    line-height:18px;
    padding:0 6px;
    text-align:center;
    white-space:nowrap;
    border:1px solid #fff;
    position: absolute;
    right: 10px;
    top: 0;
    transform: translateX(100%);
  }
</style>
