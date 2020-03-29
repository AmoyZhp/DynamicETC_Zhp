<template>
    <div class="col-lg-3">
        <nav class="d-none d-md-block bg-light sidebar">
            <div class="sidebar-sticky">
                <ul class="nav flex-column accordion" id="accordionExample">
                    <li class="nav-item card">
                        <div
                            class="card-header justify-content-between align-items-center d-flex"
                            id="headingOne"
                        >
                            <h2 class="mb-0">
                                <button
                                    class="btn btn-link"
                                    type="button"
                                    data-toggle="collapse"
                                    data-target="#collapseOne"
                                    aria-expanded="true"
                                    aria-controls="collapseOne"
                                >Origin Destination</button>
                            </h2>
                            <h5>
                                <span class="badge">{{ selectedOdDemand }}</span>
                            </h5>
                        </div>
                        <div
                            id="collapseOne"
                            class="collapse show"
                            aria-labelledby="headingOne"
                            data-parent="#accordionExample"
                        >
                            <div class="card-body">
                                <div class="input-group mb-3">
                                    <input
                                        type="text"
                                        class="form-control"
                                        aria-label="Dollar amount (with dot and two decimal places)"
                                    />
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
                                    <input
                                        type="text"
                                        class="form-control"
                                        aria-label="Dollar amount (with dot and two decimal places)"
                                    />
                                    <div class="input-group-append" id="button-addon4">
                                        <button class="btn btn-info" type="button" @click="findOD">Find</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </li>
                </ul>
            </div>
        </nav>
    </div>
</template>
<script>
export default {
    methods:{
        findOD(){

        },
    },
    data: function(){
        return{
            selectedOdDemand:0,
        }
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