import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { finishWinterMaterial } from './winterMaterials';
import { createIceEnvironment, CARD_GROUND_Y } from './iceEnvironment';
import { surfaceVertex, foilFragment, artworkVertex, artworkFragment, artworkShadowFragment } from './shaders';

export type Finish = 'prismatic' | 'glacier' | 'gold';
export interface CardSettings { finish: Finish; foil: number; flipped: boolean; autoRotate: boolean; light: number; depth: number }
export const defaultSettings: CardSettings = { finish: 'glacier', foil: .65, flipped: false, autoRotate: false, light: 0, depth: 1 };
export interface CardScene { ready: Promise<void>; update: (settings: CardSettings) => void; reset: () => void; dispose: () => void }

function disposeGraph(root: THREE.Object3D) {
  const geometries = new Set<THREE.BufferGeometry>();
  const materials = new Set<THREE.Material>();
  root.traverse(object => {
    if(object instanceof THREE.Mesh || object instanceof THREE.Points) {
      geometries.add(object.geometry);
      for(const material of Array.isArray(object.material) ? object.material : [object.material]) materials.add(material);
    }
  });
  geometries.forEach(geometry => geometry.dispose());
  materials.forEach(material => material.dispose());
}

/** Owns the renderer, input and every GPU resource for one mounted canvas. */
export function createCardScene(canvas: HTMLCanvasElement): CardScene {
  let settings = { ...defaultSettings };
  let disposed = false;
  let loaded = false;
  let frame = 0;
  let previousTime = 0;
  let elapsed = 0;
  let dragStart: { x: number; y: number; rotation: number } | null = null;
  let dragRotation = 0;
  let autoRotation = 0;
  const pointer = new THREE.Vector2(0, 0);
  const smoothPointer = new THREE.Vector2(.14, .1);
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0xc1d1da);
  scene.fog = new THREE.FogExp2(0xc1d1da,.018);
  const camera = new THREE.PerspectiveCamera(35, 1, .1, 100);
  camera.position.set(0, 1.8, 11.5);
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: 'high-performance' });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.75));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = .96;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFShadowMap;
  renderer.setClearColor(0xc1d1da, 1);

  const environmentScene = new RoomEnvironment();
  const pmrem = new THREE.PMREMGenerator(renderer);
  const environment = pmrem.fromScene(environmentScene, .04);
  scene.environment = environment.texture;
  scene.environmentIntensity = .7;
  environmentScene.dispose();
  pmrem.dispose();
  scene.add(new THREE.HemisphereLight(0xe0f1ff, 0x567c92, .9));
  const key = new THREE.DirectionalLight(0xe7f3ff, 2.05);
  key.position.set(-4, 7, 5); scene.add(key);
  key.castShadow = true;
  key.shadow.mapSize.set(1024,1024);
  key.shadow.radius=3;
  Object.assign(key.shadow.camera,{left:-5.2,right:5.2,top:5.5,bottom:-4.5,near:.1,far:24});
  key.shadow.bias = -.00025;
  key.shadow.normalBias = .012;
  const rim = new THREE.DirectionalLight(0x99c9df, 1.2);
  rim.position.set(4, -1, 3); scene.add(rim);
  const iceWorld = createIceEnvironment(scene);

  const card = new THREE.Group();
  card.rotation.set(.04, -.15, -.055);
  scene.add(card);
  const textures: THREE.Texture[] = [];
  const bottomCorner = new THREE.Vector3();
  const commonUniforms = {
    uPointer: { value: new THREE.Vector2() }, uTime: { value: 0 },
    uFoil: { value: settings.foil }, uFinish: { value: 0 },
  };
  const artUniforms = { ...commonUniforms, uArtwork: { value: null as THREE.Texture | null }, uDepth: { value: 1 } };
  const front = new THREE.Mesh(new THREE.PlaneGeometry(2.60,2.86),new THREE.ShaderMaterial({
    vertexShader: surfaceVertex, fragmentShader: foilFragment,
    uniforms: { ...commonUniforms, uBack: { value: 0 } },
  }));
  front.position.set(0,.10,.148);
  card.add(front);
  function resize() {
    if(disposed) return;
    const width = Math.max(1,canvas.clientWidth);
    const height = Math.max(1,canvas.clientHeight);
    renderer.setSize(width,height,false);
    camera.aspect = width/height;
    // Fit the card in both axes. World space stays stable across breakpoints.
    camera.position.z = Math.max(11.5, 7.1 / (2*Math.tan(THREE.MathUtils.degToRad(17.5))), 4.15/(2*Math.tan(THREE.MathUtils.degToRad(17.5))*camera.aspect));
    camera.lookAt(0,-.10,0);
    camera.updateProjectionMatrix();
  }
  const resizeObserver = new ResizeObserver(resize);
  resizeObserver.observe(canvas);
  resize();

  const ready = (async () => {
    // Each asynchronous asset registers with this instance before it can be retired.
    const artPromise = new THREE.TextureLoader().loadAsync('/assets/penguin-original.png').then(texture => {
      if(disposed) { texture.dispose(); return null; }
      texture.colorSpace = THREE.SRGBColorSpace;
      texture.anisotropy = Math.min(8,renderer.capabilities.getMaxAnisotropy());
      textures.push(texture);
      return texture;
    });
    const modelPromise = new GLTFLoader().loadAsync('/assets/winter-crown.glb?v=clean-title-1').then(gltf => {
      if(disposed) { disposeGraph(gltf.scene); return null; }
      card.add(gltf.scene);
      const detached: THREE.Object3D[] = [];
      gltf.scene.traverse(object => {
        if(object.name.startsWith('Crystal_')) detached.push(object);
        if(object instanceof THREE.Mesh) {
          object.castShadow = true; object.receiveShadow = true;
          const materials = Array.isArray(object.material) ? object.material : [object.material];
          for(const material of materials) {
            if(material instanceof THREE.MeshStandardMaterial) finishWinterMaterial(material,commonUniforms);
          }
        }
      });
      detached.forEach(object => {
        object.removeFromParent();
        disposeGraph(object);
      });
      return gltf;
    });
    const [art] = await Promise.all([artPromise,modelPromise,iceWorld.ready]);
    if(disposed || !art) return;
    artUniforms.uArtwork.value = art;
    const reliefShadow = new THREE.Mesh(new THREE.PlaneGeometry(2.94,2.94),new THREE.ShaderMaterial({
      vertexShader:surfaceVertex,fragmentShader:artworkShadowFragment,uniforms:artUniforms,
      transparent:true,depthWrite:false,toneMapped:false,
    }));
    reliefShadow.name = 'Penguin contact shadow';
    reliefShadow.position.set(.01,.085,.160);
    card.add(reliefShadow);
    // Extend the image beneath the bezel instead of exposing its square bottom.
    const artwork = new THREE.Mesh(new THREE.PlaneGeometry(2.94,2.94,150,150),new THREE.ShaderMaterial({
      vertexShader:artworkVertex,fragmentShader:artworkFragment,uniforms:artUniforms,
      transparent:true,depthWrite:true,toneMapped:false,
    }));
    artwork.name = 'Original penguin relief';
    artwork.position.set(0,.10,.183);
    card.add(artwork);
    loaded = true;
    canvas.dataset.ready = 'true';
  })();

  function onPointerMove(event: PointerEvent) {
    const rect = canvas.getBoundingClientRect();
    pointer.set(THREE.MathUtils.clamp(((event.clientX-rect.left)/rect.width-.5)*2,-1,1),THREE.MathUtils.clamp(-((event.clientY-rect.top)/rect.height-.5)*2,-1,1));
    if(dragStart) dragRotation = dragStart.rotation+(event.clientX-dragStart.x)*.008;
  }
  function onPointerDown(event: PointerEvent) {
    if(event.button !== 0) return;
    dragStart = { x:event.clientX,y:event.clientY,rotation:dragRotation };
    canvas.setPointerCapture(event.pointerId);
    canvas.style.cursor='grabbing';
    onPointerMove(event);
  }
  function onPointerUp(event: PointerEvent) {
    dragStart=null;
    if(canvas.hasPointerCapture(event.pointerId)) canvas.releasePointerCapture(event.pointerId);
    canvas.style.cursor='grab';
  }
  function onPointerLeave() { if(!dragStart) pointer.set(0,0); }
  function onKeyDown(event: KeyboardEvent) {
    if(event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
      event.preventDefault(); dragRotation += event.key === 'ArrowLeft' ? -.18 : .18;
    }
    if(event.key === 'Home') { event.preventDefault(); dragRotation=0;autoRotation=0;pointer.set(0,0); }
  }
  function contextLost(event: Event) { event.preventDefault(); canvas.dataset.ready='false'; canvas.dispatchEvent(new CustomEvent('carderror',{detail:'The graphics context was interrupted. Reload to restore the card.'})); }
  canvas.addEventListener('pointermove',onPointerMove);
  canvas.addEventListener('pointerdown',onPointerDown);
  canvas.addEventListener('pointerup',onPointerUp);
  canvas.addEventListener('pointercancel',onPointerUp);
  canvas.addEventListener('pointerleave',onPointerLeave);
  canvas.addEventListener('keydown',onKeyDown);
  canvas.addEventListener('webglcontextlost',contextLost);

  function animate(time: number) {
    if(disposed) return;
    frame=requestAnimationFrame(animate);
    const delta=Math.min((time-previousTime)/1000,.05);
    previousTime=time;
    if(document.hidden) return;
    elapsed+=delta;
    const damping=motion.matches ? 1 : 1-Math.exp(-8*delta);
    smoothPointer.lerp(pointer,damping);
    commonUniforms.uPointer.value.set(smoothPointer.x+Math.sin(settings.light)*.75,smoothPointer.y+Math.cos(settings.light)*.2);
    commonUniforms.uTime.value=elapsed;
    commonUniforms.uFoil.value=settings.foil;
    commonUniforms.uFinish.value={prismatic:0,glacier:1,gold:2}[settings.finish];
    artUniforms.uDepth.value=settings.depth;
    if(settings.autoRotate && !motion.matches) autoRotation+=delta*.30;
    const idle=motion.matches ? 0 : Math.sin(elapsed*.65)*.025;
    const targetX=motion.matches ? 0 : -smoothPointer.y*.19+.045;
    const targetY=(settings.flipped ? Math.PI : 0)+dragRotation+autoRotation+(motion.matches ? 0 : smoothPointer.x*.26-.13+idle);
    card.rotation.x=THREE.MathUtils.lerp(card.rotation.x,targetX,damping);
    card.rotation.y=THREE.MathUtils.lerp(card.rotation.y,targetY,damping);
    card.rotation.z=THREE.MathUtils.lerp(card.rotation.z,motion.matches ? 0 : -.035-smoothPointer.x*.025,damping);
    // Keep the lowest corner on the original ice floor while the card turns.
    let lowest=Infinity;
    for(const x of [-1.62,1.62]) for(const z of [-.34,.34]) {
      bottomCorner.set(x,-2.355,z).applyEuler(card.rotation);
      lowest=Math.min(lowest,bottomCorner.y);
    }
    card.position.y=CARD_GROUND_Y-lowest+.025;
    if(loaded) renderer.render(scene,camera);
  }
  frame=requestAnimationFrame(animate);

  return {
    ready,
    update(next) { settings={...next}; },
    reset() { dragRotation=0;autoRotation=0;pointer.set(0,0); },
    dispose() {
      if(disposed) return;
      disposed=true;
      cancelAnimationFrame(frame);
      resizeObserver.disconnect();
      canvas.removeEventListener('pointermove',onPointerMove);
      canvas.removeEventListener('pointerdown',onPointerDown);
      canvas.removeEventListener('pointerup',onPointerUp);
      canvas.removeEventListener('pointercancel',onPointerUp);
      canvas.removeEventListener('pointerleave',onPointerLeave);
      canvas.removeEventListener('keydown',onKeyDown);
      canvas.removeEventListener('webglcontextlost',contextLost);
      iceWorld.dispose();
      disposeGraph(scene);
      textures.forEach(texture => texture.dispose());
      key.shadow.dispose();
      environment.dispose();
      renderer.dispose();
    },
  };
}
