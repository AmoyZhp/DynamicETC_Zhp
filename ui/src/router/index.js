import Vue from 'vue'
import VueRouter from 'vue-router'
import DyETC from '@/views/DyETC.vue'
import Graph from '@/components/Graph.vue'
import StateTable from '@/components/StateTable.vue'

Vue.use(VueRouter)

const routes = [
{
    path: '/',
    name: 'dyetc',
    component: DyETC,
    children: [
        { path: '', component: Graph },
        {
            path: '/graph',
            name: 'graph',
            component: Graph
        },
        {
            path: '/stateTable',
            name: 'stateTable',
            component: StateTable
        },
    ]
},
]

const router = new VueRouter({
  routes
})

export default router
