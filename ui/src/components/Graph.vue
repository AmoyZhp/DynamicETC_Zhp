<template>
    <div class="row">
        <LeftSideBar />
        <div class="col-lg-3">
            <div id="graph" style="position: relative"></div>
        </div>
        <div class="col-lg-3">
            <div class="card">
                <div class="card-header justify-content-between align-items-center d-flex">
                    <a href="#" @click="searchOD">Origin Destination</a>
                    <h5>
                        <span class="badge">{{ selectedOdDemand }}</span>
                    </h5>
                </div>
                <div class="card-body">
                    <div class="input-group mb-3">
                        <div class="input-group-prepend">
                            <span class="input-group-text" id="basic-addon1">Origin</span>
                        </div>
                        <input type="text" class="form-control" v-model="originID" />
                    </div>
                    <div class="input-group mb-3">
                        <div class="input-group-prepend">
                            <span class="input-group-text" id="basic-addon1">Destination</span>
                        </div>
                        <input type="text" class="form-control" v-model="destinationID" />
                    </div>
                </div>
            </div>
        </div>
        <div class="col-lg-3">
            <div class="row">
                <div class="col-lg-9">
                    <div class="card" style="position: relative">
                        <div class="card-header justify-content-between align-items-center d-flex">
                            Edge
                            <h5>
                                <span class="badge">ID: {{ selectedEdge.id }}</span>
                            </h5>
                        </div>
                        <ul class="list-group list-group-flush">
                            <li
                                class="list-group-item justify-content-between align-items-center d-flex"
                            >
                                <a href="#" @click="changeEdgeDetail">Vechicels</a>
                                <span class="badge badge-info">{{ selectedEdge.vechicels }}</span>
                            </li>
                            <li
                                class="list-group-item sub-list-group-item"
                                v-if="edgesDetail && selectedEdge.detail.length > 0 "
                            >
                                <ul class="list-group list-group-flush">
                                    <li
                                        class="list-group-item justify-content-between align-items-center d-flex"
                                        v-for="item in selectedEdge.detail"
                                        :key="item.id"
                                    >
                                        To Zone {{item.id}}
                                        <span
                                            class="badge badge-light"
                                        >{{item.number}}</span>
                                    </li>
                                </ul>
                            </li>
                            <li
                                class="list-group-item justify-content-between align-items-center d-flex"
                            >
                                Toll
                                <span class="badge badge-info">{{ selectedEdge.toll }}</span>
                            </li>
                            <li
                                class="list-group-item justify-content-between align-items-center d-flex"
                            >
                                Length
                                <span class="badge badge-info">{{ selectedEdge.length }}</span>
                            </li>
                            <li
                                class="list-group-item justify-content-between align-items-center d-flex"
                            >
                                Capacity
                                <span class="badge badge-info">{{ selectedEdge.capacity }}</span>
                            </li>
                            <li
                                class="list-group-item justify-content-between align-items-center d-flex"
                            >
                                Free flow travel time
                                <span
                                    class="badge badge-info"
                                >{{ selectedEdge.freeFlowTravelTime }}</span>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
import G6 from "@antv/g6";
import { mapState } from "vuex";
import LeftSideBar from "@/components/LeftSideBar"

