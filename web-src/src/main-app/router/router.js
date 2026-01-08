import {routerChildren as executionRouterChildren} from '@/common/components/history/executions-log-page';
import Vue from 'vue';
import VueRouter from 'vue-router';
import AppWelcomePanel from '../components/AppWelcomePanel';
import AppHistoryHeader from '../components/history/AppHistoryHeader';
import AppHistoryPanel from '../components/history/AppHistoryPanel';
import ScheduledPage from '../components/scheduled/ScheduledPage';
import ScheduledHeader from '../components/scheduled/ScheduledHeader';
import MainAppContent from '../components/scripts/MainAppContent';
import ScriptHeader from '../components/scripts/ScriptHeader';

// Admin components
import AdminLayout from '../components/admin/AdminLayout';
import AdminExecutionsLogPage from '@/admin/components/history/AdminExecutionsLogPage';
import ScriptConfigListPage from '@/admin/components/scripts-config/ScriptConfigListPage';
import ScriptsList from '@/admin/components/scripts-config/ScriptsList';
import ScriptConfig from '@/admin/components/scripts-config/ScriptConfig';
import UserManagement from '@/admin/components/UserManagement';

Vue.use(VueRouter);

const router = new VueRouter({
    mode: 'hash',
    routes: [
        // Admin routes (must be before /:scriptName catch-all)
        {
            path: '/admin',
            component: AdminLayout,
            meta: { requiresAdmin: true },
            children: [
                {
                    path: 'logs',
                    component: AdminExecutionsLogPage,
                    children: executionRouterChildren
                },
                {
                    path: 'scripts',
                    component: ScriptConfigListPage,
                    children: [
                        {path: '', component: ScriptsList},
                        {path: ':scriptName', component: ScriptConfig, props: true}
                    ]
                },
                {
                    path: 'users',
                    component: UserManagement
                },
                {path: '', redirect: 'logs'}
            ]
        },
        // Main app routes
        {
            path: '/history',
            components: {
                default: AppHistoryPanel,
                header: AppHistoryHeader
            },
            children: executionRouterChildren
        },
        {
            path: '/scheduled',
            components: {
                default: ScheduledPage,
                header: ScheduledHeader
            }
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
                default: AppHistoryPanel,
                header: AppHistoryHeader
            },
            children: executionRouterChildren
        }
    ]
});

// Navigation guard for admin routes
router.beforeEach((to, from, next) => {
    if (to.matched.some(record => record.meta.requiresAdmin)) {
        // Check if user is admin - import store lazily to avoid circular deps
        import('../store').then(({ default: store }) => {
            if (store.state.auth.admin) {
                next();
            } else {
                // Redirect non-admin users to home
                next('/');
            }
        });
    } else {
        next();
    }
});

export default router