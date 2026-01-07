import '@/common/materializecss/imports/tabs'
import '@/common/style_imports';
import {initTheme} from '@/common/utils/theme';
import Vue from 'vue';
import AdminApp from './AdminApp';
import './AdminApp';
import router from './router/router';
import vueDirectives from '@/common/vueDirectives'
import {forEachKeyValue} from '@/common/utils/common'

// Initialize theme early before Vue renders
initTheme();

forEachKeyValue(vueDirectives, (id, definition) => {
    Vue.directive(id, definition)
})

//noinspection JSAnnotator
new Vue({
    router,
    render: h => h(AdminApp)
}).$mount('#admin-page');
