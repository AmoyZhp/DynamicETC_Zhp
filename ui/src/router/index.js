import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '../views/Home.vue'
import Graph from '@/components/Graph.vue'
import StateTable from '@/components/StateTable.vue'

Vue.use(VueRouter)

const routes = [
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

const router = new VueRouter({
  routes
})

export default router
