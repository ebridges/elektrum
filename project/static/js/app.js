webpackJsonp([2,0],{0:function(e,t,n){"use strict";function o(e){return e&&e.__esModule?e:{default:e}}var r=n(110),u=o(r),a=n(106),i=o(a);new u.default({el:"#app",template:"<App/>",components:{App:i.default}})},60:function(e,t){"use strict";Object.defineProperty(t,"__esModule",{value:!0}),t.default={AWS_LAMBDA_GETSIGNEDURL_ENDPOINT:"/media/request-upload/"}},61:function(e,t,n){"use strict";function o(e){return e&&e.__esModule?e:{default:e}}Object.defineProperty(t,"__esModule",{value:!0});var r=n(64),u=o(r),a=n(65),i=o(a),s=n(42),c=o(s),d=n(60),l=o(d);t.default={getSignedURL:function(e){var t=this,n=l.default.AWS_LAMBDA_GETSIGNEDURL_ENDPOINT,o=new FormData;o.set("mime_type",e.type);var r=document.cookie.split("=")[1],u={"X-CSRFToken":r,"Content-Type":"multipart/form-data"};return c.default.post(n,o,{headers:u}).then(function(e){var n=t.getPropValue(e.headers,"Location");return i.default.resolve(n||"/")}).catch(function(e){return console.error(e),i.default.reject("/")})},getPropValue:function(e,t){var n=(0,u.default)(e).toString(),o=new RegExp(t,"i").exec(n);return o&&(o.length>0?e[o[0]]:"")}}},62:function(e,t,n){"use strict";function o(e){return e&&e.__esModule?e:{default:e}}Object.defineProperty(t,"__esModule",{value:!0});var r=n(107),u=o(r);t.default={name:"app",components:{Dropzone:u.default}}},63:function(e,t,n){"use strict";function o(e){return e&&e.__esModule?e:{default:e}}Object.defineProperty(t,"__esModule",{value:!0});var r=n(103),u=o(r);n(104);var a=n(61),i=o(a);u.default.autoDiscover=!1,t.default={name:"dropzone",mounted:function(){var e=this,t={url:"/",method:"put",sending:function(e,t){var n=t.send;t.send=function(){n.call(t,e)}},parallelUploads:1,uploadMultiple:!1,header:"",dictDefaultMessage:document.querySelector("#dropzone-message").innerHTML,autoProcessQueue:!1,accept:function(t,n){i.default.getSignedURL(t).then(function(o){t.uploadURL=o,n(),setTimeout(function(){return e.dropzone.processFile(t)})}).catch(function(e){n("Failed to get an S3 signed upload URL",e)})}};this.dropzone=new u.default(this.$el,t),e.dropzone.on("processing",function(t){e.dropzone.options.url=t.uploadURL})}}},104:function(e,t){},105:function(e,t){},106:function(e,t,n){var o,r;o=n(62);var u=n(108);r=o=o||{},"object"!=typeof o.default&&"function"!=typeof o.default||(r=o=o.default),"function"==typeof r&&(r=r.options),r.render=u.render,r.staticRenderFns=u.staticRenderFns,e.exports=o},107:function(e,t,n){var o,r;n(105),o=n(63);var u=n(109);r=o=o||{},"object"!=typeof o.default&&"function"!=typeof o.default||(r=o=o.default),"function"==typeof r&&(r=r.options),r.render=u.render,r.staticRenderFns=u.staticRenderFns,e.exports=o},108:function(e,t){e.exports={render:function(){var e=this;return e._c("div",{attrs:{id:"app"}},[e._c("dropzone")],1)},staticRenderFns:[]}},109:function(e,t){e.exports={render:function(){var e=this;return e._m(0)},staticRenderFns:[function(){var e=this;return e._c("form",{staticClass:"dropzone"},[e._c("div",{staticStyle:{display:"none"},attrs:{id:"dropzone-message"}},[e._c("span",{staticClass:"dropzone-title"},[e._v("Drop files here or click to select")]),e._v(" "),e._c("span",{staticClass:"dropzone-info"},[e._v("You can upload multiple files at once")])])])}]}}});
//# sourceMappingURL=app.edbcf3c9eaea58803abd.js.map
