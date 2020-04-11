
export default{
    trafficStateHisotry: state => {
        let trafficStateHisotry = []
        for (let dyetcState of state.trajectory) {
            trafficStateHisotry.push(dyetcState.trafficState)
        }
        return trafficStateHisotry
    },
    originDestPairMatrixHisotry: state => {
        let originDestPairMatrixHisotry = []
        for (let dyetcState of state.trajectory) {
            originDestPairMatrixHisotry.push(dyetcState.originDestPairMatrix)
        }
        return originDestPairMatrixHisotry
    }
}