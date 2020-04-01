import axios from 'axios'

const nodes = [
    {
        id:0,
        label:'0',
    },
    {
        id:1,
        label:1,
    },
    {
        id:2,
        label:2,
    },
    {
        id:3,
        label:3,
    }
]

const edges = [
    {
        id : 0,
        source: 0,
        target: 1,
        vechicels : 1,
        length: 1,
        capacity: 1,
        freeFlowTravelTime : 1.0,
        toll : 1.0,
    },
    {
        id : 1,
        source: 0,
        target: 2,
        vechicels : 2,
        length: 2,
        capacity: 2,
        freeFlowTravelTime : 2.0,
        toll : 2.0,
    },
    {
        id : 2,
        source: 0,
        target: 3,
        vechicels : 3,
        length: 3,
        capacity: 3,
        freeFlowTravelTime : 3,
        toll : 3.0,
    },
    {
        id : 3,
        source: 3,
        target: 0,
        vechicels : 4,
        length: 4,
        capacity: 4,
        freeFlowTravelTime : 4.0,
        toll : 4.0,
    },
    {
        id : 4,
        source: 2,
        target: 0,
        vechicels : 5,
        length: 5,
        capacity: 5,
        freeFlowTravelTime : 5.0,
        toll : 5.0,
    },
    {
        id : 5,
        source: 1,
        target: 0,
        vechicels : 6,
        length: 6,
        capacity: 6,
        freeFlowTravelTime : 6.0,
        toll : 6.0,
    },
    {
        id : 6,
        source: 1,
        target: 3,
        vechicels : 7,
        length: 5,
        capacity: 1,
        freeFlowTravelTime : 1.0,
        toll : 5.0,
    },
    {
        id : 7,
        source: 3,
        target: 2,
        vechicels : 8,
        length: 5,
        capacity: 1,
        freeFlowTravelTime : 1.0,
        toll : 5.0,
    }
]


export default{
    async initData(){
        let remoteData = {}
        try{
            const response = await axios.get("/data.json")
            console.log(response.data)
        } catch(error){
            console.log(error)
        }
        let data = {
            nodes: nodes,
            edges: edges,
        }
        data.originDestinationPairMatrix = new Array(data.nodes.length)
        for(let i = 0 ; i < data.originDestinationPairMatrix.length; i += 1){
            data.originDestinationPairMatrix[i] = new Array(data.nodes.length)
        }
        data.originDestinationPairMatrix[0][3] = {
            origin: 0,
            destination: 3,
            demand: 2,
            contained_roads:[ [0,3],[0,1],[1,3] ],
        }
        data.originDestinationPairMatrix[0][2] = {
            origin: 0,
            destination: 2,
            demand: 12,
            contained_roads:[ [0,3],[0,1],[1,3],[0,2],[3,2] ],
        } 
        let state = new Array(data.edges.length)
        for(let i = 0 ; i < state.length; i += 1){
            state[i] = new Array(data.nodes.length)
            for(let j = 0 ; j < state[i].length; j += 1){
                state[i][j] = 0
            }
        }
        console.log(state)
        state[0][1] = 1
        state[0][2] = 2
        state[0][3] = 3
        state[1][2] = 2
        data.state = state
        console.log(data)
        return data
    },
    step(){

    }
}