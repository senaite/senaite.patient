!function(e){var t={};function n(i){if(t[i])return t[i].exports;var r=t[i]={i:i,l:!1,exports:{}};return e[i].call(r.exports,r,r.exports,n),r.l=!0,r.exports}n.m=e,n.c=t,n.d=function(e,t,i){n.o(e,t)||Object.defineProperty(e,t,{enumerable:!0,get:i})},n.r=function(e){"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(e,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(e,"__esModule",{value:!0})},n.t=function(e,t){if(1&t&&(e=n(e)),8&t)return e;if(4&t&&"object"==typeof e&&e&&e.__esModule)return e;var i=Object.create(null);if(n.r(i),Object.defineProperty(i,"default",{enumerable:!0,value:e}),2&t&&"string"!=typeof e)for(var r in e)n.d(i,r,function(t){return e[t]}.bind(null,r));return i},n.n=function(e){var t=e&&e.__esModule?function(){return e.default}:function(){return e};return n.d(t,"a",t),t},n.o=function(e,t){return Object.prototype.hasOwnProperty.call(e,t)},n.p="/++plone++senaite.patient.static/bundles",n(n.s=1)}([function(e,t){e.exports=jQuery},function(e,t,n){e.exports=n(2)},function(e,t,n){"use strict";n.r(t);var i=n(0),r=n.n(i);function a(e,t){for(var n=0;n<t.length;n++){var i=t[n];i.enumerable=i.enumerable||!1,i.configurable=!0,"value"in i&&(i.writable=!0),Object.defineProperty(e,i.key,i)}}var o=function(){function e(){return function(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}(this,e),this.reset_values=this.reset_values.bind(this),this.reset_value=this.reset_value.bind(this),this.bind_event_handler=this.bind_event_handler.bind(this),this.on_temporary_change=this.on_temporary_change.bind(this),this.on_value_change=this.on_value_change.bind(this),this.on_keypress=this.on_keypress.bind(this),this.set_temporary=this.set_temporary.bind(this),this.set_current_id=this.set_current_id.bind(this),this.get_current_id=this.get_current_id.bind(this),this.get_autogenerated_id=this.get_autogenerated_id.bind(this),this.get_input_element=this.get_input_element.bind(this),this.get_field_name=this.get_field_name.bind(this),this.get_sibling=this.get_sibling.bind(this),this.set_sibling_value=this.set_sibling_value.bind(this),this.format_date=this.format_date.bind(this),this.get_subfield=this.get_subfield.bind(this),this.search_mrn=this.search_mrn.bind(this),this.template_dialog=this.template_dialog.bind(this),this.render_template=this.render_template.bind(this),this.ajax_submit=this.ajax_submit.bind(this),this.get_portal_url=this.get_portal_url.bind(this),this.debug=this.debug.bind(this),console.debug("TemporaryIdentifierWidget::load"),this.auto_wildcard="-- autogenerated --",this.is_add_sample_form=document.body.classList.contains("template-ar_add"),this.is_add_sample_form&&this.reset_values(),this.bind_event_handler(),this}var t,n,i;return t=e,(n=[{key:"reset_values",value:function(){var e,t,n,i,r,a,o,u,l,s,d,c;for(this.debug("°°° TemporaryIdentifierWidget::reset_values"),c=".TemporaryIdentifier.temporary-id input[id$='_value']",t=0,r=(u=document.querySelectorAll(c)).length;t<r;t++)e=u[t],this.reset_value(e,this.auto_wildcard);for(c=".TemporaryIdentifier.temporary-id input[name*='.value:']",n=0,a=(l=document.querySelectorAll(c)).length;n<a;n++)e=l[n],this.reset_value(e,this.auto_wildcard);for(c=".TemporaryIdentifier input[name*='.value_auto:']",d=[],i=0,o=(s=document.querySelectorAll(c)).length;i<o;i++)e=s[i],d.push(this.reset_value(e));return d}},{key:"reset_value",value:function(e){var t=arguments.length>1&&void 0!==arguments[1]?arguments[1]:"";return this.debug("°°° TemporaryIdentifierWidget::reset_value:el=".concat(e.id||e.name,",value='").concat(t,"'")),e.value=t}},{key:"bind_event_handler",value:function(){return this.debug("TemporaryIdentifierWidget::bind_event_handler"),r()("body").on("change",".TemporaryIdentifier input[type='checkbox']",this.on_temporary_change),r()("body").on("change",".TemporaryIdentifier input[type='text']",this.on_value_change),r()("body").on("keypress",".TemporaryIdentifier input[type='text']",this.on_keypress)}},{key:"on_temporary_change",value:function(e){var t,n,i,a,o;return this.debug("°°° TemporaryIdentifierWidget::on_temporary_change °°°"),n=e.currentTarget,i=this.get_field_name(n),o=n.checked,this.set_temporary(i,o),t=this.get_autogenerated_id(i,this.auto_wildcard),(a=this.get_input_element(i)).disabled=o,o&&!a.value?(a.value=t,r()(a).trigger("change")):o||a.value!==t?void 0:(a.value="",r()(a).trigger("change"))}},{key:"on_value_change",value:function(e){var t,n,i,a;if(this.debug("°°° TemporaryIdentifierWidget::on_value_change °°°"),i=e.currentTarget,a=this.get_field_name(i),n=this.get_current_id(a),this.set_current_id(a,i.value),i.value&&i.value!==this.auto_wildcard)return t=i.closest(".field").querySelector('[name="config_catalog"]').value,this.search_mrn(i.value,t).done((function(e){var t,o,u,l,s,d;if(e)return t=[e.address,e.zipcode,e.city,e.country].filter((function(e){return e})),s={PatientFullName:e.fullname,PatientAddress:t.join(", "),DateOfBirth:this.format_date(e.birthdate),Age:e.age,Gender:e.gender,review_state:e.review_state},d="existing-identifier",o=null,"inactive"===e.review_state&&(d="inactive-patient",(o={})[_t("Close")]=function(){return r()(this).trigger("no"),r()(this).dialog("close")}),l=this,null==e.identifier&&(e.identifier=i.value),(u=this.template_dialog(d,e,o)).on("yes",(function(){var e,t;for(a in e=[],s)t=s[a],e.push(l.set_sibling_value(i,a,t));return e})),u.on("no",(function(){return i.value=n,l.set_current_id(a,n)}))}))}},{key:"on_keypress",value:function(e){var t;if(13===e.keyCode)return t=e.currentTarget,r()(t).trigger("blur"),e.preventDefault()}},{key:"set_temporary",value:function(e,t){return this.get_subfield(e,"temporary").value=t||""}},{key:"set_current_id",value:function(e,t){return this.get_subfield(e,"value").value=t}},{key:"get_current_id",value:function(e){var t=arguments.length>1&&void 0!==arguments[1]?arguments[1]:"";return this.get_subfield(e,"value").value||t}},{key:"get_autogenerated_id",value:function(e){var t=arguments.length>1&&void 0!==arguments[1]?arguments[1]:"";return this.get_subfield(e,"value_auto").value||t}},{key:"get_input_element",value:function(e){return document.querySelector("#".concat(e,"_value"))}},{key:"get_field_name",value:function(e){var t;return t=e.closest("div[data-fieldname]"),r()(t).attr("data-fieldname")}},{key:"get_sibling",value:function(e,t){var n,i;return n=t,this.is_add_sample_form&&(i=e.closest("td[arnum]"),n=t+"-"+r()(i).attr("arnum")),document.querySelector('[name="'+n+'"]')}},{key:"set_sibling_value",value:function(e,t,n){var i;if(this.debug("°°° TemporaryIdentifierWidget::set_sibling_value:name=".concat(t,",value=").concat(n," °°°")),i=this.get_sibling(e,t))return this.debug(">>> ".concat(i.name," = ").concat(n," ")),i.value=n,r()(i).trigger("change")}},{key:"format_date",value:function(e){var t;return null==e?"":[(t=new Date(e)).getFullYear(),("0"+(t.getMonth()+1)).slice(-2),("0"+t.getDate()).slice(-2)].join("-")}},{key:"get_subfield",value:function(e,t){return document.querySelector('input[name^="'+e+"."+t+':"]')}},{key:"search_mrn",value:function(e,t){var n,i,a;return this.debug("°°° TemporaryIdentifierWidget::search_mrn:mrn=".concat(e," °°°")),i=["fullname","age","birthdate","gender","email","address","zipcode","city","country","review_state"],n=r.a.Deferred(),a={url:this.get_portal_url()+"/@@API/read",data:{portal_type:"Patient",catalog_name:t,patient_mrn:e,include_fields:i,page_size:1}},this.ajax_submit(a).done((function(e){var t;return t={},e.objects&&(t=e.objects[0]),n.resolveWith(this,[t])})),n.promise()}},{key:"template_dialog",value:function(e,t,n){var i;return null==n&&((n={})[_t("Yes")]=function(){return r()(this).trigger("yes"),r()(this).dialog("close")},n[_t("No")]=function(){return r()(this).trigger("no"),r()(this).dialog("close")}),i=this.render_template(e,t),r()(i).dialog({width:450,resizable:!1,closeOnEscape:!1,buttons:n,open:function(e,t){return r()(".ui-dialog-titlebar-close").hide()}})}},{key:"render_template",value:function(e,t){var n;if(this.debug("°°° TemporaryIdentifierWidget::render_template:template_id:".concat(e," °°°")),n=r()("#".concat(e)).html())return Handlebars.compile(n)(t)}},{key:"ajax_submit",value:function(){var e,t=arguments.length>0&&void 0!==arguments[0]?arguments[0]:{};return this.debug("°°° TemporaryIdentifierWidget::ajax_submit °°°"),null==t.type&&(t.type="POST"),null==t.url&&(t.url=this.get_portal_url()),null==t.context&&(t.context=this),null==t.dataType&&(t.dataType="json"),null==t.data&&(t.data={}),null==t._authenticator&&(t._authenticator=r()("input[name='_authenticator']").val()),console.debug(">>> ajax_submit::options=",t),r()(this).trigger("ajax:submit:start"),e=function(){return r()(this).trigger("ajax:submit:end")},r.a.ajax(t).done(e)}},{key:"get_portal_url",value:function(){return r()("input[name=portal_url]").val()||window.portal_url}},{key:"debug",value:function(e){return console.debug("[senaite.patient.temporary_identifier_widget] ",e)}}])&&a(t.prototype,n),i&&a(t,i),e}();function u(e,t){for(var n=0;n<t.length;n++){var i=t[n];i.enumerable=i.enumerable||!1,i.configurable=!0,"value"in i&&(i.writable=!0),Object.defineProperty(e,i.key,i)}}var l=function(){function e(){var t,n,i,a;for(function(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}(this,e),this.bind_event_handler=this.bind_event_handler.bind(this),this.on_age_selector_change=this.on_age_selector_change.bind(this),this.on_fallback_dob_change=this.on_fallback_dob_change.bind(this),console.debug("AgeDoBWidgetController::load"),this.bind_event_handler(),".AgeDoBWidget input[type='radio'][checked]",n=0,i=(a=document.querySelectorAll(".AgeDoBWidget input[type='radio'][checked]")).length;n<i;n++)t=a[n],r()(t).trigger("change");return this}var t,n,i;return t=e,(n=[{key:"bind_event_handler",value:function(){var e;return console.debug("AgeDoBWidgetController::bind_event_handler"),e=".AgeDoBWidget input[type='radio']",r()("body").on("change",e,this.on_age_selector_change),e=".AgeDoBWidget input[id$='-dob-fallback']",r()("body").on("change",e,this.on_fallback_dob_change)}},{key:"on_age_selector_change",value:function(e){var t,n,i,a,o,u,l,s;return console.debug("AgeDoBWidgetController::on_age_selector_change"),l=(a=e.currentTarget).closest(".AgeDoBWidget"),u=null!=(o="1"===r()(l).attr("data-required"))?o:{required:""},t=l.querySelector('[id$="_age_controls"]'),n=l.querySelector('[id$="_dob_controls"]'),s=l.querySelector('[id$=".years:ignore_empty:record"]'),i=l.querySelector('[id$=".dob:ignore_empty:record"]'),"age"===r()(a).val()?(r()(t).show(),r()(n).hide(),s.setAttribute("required",u),i.removeAttribute("required")):(r()(t).hide(),r()(n).show(),s.removeAttribute("required"),i.setAttribute("required",u))}},{key:"on_fallback_dob_change",value:function(e){var t,n,i;return console.debug("AgeDoBWidgetController::on_fallback_dob_change"),(t=(i=(n=e.currentTarget).closest(".AgeDoBWidget")).querySelector("input[id$='_dob_selector']")).setAttribute("checked",""),r()(t).trigger("change"),i.querySelector('[id$=".dob:ignore_empty:record"]').value=n.value}}])&&u(t.prototype,n),i&&u(t,i),e}();document.addEventListener("DOMContentLoaded",(function(){console.debug("*** SENAITE PATIENT JS LOADED ***"),window.temporary_identifier_widget=new o,window.age_dob_widget=new l}))}]);