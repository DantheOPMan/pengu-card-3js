/**
 * The spectrum and grating equations are adapted from Vercel Labs' MIT-licensed
 * vgpu holographic-card example (reference/vgpu-source.md). Composition, masks,
 * snowflake engraving, image relief and finish palettes are authored here.
 */
export const surfaceVertex = /* glsl */ `
varying vec2 vUv;
varying vec3 vWorld;
varying vec3 vNormal;
varying vec3 vRight;
varying vec3 vUp;
void main() {
  vUv = uv;
  vec4 world = modelMatrix * vec4(position, 1.0);
  vWorld = world.xyz;
  vNormal = normalize(mat3(modelMatrix) * normal);
  vRight = normalize(mat3(modelMatrix) * vec3(1.,0.,0.));
  vUp = normalize(mat3(modelMatrix) * vec3(0.,1.,0.));
  gl_Position = projectionMatrix * viewMatrix * world;
}`;

const optics = /* glsl */ `
uniform vec2 uPointer;
uniform float uTime;
uniform float uFoil;
uniform float uFinish;
varying vec2 vUv;
varying vec3 vWorld;
varying vec3 vNormal;
varying vec3 vRight;
varying vec3 vUp;
float hash(vec2 p) { return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453); }
vec3 wavelength(float wave) {
  vec3 response = (vec3(wave)-vec3(.610,.545,.460))/vec3(.045,.038,.032);
  return exp(-.5*response*response)*smoothstep(.38,.41,wave)*(1.-smoothstep(.7,.78,wave));
}
vec3 diffraction(vec2 across, vec2 lightView, float spacing) {
  float pathDifference = spacing*abs(dot(lightView,across));
  float along = dot(lightView,vec2(-across.y,across.x));
  vec3 reflected = vec3(0.);
  for(int order=1;order<=3;order++) {
    float m=float(order);
    reflected += wavelength(pathDifference/m)/(m*m);
  }
  return reflected*exp(-along*along/.36);
}
vec3 pearl(float phase) {
  vec3 spectral = .56+.44*cos(6.2831853*(phase+vec3(.04,.36,.67)));
  if(uFinish>.5 && uFinish<1.5) return mix(vec3(.34,.72,.96),vec3(.83,.92,1.),spectral.g);
  if(uFinish>1.5) return mix(vec3(.44,.21,.06),vec3(1.,.82,.39),spectral.r);
  return spectral;
}
float roundBox(vec2 p,vec2 bounds,float radius) {
  vec2 q=abs(p)-bounds+radius;
  return length(max(q,0.))+min(max(q.x,q.y),0.)-radius;
}
float line(float d,float width) { return 1.-smoothstep(width,width+max(fwidth(d),.0004),abs(d)); }
`;

export const foilFragment = /* glsl */ `
${optics}
float iceNoise(vec2 p) {
  vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);
  return mix(mix(hash(i),hash(i+vec2(1.,0.)),f.x),mix(hash(i+vec2(0.,1.)),hash(i+1.),f.x),f.y);
}
float iceCrack(vec2 p) {
  vec2 id=floor(p),f=fract(p);float a=8.,b=8.;
  for(int y=-1;y<=1;y++) for(int x=-1;x<=1;x++) {
    vec2 n=vec2(float(x),float(y));
    vec2 offset=vec2(hash(id+n),hash(id+n+37.));float d=length(n+offset-f);
    if(d<a){b=a;a=d;}else{b=min(b,d);}
  }
  return 1.-smoothstep(.007,.025,b-a);
}
void main() {
  vec2 p=(vUv-.5)*vec2(2.60,2.86);
  if(roundBox(p,vec2(1.30,1.43),.12)>0.) discard;
  vec3 V=normalize(cameraPosition-vWorld);
  vec3 L=normalize(vec3(uPointer*vec2(3.8,4.8),5.)-vWorld);
  vec2 lightView=vec2(dot(L+V,vRight),dot(L+V,vUp));
  float cloud=iceNoise(p*7.)*.56+iceNoise(p*21.)*.29+iceNoise(p*65.)*.15;
  float frost=iceCrack(p*12.+iceNoise(p*4.)*.4);
  vec2 q=p-vec2(0.,.31);
  float halo=exp(-dot(q,q)*.75);
  vec3 color=mix(vec3(.058,.105,.15),vec3(.16,.26,.33),cloud*.65+halo*.35);
  color+=frost*vec3(.13,.20,.24)*(.13+smoothstep(.35,1.27,abs(p.x))*.4);
  float radius=length(q),angle=atan(q.y,q.x);
  float ring=line(radius-.92,.003)+line(radius-1.04,.002);
  float rays=line(sin(angle*30.),.035)*smoothstep(.89,.91,radius)*(1.-smoothstep(1.11,1.15,radius));
  color+=(ring+rays*.65)*vec3(.25,.33,.37);
  float band=(p.x-uPointer.x*1.7)*.7+(p.y-uPointer.y*2.2)*.53;
  float sweep=exp(-band*band/.16);
  vec3 spectral=pearl(dot(lightView,vec2(.48,-.34))+p.y*.18);
  color+=spectral*sweep*(frost*.045+ring*.04)*uFoil;
  if(uFinish>1.5) color*=vec3(1.14,1.02,.86);
  float grain=hash(floor(vUv*vec2(1300.,1450.)));
  color+=grain*.008;
  gl_FragColor=vec4(color,1.);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}`;

