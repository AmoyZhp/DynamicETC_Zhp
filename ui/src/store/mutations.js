import {
    INIT_GRAPH,
    FIND_OD,
    STEP,
    SELECT_STATE
} from './mutation-types.js'
import G6 from "@antv/g6"
import conf from "@/config/graph"

export default {
    [INIT_GRAPH] (state, { nodes, edges, historyStates, originDestinationPairMatrix}) {
        state.nodes = nodes
        state.edges = edges
        state.historyStates = historyStates
        
        state.timestep = 0
        state.currentState = state.historyStates[state.timestep]
        state.originDestinationPairMatrix = originDestinationPairMatrix
        // 生成用于渲染图的数据（nodes，edge）
        state.data.nodes = []
        state.edgesMatrix = new Array(state.nodes.length)
        for(let i = 0; i < state.nodes.length; i++){
            state.edgesMatrix[i] = new Array(state.nodes.length)
        }
        for (let index in state.nodes) {
            let node = state.nodes[index]
            state.data.nodes.push({
                id: 'n-'+node.id,
                label: ''+node.label,
            })
        }
        state.data.edges = []
        for (let index in state.edges) {
            let edge = state.edges[index]
            let vechicels = edge.vechicels
            state.data.edges.push({
                id: 'e-' + index,
                source: 'n-'+edge.source,
                target: 'n-'+edge.target,
            })
            state.edgesMatrix[edge.source][edge.target] = edge
        }
        state.graph = new G6.Graph({
            container: "graph", // String | HTMLElement，必须，创建的容器 id 或容器本身
            width: conf.width, // Number，必须，图的宽度
            height: conf.height, // Number，必须，图的高度
            layout: conf.layout,
            modes: conf.modes,
            defaultNode: conf.defaultNode,
            defaultEdge: conf.defaultEdge,
            nodeStateStyles: conf.nodeStateStyles,
            edgeStateStyles: conf.edgeStateStyles
        });
        state.graph.data(state.data); // 读取数据到图源上
        state.graph.render(); // 渲染图
        state.graph.on("node:click", e => {
            // 先将所有当前是 click 状态的节点置为非 click 状态
            const clickNodes = state.graph.findAllByState("node", "click");
            clickNodes.forEach(cn => {
                state.graph.setItemState(cn, "click", false);
            });
            const nodeItem = e.item; // 获取被点击的节点元素对象
            const cfg = nodeItem.defaultCfg;
            console.log(cfg);
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
            console.log(cfg);
            let id = cfg.id.split("-")[1];
            state.selectedEdge = state.edges[id];
            console.log(state.selectedEdge)
            let edgeDetail = [];
            for (let index in state.currentState[id]) {
                let num = state.currentState[id][index];
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
    [FIND_OD](state, payload){
        let origin = payload.origin
        let destination = payload.destination
        let {graph, originDestinationPairMatrix, 
            edgesMatrix} = state
        const clickEdges = graph.findAllByState(
            "edge",
            "click"
        );
        clickEdges.forEach(ce => {
            graph.setItemState(ce, "click", false);
        });
        if ( origin >= 0 &&
            origin < originDestinationPairMatrix.length &&
            destination >= 0 &&
            destination < originDestinationPairMatrix.length
        ) {
            let od = originDestinationPairMatrix[origin][
                destination
            ];
            if (od != null) {
                state.selectedOD = od
                let edgesId = od.containedRoads;
                edgesId.forEach(e => {
                    let src = e[0];
                    let target = e[1];
                    let edge = edgesMatrix[src][target];
                    if (edge != null) {
                        let edgeItem = graph.findById(
                            "e-" + edge.id
                        );
                        graph.setItemState(
                            edgeItem,
                            "click",
                            true
                        );
                    }
                });
            }
        }
    },
    [STEP](state){
        state.timestep += 1
        state.currentState = state.historyStates[state.timestep]
    },
    
    [SELECT_STATE](state, index){
        if(index >= 0 && index < state.historyStates.length){
            state.currentState = state.historyStates[index]
        }
    }
}