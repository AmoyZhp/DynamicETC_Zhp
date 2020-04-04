<template>
    <div class="row">
        <div class="col">
            <div class="row">
                <div class="col">
                    <table class="table">
                        <thead>
                            <tr>
                                <th scope="col">timestep : {{timestep}}</th>
                                <th v-for="node in zones" :key="node.id" scope="col">n-{{node.id}}</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="(row, index) in originDestPairMatrix" :key="index">
                                <th scope="row">n-{{index}}</th>
                                <td
                                    v-for="(od, index) in row"
                                    :key="index"
                                >{{od == null? 0 : od.demand}}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            <div class="row">
                <div class="col-lg-4 offset-lg-4">
                    <nav>
                        <ul class="pagination">
                            <li class="page-item">
                                <a
                                    class="page-link"
                                    href="#"
                                    aria-label="Previous"
                                    @click="selectOD(timestep-1)"
                                >
                                    <span aria-hidden="true">&laquo;</span>
                                </a>
                            </li>
                            <li
                                v-for="(row, index) in originDestPairMatrix"
                                :key="index"
                                class="page-item"
                                v-bind:class="{ active: index == timestep }"
                            >
                                <a class="page-link" href="#" @click="selectOD(index)">{{index}}</a>
                            </li>
                            <li class="page-item">
                                <a
                                    class="page-link"
                                    href="#"
                                    aria-label="Next"
                                    @click="selectOD(timestep+1)"
                                >
                                    <span aria-hidden="true">&raquo;</span>
                                </a>
                            </li>
                        </ul>
                    </nav>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
import { mapState, mapGetters } from "vuex";
export default {
    mounted: function() {
        this.originDestPairMatrix = this.originDestPairMatrixHisotry[
            this.timestep
        ];
        console.log(this.originDestPairMatrixHisotry)
    },
    methods: {
        selectOD(index) {
            if (index >= 0 && index < this.originDestPairMatrixHisotry.length) {
                this.originDestPairMatrix = this.originDestPairMatrixHisotry[
                    index
                ];
                this.timestep = index;
            }
        }
    },
    computed: {
        ...mapState(['zones']),
        ...mapGetters([
            "originDestPairMatrixHisotry"
            // ...
        ]),
    },
    data: function() {
        return {
            originDestPairMatrix: {},
            timestep: 0
        };
    }
};
</script>