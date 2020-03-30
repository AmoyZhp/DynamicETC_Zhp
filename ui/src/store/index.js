import Vue from 'vue'
import Vuex from 'vuex'
import mutations from './mutations'
import actions from './actions'
import getters from './getters'
import G6 from "@antv/g6"
Vue.use(Vuex)

export default new Vuex.Store({
    state: {
        graph:{},
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
        selectedEdge:{},
        selectedOD: {},
    },
    mutations: mutations,
    actions: actions,
    getters: getters,
})

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