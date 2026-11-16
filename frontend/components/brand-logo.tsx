/** Hand-drawn, resolution-independent CERA wordmark and monogram. */
export function BrandLogo({light=false,wordmark=true}:{light?:boolean;wordmark?:boolean}){
 const color=light?'#F2F3EE':'#182722';
 return <svg width={wordmark?178:38} height={wordmark?42:38} viewBox={wordmark?'0 0 390 80':'0 0 80 80'} fill="none" role="img" aria-label="CERA">
  <path d="M67 17H36C24 17 19 24 19 35V45C19 56 24 63 36 63H67" stroke={color} strokeWidth="9" strokeLinejoin="miter"/>
  <path d="M65 40H48" stroke="#E9875C" strokeWidth="7.5"/>
  {wordmark&&<g transform="translate(97 3) scale(1.18)" stroke={color} strokeWidth="4.5" strokeLinecap="square" strokeLinejoin="miter">
   <path d="M44 8H26C15 8 11 14 11 25V39C11 50 15 56 26 56H44"/>
   <path d="M85 8H58V56H85M58 32H79"/>
   <path d="M99 56V8H118C132 8 137 15 137 23C137 31 132 39 118 39H99M118 39L141 56"/>
   <path d="M154 56L176 8L198 56M163 37H189"/>
  </g>}
 </svg>;
}
