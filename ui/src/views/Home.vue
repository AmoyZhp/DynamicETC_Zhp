<template>
    <div class="container-fluid">
        <div class="row">
            <div class="col ">
                <nav class="navbar navbar-dark bg-dark">
                    <a class="navbar-brand" href="#">Dynamic ETC</a>
                </nav>
            </div>
        </div>
        <Graph />
    </div>
</template>
<script>
import Graph from "@/components/Graph";

export default {
    components: {
        Graph
    }
};
</script>