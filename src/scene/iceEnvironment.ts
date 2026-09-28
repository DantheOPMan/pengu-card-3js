import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { Reflector } from 'three/addons/objects/Reflector.js';

export const ICE_FLOOR_Y = -2.60;
export const CARD_GROUND_Y = ICE_FLOOR_Y;

const iceNoise = /* glsl */ `
float iceHash(vec2 p) { return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453); }
float iceGrain(vec2 p) {
  vec2 i=floor(p),f=fract(p); f=f*f*(3.-2.*f);
  return mix(mix(iceHash(i),iceHash(i+vec2(1.,0.)),f.x),mix(iceHash(i+vec2(0.,1.)),iceHash(i+1.),f.x),f.y);
}
float iceSeam(vec2 p) {
  vec2 cell=floor(p),f=fract(p);float a=10.,b=10.;
  for(int y=-1;y<=1;y++) for(int x=-1;x<=1;x++) {
    vec2 n=vec2(float(x),float(y));
    float d=length(n+vec2(iceHash(cell+n),iceHash(cell+n+31.))-f);
    if(d<a){b=a;a=d;}else{b=min(b,d);}
  }
  return 1.-smoothstep(.002,.018,b-a);
}
`;

function frostSurface(material: THREE.MeshStandardMaterial) {
  const weathered=material.name.startsWith('Weathered ice wall');
  material.onBeforeCompile = shader => {
    shader.vertexShader = shader.vertexShader.replace('#include <common>', '#include <common>\nvarying vec3 vIcePosition;')
      .replace('#include <worldpos_vertex>', '#include <worldpos_vertex>\nvIcePosition=(modelMatrix*vec4(transformed,1.)).xyz;');
    shader.fragmentShader = shader.fragmentShader.replace('#include <common>', `#include <common>\nvarying vec3 vIcePosition;\n${iceNoise}`)
      .replace('#include <color_fragment>', weathered ? `#include <color_fragment>
        vec2 iceP=vec2(vIcePosition.x+vIcePosition.z*.3,vIcePosition.y);
        float cloud=iceGrain(iceP*.9)*.55+iceGrain(iceP*3.4)*.30+iceGrain(iceP*12.)*.15;
        float veins=iceSeam(iceP*vec2(1.9,.8)+iceGrain(iceP*2.)*.38);
        float layer=pow(.5+.5*sin(vIcePosition.y*14.+iceGrain(vIcePosition.xz*.8)*5.),9.);
        diffuseColor.rgb*=.87+cloud*.17;
        diffuseColor.rgb=mix(diffuseColor.rgb,vec3(.09,.25,.34),veins*.07+layer*.045);
        diffuseColor.rgb=mix(diffuseColor.rgb,vec3(.65,.77,.80),smoothstep(.54,.77,cloud)*.19);
      ` : `#include <color_fragment>
        vec2 iceP=vIcePosition.xy+vIcePosition.z*.19;
        float grain=iceGrain(iceP*19.)*.6+iceGrain(iceP*65.)*.4;
        float veins=iceSeam(iceP*1.4+iceGrain(iceP*3.)*.18);
        diffuseColor.rgb*=.82+grain*.24;
        diffuseColor.rgb=mix(diffuseColor.rgb,vec3(.08,.23,.32),veins*.30);
      `)
      .replace('#include <normal_fragment_begin>', weathered ? `#include <normal_fragment_begin>
        vec2 bumpP=vIcePosition.xy+vIcePosition.z*.30;
        float iceBump=iceGrain(bumpP*11.)*.55+iceGrain(bumpP*47.)*.3+iceGrain(bumpP*103.)*.15;
        normal=normalize(normal+vec3(dFdx(iceBump),dFdy(iceBump),0.)*.075);
      ` : `#include <normal_fragment_begin>
        float iceBump=iceGrain((vIcePosition.xy+vIcePosition.z*.17)*38.);
        normal=normalize(normal+vec3(dFdx(iceBump),dFdy(iceBump),0.)*.23);
      `);
    if(weathered) shader.fragmentShader=shader.fragmentShader.replace('#include <roughnessmap_fragment>', `#include <roughnessmap_fragment>
      roughnessFactor*=.82+iceGrain((vIcePosition.xy+vIcePosition.z*.3)*5.)*.72;
    `);
  };
  material.customProgramCacheKey = () => `original-ice-refined-v1-${weathered}`;
}

