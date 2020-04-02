import api from '@/api/api'
import {
	INIT_GRAPH
} from './mutation-types.js'

export default{
    async init({ commit }) {
        let data = await api.initData()
        console.log("received env data is : ",data)
        
        let originDestinationPairMatrixList = []
        for(let row of data.originDestinationPairsList){
            let originDestinationPairMatrix = new Array(data.nodes.length)
            for(let i = 0; i < originDestinationPairMatrix.length; i++){
                originDestinationPairMatrix[i] = new Array(data.nodes.length)
            }
            for(let od of row){
                originDestinationPairMatrix[od.origin][od.destination] = {
                    origin : od.origin,
                    destination : od.destination,
                    containedRoads : od.containedRoads,
                    demand : od.demand,
                }
            }
            originDestinationPairMatrixList.push(originDestinationPairMatrix)
        }
        
        commit({
            type: INIT_GRAPH,
            nodes: data.nodes,
            edges: data.edges,
            historyStates: data.historyStates,
            originDestinationPairMatrixList: originDestinationPairMatrixList,
        })
    },

    step({ dispatch, state, commit }) {

    },
}