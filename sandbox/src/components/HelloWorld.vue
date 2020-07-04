<template>
  <div class="hello">
    <h1>{{ msg }}</h1>
    <p>
      For a guide and recipes on how to configure / customize this project,<br>
      check out the
      <a href="https://cli.vuejs.org" rel="noopener">vue-cli documentation</a>.
    </p>
    <h3>Installed CLI Plugins</h3>
    <ul>
      <li><a href="https://github.com/vuejs/vue-cli/tree/dev/packages/%40vue/cli-plugin-babel" rel="noopener">babel</a></li>
      <li><a href="https://github.com/vuejs/vue-cli/tree/dev/packages/%40vue/cli-plugin-eslint" rel="noopener">eslint</a></li>
    </ul>
    <h3>Essential Links</h3>
    <ul>
      <li><a href="https://vuejs.org" rel="noopener">Core Docs</a></li>
      <li><a href="https://forum.vuejs.org" rel="noopener">Forum</a></li>
      <li><a href="https://chat.vuejs.org" rel="noopener">Community Chat</a></li>
      <li><a href="https://twitter.com/vuejs" rel="noopener">Twitter</a></li>
      <li><a href="https://news.vuejs.org" rel="noopener">News</a></li>
      <li style="display: none;">HiddenItem</li>
    </ul>
    <h3>Ecosystem</h3>
    <ul>
      <li><a href="https://router.vuejs.org" rel="noopener">vue-router</a></li>
      <li><a href="https://vuex.vuejs.org" rel="noopener">vuex</a></li>
      <li><a href="https://github.com/vuejs/vue-devtools#vue-devtools" rel="noopener">vue-devtools</a></li>
      <li><a href="https://vue-loader.vuejs.org" rel="noopener">vue-loader</a></li>
      <li><a href="https://github.com/vuejs/awesome-vue" rel="noopener">awesome-vue</a></li>
    </ul>
  </div>
</template>

<script>
export default {
  name: 'HelloWorld',
  props: {
    msg: String
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
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
