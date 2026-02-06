import {routerChildren as executionRouterChildren} from '@/common/components/history/executions-log-page';
import Vue from 'vue';
import VueRouter from 'vue-router';
import AppWelcomePanel from '../components/AppWelcomePanel';
import ActivityPage from '../components/activity/ActivityPage';
import ActivityHeader from '../components/activity/ActivityHeader';
import MainAppContent from '../components/scripts/MainAppContent';
import ScriptHeader from '../components/scripts/ScriptHeader';

Vue.use(VueRouter);

const router = new VueRouter({
    mode: 'hash',
    routes: [
        {
            path: '/activity',
            components: {
                default: ActivityPage,
                header: ActivityHeader
            },
            children: executionRouterChildren
        },
        {
            path: '/:scriptName',
            components: {
                default: MainAppContent,
                header: ScriptHeader
            },
            name: 'script'
        },
        {
            path: '',
            components: {
                default: ActivityPage,
                header: ActivityHeader
            },
            children: executionRouterChildren
        }
    ]
});

export default router