export const artworkVertex = /* glsl */ `
uniform sampler2D uArtwork;
uniform float uDepth;
varying vec2 vUv;
varying vec3 vWorld;
varying vec3 vNormal;
varying vec3 vRight;
varying vec3 vUp;
void main() {
  vUv=uv;
  vec2 beardPoint=(uv-vec2(.60,.29))/vec2(.29,.28);
  vec2 capPoint=(uv-vec2(.48,.67))/vec2(.39,.19);
  float beard=exp(-dot(beardPoint,beardPoint)*1.8);
  float cap=exp(-dot(capPoint,capPoint)*1.7);
  // Smooth, hand-authored depth fields avoid tearing the illustration's outlines.
  // They continue through discarded background texels to keep edge vertices stable.
  // Replace these two fields with a depth texture for differently composed artwork.
  float depth=(.045+beard*.16+cap*.09)*smoothstep(0.,.08,uv.y);
  vec3 displaced=position+vec3(0.,0.,depth*uDepth);
  vec4 world=modelMatrix*vec4(displaced,1.);
  vWorld=world.xyz;
  vNormal=normalize(mat3(modelMatrix)*normal);
  vRight=normalize(mat3(modelMatrix)*vec3(1.,0.,0.));
  vUp=normalize(mat3(modelMatrix)*vec3(0.,1.,0.));
  gl_Position=projectionMatrix*viewMatrix*world;
}`;

// Remove the yellow contribution from antialiased outline pixels as well as
// the solid background. Ratios distinguish yellow from the orange beak.
const artworkKey = /* glsl */ `
vec4 keyArtwork(vec4 art) {
  vec3 key=vec3(.955973,.799103,.070360);
  float yellow=smoothstep(.68,.78,art.g/max(art.r,.0001))
    *(1.-smoothstep(.28,.50,art.b/max(art.g,.0001)));
  float coverage=clamp(max((art.r-art.b)/(key.r-key.b),
    (art.g-art.b)/(key.g-key.b)),0.,1.);
  float solid=smoothstep(.62,.78,art.r)*smoothstep(.61,.77,art.g)
    *(1.-smoothstep(.38,.52,art.b));
  float background=max(solid,yellow*coverage);
  float alpha=1.-background;
  vec3 clean=clamp((art.rgb-key*background)/max(alpha,.001),0.,1.);
  return vec4(clean,art.a*alpha);
}
`;

export const artworkFragment = /* glsl */ `
${optics}
${artworkKey}
uniform sampler2D uArtwork;
void main() {
  if(roundBox((vUv-.5)*2.94,vec2(1.30,1.43),.12)>0.) discard;
  vec4 art=keyArtwork(texture2D(uArtwork,vUv));
  if(art.a<.03) discard;
  vec3 V=normalize(cameraPosition-vWorld);
  vec3 L=normalize(vec3(uPointer*vec2(3.8,4.8),5.)-vWorld);
  vec2 lightView=vec2(dot(L+V,vRight),dot(L+V,vUp));
  vec3 rainbow=pearl(dot(lightView,vec2(.5,-.4))+vUv.y*.5);
  float highlight=pow(max(dot(normalize(L+V),vNormal),0.),36.);
  float cap=step(art.g*1.65,art.r)*step(art.b*1.3,art.r);
  float brightness=dot(art.rgb,vec3(.299,.587,.114));
  float etched=line(sin(vUv.y*920.+sin(vUv.x*22.)*1.2),.02);
  vec3 color=art.rgb*(.89+max(dot(vNormal,L),0.)*.11);
  color += rainbow*(.025+highlight*.16)*uFoil*brightness;
  color += etched*rainbow*.03*uFoil;
  color += vec3(1.,.75,.66)*cap*highlight*.12;
  gl_FragColor=vec4(color,art.a);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}`;

/** Soft contact shadow keeps the illustrated relief visually above the ice recess. */
export const artworkShadowFragment = /* glsl */ `
${optics}
${artworkKey}
uniform sampler2D uArtwork;
float silhouette(vec2 uv) {
  if(any(lessThan(uv,vec2(0.))) || any(greaterThan(uv,vec2(1.)))) return 0.;
  return keyArtwork(texture2D(uArtwork,uv)).a;
}
void main() {
  if(roundBox((vUv-.5)*2.94,vec2(1.30,1.43),.12)>0.) discard;
  vec2 uv=vUv+vec2(.008,.012)+uPointer*.010;
  float shadow=silhouette(uv)*.4;
  shadow+=silhouette(uv+vec2(.006,0.))*.15;
  shadow+=silhouette(uv-vec2(.006,0.))*.15;
  shadow+=silhouette(uv+vec2(0.,.006))*.15;
  shadow+=silhouette(uv-vec2(0.,.006))*.15;
  gl_FragColor=vec4(.012,.024,.035,shadow*.56);
  #include <colorspace_fragment>
}`;
