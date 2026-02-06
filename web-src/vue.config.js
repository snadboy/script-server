const webpack = require('webpack');

// Generate build timestamp in format: MMDD-HHMM (e.g., 0103-1430)
const buildTime = new Date();
const buildTimestamp = String(buildTime.getMonth() + 1).padStart(2, '0') +
    String(buildTime.getDate()).padStart(2, '0') + '-' +
    String(buildTime.getHours()).padStart(2, '0') +
    String(buildTime.getMinutes()).padStart(2, '0');

module.exports = {
    // don't set absolute paths, otherwise reverse proxies with a custom path won't work
    publicPath: '',

    outputDir: '../web',

    devServer: {
        proxy: {
            '': {
                target: 'http://localhost:5000'
            },
            '/': {
                target: 'ws://localhost:5000',
                ws: true,
                headers: {
                    Origin: 'http://localhost:5000'
                }
            }
        }
    },

    pages: {
        index: {
            entry: 'src/main-app/index.js',
            template: 'public/index.html',
            chunks: ['chunk-index-vendors', 'index']
        },
        login: {
            entry: 'src/login/login.js',
            template: 'public/login.html',
            chunks: ['chunk-login-vendors', 'login']
        }
    },

    css: {
        loaderOptions: {
            scss: {
                additionalData: '@import "./src/assets/css/color_variables.scss"; '
                    + '@import "materialize-css/sass/components/_variables.scss"; '
                    + '@import "materialize-css/sass/components/_global.scss"; '
                    + '@import "materialize-css/sass/components/_typography.scss"; '
            }
        }
    },

    configureWebpack: {
        plugins: [
            new webpack.DefinePlugin({
                'process.env.VUE_APP_BUILD_TIMESTAMP': JSON.stringify(buildTimestamp)
            })
        ]
    },

    chainWebpack: config => {
        const options = module.exports;
        const pages = options.pages;
        const pageKeys = Object.keys(pages);

        const IS_VENDOR = /[\\/]node_modules[\\/]/;

        // ATTENTION! do not use minSize/maxSize until vue-cli moved to the 4th version of html-webpack-plugin
        // Otherwise plugin won't be able to find split packages
        config.optimization
            .splitChunks({
                cacheGroups: {
                    ...pageKeys.map(key => ({
                        name: `chunk-${key}-vendors`,
                        priority: -11,
                        chunks: chunk => chunk.name === key,
                        test: IS_VENDOR,
                        enforce: true
                    }))
                }
            });
    },

    pluginOptions: {
        karma: {
            files: ['tests/unit/index.js'],
            customLaunchers: {
                ChromeHeadless: {
                    base: 'Chrome',
                    flags: [
                        '--headless',
                        '--disable-gpu',
                        '--no-sandbox',
                        '--remote-debugging-port=9222'
                    ]
                }
            },
            browsers: ['Chrome', 'Firefox'],

            reporters: ['mocha', 'allure'],

            frameworks: ['mocha'],

            allureReport: {
                reportDir: '/tmp/allure_result',
                useBrowserName: true
            },

            plugins: [
                'karma-chrome-launcher',
                'karma-firefox-launcher',
                'karma-sourcemap-loader',
                'karma-webpack',
                'karma-mocha',
                'karma-mocha-reporter',
                'karma-allure-reporter'
            ]
        }
    }
};