/** Owns the Blender set, a live rough floor reflection and its shadow receiver. */
export function createIceEnvironment(scene: THREE.Scene) {
  let disposed = false;
  const root = new THREE.Group(); root.name = 'Original Blender ice studio'; scene.add(root);
  const floor = new Reflector(new THREE.PlaneGeometry(36, 36), {
    color: 0x536f83,
    textureWidth: 768, textureHeight: 768, multisample: 0, clipBias: .0001,
    shader: {
      name: 'Frosted planar ice reflection',
      uniforms: { tDiffuse: { value: null }, textureMatrix: { value: new THREE.Matrix4() }, color: { value: new THREE.Color(0x536f83) } },
      vertexShader: /* glsl */ `
        uniform mat4 textureMatrix;
        varying vec4 vUv;
        varying vec3 vFloor;
        void main() {
          vUv=textureMatrix*vec4(position,1.);
          vFloor=(modelMatrix*vec4(position,1.)).xyz;
          gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);
        }`,
      fragmentShader: /* glsl */ `
        uniform sampler2D tDiffuse;
        uniform vec3 color;
        varying vec4 vUv;
        varying vec3 vFloor;
        ${iceNoise}
        void main() {
          vec2 uv=vUv.xy/vUv.w;
          vec2 bend=vec2(iceGrain(vFloor.xz*3.),iceGrain(vFloor.zx*3.))-.5;
          uv+=bend*.0008;
          vec3 reflection=texture2D(tDiffuse,uv).rgb*.40;
          reflection+=(texture2D(tDiffuse,uv+vec2(.0018,0.)).rgb+texture2D(tDiffuse,uv-vec2(.0018,0.)).rgb)*.15;
          reflection+=(texture2D(tDiffuse,uv+vec2(0.,.0018)).rgb+texture2D(tDiffuse,uv-vec2(0.,.0018)).rgb)*.15;
          float frost=iceGrain(vFloor.xz*5.)*.5+iceGrain(vFloor.xz*31.)*.5;
          vec3 base=color*(.94+frost*.12);
          float sheen=.48*exp(-length(vFloor.xz)*.055);
          // Deeper blue ice separates the horizontal plane from the pale wall.
          vec3 result=mix(base,reflection*vec3(.68,.79,.88),sheen);
          result+=iceSeam(vFloor.xz*1.5+iceGrain(vFloor.xz*3.)*.2)*vec3(.10,.13,.14)*.12;
          gl_FragColor=vec4(result,1.);
          #include <tonemapping_fragment>
          #include <colorspace_fragment>
        }`,
    },
  });
  floor.name = 'Live ice floor reflection';
  floor.rotation.x = -Math.PI / 2; floor.position.y = ICE_FLOOR_Y + .003;
  root.add(floor);
  const shadow = new THREE.Mesh(new THREE.PlaneGeometry(36,36), new THREE.ShadowMaterial({ color: 0x334955, opacity: .28, depthWrite: false }));
  shadow.name = 'Card shadow on ice';
  shadow.rotation.x = -Math.PI / 2; shadow.position.y = ICE_FLOOR_Y + .006;
  shadow.receiveShadow = true; root.add(shadow);

  function release(object: THREE.Object3D) {
    const materials = new Set<THREE.Material>();
    object.traverse(child => {
      if (child instanceof THREE.Mesh) {
        child.geometry.dispose();
        for (const m of Array.isArray(child.material) ? child.material : [child.material]) materials.add(m);
      }
    });
    materials.forEach(material => material.dispose());
  }

  const ready = new GLTFLoader().loadAsync('/assets/ice-environment.glb?v=empty-studio-1').then(gltf => {
    if (disposed) { release(gltf.scene); return; }
    gltf.scene.traverse(object => {
      if (!(object instanceof THREE.Mesh)) return;
      object.receiveShadow = true;
      for (const material of Array.isArray(object.material) ? object.material : [object.material]) {
        if (material instanceof THREE.MeshStandardMaterial) {
          // Blender exports two-sided materials by default. The mirror camera
          // below the ice must not see the underside of the slab's top face.
          if (material.name.startsWith('Ice floor substrate')) {
            material.side=THREE.FrontSide;
            material.color.setRGB(.14,.24,.32);
          }
          if (object.name.startsWith('Sculpted glacier backdrop')) material.color.multiplyScalar(1.08);
          if(material.name.startsWith('Weathered ice wall')) material.envMapIntensity=.5;
          frostSurface(material);
        }
      }
    });
    root.add(gltf.scene);
  });

  return { ready, dispose() {
    if (disposed) return;
    disposed = true; scene.remove(root); floor.dispose(); release(root);
  } };
}
