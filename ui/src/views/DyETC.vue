<template>
    <div class="row">
        <LeftSideBar />
        <div class="col-lg-9">
            <router-view></router-view>
        </div>
    </div>
</template>
<script>

import LeftSideBar from "@/components/LeftSideBar"
export default {
    components:{
        LeftSideBar
    }
}
</script>