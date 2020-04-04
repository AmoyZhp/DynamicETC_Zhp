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
        let remoteData = null
        try{
            const response = await axios.get("/data.json")
            remoteData =  response.data
        } catch(error){
            console.log(error)
        }
        return remoteData
    },
    step(){

    }
}