<script setup></script>

<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary sticky-top">
    <router-link class="navbar-brand" to="/">StrikeTraX</router-link>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
      <span class="navbar-toggler-icon"></span>
    </button>

    <div class="collapse navbar-collapse" id="navbarSupportedContent">
      <ul class="navbar-nav">
        <li class="nav-item">
          <router-link class="nav-link" active-class="active" to="/">Home
          </router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link" active-class="active" to="/scoring">Log Game</router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link" active-class="active" to="/history">History</router-link>
        </li>
      </ul>
    </div>
  </nav>
  <router-view />
</template>

<style scoped></style>
