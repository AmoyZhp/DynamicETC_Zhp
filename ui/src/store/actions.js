import api from '@/api/api'
import {
    INIT_GRAPH,
    INIT_STATE,
    RENDER_GRAPH,
    UPDATE_TIME_STEP
} from './mutation-types.js'

export default{
    async init({ commit }, graphContainerName) {
        let data = await api.initData()
        console.log("received env data is : ",data)
        commit({
            type: INIT_STATE,
            trajectory: data.trajectory,
        })
        commit(INIT_GRAPH, graphContainerName)
        commit(UPDATE_TIME_STEP,0)
    },

    step({ dispatch, state, commit }) {
        
    },
}