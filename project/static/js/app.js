webpackJsonp([2,0],{0:function(e,t,n){"use strict";function o(e){return e&&e.__esModule?e:{default:e}}var r=n(104),u=o(r),a=n(100),s=o(a);new u.default({el:"#app",template:"<App/>",components:{App:s.default}})},59:function(e,t){"use strict";Object.defineProperty(t,"__esModule",{value:!0}),t.default={AWS_LAMBDA_GETSIGNEDURL_ENDPOINT:"/media/request-upload/"}},60:function(e,t,n){"use strict";function o(e){return e&&e.__esModule?e:{default:e}}Object.defineProperty(t,"__esModule",{value:!0});var r=n(63),u=o(r),a=n(41),s=o(a),i=n(59),d=o(i);t.default={getSignedURL:function(e){var t=d.default.AWS_LAMBDA_GETSIGNEDURL_ENDPOINT,n=new FormData;n.set("mime_type",e.type);var o=document.cookie.split("=")[1],r={"X-CSRFToken":o,"Content-Type":"multipart/form-data"};return s.default.post(t,n,{headers:r}).then(function(e){return u.default.resolve(e.headers.Location||"/")}).catch(function(e){return console.error(e),u.default.reject("/")})}}},61:function(e,t,n){"use strict";function o(e){return e&&e.__esModule?e:{default:e}}Object.defineProperty(t,"__esModule",{value:!0});var r=n(101),u=o(r);t.default={name:"app",components:{Dropzone:u.default}}},62:function(e,t,n){"use strict";function o(e){return e&&e.__esModule?e:{default:e}}Object.defineProperty(t,"__esModule",{value:!0});var r=n(97),u=o(r);n(98);var a=n(60),s=o(a);u.default.autoDiscover=!1,t.default={name:"dropzone",mounted:function(){var e=this,t={url:"/",method:"put",sending:function(e,t){var n=t.send;t.send=function(){n.call(t,e)}},parallelUploads:1,uploadMultiple:!1,header:"",dictDefaultMessage:document.querySelector("#dropzone-message").innerHTML,autoProcessQueue:!1,accept:function(t,n){s.default.getSignedURL(t).then(function(o){t.uploadURL=o,n(),setTimeout(function(){return e.dropzone.processFile(t)})}).catch(function(e){n("Failed to get an S3 signed upload URL",e)})}};this.dropzone=new u.default(this.$el,t),e.dropzone.on("processing",function(t){e.dropzone.options.url=t.uploadURL})}}},98:function(e,t){},99:function(e,t){},100:function(e,t,n){var o,r;o=n(61);var u=n(102);r=o=o||{},"object"!=typeof o.default&&"function"!=typeof o.default||(r=o=o.default),"function"==typeof r&&(r=r.options),r.render=u.render,r.staticRenderFns=u.staticRenderFns,e.exports=o},101:function(e,t,n){var o,r;n(99),o=n(62);var u=n(103);r=o=o||{},"object"!=typeof o.default&&"function"!=typeof o.default||(r=o=o.default),"function"==typeof r&&(r=r.options),r.render=u.render,r.staticRenderFns=u.staticRenderFns,e.exports=o},102:function(e,t){e.exports={render:function(){var e=this;return e._c("div",{attrs:{id:"app"}},[e._c("dropzone")],1)},staticRenderFns:[]}},103:function(e,t){e.exports={render:function(){var e=this;return e._m(0)},staticRenderFns:[function(){var e=this;return e._c("form",{staticClass:"dropzone"},[e._c("div",{staticStyle:{display:"none"},attrs:{id:"dropzone-message"}},[e._c("span",{staticClass:"dropzone-title"},[e._v("Drop files here or click to select")]),e._v(" "),e._c("span",{staticClass:"dropzone-info"},[e._v("You can upload multiple files at once")])])])}]}}});
//# sourceMappingURL=app.928528fdfb387d6130b4.js.map