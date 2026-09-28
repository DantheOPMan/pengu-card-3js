import { CanvasTexture, SRGBColorSpace } from 'three';

/** Printed ink sits in the metal recess, below the sculpted penguin surface. */
export function createCardLettering(back = false): CanvasTexture {
  const canvas = document.createElement('canvas');
  canvas.width = 1220;
  canvas.height = 1780;
  const ctx = canvas.getContext('2d')!;
  const text = (label: string, y: number, size: number, color = '#d9c7a3', title = false, italic = false) => {
    ctx.font = `${italic ? 'italic ' : ''}400 ${size}px ${title ? 'Cinzel' : '"IM Fell English"'}, Georgia, serif`;
    ctx.fillStyle = color;
    ctx.textAlign = 'center';
    ctx.shadowColor = '#000'; ctx.shadowBlur = 3; ctx.shadowOffsetY = 2;
    ctx.fillText(label, 610, y);
    ctx.shadowBlur = 0; ctx.shadowOffsetY = 0;
  };
  const ornament = (y: number, halfWidth = 280) => {
    ctx.strokeStyle = '#a17b4766'; ctx.lineWidth = 1.8;
    for(const side of [-1,1]) {
      ctx.beginPath(); ctx.moveTo(610+side*28,y);
      ctx.bezierCurveTo(610+side*110,y-7,610+side*180,y+7,610+side*halfWidth,y);
      ctx.stroke();
    }
    ctx.fillStyle='#b9965c'; ctx.beginPath();
    ctx.moveTo(610,y-7);ctx.lineTo(616,y);ctx.lineTo(610,y+7);ctx.lineTo(604,y);ctx.closePath();ctx.fill();
  };
  if(back) {
    text('THE NORTHERN REALMS',159,35,'#b59c73',true);
    ornament(203,380);
    text('An oath in ice.',385,57,'#ddd0b3',false,true);
    text('A heart that will not yield.',447,33,'#a8a89c',false,true);
    // The raised heraldic snowflake occupies the center of the card.
    text('The Frost King',1400,56,'#e1cfab',true);
    text('Guardian of the long winter',1460,32,'#b4b3a6',false,true);
    ornament(1501);
    text('Where the last ember fades,',1562,32,'#b8ae98');
    text('his watch begins.',1608,32,'#b8ae98');
    text('First of his name · I / C',1677,26,'#9b825d');
  } else {
    text('The Frost King',158,77,'#e4d4af',true);
    text('Lord of the long winter',215,30,'#b8ad93',false,true);
    // Portrait placement and displacement are deliberately unchanged.
    text('Even winter bends the knee.',1533,44,'#dbc6a0',false,true);
    ornament(1574,330);
    text('Frostborn  ·  Unbroken  ·  Eternal',1636,28,'#b9b4a0');
    text('Legendary',1706,36,'#c6a66d',true);
  }
  const texture = new CanvasTexture(canvas);
  texture.colorSpace = SRGBColorSpace;
  texture.anisotropy = 8;
  return texture;
}
