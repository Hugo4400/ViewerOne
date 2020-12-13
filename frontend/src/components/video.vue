<template>
  <div class="yt-frame">
    <h1>VIDEO WILL GO HERE I SWEAR</h1>
    <iframe v-if="video" src="{{video}}"
            allow="autoplay; clipboard-write; encrypted-media; picture-in-picture" allowfullscreen>
    </iframe>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator';
import Axios from 'axios';

const config = {
  server: '127.0.0.1:5000',
};

@Component
export default class Video extends Vue {
  error = false

  video = false

  msg = ''

  // eslint-disable-next-line class-methods-use-this
  mounted() {
    Axios.get(`${config.server}/video`).then((res) => {
      if (res.status === 200) {
        if (!res.data.status) {
          this.error = true;
          this.msg = res.data.msg;
        } else if (res.data.ttl > 0) {
          this.video = res.data.fetched.items.id;
        } else {
          this.mounted();
        }
      } else {
        this.error = true;
        this.msg = res.statusText;
      }
    });
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
h3 {
  margin: 40px 0 0;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
</style>
