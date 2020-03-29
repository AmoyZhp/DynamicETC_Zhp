
export default {
    layout: {
        // Object，可选，布局的方法及其配置项，默认为 random 布局。
        type: "force", // 指定为力导向布局
        preventOverlap: true, // 防止节点重叠
        linkDistance: 100
        // nodeSize: 30        // 节点大小，用于算法中防止节点重叠时的碰撞检测。由于已经在上一节的元素配置中设置了每个节点的 size 属性，则不需要在此设置 nodeSize。
    },
    defaultNode: {
        size: 30, // 节点大小
        // ...                 // 节点的其他配置
        // 节点样式配置
        style: {
            fill: "#DEE9FF",
            stroke: "#5B8FF9",
            lineWidth: 1 // 节点描边粗细
        }
    },
    // 边在默认状态下的样式配置（style）和其他配置
    defaultEdge: {
        // ...                 // 边的其他配置
        // 边样式配置
        type: "circle-running",

        // 边上的标签文本配置
        labelCfg: {
            autoRotate: true // 边上的标签文本根据边的方向旋转
        }
    },
    nodeStateStyles: {
        // 鼠标 hover 上节点，即 hover 状态为 true 时的样式
        hover: {
            fill: "lightsteelblue"
        },
        // 鼠标点击节点，即 click 状态为 true 时的样式
        click: {
            stroke: "#000",
            lineWidth: 3
        }
    },
    // 边不同状态下的样式集合
    edgeStateStyles: {
        // 鼠标点击边，即 click 状态为 true 时的样式
        click: {
            stroke: "red"
        }
    },

    modes: {
        default: ["drag-canvas", "zoom-canvas", "drag-node"] // 允许拖拽画布、放缩画布、拖拽节点
    },
}