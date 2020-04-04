import {
    INIT_GRAPH,
    UPDATE_TIME_STEP,
    INIT_STATE,
} from './mutation-types.js'
import G6 from "@antv/g6"
import conf from "@/config/graph"

export default {

    [INIT_STATE](state, payload) {
        state.timestep = 0
        let trajectory = payload.trajectory
        for (let dyetcState of trajectory) {
            let trafficState = dyetcState.trafficState
            let zones = []
            for (let zone of dyetcState.zones) {
                zones.push({
                    id: zone.id,
                    label: zone.label
                })
            }
            let roads = []
            for (let road of dyetcState.roads) {
                roads.push({
                    id: road.id,
                    source: road.source,
                    target: road.target,
                    vehicles: road.vehicles,
                    toll: road.toll,
                    length: road.length,
                    capacity: road.capacity,
                    freeFlowTravelTime: road.freeFlowTravelTime,
                    label: road.label
                })
            }

            // 把 road list 还原成 road matrix
            let roadsMatrix = new Array(zones.length)
            for (let i = 0; i < roadsMatrix.length; i++) {
                roadsMatrix[i] = new Array(zones.length)
            }
            for (let road of roads) {
                roadsMatrix[road.source][road.target] = road
            }
            // 把 od list 还原成 od matrix
            let originDestPairMatrix = new Array(zones.length)
            for (let i = 0; i < originDestPairMatrix.length; i++) {
                originDestPairMatrix[i] = new Array(zones.length)
            }

            for (let od of dyetcState.originDestPairs) {
                originDestPairMatrix[od.origin][od.destination] = {
                    origin: od.origin,
                    destination: od.destination,
                    containedRoads: od.containedRoads,
                    demand: od.demand,
                }
            }
            // 把 od matrix  road matrix , zones 和 roads 押入 轨迹中
            state.trajectory.push({
                zones: zones,
                roads: roads,
                trafficState: trafficState,
                roadsMatrix: roadsMatrix,
                originDestPairMatrix: originDestPairMatrix,
            })
        }
        console.log(state.trajectory)
    },

    [INIT_GRAPH](state, containerName) {
        state.graph = new G6.Graph({
            container: containerName, // String | HTMLElement，必须，创建的容器 id 或容器本身
            width: conf.width, // Number，必须，图的宽度
            height: conf.height, // Number，必须，图的高度
            layout: conf.layout,
            modes: conf.modes,
            defaultNode: conf.defaultNode,
            defaultEdge: conf.defaultEdge,
            nodeStateStyles: conf.nodeStateStyles,
            edgeStateStyles: conf.edgeStateStyles
        });
        state.graph.on("node:click", e => {
            // 先将所有当前是 click 状态的节点置为非 click 状态
            const clickNodes = state.graph.findAllByState("node", "click");
            clickNodes.forEach(cn => {
                state.graph.setItemState(cn, "click", false);
            });
            const nodeItem = e.item; // 获取被点击的节点元素对象
            state.graph.setItemState(nodeItem, "click", true); // 设置当前节点的 click 状态为 true
        });
        state.graph.on("edge:click", e => {
            // 先将所有当前是 click 状态的边置为非 click 状态
            const clickEdges = state.graph.findAllByState("edge", "click");
            clickEdges.forEach(ce => {
                state.graph.setItemState(ce, "click", false);
            });
            const edgeItem = e.item; // 获取被点击的边元素对象
            const cfg = edgeItem.defaultCfg;
            let id = cfg.id.split("-")[1];
            console.log(id)
            state.selectedEdge = state.roads[id];
            let edgeDetail = [];
            for (let index in state.trafficState[id]) {
                let num = state.trafficState[id][index];
                if (num != 0) {
                    edgeDetail.push({
                        id: index,
                        number: num
                    });
                }
            }
            state.selectedEdge.detail = edgeDetail;
            if (edgeDetail.length > 0) {
                state.edgesDetail = true;
            }
            state.graph.setItemState(edgeItem, "click", true); // 设置当前边的 click 状态为 true
        });
        // 监听鼠标进入节点事件
        state.graph.on("node:mouseenter", evt => {
            const node = evt.item;
            // 激活该节点的 hover 状态
            state.graph.setItemState(node, "hover", true);
        });
        // 监听鼠标离开节点事件
        state.graph.on("node:mouseleave", evt => {
            const node = evt.item;
            // 关闭该节点的 hover 状态
            state.graph.setItemState(node, "hover", false);
        });
    },

    [UPDATE_TIME_STEP] (state, timestep){
        /**
         * 当前的所有状态会根据 timestep 的变换而变化
         */
        if (timestep >= 0 && timestep < state.trajectory.length) {
            state.timestep = timestep
            state.zones = state.trajectory[state.timestep].zones
            state.roads = state.trajectory[state.timestep].roads
            state.trafficState = state.trajectory[state.timestep].trafficState
            state.roadsMatrix = state.trajectory[state.timestep].roadsMatrix
            state.originDestPairMatrix = state.trajectory[state.timestep].originDestPairMatrix
            // 生成用于渲染图的数据（nodes，edge）
            state.renderData.nodes = []
            for (let zone of state.zones) {
                state.renderData.nodes.push({
                    id: 'n-' + zone.id,
                    label: '' + zone.label,
                })
            }
            state.renderData.edges = []
            for (let road of state.roads) {
                let vehicles = road.vehicles
                let lineWidth = (vehicles / 500) * 5
                if( lineWidth < 1 ){
                    lineWidth = 1
                }
                if( lineWidth > 5 ){
                    lineWidth = 5
                }
                state.renderData.edges.push({
                    id: 'e-' + road.id,
                    source: 'n-' + road.source,
                    target: 'n-' + road.target,
                    style:{
                        cursor: "pointer",
                        lineAppendWidth: 5, //边响应鼠标事件时的检测宽度
                        opacity: 0.6, // 边透明度
                        stroke: "#bae7ff", // 边描边颜色
                        endArrow: true, //在边的结束点画箭头
                        lineWidth: lineWidth
                    },
                })
            }
            state.graph.data(state.renderData); // 读取数据到图源上
            state.graph.render(); // 渲染图
        }
    },

}