<template>
    <div class="container-fluid">
        <div class="row">
            <div class="col ">
                <nav class="navbar navbar-dark bg-dark">
                    <router-link class="navbar-brand" to="/graph">Dynamic ETC</router-link>
                    <ul class="navbar-nav">
                        <li class="nav-item" > <router-link class="navbar-brand" to="/stateTable">State table</router-link> </li>
                    </ul>
                </nav>
            </div>
        </div>
        <router-view></router-view>
    </div>
</template>
<script>

export default {
    
};
</script>