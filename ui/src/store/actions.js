import api from '@/api/api'
import {
	INIT_GRAPH
} from './mutation-types.js'

export default{
    async init({ commit }) {
        let data = await api.initData()
        console.log(data)
        commit({
            type: INIT_GRAPH,
            nodes: data.nodes,
            edges: data.edges,
            dyetcState: data.state,
            originDestinationPairMatrix: data.originDestinationPairMatrix,
        })
    },

    step({ dispatch, state, commit }) {

    },
}