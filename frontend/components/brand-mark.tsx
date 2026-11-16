/** CERA's aperture: a C with an independent measurement crossing its open side. */
export function BrandMark({size=36,light=false}:{size?:number;light?:boolean}){
 return <svg width={size} height={size} viewBox="0 0 80 80" fill="none" aria-hidden="true" focusable="false">
  <path d="M62 17H32C20 17 15 24 15 35V45C15 56 20 63 32 63H62" stroke={light?'#F2F3EE':'#182722'} strokeWidth="10" strokeLinejoin="miter"/>
  <path d="M60 40H43" stroke="#E9875C" strokeWidth="8"/>
 </svg>;
}
