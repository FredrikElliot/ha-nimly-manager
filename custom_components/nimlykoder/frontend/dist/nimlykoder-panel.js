var t=globalThis;var e=t.ShadowRoot&&(void 0===t.ShadyCSS||t.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype;var s=Symbol();var o=new WeakMap;var n=class{constructor(t3,e4,o5){if(this._$cssResult$=true,o5!==s)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t3,this.t=e4}get styleSheet(){let t3=this.o;const s4=this.t;if(e&&void 0===t3){const e4=void 0!==s4&&1===s4.length;e4&&(t3=o.get(s4)),void 0===t3&&((this.o=t3=new CSSStyleSheet).replaceSync(this.cssText),e4&&o.set(s4,t3))}return t3}toString(){return this.cssText}};var r=t3=>new n("string"==typeof t3?t3:t3+"",void 0,s);var i=(t3,...e4)=>{const o5=1===t3.length?t3[0]:e4.reduce((e5,s4,o6)=>e5+(t4=>{if(true===t4._$cssResult$)return t4.cssText;if("number"==typeof t4)return t4;throw Error("Value passed to 'css' function must be a 'css' function result: "+t4+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(s4)+t3[o6+1],t3[0]);return new n(o5,t3,s)};var S=(s4,o5)=>{if(e)s4.adoptedStyleSheets=o5.map(t3=>t3 instanceof CSSStyleSheet?t3:t3.styleSheet);else for(const e4 of o5){const o6=document.createElement("style"),n4=t.litNonce;void 0!==n4&&o6.setAttribute("nonce",n4),o6.textContent=e4.cssText,s4.appendChild(o6)}};var c=e?t3=>t3:t3=>t3 instanceof CSSStyleSheet?(t4=>{let e4="";for(const s4 of t4.cssRules)e4+=s4.cssText;return r(e4)})(t3):t3;var{is:i2,defineProperty:e2,getOwnPropertyDescriptor:h,getOwnPropertyNames:r2,getOwnPropertySymbols:o2,getPrototypeOf:n2}=Object;var a=globalThis;var c2=a.trustedTypes;var l=c2?c2.emptyScript:"";var p=a.reactiveElementPolyfillSupport;var d=(t3,s4)=>t3;var u={toAttribute(t3,s4){switch(s4){case Boolean:t3=t3?l:null;break;case Object:case Array:t3=null==t3?t3:JSON.stringify(t3)}return t3},fromAttribute(t3,s4){let i5=t3;switch(s4){case Boolean:i5=null!==t3;break;case Number:i5=null===t3?null:Number(t3);break;case Object:case Array:try{i5=JSON.parse(t3)}catch(t4){i5=null}}return i5}};var f=(t3,s4)=>!i2(t3,s4);var b={attribute:true,type:String,converter:u,reflect:false,useDefault:false,hasChanged:f};Symbol.metadata??=Symbol("metadata"),a.litPropertyMetadata??=new WeakMap;var y=class extends HTMLElement{static addInitializer(t3){this._$Ei(),(this.l??=[]).push(t3)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t3,s4=b){if(s4.state&&(s4.attribute=false),this._$Ei(),this.prototype.hasOwnProperty(t3)&&((s4=Object.create(s4)).wrapped=true),this.elementProperties.set(t3,s4),!s4.noAccessor){const i5=Symbol(),h3=this.getPropertyDescriptor(t3,i5,s4);void 0!==h3&&e2(this.prototype,t3,h3)}}static getPropertyDescriptor(t3,s4,i5){const{get:e4,set:r4}=h(this.prototype,t3)??{get(){return this[s4]},set(t4){this[s4]=t4}};return{get:e4,set(s5){const h3=e4?.call(this);r4?.call(this,s5),this.requestUpdate(t3,h3,i5)},configurable:true,enumerable:true}}static getPropertyOptions(t3){return this.elementProperties.get(t3)??b}static _$Ei(){if(this.hasOwnProperty(d("elementProperties")))return;const t3=n2(this);t3.finalize(),void 0!==t3.l&&(this.l=[...t3.l]),this.elementProperties=new Map(t3.elementProperties)}static finalize(){if(this.hasOwnProperty(d("finalized")))return;if(this.finalized=true,this._$Ei(),this.hasOwnProperty(d("properties"))){const t4=this.properties,s4=[...r2(t4),...o2(t4)];for(const i5 of s4)this.createProperty(i5,t4[i5])}const t3=this[Symbol.metadata];if(null!==t3){const s4=litPropertyMetadata.get(t3);if(void 0!==s4)for(const[t4,i5]of s4)this.elementProperties.set(t4,i5)}this._$Eh=new Map;for(const[t4,s4]of this.elementProperties){const i5=this._$Eu(t4,s4);void 0!==i5&&this._$Eh.set(i5,t4)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(s4){const i5=[];if(Array.isArray(s4)){const e4=new Set(s4.flat(1/0).reverse());for(const s5 of e4)i5.unshift(c(s5))}else void 0!==s4&&i5.push(c(s4));return i5}static _$Eu(t3,s4){const i5=s4.attribute;return false===i5?void 0:"string"==typeof i5?i5:"string"==typeof t3?t3.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=false,this.hasUpdated=false,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t3=>this.enableUpdating=t3),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t3=>t3(this))}addController(t3){(this._$EO??=new Set).add(t3),void 0!==this.renderRoot&&this.isConnected&&t3.hostConnected?.()}removeController(t3){this._$EO?.delete(t3)}_$E_(){const t3=new Map,s4=this.constructor.elementProperties;for(const i5 of s4.keys())this.hasOwnProperty(i5)&&(t3.set(i5,this[i5]),delete this[i5]);t3.size>0&&(this._$Ep=t3)}createRenderRoot(){const t3=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return S(t3,this.constructor.elementStyles),t3}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(true),this._$EO?.forEach(t3=>t3.hostConnected?.())}enableUpdating(t3){}disconnectedCallback(){this._$EO?.forEach(t3=>t3.hostDisconnected?.())}attributeChangedCallback(t3,s4,i5){this._$AK(t3,i5)}_$ET(t3,s4){const i5=this.constructor.elementProperties.get(t3),e4=this.constructor._$Eu(t3,i5);if(void 0!==e4&&true===i5.reflect){const h3=(void 0!==i5.converter?.toAttribute?i5.converter:u).toAttribute(s4,i5.type);this._$Em=t3,null==h3?this.removeAttribute(e4):this.setAttribute(e4,h3),this._$Em=null}}_$AK(t3,s4){const i5=this.constructor,e4=i5._$Eh.get(t3);if(void 0!==e4&&this._$Em!==e4){const t4=i5.getPropertyOptions(e4),h3="function"==typeof t4.converter?{fromAttribute:t4.converter}:void 0!==t4.converter?.fromAttribute?t4.converter:u;this._$Em=e4;const r4=h3.fromAttribute(s4,t4.type);this[e4]=r4??this._$Ej?.get(e4)??r4,this._$Em=null}}requestUpdate(t3,s4,i5,e4=false,h3){if(void 0!==t3){const r4=this.constructor;if(false===e4&&(h3=this[t3]),i5??=r4.getPropertyOptions(t3),!((i5.hasChanged??f)(h3,s4)||i5.useDefault&&i5.reflect&&h3===this._$Ej?.get(t3)&&!this.hasAttribute(r4._$Eu(t3,i5))))return;this.C(t3,s4,i5)}false===this.isUpdatePending&&(this._$ES=this._$EP())}C(t3,s4,{useDefault:i5,reflect:e4,wrapped:h3},r4){i5&&!(this._$Ej??=new Map).has(t3)&&(this._$Ej.set(t3,r4??s4??this[t3]),true!==h3||void 0!==r4)||(this._$AL.has(t3)||(this.hasUpdated||i5||(s4=void 0),this._$AL.set(t3,s4)),true===e4&&this._$Em!==t3&&(this._$Eq??=new Set).add(t3))}async _$EP(){this.isUpdatePending=true;try{await this._$ES}catch(t4){Promise.reject(t4)}const t3=this.scheduleUpdate();return null!=t3&&await t3,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(const[t5,s5]of this._$Ep)this[t5]=s5;this._$Ep=void 0}const t4=this.constructor.elementProperties;if(t4.size>0)for(const[s5,i5]of t4){const{wrapped:t5}=i5,e4=this[s5];true!==t5||this._$AL.has(s5)||void 0===e4||this.C(s5,void 0,i5,e4)}}let t3=false;const s4=this._$AL;try{t3=this.shouldUpdate(s4),t3?(this.willUpdate(s4),this._$EO?.forEach(t4=>t4.hostUpdate?.()),this.update(s4)):this._$EM()}catch(s5){throw t3=false,this._$EM(),s5}t3&&this._$AE(s4)}willUpdate(t3){}_$AE(t3){this._$EO?.forEach(t4=>t4.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=true,this.firstUpdated(t3)),this.updated(t3)}_$EM(){this._$AL=new Map,this.isUpdatePending=false}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t3){return true}update(t3){this._$Eq&&=this._$Eq.forEach(t4=>this._$ET(t4,this[t4])),this._$EM()}updated(t3){}firstUpdated(t3){}};y.elementStyles=[],y.shadowRootOptions={mode:"open"},y[d("elementProperties")]=new Map,y[d("finalized")]=new Map,p?.({ReactiveElement:y}),(a.reactiveElementVersions??=[]).push("2.1.2");var t2=globalThis;var i3=t3=>t3;var s2=t2.trustedTypes;var e3=s2?s2.createPolicy("lit-html",{createHTML:t3=>t3}):void 0;var h2="$lit$";var o3=`lit$${Math.random().toFixed(9).slice(2)}$`;var n3="?"+o3;var r3=`<${n3}>`;var l2=document;var c3=()=>l2.createComment("");var a2=t3=>null===t3||"object"!=typeof t3&&"function"!=typeof t3;var u2=Array.isArray;var d2=t3=>u2(t3)||"function"==typeof t3?.[Symbol.iterator];var f2="[ 	\n\f\r]";var v=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g;var _=/-->/g;var m=/>/g;var p2=RegExp(`>|${f2}(?:([^\\s"'>=/]+)(${f2}*=${f2}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g");var g=/'/g;var $=/"/g;var y2=/^(?:script|style|textarea|title)$/i;var x=t3=>(i5,...s4)=>({_$litType$:t3,strings:i5,values:s4});var b2=x(1);var w=x(2);var T=x(3);var E=Symbol.for("lit-noChange");var A=Symbol.for("lit-nothing");var C=new WeakMap;var P=l2.createTreeWalker(l2,129);function V(t3,i5){if(!u2(t3)||!t3.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==e3?e3.createHTML(i5):i5}var N=(t3,i5)=>{const s4=t3.length-1,e4=[];let n4,l3=2===i5?"<svg>":3===i5?"<math>":"",c4=v;for(let i6=0;i6<s4;i6++){const s5=t3[i6];let a3,u3,d3=-1,f3=0;for(;f3<s5.length&&(c4.lastIndex=f3,u3=c4.exec(s5),null!==u3);)f3=c4.lastIndex,c4===v?"!--"===u3[1]?c4=_:void 0!==u3[1]?c4=m:void 0!==u3[2]?(y2.test(u3[2])&&(n4=RegExp("</"+u3[2],"g")),c4=p2):void 0!==u3[3]&&(c4=p2):c4===p2?">"===u3[0]?(c4=n4??v,d3=-1):void 0===u3[1]?d3=-2:(d3=c4.lastIndex-u3[2].length,a3=u3[1],c4=void 0===u3[3]?p2:'"'===u3[3]?$:g):c4===$||c4===g?c4=p2:c4===_||c4===m?c4=v:(c4=p2,n4=void 0);const x2=c4===p2&&t3[i6+1].startsWith("/>")?" ":"";l3+=c4===v?s5+r3:d3>=0?(e4.push(a3),s5.slice(0,d3)+h2+s5.slice(d3)+o3+x2):s5+o3+(-2===d3?i6:x2)}return[V(t3,l3+(t3[s4]||"<?>")+(2===i5?"</svg>":3===i5?"</math>":"")),e4]};var S2=class _S{constructor({strings:t3,_$litType$:i5},e4){let r4;this.parts=[];let l3=0,a3=0;const u3=t3.length-1,d3=this.parts,[f3,v2]=N(t3,i5);if(this.el=_S.createElement(f3,e4),P.currentNode=this.el.content,2===i5||3===i5){const t4=this.el.content.firstChild;t4.replaceWith(...t4.childNodes)}for(;null!==(r4=P.nextNode())&&d3.length<u3;){if(1===r4.nodeType){if(r4.hasAttributes())for(const t4 of r4.getAttributeNames())if(t4.endsWith(h2)){const i6=v2[a3++],s4=r4.getAttribute(t4).split(o3),e5=/([.?@])?(.*)/.exec(i6);d3.push({type:1,index:l3,name:e5[2],strings:s4,ctor:"."===e5[1]?I:"?"===e5[1]?L:"@"===e5[1]?z:H}),r4.removeAttribute(t4)}else t4.startsWith(o3)&&(d3.push({type:6,index:l3}),r4.removeAttribute(t4));if(y2.test(r4.tagName)){const t4=r4.textContent.split(o3),i6=t4.length-1;if(i6>0){r4.textContent=s2?s2.emptyScript:"";for(let s4=0;s4<i6;s4++)r4.append(t4[s4],c3()),P.nextNode(),d3.push({type:2,index:++l3});r4.append(t4[i6],c3())}}}else if(8===r4.nodeType)if(r4.data===n3)d3.push({type:2,index:l3});else{let t4=-1;for(;-1!==(t4=r4.data.indexOf(o3,t4+1));)d3.push({type:7,index:l3}),t4+=o3.length-1}l3++}}static createElement(t3,i5){const s4=l2.createElement("template");return s4.innerHTML=t3,s4}};function M(t3,i5,s4=t3,e4){if(i5===E)return i5;let h3=void 0!==e4?s4._$Co?.[e4]:s4._$Cl;const o5=a2(i5)?void 0:i5._$litDirective$;return h3?.constructor!==o5&&(h3?._$AO?.(false),void 0===o5?h3=void 0:(h3=new o5(t3),h3._$AT(t3,s4,e4)),void 0!==e4?(s4._$Co??=[])[e4]=h3:s4._$Cl=h3),void 0!==h3&&(i5=M(t3,h3._$AS(t3,i5.values),h3,e4)),i5}var R=class{constructor(t3,i5){this._$AV=[],this._$AN=void 0,this._$AD=t3,this._$AM=i5}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t3){const{el:{content:i5},parts:s4}=this._$AD,e4=(t3?.creationScope??l2).importNode(i5,true);P.currentNode=e4;let h3=P.nextNode(),o5=0,n4=0,r4=s4[0];for(;void 0!==r4;){if(o5===r4.index){let i6;2===r4.type?i6=new k(h3,h3.nextSibling,this,t3):1===r4.type?i6=new r4.ctor(h3,r4.name,r4.strings,this,t3):6===r4.type&&(i6=new Z(h3,this,t3)),this._$AV.push(i6),r4=s4[++n4]}o5!==r4?.index&&(h3=P.nextNode(),o5++)}return P.currentNode=l2,e4}p(t3){let i5=0;for(const s4 of this._$AV)void 0!==s4&&(void 0!==s4.strings?(s4._$AI(t3,s4,i5),i5+=s4.strings.length-2):s4._$AI(t3[i5])),i5++}};var k=class _k{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t3,i5,s4,e4){this.type=2,this._$AH=A,this._$AN=void 0,this._$AA=t3,this._$AB=i5,this._$AM=s4,this.options=e4,this._$Cv=e4?.isConnected??true}get parentNode(){let t3=this._$AA.parentNode;const i5=this._$AM;return void 0!==i5&&11===t3?.nodeType&&(t3=i5.parentNode),t3}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t3,i5=this){t3=M(this,t3,i5),a2(t3)?t3===A||null==t3||""===t3?(this._$AH!==A&&this._$AR(),this._$AH=A):t3!==this._$AH&&t3!==E&&this._(t3):void 0!==t3._$litType$?this.$(t3):void 0!==t3.nodeType?this.T(t3):d2(t3)?this.k(t3):this._(t3)}O(t3){return this._$AA.parentNode.insertBefore(t3,this._$AB)}T(t3){this._$AH!==t3&&(this._$AR(),this._$AH=this.O(t3))}_(t3){this._$AH!==A&&a2(this._$AH)?this._$AA.nextSibling.data=t3:this.T(l2.createTextNode(t3)),this._$AH=t3}$(t3){const{values:i5,_$litType$:s4}=t3,e4="number"==typeof s4?this._$AC(t3):(void 0===s4.el&&(s4.el=S2.createElement(V(s4.h,s4.h[0]),this.options)),s4);if(this._$AH?._$AD===e4)this._$AH.p(i5);else{const t4=new R(e4,this),s5=t4.u(this.options);t4.p(i5),this.T(s5),this._$AH=t4}}_$AC(t3){let i5=C.get(t3.strings);return void 0===i5&&C.set(t3.strings,i5=new S2(t3)),i5}k(t3){u2(this._$AH)||(this._$AH=[],this._$AR());const i5=this._$AH;let s4,e4=0;for(const h3 of t3)e4===i5.length?i5.push(s4=new _k(this.O(c3()),this.O(c3()),this,this.options)):s4=i5[e4],s4._$AI(h3),e4++;e4<i5.length&&(this._$AR(s4&&s4._$AB.nextSibling,e4),i5.length=e4)}_$AR(t3=this._$AA.nextSibling,s4){for(this._$AP?.(false,true,s4);t3!==this._$AB;){const s5=i3(t3).nextSibling;i3(t3).remove(),t3=s5}}setConnected(t3){void 0===this._$AM&&(this._$Cv=t3,this._$AP?.(t3))}};var H=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t3,i5,s4,e4,h3){this.type=1,this._$AH=A,this._$AN=void 0,this.element=t3,this.name=i5,this._$AM=e4,this.options=h3,s4.length>2||""!==s4[0]||""!==s4[1]?(this._$AH=Array(s4.length-1).fill(new String),this.strings=s4):this._$AH=A}_$AI(t3,i5=this,s4,e4){const h3=this.strings;let o5=false;if(void 0===h3)t3=M(this,t3,i5,0),o5=!a2(t3)||t3!==this._$AH&&t3!==E,o5&&(this._$AH=t3);else{const e5=t3;let n4,r4;for(t3=h3[0],n4=0;n4<h3.length-1;n4++)r4=M(this,e5[s4+n4],i5,n4),r4===E&&(r4=this._$AH[n4]),o5||=!a2(r4)||r4!==this._$AH[n4],r4===A?t3=A:t3!==A&&(t3+=(r4??"")+h3[n4+1]),this._$AH[n4]=r4}o5&&!e4&&this.j(t3)}j(t3){t3===A?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t3??"")}};var I=class extends H{constructor(){super(...arguments),this.type=3}j(t3){this.element[this.name]=t3===A?void 0:t3}};var L=class extends H{constructor(){super(...arguments),this.type=4}j(t3){this.element.toggleAttribute(this.name,!!t3&&t3!==A)}};var z=class extends H{constructor(t3,i5,s4,e4,h3){super(t3,i5,s4,e4,h3),this.type=5}_$AI(t3,i5=this){if((t3=M(this,t3,i5,0)??A)===E)return;const s4=this._$AH,e4=t3===A&&s4!==A||t3.capture!==s4.capture||t3.once!==s4.once||t3.passive!==s4.passive,h3=t3!==A&&(s4===A||e4);e4&&this.element.removeEventListener(this.name,this,s4),h3&&this.element.addEventListener(this.name,this,t3),this._$AH=t3}handleEvent(t3){"function"==typeof this._$AH?this._$AH.call(this.options?.host??this.element,t3):this._$AH.handleEvent(t3)}};var Z=class{constructor(t3,i5,s4){this.element=t3,this.type=6,this._$AN=void 0,this._$AM=i5,this.options=s4}get _$AU(){return this._$AM._$AU}_$AI(t3){M(this,t3)}};var B=t2.litHtmlPolyfillSupport;B?.(S2,k),(t2.litHtmlVersions??=[]).push("3.3.3");var D=(t3,i5,s4)=>{const e4=s4?.renderBefore??i5;let h3=e4._$litPart$;if(void 0===h3){const t4=s4?.renderBefore??null;e4._$litPart$=h3=new k(i5.insertBefore(c3(),t4),t4,void 0,s4??{})}return h3._$AI(t3),h3};var s3=globalThis;var i4=class extends y{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){const t3=super.createRenderRoot();return this.renderOptions.renderBefore??=t3.firstChild,t3}update(t3){const r4=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t3),this._$Do=D(r4,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(true)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(false)}render(){return E}};i4._$litElement$=true,i4["finalized"]=true,s3.litElementHydrateSupport?.({LitElement:i4});var o4=s3.litElementPolyfillSupport;o4?.({LitElement:i4});(s3.litElementVersions??=[]).push("4.2.2");var NimlykoderPanel=class extends i4{static get properties(){return{hass:{type:Object},narrow:{type:Boolean},route:{type:Object},panel:{type:Object},codes:{type:Array},loading:{type:Boolean},error:{type:String},searchQuery:{type:String},showAddDialog:{type:Boolean},showEditDialog:{type:Boolean},showRemoveDialog:{type:Boolean},showPinConfirmDialog:{type:Boolean},editingCode:{type:Object},editFormError:{type:String},removingCode:{type:Object},config:{type:Object},showExpiredInfo:{type:Boolean},suggestedSlot:{type:Number},translations:{type:Object},pendingPinUpdate:{type:Object}}}constructor(){super();this.codes=[];this.loading=true;this.error=null;this.searchQuery="";this.showAddDialog=false;this.showEditDialog=false;this.showRemoveDialog=false;this.showPinConfirmDialog=false;this.editingCode=null;this.editFormError=null;this.removingCode=null;this.config={auto_expire:true,cleanup_time:"03:00:00",reserved_slots:[]};this.showExpiredInfo=false;this.suggestedSlot=null;this.translations=this._defaultTranslations();this.pendingPinUpdate=null}_defaultTranslations(){return{title:"Nimlykoder",subtitle:"Manage credentials for your Nimly lock",add_code:"Add Code",search_placeholder:"Search by name, slot, or type...",stats:{total:"Total Codes",permanent:"Permanent",guest:"Guest",expired:"Expired"},status:{active:"Active",expired:"Expired",reserved:"Reserved"},type:{permanent:"Permanent",guest:"Guest",pin:"PIN codes",tag:"Tags",fingerprint:"Fingerprints"},manually_configured:"Manually configured",dialog:{add_title:"Add New Person",edit_title:"Edit Person",remove_title:"Remove Person",confirm_remove:"Are you sure you want to remove",remove_description:"This will delete the PIN code from slot {slot} and remove it from the lock.",tag_remove_description:"This only removes the tag record from Nimlykoder. It does not revoke access on the lock. Delete the tag using the lock keypad or vendor app. If it is used again, it can be discovered again.",fingerprint_remove_description:"This only removes the fingerprint record from Nimlykoder. It does not revoke access on the lock. Delete the fingerprint using the lock keypad or vendor app. If it is used again, it can be discovered again.",reserved_pin:"Reserved PIN slots cannot be removed here.",name:"Name",name_placeholder:"e.g., John Doe",pin_code:"PIN Code",pin_placeholder:"6 digits",pin_hint:"Enter a 6 digit PIN code",change_pin:"Change PIN Code",pin_change_warning:"Leave empty to keep the current PIN code",confirm_pin_change:"Confirm PIN Change",pin_warning_title:"Warning: Irreversible Action",pin_warning_message:"Changing the PIN code will permanently replace the old code. There is no way to retrieve the previous PIN code.",pin_confirm_question:"Are you sure you want to change the PIN code for {name}?",confirm_change:"Yes, Change PIN",type:"Type",expiry:"Expiry Date",expiry_hint:"Leave empty for no expiry (permanent access)",permanent_no_expiry:"Permanent codes do not have an expiry date.",slot:"Slot",next_available:"Next available",cancel:"Cancel",save:"Save Changes",add:"Add Person",remove:"Remove",remove_local:"Remove from Nimlykoder"},errors:{name_required:"Name is required",pin_invalid:"PIN code must be exactly 6 digits"},empty:{title:"No PIN codes yet",description:"Add your first person to get started with Nimlykoder",add_first:"Add First Person"},section_empty:"No entries",no_results:{title:"No results found",description:"Try a different search term"},loading:"Loading codes...",retry:"Retry",expires:"Expires",expired_on:"Expired",slot_label:"Slot",expired_info:{title:"Expired Codes",description:"Expired codes have passed their set expiry date and are no longer valid for entry.",auto_cleanup:"Auto-cleanup is enabled. Expired codes will be automatically removed at {time}.",manual_cleanup:"Auto-cleanup is disabled. Remove expired codes manually."}}}static get styles(){return i`
            :host {
                display: block;
                --primary-color: var(--ha-primary-color, #03a9f4);
                --text-primary: var(--primary-text-color, #212121);
                --text-secondary: var(--secondary-text-color, #727272);
                --divider: var(--divider-color, #e0e0e0);
                --card-bg: var(--card-background-color, #fff);
                --bg: var(--primary-background-color, #fafafa);
            }

            /* Top App Bar - Home Assistant style */
            .app-header {
                background-color: var(--app-header-background-color, var(--primary-color));
                color: var(--app-header-text-color, var(--text-primary-color, #fff));
                display: flex;
                align-items: center;
                height: 56px;
                padding: 0 4px;
                box-sizing: border-box;
                position: sticky;
                top: 0;
                z-index: 4;
            }

            .menu-btn {
                width: 48px;
                height: 48px;
                display: flex;
                align-items: center;
                justify-content: center;
                background: none;
                border: none;
                cursor: pointer;
                color: inherit;
                border-radius: 50%;
                margin: 0 4px;
            }

            .menu-btn:hover {
                background: rgba(255, 255, 255, 0.1);
            }

            .menu-btn svg {
                width: 24px;
                height: 24px;
            }

            .app-header-title {
                font-size: 20px;
                font-weight: 400;
                margin-left: 8px;
                flex: 1;
            }

            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 16px;
            }

            /* Lock Status Bar */
            .lock-status-bar {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 12px 16px;
                background: var(--card-bg);
                border-radius: 12px;
                margin-bottom: 20px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            }

            .lock-status-icon {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-shrink: 0;
            }

            .lock-status-icon.locked {
                background: rgba(76, 175, 80, 0.15);
                color: #4caf50;
            }

            .lock-status-icon.unlocked {
                background: rgba(255, 152, 0, 0.15);
                color: #ff9800;
            }

            .lock-status-icon.unknown {
                background: rgba(158, 158, 158, 0.15);
                color: #9e9e9e;
            }

            .lock-status-icon svg {
                width: 24px;
                height: 24px;
            }

            .lock-status-info {
                flex: 1;
                min-width: 0;
            }

            .lock-status-name {
                font-size: 16px;
                font-weight: 500;
                color: var(--text-primary);
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }

            .lock-status-state {
                font-size: 13px;
                color: var(--text-secondary);
                display: flex;
                align-items: center;
                gap: 6px;
            }

            .lock-status-state .dot {
                width: 8px;
                height: 8px;
                border-radius: 50%;
            }

            .lock-status-state .dot.locked {
                background: #4caf50;
            }

            .lock-status-state .dot.unlocked {
                background: #ff9800;
            }

            .lock-status-state .dot.unknown {
                background: #9e9e9e;
            }

            .lock-status-slots {
                text-align: right;
                flex-shrink: 0;
            }

            .lock-status-slots-count {
                font-size: 20px;
                font-weight: 600;
                color: var(--primary-color);
            }

            .lock-status-slots-label {
                font-size: 11px;
                color: var(--text-secondary);
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }

            /* Search and Actions Bar */
            .toolbar {
                display: flex;
                gap: 12px;
                margin-bottom: 20px;
                flex-wrap: wrap;
            }

            .search-container {
                flex: 1;
                min-width: 200px;
                position: relative;
            }

            .search-input {
                width: 100%;
                padding: 12px 16px 12px 44px;
                border: 1px solid var(--divider);
                border-radius: 28px;
                font-size: 16px;
                background: var(--card-bg);
                color: var(--text-primary);
                outline: none;
                transition: border-color 0.2s, box-shadow 0.2s;
                box-sizing: border-box;
            }

            .search-input:focus {
                border-color: var(--primary-color);
                box-shadow: 0 0 0 1px var(--primary-color);
            }

            .search-input::placeholder {
                color: var(--text-secondary);
            }

            .search-icon {
                position: absolute;
                left: 16px;
                top: 50%;
                transform: translateY(-50%);
                color: var(--text-secondary);
                pointer-events: none;
            }

            /* Buttons */
            .btn {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 12px 24px;
                border: none;
                border-radius: 28px;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }

            .btn-primary {
                background: var(--primary-color);
                color: var(--text-primary-color, white);
                box-shadow: 0 2px 8px rgba(var(--rgb-primary-color, 3, 169, 244), 0.4);
            }

            .btn-primary:hover {
                filter: brightness(1.1);
                box-shadow: 0 4px 16px rgba(var(--rgb-primary-color, 3, 169, 244), 0.5);
                transform: translateY(-1px);
            }

            .btn-secondary {
                background: var(--card-bg);
                color: var(--text-primary);
                border: 1px solid var(--divider);
            }

            .btn-secondary:hover {
                background: var(--bg);
            }

            .btn-danger {
                background: #f44336;
                color: white;
            }

            .btn-danger:hover {
                background: #d32f2f;
            }

            .btn-text {
                background: transparent;
                color: var(--primary-color);
                padding: 8px 16px;
            }

            .btn-text:hover {
                background: rgba(3, 169, 244, 0.1);
            }

            .btn-icon {
                width: 40px;
                height: 40px;
                padding: 0;
                border-radius: 50%;
                justify-content: center;
            }

            .btn svg {
                width: 20px;
                height: 20px;
                flex-shrink: 0;
            }

            /* Stats Cards */
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 16px;
                margin-bottom: 24px;
            }

            .stat-card {
                background: var(--card-bg);
                border-radius: 16px;
                padding: 20px;
                text-align: center;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            }

            .stat-value {
                font-size: 32px;
                font-weight: 600;
                color: var(--text-primary);
            }

            .stat-label {
                font-size: 13px;
                color: var(--text-secondary);
                margin-top: 4px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }

            .stat-header {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
            }

            .info-icon {
                width: 20px;
                height: 20px;
                color: var(--text-secondary);
                cursor: pointer;
                transition: color 0.2s;
            }

            .info-icon:hover {
                color: var(--primary-color);
            }

            .stat-card.expired {
                position: relative;
            }

            /* Info Tooltip */
            .info-tooltip {
                position: absolute;
                bottom: calc(100% + 12px);
                left: 50%;
                transform: translateX(-50%);
                background: var(--card-bg);
                border: 1px solid var(--divider);
                border-radius: 12px;
                padding: 16px;
                width: 280px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
                z-index: 100;
                text-align: left;
            }

            .info-tooltip::after {
                content: '';
                position: absolute;
                top: 100%;
                left: 50%;
                transform: translateX(-50%);
                border: 8px solid transparent;
                border-top-color: var(--card-bg);
            }

            .info-tooltip::before {
                content: '';
                position: absolute;
                top: 100%;
                left: 50%;
                transform: translateX(-50%);
                border: 9px solid transparent;
                border-top-color: var(--divider);
            }

            .info-tooltip h4 {
                margin: 0 0 8px 0;
                font-size: 14px;
                font-weight: 600;
                color: var(--text-primary);
                display: flex;
                align-items: center;
                gap: 8px;
            }

            .info-tooltip h4 svg {
                width: 18px;
                height: 18px;
                color: #f44336;
            }

            .info-tooltip p {
                margin: 0;
                font-size: 13px;
                color: var(--text-secondary);
                line-height: 1.5;
            }

            .info-tooltip .highlight {
                color: var(--primary-color);
                font-weight: 500;
            }

            .stat-card.permanent .stat-value { color: #4caf50; }
            .stat-card.guest .stat-value { color: #2196f3; }
            .stat-card.expired .stat-value { color: #f44336; }

            /* Person List */
            .person-list {
                display: grid;
                gap: 12px;
            }

            .credential-section {
                margin-top: 24px;
            }

            .credential-section h2 {
                margin: 0 0 12px;
                font-size: 18px;
                font-weight: 500;
            }

            .credential-empty {
                color: var(--text-secondary);
                margin: 0;
            }

            .person-card {
                background: var(--card-bg);
                border-radius: 16px;
                padding: 16px 20px;
                display: flex;
                align-items: center;
                gap: 16px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
                transition: box-shadow 0.2s, transform 0.2s;
            }

            .person-card:hover {
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
            }

            .person-avatar {
                width: 52px;
                height: 52px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 20px;
                font-weight: 600;
                color: white;
                flex-shrink: 0;
            }

            .avatar-permanent {
                background: linear-gradient(135deg, #4caf50 0%, #2e7d32 100%);
            }

            .avatar-guest {
                background: linear-gradient(135deg, #2196f3 0%, #1565c0 100%);
            }

            .avatar-expired {
                background: linear-gradient(135deg, #9e9e9e 0%, #616161 100%);
            }

            .person-info {
                flex: 1;
                min-width: 0;
            }

            .person-name {
                font-size: 16px;
                font-weight: 500;
                color: var(--text-primary);
                margin: 0 0 4px 0;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }

            .person-details {
                display: flex;
                gap: 16px;
                flex-wrap: wrap;
            }

            .person-detail {
                display: flex;
                align-items: center;
                gap: 4px;
                font-size: 13px;
                color: var(--text-secondary);
            }

            .person-detail svg {
                width: 16px;
                height: 16px;
                opacity: 0.7;
            }

            .badge {
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }

            .badge-permanent {
                background: #e8f5e9;
                color: #2e7d32;
            }

            .badge-guest {
                background: #e3f2fd;
                color: #1565c0;
            }

            .badge-expired {
                background: #ffebee;
                color: #c62828;
            }

            .person-actions {
                display: flex;
                gap: 8px;
            }

            /* Empty State */
            .empty-state {
                text-align: center;
                padding: 60px 20px;
                background: var(--card-bg);
                border-radius: 16px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
            }

            .empty-icon {
                width: 80px;
                height: 80px;
                margin: 0 auto 20px;
                background: var(--primary-color);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
            }

            .empty-icon svg {
                width: 40px;
                height: 40px;
            }

            .empty-state h2 {
                margin: 0 0 8px 0;
                font-size: 20px;
                font-weight: 500;
                color: var(--text-primary);
            }

            .empty-state p {
                margin: 0 0 24px 0;
                color: var(--text-secondary);
            }

            /* Loading */
            .loading-container {
                text-align: center;
                padding: 60px 20px;
            }

            .spinner {
                width: 48px;
                height: 48px;
                border: 3px solid var(--divider);
                border-top-color: var(--primary-color);
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin: 0 auto 16px;
            }

            @keyframes spin {
                to { transform: rotate(360deg); }
            }

            /* Error */
            .error-banner {
                background: #ffebee;
                color: #c62828;
                padding: 12px 16px;
                border-radius: 8px;
                margin-bottom: 16px;
                display: flex;
                align-items: center;
                gap: 12px;
            }

            .error-banner svg {
                width: 24px;
                height: 24px;
                flex-shrink: 0;
            }

            .error-banner span {
                flex: 1;
            }

            /* Dialog Overlay */
            .dialog-overlay {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 1000;
                padding: 16px;
            }

            .dialog {
                background: var(--card-bg);
                border-radius: 16px;
                width: 100%;
                max-width: 480px;
                max-height: 90vh;
                overflow: auto;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            }

            .dialog-header {
                padding: 20px 24px;
                border-bottom: 1px solid var(--divider);
                display: flex;
                align-items: center;
                justify-content: space-between;
            }

            .dialog-header h2 {
                margin: 0;
                font-size: 20px;
                font-weight: 500;
            }

            .dialog-content {
                padding: 24px;
            }

            .dialog-actions {
                padding: 16px 24px;
                border-top: 1px solid var(--divider);
                display: flex;
                justify-content: flex-end;
                gap: 12px;
            }

            /* Form */
            .form-group {
                margin-bottom: 20px;
            }

            .form-group label {
                display: block;
                margin-bottom: 8px;
                font-size: 14px;
                font-weight: 500;
                color: var(--text-primary);
            }

            .form-group input,
            .form-group select {
                width: 100%;
                padding: 12px 16px;
                border: 1px solid var(--divider);
                border-radius: 8px;
                font-size: 16px;
                background: var(--bg);
                color: var(--text-primary);
                outline: none;
                transition: border-color 0.2s;
                box-sizing: border-box;
            }

            .form-group input:focus,
            .form-group select:focus {
                border-color: var(--primary-color);
            }

            .form-group small {
                display: block;
                margin-top: 6px;
                font-size: 12px;
                color: var(--text-secondary);
            }

            .form-group .field-error {
                color: #c62828;
                font-weight: 500;
            }

            .form-row {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 16px;
            }

            /* Responsive */
            @media (max-width: 600px) {
                .header {
                    flex-direction: column;
                    align-items: flex-start;
                }

                .toolbar {
                    flex-direction: column;
                }

                .search-container {
                    width: 100%;
                }

                .person-card {
                    flex-wrap: wrap;
                }

                .person-actions {
                    width: 100%;
                    justify-content: flex-end;
                    margin-top: 8px;
                    padding-top: 12px;
                    border-top: 1px solid var(--divider);
                }

                .form-row {
                    grid-template-columns: 1fr;
                }

                .stats {
                    grid-template-columns: repeat(2, 1fr);
                }
            }
        `}connectedCallback(){super.connectedCallback();this.loadTranslations();this.loadCodes();this.loadConfig()}async loadCodes(){try{this.loading=true;this.error=null;const result=await this.hass.callWS({type:"nimlykoder/list"});this.codes=result.codes||[];this.loading=false}catch(err){this.error=err.message;this.loading=false}}async loadConfig(){try{const result=await this.hass.callWS({type:"nimlykoder/config"});this.config=result}catch(err){console.error("Failed to load config:",err)}}async loadTranslations(){try{const result=await this.hass.callWS({type:"nimlykoder/translations"});if(result&&result.translations){this.translations=this._mergeTranslations(this._defaultTranslations(),result.translations)}}catch(err){console.error("Failed to load translations:",err)}}_mergeTranslations(defaults,loaded){const result={...defaults};for(const key of Object.keys(loaded)){if(typeof loaded[key]==="object"&&loaded[key]!==null&&!Array.isArray(loaded[key])){result[key]=this._mergeTranslations(defaults[key]||{},loaded[key])}else{result[key]=loaded[key]}}return result}t(path,replacements={}){const keys=path.split(".");let value=this.translations;for(const key of keys){if(value&&typeof value==="object"&&key in value){value=value[key]}else{return path}}if(typeof value==="string"){for(const[k2,v2]of Object.entries(replacements)){value=value.replace(`{${k2}}`,v2)}}return value}get cleanupTimeFormatted(){const time=this.config?.cleanup_time||"03:00:00";const[hours,minutes]=time.split(":");const hour=parseInt(hours);const min=minutes||"00";if(hour===0)return`12:${min} AM`;if(hour<12)return`${hour}:${min} AM`;if(hour===12)return`12:${min} PM`;return`${hour-12}:${min} PM`}get filteredCodes(){if(!this.searchQuery)return this.codes;const query=this.searchQuery.toLowerCase();return this.codes.filter(code=>this.displayName(code).toLowerCase().includes(query)||code.slot.toString().includes(query)||(code.method||"pin").toLowerCase().includes(query)||(code.type||"").toLowerCase().includes(query))}get stats(){const total=this.codes.length;const permanent=this.codes.filter(c4=>(c4.method||"pin")==="pin"&&c4.type==="permanent").length;const guest=this.codes.filter(c4=>(c4.method||"pin")==="pin"&&c4.type==="guest").length;const expired=this.codes.filter(c4=>(c4.method||"pin")==="pin"&&c4.expiry&&new Date(c4.expiry)<new Date).length;return{total,permanent,guest,expired}}getInitials(name){if(!name)return"?";return name.split(" ").map(n4=>n4[0]).join("").toUpperCase().slice(0,2)}isExpired(code){return(code.method||"pin")==="pin"&&code.expiry&&new Date(code.expiry)<new Date}displayName(code){return code.name||this.t("manually_configured")}isPinReserved(code){return(code.method||"pin")==="pin"&&(code.slot===0||(this.config?.reserved_slots||[]).includes(code.slot))}getAvatarClass(code){if(this.isExpired(code))return"avatar-expired";return code.type==="permanent"?"avatar-permanent":"avatar-guest"}getBadgeClass(code){if(this.isExpired(code))return"badge-expired";return code.type==="permanent"?"badge-permanent":"badge-guest"}getBadgeText(code){const method=code.method||"pin";if(method!=="pin")return this.t(`type.${method}`);if(this.isExpired(code))return this.t("status.expired");return code.type==="permanent"?this.t("type.permanent"):this.t("type.guest")}formatDate(dateStr){if(!dateStr)return"\u2014";const date=new Date(dateStr);return date.toLocaleDateString(void 0,{year:"numeric",month:"short",day:"numeric"})}render(){return b2`
            ${this._renderAppHeader()}
            <div class="container">
                ${this.error?this._renderError():""}
                ${this.loading?this._renderLoading():b2`
                          ${this._renderLockStatus()}
                          ${this._renderStats()}
                          ${this._renderToolbar()}
                          ${this._renderPersonList()}
                      `}
                ${this.showAddDialog?this._renderAddDialog():""}
                ${this.showEditDialog?this._renderEditDialog():""}
                ${this.showRemoveDialog?this._renderRemoveDialog():""}
                ${this.showPinConfirmDialog?this._renderPinConfirmDialog():""}
            </div>
        `}_renderAppHeader(){return b2`
            <div class="app-header">
                <button class="menu-btn" @click=${this._toggleMenu} aria-label="Open menu">
                    <svg viewBox="0 0 24 24" fill="currentColor">
                        <path d="M3,6H21V8H3V6M3,11H21V13H3V11M3,16H21V18H3V16Z"/>
                    </svg>
                </button>
                <div class="app-header-title">${this.t("title")}</div>
            </div>
        `}_toggleMenu(){this.dispatchEvent(new CustomEvent("hass-toggle-menu",{bubbles:true,composed:true}))}_renderLockStatus(){const lockEntityId=this.config?.lock_entity||"";const lockState=this.hass?.states?.[lockEntityId];const lockName=lockState?.attributes?.friendly_name||lockEntityId.split(".").pop()||"Lock";const state=lockState?.state||"unknown";const isLocked=state==="locked";const isUnlocked=state==="unlocked";const stateClass=isLocked?"locked":isUnlocked?"unlocked":"unknown";const stateText=isLocked?"Locked":isUnlocked?"Unlocked":"Unknown";const availableSlots=(this.config?.slot_max||99)-(this.config?.slot_min||0)+1-this.codes.length;return b2`
            <div class="lock-status-bar">
                <div class="lock-status-icon ${stateClass}">
                    ${isLocked?b2`
                        <svg viewBox="0 0 24 24" fill="currentColor">
                            <path d="M12,17A2,2 0 0,0 14,15C14,13.89 13.1,13 12,13A2,2 0 0,0 10,15A2,2 0 0,0 12,17M18,8A2,2 0 0,1 20,10V20A2,2 0 0,1 18,22H6A2,2 0 0,1 4,20V10C4,8.89 4.9,8 6,8H7V6A5,5 0 0,1 12,1A5,5 0 0,1 17,6V8H18M12,3A3,3 0 0,0 9,6V8H15V6A3,3 0 0,0 12,3Z"/>
                        </svg>
                    `:b2`
                        <svg viewBox="0 0 24 24" fill="currentColor">
                            <path d="M18,8A2,2 0 0,1 20,10V20A2,2 0 0,1 18,22H6C4.89,22 4,21.1 4,20V10A2,2 0 0,1 6,8H15V6A3,3 0 0,0 12,3A3,3 0 0,0 9,6H7A5,5 0 0,1 12,1A5,5 0 0,1 17,6V8H18M12,17A2,2 0 0,0 14,15A2,2 0 0,0 12,13A2,2 0 0,0 10,15A2,2 0 0,0 12,17Z"/>
                        </svg>
                    `}
                </div>
                <div class="lock-status-info">
                    <div class="lock-status-name">${lockName}</div>
                    <div class="lock-status-state">
                        <span class="dot ${stateClass}"></span>
                        ${stateText}
                    </div>
                </div>
                <div class="lock-status-slots">
                    <div class="lock-status-slots-count">${availableSlots}</div>
                    <div class="lock-status-slots-label">Slots available</div>
                </div>
            </div>
        `}_renderStats(){const{total,permanent,guest,expired}=this.stats;const autoExpireEnabled=this.config?.auto_expire!==false;return b2`
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-value">${total}</div>
                    <div class="stat-label">${this.t("stats.total")}</div>
                </div>
                <div class="stat-card permanent">
                    <div class="stat-value">${permanent}</div>
                    <div class="stat-label">${this.t("stats.permanent")}</div>
                </div>
                <div class="stat-card guest">
                    <div class="stat-value">${guest}</div>
                    <div class="stat-label">${this.t("stats.guest")}</div>
                </div>
                <div class="stat-card expired">
                    <div class="stat-header">
                        <div class="stat-value">${expired}</div>
                        <svg 
                            class="info-icon" 
                            viewBox="0 0 24 24" 
                            fill="currentColor"
                            @click=${e4=>{e4.stopPropagation();this.showExpiredInfo=!this.showExpiredInfo}}
                            @mouseenter=${()=>this.showExpiredInfo=true}
                            @mouseleave=${()=>this.showExpiredInfo=false}
                        >
                            <path d="M13,9H11V7H13M13,17H11V11H13M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2Z"/>
                        </svg>
                    </div>
                    <div class="stat-label">${this.t("stats.expired")}</div>
                    ${this.showExpiredInfo?b2`
                        <div class="info-tooltip">
                            <h4>
                                <svg viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M12,20A8,8 0 0,0 20,12A8,8 0 0,0 12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20M12,2A10,10 0 0,1 22,12A10,10 0 0,1 12,22C6.47,22 2,17.5 2,12A10,10 0 0,1 12,2M12.5,7V12.25L17,14.92L16.25,16.15L11,13V7H12.5Z"/>
                                </svg>
                                ${this.t("expired_info.title")}
                            </h4>
                            <p>
                                ${this.t("expired_info.description")}
                                ${autoExpireEnabled?b2`<br><br>${this.t("expired_info.auto_cleanup",{time:this.cleanupTimeFormatted})}`:b2`<br><br>${this.t("expired_info.manual_cleanup")}`}
                            </p>
                        </div>
                    `:""}
                </div>
            </div>
        `}_renderToolbar(){return b2`
            <div class="toolbar">
                <div class="search-container">
                    <svg class="search-icon" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M9.5,3A6.5,6.5 0 0,1 16,9.5C16,11.11 15.41,12.59 14.44,13.73L14.71,14H15.5L20.5,19L19,20.5L14,15.5V14.71L13.73,14.44C12.59,15.41 11.11,16 9.5,16A6.5,6.5 0 0,1 3,9.5A6.5,6.5 0 0,1 9.5,3M9.5,5C7,5 5,7 5,9.5C5,12 7,14 9.5,14C12,14 14,12 14,9.5C14,7 12,5 9.5,5Z"/>
                    </svg>
                    <input
                        type="text"
                        class="search-input"
                        placeholder="${this.t("search_placeholder")}"
                        .value=${this.searchQuery}
                        @input=${e4=>this.searchQuery=e4.target.value}
                    />
                </div>
                <button class="btn btn-primary" @click=${()=>this._openAddDialog()}>
                    <svg viewBox="0 0 24 24" fill="currentColor">
                        <path d="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z"/>
                    </svg>
                    ${this.t("add_code")}
                </button>
            </div>
        `}_renderPersonList(){const codes=this.filteredCodes;if(this.codes.length===0){return this._renderEmptyState()}if(codes.length===0){return b2`
                <div class="empty-state">
                    <h2>${this.t("no_results.title")}</h2>
                    <p>${this.t("no_results.description")}</p>
                </div>
            `}return b2`
            ${["pin","tag","fingerprint"].map(method=>{const methodCodes=codes.filter(code=>(code.method||"pin")===method);return b2`
                    <section class="credential-section">
                        <h2>${this.t(`type.${method}`)}</h2>
                        ${methodCodes.length?b2`<div class="person-list">
                                  ${methodCodes.map(code=>this._renderPersonCard(code))}
                              </div>`:b2`<p class="credential-empty">${this.t("section_empty")}</p>`}
                    </section>
                `})}
        `}_renderPersonCard(code){return b2`
            <div class="person-card">
                <div class="person-avatar ${this.getAvatarClass(code)}">
                    ${this.getInitials(this.displayName(code))}
                </div>
                <div class="person-info">
                    <h3 class="person-name">${this.displayName(code)}</h3>
                    <div class="person-details">
                        <span class="person-detail">
                            <svg viewBox="0 0 24 24" fill="currentColor">
                                <path d="M12,1L3,5V11C3,16.55 6.84,21.74 12,23C17.16,21.74 21,16.55 21,11V5L12,1M12,5A3,3 0 0,1 15,8A3,3 0 0,1 12,11A3,3 0 0,1 9,8A3,3 0 0,1 12,5M17.13,17C15.92,18.85 14.11,20.24 12,20.92C9.89,20.24 8.08,18.85 6.87,17C6.53,16.5 6.24,16 6,15.47C6,13.82 8.71,12.47 12,12.47C15.29,12.47 18,13.79 18,15.47C17.76,16 17.47,16.5 17.13,17Z"/>
                            </svg>
                            ${this.t("slot_label")} ${code.slot}
                        </span>
                        ${code.expiry?b2`
                                  <span class="person-detail">
                                      <svg viewBox="0 0 24 24" fill="currentColor">
                                          <path d="M12,20A8,8 0 0,0 20,12A8,8 0 0,0 12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20M12,2A10,10 0 0,1 22,12A10,10 0 0,1 12,22C6.47,22 2,17.5 2,12A10,10 0 0,1 12,2M12.5,7V12.25L17,14.92L16.25,16.15L11,13V7H12.5Z"/>
                                      </svg>
                                      ${this.isExpired(code)?this.t("expired_on"):this.t("expires")} ${this.formatDate(code.expiry)}
                                  </span>
                              `:""}
                    </div>
                </div>
                <span class="badge ${this.getBadgeClass(code)}">${this.getBadgeText(code)}</span>
                <div class="person-actions">
                    <button
                        class="btn btn-icon btn-secondary"
                        @click=${()=>{this.editingCode=code;this.showEditDialog=true}}
                        title="${this.t("dialog.edit_title")}"
                    >
                        <svg viewBox="0 0 24 24" fill="currentColor">
                            <path d="M20.71,7.04C21.1,6.65 21.1,6 20.71,5.63L18.37,3.29C18,2.9 17.35,2.9 16.96,3.29L15.12,5.12L18.87,8.87M3,17.25V21H6.75L17.81,9.93L14.06,6.18L3,17.25Z"/>
                        </svg>
                    </button>
                    <button
                        class="btn btn-icon btn-secondary"
                        ?disabled=${this.isPinReserved(code)}
                        @click=${()=>{this.removingCode=code;this.showRemoveDialog=true}}
                        title="${this.isPinReserved(code)?this.t("dialog.reserved_pin"):this.t("dialog.remove")}"
                    >
                        <svg viewBox="0 0 24 24" fill="currentColor">
                            <path d="M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z"/>
                        </svg>
                    </button>
                </div>
            </div>
        `}_renderEmptyState(){return b2`
            <div class="empty-state">
                <div class="empty-icon">
                    <svg viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12,4A4,4 0 0,1 16,8A4,4 0 0,1 12,12A4,4 0 0,1 8,8A4,4 0 0,1 12,4M12,14C16.42,14 20,15.79 20,18V20H4V18C4,15.79 7.58,14 12,14Z"/>
                    </svg>
                </div>
                <h2>${this.t("empty.title")}</h2>
                <p>${this.t("empty.description")}</p>
                <button class="btn btn-primary" @click=${()=>this._openAddDialog()}>
                    <svg viewBox="0 0 24 24" fill="currentColor">
                        <path d="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z"/>
                    </svg>
                    ${this.t("empty.add_first")}
                </button>
            </div>
        `}_renderLoading(){return b2`
            <div class="loading-container">
                <div class="spinner"></div>
                <p>${this.t("loading")}</p>
            </div>
        `}_renderError(){return b2`
            <div class="error-banner">
                <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M13,13H11V7H13M13,17H11V15H13M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2Z"/>
                </svg>
                <span>${this.error}</span>
                <button class="btn btn-text" @click=${()=>this.loadCodes()}>${this.t("retry")}</button>
            </div>
        `}_renderAddDialog(){return b2`
            <div class="dialog-overlay" @click=${this._closeAddDialog}>
                <div class="dialog" @click=${e4=>e4.stopPropagation()}>
                    <div class="dialog-header">
                        <h2>${this.t("dialog.add_title")}</h2>
                        <button class="btn btn-icon btn-text" @click=${this._closeAddDialog}>
                            <svg viewBox="0 0 24 24" fill="currentColor">
                                <path d="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"/>
                            </svg>
                        </button>
                    </div>
                    <div class="dialog-content" @click=${e4=>e4.stopPropagation()}>
                        <div class="form-group">
                            <label for="add-name">${this.t("dialog.name")} *</label>
                            <input type="text" id="add-name" placeholder="${this.t("dialog.name_placeholder")}" required />
                        </div>
                        <div class="form-group">
                            <label for="add-pin">${this.t("dialog.pin_code")} *</label>
                            <input type="password" id="add-pin" placeholder="${this.t("dialog.pin_placeholder")}" pattern="[0-9]{6}" maxlength="6" required />
                            <small>${this.t("dialog.pin_hint")}</small>
                        </div>
                        <div class="form-row">
                            <div class="form-group">
                                <label for="add-type">${this.t("dialog.type")} *</label>
                                <select id="add-type" @change=${this._onTypeChange} @click=${e4=>e4.stopPropagation()}>
                                    <option value="permanent">${this.t("type.permanent")}</option>
                                    <option value="guest">${this.t("type.guest")}</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="add-slot">${this.t("dialog.slot")}</label>
                                <input type="number" id="add-slot" min="0" max="99" .value=${this.suggestedSlot!==null?String(this.suggestedSlot):""} />
                                <small>${this.t("dialog.next_available")}: ${this.suggestedSlot!==null?this.suggestedSlot:"..."}</small>
                            </div>
                        </div>
                        <div class="form-group" id="expiry-group" style="display: none;">
                            <label for="add-expiry">${this.t("dialog.expiry")}</label>
                            <input type="date" id="add-expiry" />
                        </div>
                    </div>
                    <div class="dialog-actions">
                        <button class="btn btn-secondary" @click=${this._closeAddDialog}>${this.t("dialog.cancel")}</button>
                        <button class="btn btn-primary" @click=${this._handleAddSubmit}>${this.t("dialog.add")}</button>
                    </div>
                </div>
            </div>
        `}_renderEditDialog(){if(!this.editingCode)return"";const isPin=(this.editingCode.method||"pin")==="pin";const isGuest=this.editingCode.type==="guest";return b2`
            <div class="dialog-overlay" @click=${this._closeEditDialog}>
                <div class="dialog" @click=${e4=>e4.stopPropagation()}>
                    <div class="dialog-header">
                        <h2>${this.t("dialog.edit_title")}</h2>
                        <button class="btn btn-icon btn-text" @click=${this._closeEditDialog}>
                            <svg viewBox="0 0 24 24" fill="currentColor">
                                <path d="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"/>
                            </svg>
                        </button>
                    </div>
                    <div class="dialog-content">
                        <div class="form-group">
                            <label for="edit-name">${this.t("dialog.name")}</label>
                            <input type="text" id="edit-name" .value=${this.editingCode.name||""} placeholder="${this.t("dialog.name_placeholder")}" @input=${()=>this.editFormError=null} />
                            ${this.editFormError==="name_required"?b2`<small class="field-error">${this.t("errors.name_required")}</small>`:""}
                        </div>
                        
                        ${isPin&&isGuest?b2`
                            <div class="form-group">
                                <label for="edit-expiry">${this.t("dialog.expiry")}</label>
                                <input type="date" id="edit-expiry" .value=${this.editingCode.expiry||""} />
                                <small>${this.t("dialog.expiry_hint")}</small>
                            </div>
                        `:isPin?b2`
                            <p style="color: var(--text-secondary); margin-bottom: 16px;">${this.t("dialog.permanent_no_expiry")}</p>
                        `:""}
                        
                        ${isPin?b2`<div class="form-group" style="border-top: 1px solid var(--divider); padding-top: 16px; margin-top: 16px;">
                            <label for="edit-pin">${this.t("dialog.change_pin")}</label>
                            <input type="text" id="edit-pin" placeholder="${this.t("dialog.pin_placeholder")}" pattern="[0-9]{6}" maxlength="6" inputmode="numeric" @input=${()=>this.editFormError=null} />
                            <small style="color: var(--warning-color, #ff9800);">${this.t("dialog.pin_change_warning")}</small>
                            ${this.editFormError==="pin_invalid"?b2`<small class="field-error">${this.t("errors.pin_invalid")}</small>`:""}
                        </div>`:""}
                    </div>
                    <div class="dialog-actions">
                        <button class="btn btn-secondary" @click=${this._closeEditDialog}>${this.t("dialog.cancel")}</button>
                        <button class="btn btn-primary" @click=${this._handleEditSubmit}>${this.t("dialog.save")}</button>
                    </div>
                </div>
            </div>
        `}_renderPinConfirmDialog(){if(!this.showPinConfirmDialog||!this.pendingPinUpdate)return"";return b2`
            <div class="dialog-overlay" @click=${this._closePinConfirmDialog}>
                <div class="dialog" @click=${e4=>e4.stopPropagation()}>
                    <div class="dialog-header">
                        <h2>${this.t("dialog.confirm_pin_change")}</h2>
                        <button class="btn btn-icon btn-text" @click=${this._closePinConfirmDialog}>
                            <svg viewBox="0 0 24 24" fill="currentColor">
                                <path d="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"/>
                            </svg>
                        </button>
                    </div>
                    <div class="dialog-content">
                        <div style="background: var(--warning-color, #ff9800); color: white; padding: 16px; border-radius: 8px; margin-bottom: 16px;">
                            <strong>⚠️ ${this.t("dialog.pin_warning_title")}</strong>
                            <p style="margin: 8px 0 0 0;">${this.t("dialog.pin_warning_message")}</p>
                        </div>
                        <p>${this.t("dialog.pin_confirm_question",{name:this.pendingPinUpdate.name})}</p>
                    </div>
                    <div class="dialog-actions">
                        <button class="btn btn-secondary" @click=${this._closePinConfirmDialog}>${this.t("dialog.cancel")}</button>
                        <button class="btn btn-primary" style="background: var(--warning-color, #ff9800);" @click=${this._confirmPinUpdate}>${this.t("dialog.confirm_change")}</button>
                    </div>
                </div>
            </div>
        `}_renderRemoveDialog(){if(!this.removingCode)return"";return b2`
            <div class="dialog-overlay" @click=${this._closeRemoveDialog}>
                <div class="dialog" @click=${e4=>e4.stopPropagation()}>
                    <div class="dialog-header">
                        <h2>${this.t("dialog.remove_title")}</h2>
                        <button class="btn btn-icon btn-text" @click=${this._closeRemoveDialog}>
                            <svg viewBox="0 0 24 24" fill="currentColor">
                                <path d="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"/>
                            </svg>
                        </button>
                    </div>
                    <div class="dialog-content">
                        <p>${this.t("dialog.confirm_remove")} <strong>${this.displayName(this.removingCode)}</strong>?</p>
                        <p style="margin-top: 12px; color: var(--text-secondary); font-size: 14px;">
                            ${this.t((this.removingCode.method||"pin")==="tag"?"dialog.tag_remove_description":(this.removingCode.method||"pin")==="fingerprint"?"dialog.fingerprint_remove_description":"dialog.remove_description",{slot:this.removingCode.slot})}
                        </p>
                    </div>
                    <div class="dialog-actions">
                        <button class="btn btn-secondary" @click=${this._closeRemoveDialog}>${this.t("dialog.cancel")}</button>
                        <button class="btn btn-danger" @click=${this._handleRemove}>
                            ${(this.removingCode.method||"pin")==="pin"?this.t("dialog.remove"):this.t("dialog.remove_local")}
                        </button>
                    </div>
                </div>
            </div>
        `}_onTypeChange(e4){const expiryGroup=this.shadowRoot.getElementById("expiry-group");if(expiryGroup){expiryGroup.style.display=e4.target.value==="guest"?"block":"none"}}async _openAddDialog(){try{const result=await this.hass.callWS({type:"nimlykoder/suggest_slots",count:1});this.suggestedSlot=result.slots&&result.slots.length>0?result.slots[0]:null}catch(err){console.error("Failed to fetch suggested slot:",err);this.suggestedSlot=null}this.showAddDialog=true}_closeAddDialog(){this.showAddDialog=false;this.suggestedSlot=null}_closeEditDialog(){this.showEditDialog=false;this.editingCode=null;this.editFormError=null}_closeRemoveDialog(){this.showRemoveDialog=false;this.removingCode=null}async _handleAddSubmit(){const name=this.shadowRoot.getElementById("add-name").value;const pinCode=this.shadowRoot.getElementById("add-pin").value;const codeType=this.shadowRoot.getElementById("add-type").value;const expiry=this.shadowRoot.getElementById("add-expiry").value;const slot=this.shadowRoot.getElementById("add-slot").value;if(!name||!pinCode){this.error="Please fill in all required fields";return}const data={name,pin_code:pinCode,code_type:codeType};if(expiry){data.expiry=expiry}if(slot){data.slot=parseInt(slot)}try{await this.hass.callWS({type:"nimlykoder/add",...data});this.showAddDialog=false;await this.loadCodes()}catch(err){this.error=err.message}}async _handleEditSubmit(){const name=this.shadowRoot.getElementById("edit-name").value;const isPin=(this.editingCode.method||"pin")==="pin";const expiryEl=this.shadowRoot.getElementById("edit-expiry");const expiry=expiryEl?expiryEl.value:null;const pinEl=this.shadowRoot.getElementById("edit-pin");const newPin=pinEl?pinEl.value.trim():"";if(!name||!name.trim()){this.editFormError="name_required";return}if(newPin&&!/^[0-9]{6}$/.test(newPin)){this.editFormError="pin_invalid";return}try{if(name!==this.editingCode.name){await this.hass.callWS({type:"nimlykoder/update_name",slot:this.editingCode.slot,method:this.editingCode.method||"pin",name:name.trim()})}if(isPin&&this.editingCode.type==="guest"){const currentExpiry=this.editingCode.expiry||"";if(expiry!==currentExpiry){await this.hass.callWS({type:"nimlykoder/update_expiry",slot:this.editingCode.slot,method:"pin",expiry:expiry||null})}}if(newPin){this.pendingPinUpdate={slot:this.editingCode.slot,name:name.trim(),pin_code:newPin};this.showEditDialog=false;this.showPinConfirmDialog=true;return}this.showEditDialog=false;this.editingCode=null;await this.loadCodes()}catch(err){this.error=err.message}}_closePinConfirmDialog(){this.showPinConfirmDialog=false;this.pendingPinUpdate=null}async _confirmPinUpdate(){if(!this.pendingPinUpdate)return;try{await this.hass.callWS({type:"nimlykoder/update_pin",slot:this.pendingPinUpdate.slot,pin_code:this.pendingPinUpdate.pin_code});this.showPinConfirmDialog=false;this.pendingPinUpdate=null;this.editingCode=null;await this.loadCodes()}catch(err){this.error=err.message}}async _handleRemove(){try{await this.hass.callWS({type:"nimlykoder/remove",slot:this.removingCode.slot,method:this.removingCode.method||"pin"});this.showRemoveDialog=false;this.removingCode=null;await this.loadCodes()}catch(err){this.error=err.message}}};customElements.define("nimlykoder-panel",NimlykoderPanel);
/*! Bundled license information:

@lit/reactive-element/css-tag.js:
  (**
   * @license
   * Copyright 2019 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/reactive-element.js:
lit-html/lit-html.js:
lit-element/lit-element.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

lit-html/is-server.js:
  (**
   * @license
   * Copyright 2022 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)
*/
