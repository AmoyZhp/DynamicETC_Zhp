<template>
    <div class="row">
        <div class="col">
            <div id="graph" ></div>
        </div>
    </div>
</template>
<script>
import G6 from "@antv/g6";
import { mapState } from "vuex";
export default {
    mounted: function() {
        this.initGraph();
    },
    methods: {
        async initGraph() {
            await this.$store.dispatch("init", "graph");
        }
    },
    computed: {
        ...mapState(['graph'])
    },
    data: function() {
        return {};
    }
};
</script>