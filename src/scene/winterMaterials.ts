import * as THREE from 'three';

type LightUniforms = { uPointer: { value: THREE.Vector2 }; uTime: { value: number }; uFoil: { value: number }; uFinish: { value: number } };

/** Procedural surface detail stays attached to the actual Blender geometry. */
export function finishWinterMaterial(material: THREE.MeshStandardMaterial, uniforms: LightUniforms) {
  if(material.userData.winterFinished) return;
  material.userData.winterFinished = true;
  const name = material.name;
  const bone = name.startsWith('Carved ivory');
  const crystal = name.startsWith('Rock crystal');
  const enamel = name.startsWith('Glacial enamel');
  const silver = name.startsWith('Winter silver');
  if(!(bone || crystal || enamel || silver)) return;
  material.onBeforeCompile = shader => {
    Object.assign(shader.uniforms,uniforms);
    shader.vertexShader = 'varying vec3 vCraftPosition;\n'+shader.vertexShader;
    shader.vertexShader = shader.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\nvCraftPosition = position;');
    shader.fragmentShader = /* glsl */ `
      varying vec3 vCraftPosition;
      uniform vec2 uPointer;
      uniform float uFoil;
      uniform float uFinish;
      float craftHash(vec2 p) {return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
      float craftNoise(vec2 p) {
        vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);
        return mix(mix(craftHash(i),craftHash(i+vec2(1.,0.)),f.x),mix(craftHash(i+vec2(0.,1.)),craftHash(i+1.),f.x),f.y);
      }
      float craftCrack(vec2 p) {
        vec2 id=floor(p),f=fract(p);float a=8.,b=8.;
        for(int y=-1;y<=1;y++) for(int x=-1;x<=1;x++) {
          vec2 n=vec2(float(x),float(y));
          vec2 offset=vec2(craftHash(id+n),craftHash(id+n+37.));
          float d=length(n+offset-f);
          if(d<a){b=a;a=d;}else{b=min(b,d);}
        }
        return 1.-smoothstep(.012,.034,b-a);
      }
    `+shader.fragmentShader;
    const color = bone ? /* glsl */ `
      float weather=craftNoise(craftP*11.)*.6+craftNoise(craftP*37.)*.4;
      float cracks=craftCrack(craftP*22.+craftNoise(craftP*9.)*.3);
      diffuseColor.rgb*=.73+weather*.32;
      diffuseColor.rgb=mix(diffuseColor.rgb,vec3(.13,.10,.068),cracks*.46);
      craftHeight=weather*.0013-cracks*.00055;
    ` : crystal ? /* glsl */ `
      float cracks=craftCrack(craftP*31.);
      float cloud=craftNoise(craftP*47.);
      diffuseColor.rgb=mix(diffuseColor.rgb,vec3(.80,.92,1.),cracks*.48);
      diffuseColor.rgb*=.82+cloud*.27;
      craftHeight=cloud*.0005;
    ` : enamel ? /* glsl */ `
      float cracks=craftCrack(craftP*25.);
      diffuseColor.rgb*=.80+craftNoise(craftP*21.)*.30;
      diffuseColor.rgb+=cracks*vec3(.10,.14,.17)*.3;
      craftHeight=craftNoise(craftP*75.)*.0007;
    ` : /* glsl */ `
      float pitting=craftNoise(craftP*82.);
      diffuseColor.rgb*=.56+pitting*.48;
      craftHeight=pitting*.0009;
    `;
    shader.fragmentShader=shader.fragmentShader.replace('#include <color_fragment>', /* glsl */ `
      #include <color_fragment>
      vec2 craftP=vCraftPosition.xy+vCraftPosition.z*vec2(.23,.41);
      float craftHeight=0.;
      ${color}
      if(uFinish>1.5) diffuseColor.rgb*=vec3(1.08,.96,.80);
      float shine=exp(-pow((craftP.x-uPointer.x*2.)*.7+(craftP.y-uPointer.y*2.)*.45,2.)/.15);
      vec3 spectral=.5+.5*cos((craftP.y*.15+uPointer.x*.18)*6.283+vec3(0.,2.1,4.2));
      vec3 reflectionTint=uFinish<.5 ? spectral : (uFinish>1.5 ? vec3(.85,.60,.27) : vec3(.32,.53,.72));
      diffuseColor.rgb+=reflectionTint*shine*.035*uFoil;
    `);
    shader.fragmentShader=shader.fragmentShader.replace('#include <normal_fragment_maps>', /* glsl */ `
      #include <normal_fragment_maps>
      vec3 craftDX=dFdx(-vViewPosition),craftDY=dFdy(-vViewPosition);
      vec3 craftRX=cross(craftDY,normal),craftRY=cross(normal,craftDX);
      float craftDet=dot(craftDX,craftRX);
      vec3 craftGradient=sign(craftDet)*(dFdx(craftHeight)*craftRX+dFdy(craftHeight)*craftRY);
      normal=normalize(abs(craftDet)*normal-craftGradient);
    `);
  };
  material.customProgramCacheKey=()=>`winter-crown-${name}`;
}
