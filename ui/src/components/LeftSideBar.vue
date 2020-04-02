<template>
    <div class="col-lg-3">
        <nav class="d-none d-md-block bg-light sidebar">
            <div class="sidebar-sticky">
                <ul class="nav flex-column accordion" id="leftSideBar">
                    <li class="nav-item card">
                        <div class="card-header justify-content-between align-items-center d-flex">
                            <a
                                data-toggle="collapse"
                                href="#odBox"
                                aria-expanded="true"
                                aria-controls="odBox"
                            >Origin Destination</a>
                            <h5>
                                <span class="badge">Demand : {{ selectedOD.demand }}</span>
                            </h5>
                        </div>
                        <div id="odBox" class="collapse show" data-parent="#leftSideBar">
                            <div class="card-body">
                                <div class="input-group mb-3">
                                    <input class="form-control" v-model="originID" />
                                    <div class="input-group-append">
                                        <span class="input-group-text">
                                            <svg
                                                class="bi bi-arrow-right"
                                                width="1em"
                                                height="1em"
                                                viewBox="0 0 16 16"
                                                fill="currentColor"
                                                xmlns="http://www.w3.org/2000/svg"
                                            >
                                                <path
                                                    fill-rule="evenodd"
                                                    d="M10.146 4.646a.5.5 0 01.708 0l3 3a.5.5 0 010 .708l-3 3a.5.5 0 01-.708-.708L12.793 8l-2.647-2.646a.5.5 0 010-.708z"
                                                    clip-rule="evenodd"
                                                />
                                                <path
                                                    fill-rule="evenodd"
                                                    d="M2 8a.5.5 0 01.5-.5H13a.5.5 0 010 1H2.5A.5.5 0 012 8z"
                                                    clip-rule="evenodd"
                                                />
                                            </svg>
                                        </span>
                                    </div>
                                    <input class="form-control" v-model="destinationID" />
                                    <div class="input-group-append">
                                        <button class="btn btn-info" @click="findOD">Find</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </li>
                    <li class="nav-item card">
                        <div class="card-header justify-content-between align-items-center d-flex">
                            <a
                                data-toggle="collapse"
                                href="#edgeBox"
                                aria-expanded="true"
                                aria-controls="edgeBox"
                            >Edge</a>
                            <h5>
                                <span class="badge">ID: {{ selectedEdge.id }}</span>
                            </h5>
                        </div>
                        <div id="edgeBox" class="car-body collapse show" data-parent="#leftSideBar">
                            <ul class="list-group list-group-flush">
                                <li
                                    class="list-group-item justify-content-between align-items-center d-flex"
                                >
                                    <a href="#" @click="changeEdgeDetail">Vehicles</a>
                                    <span class="badge badge-info">{{ selectedEdge.vehicles }}</span>
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
                                    <span
                                        class="badge badge-info"
                                    >{{ selectedEdge.capacity }}</span>
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
                    </li>
                    
                </ul>
            </div>
        </nav>
    </div>
</template>
<script>
import { mapState, mapMutations } from "vuex";
export default {
    methods: {
        findOD() {
            let origin = this.originID;
            let destination = this.destinationID;
            if (origin != null && destination != null) {
                this.FIND_OD({
                    origin: Number(origin),
                    destination: Number(destination)
                });
            }
        },
        changeEdgeDetail(e) {
            if (this.edgesDetail) {
                this.edgesDetail = false;
            } else {
                this.edgesDetail = true;
            }
        },
        ...mapMutations(["FIND_OD"])
    },
    computed: {
        ...mapState(["graph", "selectedEdge","selectedOD"])
    },
    data: function() {
        return {
            originID: "",
            destinationID: "",
            edgesDetail: false
        };
    }
};
</script>
<style scoped>
.feather {
    width: 16px;
    height: 16px;
    vertical-align: text-bottom;
}

/*
 * Sidebar
 */

.sidebar {
    top: 0;
    bottom: 0;
    left: 0;

    box-shadow: inset -1px 0 0 rgba(0, 0, 0, 0.1);
}

.sidebar-sticky {
    position: relative;
    top: 0;
    height: calc(100vh - 48px);
    padding-top: 0.5rem;
    overflow-x: hidden;
    overflow-y: auto; /* Scrollable contents if viewport is shorter than content. */
}

@supports ((position: -webkit-sticky) or (position: sticky)) {
    .sidebar-sticky {
        position: -webkit-sticky;
        position: sticky;
    }
}

.sidebar .nav-link {
    font-weight: 500;
    color: #333;
}

.sidebar .nav-link .feather {
    margin-right: 4px;
    color: #999;
}

.sidebar .nav-link.active {
    color: #007bff;
}

.sidebar .nav-link:hover .feather,
.sidebar .nav-link.active .feather {
    color: inherit;
}

.sidebar-heading {
    font-size: 0.75rem;
    text-transform: uppercase;
}

/*
 * Content
 */

[role="main"] {
    padding-top: 133px; /* Space for fixed navbar */
}

@media (min-width: 768px) {
    [role="main"] {
        padding-top: 48px; /* Space for fixed navbar */
    }
}

/*
 * Navbar
 */

.navbar-brand {
    padding-top: 0.75rem;
    padding-bottom: 0.75rem;
    font-size: 1rem;
    background-color: rgba(0, 0, 0, 0.25);
    box-shadow: inset -1px 0 0 rgba(0, 0, 0, 0.25);
}

.navbar .form-control {
    padding: 0.75rem 1rem;
    border-width: 0;
    border-radius: 0;
}

.form-control-dark {
    color: #fff;
    background-color: rgba(255, 255, 255, 0.1);
    border-color: rgba(255, 255, 255, 0.1);
}

.form-control-dark:focus {
    border-color: transparent;
    box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.25);
}
</style>