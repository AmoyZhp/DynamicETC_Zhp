<template>
    <div class="row">
        <LeftSideBar />
        <div class="col-lg-9">
            <div id="graph"></div>
        </div>
    </div>
</template>
<script>
import G6 from "@antv/g6";
import { mapState } from "vuex";
import LeftSideBar from "@/components/LeftSideBar"

export default {
    components:{
        LeftSideBar,
    },
    mounted: function() {
        this.initGraph();
    },
    methods: {
        async initGraph() {
            await this.$store.dispatch("init");
        },
    },
    computed: {

    },
    data: function() {
        return {

        };
    }
};



</script>
<style scoped>
.card {
    background-color: rgba(0, 0, 128, 0.1);
}
.card-header {
    background-color: rgba(0, 0, 128, 0.1);
}
li.list-group-item {
    background-color: rgba(176, 224, 230, 0.1);
}
li.sub-list-group-item {
    background-color: rgba(0, 206, 209, 0.1);
}


</style>