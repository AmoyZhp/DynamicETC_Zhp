<template>
    <div class="row">
        <div class="col">
            <div class="row">
                <div class="col">
                    <table class="table">
                        <thead>
                            <tr>
                                <th scope="col">timestep : {{timestep}}</th>
                                <th v-for="node in nodes" :key="node.id" scope="col">n-{{node.id}}</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="(row, index) in currentState" :key="index" scope="col">
                                <th scope="row">{{edges[index].source}} -> {{edges[index].target}}</th>
                                <td v-for="(num, index) in row" :key="index">{{num}}</td>
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
                                <a class="page-link" href="#" aria-label="Previous" @click="selectState(timestep-1)">
                                    <span aria-hidden="true">&laquo;</span>
                                </a>
                            </li>
                            <li v-for="(row, index) in historyStates" :key="index" class="page-item" v-bind:class="{ active: index == timestep }">
                                <a
                                    class="page-link"
                                    href="#"
                                    @click="selectState(index)"
                                    
                                >{{index}}
                                    
                                </a>
                            </li>
                            <li class="page-item">
                                <a class="page-link" href="#" aria-label="Next" @click="selectState(timestep+1)">
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
import { mapState, mapMutations } from "vuex";

export default {
    mounted: function(){
      this.currentState = this.historyStates[0]  
    },
    methods: {
        selectState(index){
            if(index >= 0 && index < this.historyStates.length){
                this.timestep = index
                this.currentState = this.historyStates[index]
            }
        },
        ...mapMutations(["SELECT_STATE"])
    },
    computed: {
        ...mapState(["nodes", "edges", "historyStates"])
    },
    data: function(){
        return{
            timestep: 0,
            currentState: {}
        }
    }
};
</script>