export default {

    components:{
        LeftSideBar,
    },
    mounted: function() {
        this.initGraph();
    },
    methods: {
        async initGraph() {
            await this.$store.dispatch("init");
            this.graph = new G6.Graph({
                container: "graph", // String | HTMLElement，必须，创建的容器 id 或容器本身
                width: this.width, // Number，必须，图的宽度
                height: this.height, // Number，必须，图的高度
                layout: this.layout,
                modes: this.modes,
                defaultNode: this.defaultNode,
                defaultEdge: this.defaultEdge,
                nodeStateStyles: this.nodeStateStyles,
                edgeStateStyles: this.edgeStateStyles
            });
            this.graph.data(this.renderData); // 读取数据到图源上
            this.graph.render(); // 渲染图
            this.mountEventOnGraph(this.graph);
        },
        mountEventOnGraph(graph) {
            // 点击节点
            graph.on("node:click", e => {
                this.nodeClickCnt = (this.nodeClickCnt + 1) % 2;
                // 先将所有当前是 click 状态的节点置为非 click 状态
                const clickNodes = graph.findAllByState("node", "click");
                clickNodes.forEach(cn => {
                    graph.setItemState(cn, "click", false);
                });
                const nodeItem = e.item; // 获取被点击的节点元素对象
                const cfg = nodeItem.defaultCfg;
                console.log(cfg);
                if (this.nodeClickCnt == 1) {
                    this.originID = cfg.id;
                    this.destinationID = "";
                } else if (this.nodeClickCnt == 0) {
                    this.destinationID = cfg.id;
                }

                graph.setItemState(nodeItem, "click", true); // 设置当前节点的 click 状态为 true
            });
            // 点击边
            graph.on("edge:click", e => {
                // 先将所有当前是 click 状态的边置为非 click 状态
                const clickEdges = graph.findAllByState("edge", "click");
                clickEdges.forEach(ce => {
                    graph.setItemState(ce, "click", false);
                });
                const edgeItem = e.item; // 获取被点击的边元素对象
                const cfg = edgeItem.defaultCfg;
                console.log(cfg);
                let id = cfg.id.split("-")[1];
                this.selectedEdge = this.edges[id];
                let edgeDetail = [];
                for (let index in this.dyetcState[id]) {
                    let num = this.dyetcState[id][index];
                    if (num != 0) {
                        edgeDetail.push({
                            id: index,
                            number: num
                        });
                    }
                }
                this.selectedEdge.detail = edgeDetail;
                if (edgeDetail.length > 0) {
                    this.edgesDetail = true;
                }
                graph.setItemState(edgeItem, "click", true); // 设置当前边的 click 状态为 true
            });
            // 监听鼠标进入节点事件
            graph.on("node:mouseenter", evt => {
                const node = evt.item;
                // 激活该节点的 hover 状态
                graph.setItemState(node, "hover", true);
            });
            // 监听鼠标离开节点事件
            graph.on("node:mouseleave", evt => {
                const node = evt.item;
                // 关闭该节点的 hover 状态
                graph.setItemState(node, "hover", false);
            });
        },
        changeEdgeDetail(e) {
            console.log("in changeEdgeDetail");
            if (this.edgesDetail) {
                this.edgesDetail = false;
            } else {
                this.edgesDetail = true;
            }
        },
        searchOD(e) {
            let origin = this.originID.split("-")[1];
            let destination = this.destinationID.split("-")[1];
            this.selectedOdDemand = 0;
            if (origin != null && destination != null) {
                if (
                    origin >= 0 &&
                    origin < this.originDestinationPairMatrix.length &&
                    destination >= 0 &&
                    destination < this.originDestinationPairMatrix.length
                ) {
                    let od = this.originDestinationPairMatrix[origin][
                        destination
                    ];
                    console.log(od);
                    if (od != null) {
                        this.selectedOdDemand = od.demand;
                        let edgesId = od.contained_roads;
                        const clickEdges = this.graph.findAllByState(
                            "edge",
                            "click"
                        );
                        clickEdges.forEach(ce => {
                            this.graph.setItemState(ce, "click", false);
                        });
                        edgesId.forEach(e => {
                            let src = e[0];
                            let target = e[1];
                            let edge = this.edgesMatrix[src][target];
                            if (edge != null) {
                                let edgeItem = this.graph.findById(
                                    "e-" + edge.id
                                );
                                this.graph.setItemState(
                                    edgeItem,
                                    "click",
                                    true
                                );
                            }
                        });
                    }
                }
            }
        }
    },
    computed: {
        ...mapState({
            renderData: "data",
            width: state => state.config.width,
            height: state => state.config.height,
            defaultNode: state => state.config.defaultNode,
            defaultEdge: state => state.config.defaultEdge,
            layout: state => state.config.layout,
            modes: state => state.config.modes,
            edgeStateStyles: state => state.config.edgeStateStyles,
            nodeStateStyles: state => state.config.nodeStateStyles
        }),
        ...mapState([
            "nodes",
            "edges",
            "originDestinationPairMatrix",
            "edgesMatrix",
            "dyetcState"
        ])
    },
    data: function() {
        return {
            selectedEdge: {
                id: 0,
                source: 0,
                target: 0,
                vechicels: 0,
                length: 0,
                capacity: 0,
                freeFlowTravelTime: 0,
                toll: 0.0,
                label: "",
                detail: []
            },

            selectedOdDemand: 0,
            edgesDetail: true,
            originID: "",
            destinationID: "",
            nodeClickCnt: 0,
            graph: {}
        };
    }
};


G6.registerEdge(
    "circle-running",
    {
        afterDraw(cfg, group) {
            // 获得当前边的第一个图形，这里是边本身的 path
            const shape = group.get("children")[0];
            // 边 path 的起点位置
            const startPoint = shape.getPoint(0);

            // 添加红色 circle 图形
            const circle = group.addShape("circle", {
                attrs: {
                    x: startPoint.x,
                    y: startPoint.y,
                    fill: "#1890ff",
                    r: 3
                },
                name: "circle-shape"
            });

            // 对红色圆点添加动画
            circle.animate(
                ratio => {
                    // 每一帧的操作，入参 ratio：这一帧的比例值（Number）。返回值：这一帧需要变化的参数集（Object）。
                    // 根据比例值，获得在边 path 上对应比例的位置。
                    const tmpPoint = shape.getPoint(ratio);
                    // 返回需要变化的参数集，这里返回了位置 x 和 y
                    return {
                        x: tmpPoint.x,
                        y: tmpPoint.y
                    };
                },
                {
                    repeat: true, // 动画重复
                    duration: 3000 // 一次动画的时间长度
                }
            );
        }
    },
    "quadratic"
);
</script>
<style scoped>
.card {
    background-color: rgba(0, 0, 128, 0.1);
}
.card-header {
    background-color: rgba(0, 0, 128, 0.1);
}
li.list-group-item {
    background-color: rgba(176, 224, 230, 0.1);
}
li.sub-list-group-item {
    background-color: rgba(0, 206, 209, 0.1);
}


</style>