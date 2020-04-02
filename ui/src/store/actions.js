import api from '@/api/api'
import {
	INIT_GRAPH
} from './mutation-types.js'

export default{
    async init({ commit }) {
        let data = await api.initData()
        console.log(data)
        let originDestinationPairMatrix = new Array(data.nodes.length)
        for(let i = 0; i < originDestinationPairMatrix.length; i++){
            originDestinationPairMatrix[i] = new Array(data.nodes.length)
        }

        console.log(originDestinationPairMatrix)
        for(let od of data.originDestinationPairs){
            console.log(od)
            originDestinationPairMatrix[od.origin][od.destination] = {
                origin : od.origin,
                destination : od.destination,
                containedRoads : od.containedRoads,
                demand : od.demand,
            }
        }
        
        commit({
            type: INIT_GRAPH,
            nodes: data.nodes,
            edges: data.edges,
            historyStates: data.historyStates,
            originDestinationPairMatrix: originDestinationPairMatrix,
        })
    },

    step({ dispatch, state, commit }) {

    },
}