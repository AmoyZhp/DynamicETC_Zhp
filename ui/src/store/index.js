import Vue from 'vue'
import Vuex from 'vuex'
import api from '@/api/api'

Vue.use(Vuex)


const layout = {
    // Object，可选，布局的方法及其配置项，默认为 random 布局。
    type: "force", // 指定为力导向布局
    preventOverlap: true, // 防止节点重叠
    linkDistance: 100
    // nodeSize: 30        // 节点大小，用于算法中防止节点重叠时的碰撞检测。由于已经在上一节的元素配置中设置了每个节点的 size 属性，则不需要在此设置 nodeSize。
};

const defaultNode = {
    size: 30, // 节点大小
    // ...                 // 节点的其他配置
    // 节点样式配置
    style: {
        fill: "#DEE9FF",
        stroke: "#5B8FF9",
        lineWidth: 1 // 节点描边粗细
    }
};
// 边在默认状态下的样式配置（style）和其他配置
const defaultEdge = {
    // ...                 // 边的其他配置
    // 边样式配置
    type: "circle-running",
    
    // 边上的标签文本配置
    labelCfg: {
        autoRotate: true // 边上的标签文本根据边的方向旋转
    }
};
const nodeStateStyles ={
    // 鼠标 hover 上节点，即 hover 状态为 true 时的样式
    hover: {
        fill: "lightsteelblue"
    },
    // 鼠标点击节点，即 click 状态为 true 时的样式
    click: {
        stroke: "#000",
        lineWidth: 3
    }
};

// 边不同状态下的样式集合
const edgeStateStyles = {
    // 鼠标点击边，即 click 状态为 true 时的样式
    click: {
        stroke: "red"
    }
};

const modes = {
    default: ["drag-canvas", "zoom-canvas", "drag-node"] // 允许拖拽画布、放缩画布、拖拽节点
};

export default new Vuex.Store({
    state: {
        nodes: [], // 节点的实例对象，接收到后台数据后的实例化对象
        /* node : {
              id,
              label,
          }
        */
        edges: [], // 边的实例化对象，接收到后台数据后的实例化对象
        /*
          edge: {
              id,
              source,
              target,
              vechicels,
              length,
              capacity,
              freeFlowTravelTime
              toll,
              label,
          }
        */
        edgesMatrix: [], // |V| x |V|

        dyetcState: [], // |E| x |V| 表示 边 e 上目的地是 v 的车辆的数量
        originDestinationPairMatrix: [], //
        /*
          originDestinationPair : {
              origin,
              destination,
              paths,
              contained_roads,
              demand,
          }
        */
        data: {
            // 基于 state 的数据生成的用于渲染的数据
            nodes: [],
            edges: [],
        },
        config: {
            width: 0,
            height: 0,
            modes: {},
            layout: {},
            defaultNode: {},
            defaultEdge: {},
            nodeStateStyles: {},
            edgeStateStyles: {},
        },

    },
    mutations: {
        init(state, { nodes, edges, dyetcState, originDestinationPairMatrix }) {
            state.nodes = nodes
            state.edges = edges
            state.dyetcState = dyetcState
            state.originDestinationPairMatrix = originDestinationPairMatrix
            state.data.nodes = []
            state.edgesMatrix = new Array(state.nodes.length)
            for(let i = 0; i < state.nodes.length; i++){
                state.edgesMatrix[i] = new Array(state.nodes.length)
            }
            for (let index in state.nodes) {
                let node = state.nodes[index]
                state.data.nodes.push({
                    id: 'n-'+node.id,
                    label: node.label,
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
                    style: {
                        cursor: "pointer",
                        lineAppendWidth: 5, //边响应鼠标事件时的检测宽度
                        opacity: 0.6, // 边透明度
                        stroke: "#bae7ff", // 边描边颜色
                        endArrow: true, //在边的结束点画箭头
                        lineWidth : vechicels / 10 * 5,
                    },
                })
                state.edgesMatrix[edge.source][edge.target] = edge
            }
            state.config.width = window.innerWidth
            state.config.height = window.innerHeight
            state.config.layout = layout
            state.config.defaultNode = defaultNode
            state.config.defaultEdge = defaultEdge
            state.config.modes = modes
            state.config.edgeStateStyles = edgeStateStyles
            state.config.nodeStateStyles = nodeStateStyles
        },
    },
    actions: {

        async init({ commit }) {
            let data = await api.initData()
            console.log(data)
            commit({
                type: 'init',
                nodes: data.nodes,
                edges: data.edges,
                dyetcState: data.state,
                originDestinationPairMatrix: data.originDestinationPairMatrix,
            })

        },
        step({ dispatch, state, commit }) {

        },
    },
    modules: {
    }
})
