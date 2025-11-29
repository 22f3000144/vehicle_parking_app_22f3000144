<script setup>

</script>

<template>
  <header>
    Parking Application
  </header>

   <img alt="Vue logo" class="logo" src="../assets/logo.png" width="150" height="150" />

    <div>
      <nav>
        <RouterLink to="/register">Sine-In</RouterLink><br>
        <!-- <RouterLink to="/about">About</RouterLink> -->
        <RouterLink to="/userlogin">User-Login</RouterLink><br>
        <RouterLink to="/adminlogin">Admin-Login</RouterLink>

      </nav>
    </div>
</template>

<style>
:root{
  --color-1:#005840;   /* 60% */
  --color-2:#D1F843;   /* 30% */
  --color-3:#ECF0EF;   /* 10% */
}



/* Header bar */
header{
  text-align:center;
  padding:1rem 0;
  font-size:1.6rem;
  color:#fff;
  font-weight:600;
  background: var(--color-1);
  border-bottom:3px solid var(--color-2);
}

/* Center logo + nav */
.logo {
  display:block;
  margin:2rem auto 1rem auto;
}

/* Navigation */
nav{
  text-align:center;
  margin-top:1rem;
  line-height: 2.2rem;
}




</style>
