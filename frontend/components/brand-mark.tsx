export function BrandMark({size=32,light=false}:{size?:number;light?:boolean}){
 return <svg width={size} height={size} viewBox="0 0 48 48" fill="none" aria-hidden="true" focusable="false">
   <path d="M6 11H42M6 24H18M34 24H42M6 37H42" stroke={light?'var(--paper)':'var(--ink)'} strokeWidth="3.2" strokeLinecap="square"/>
   <path d="M26 16L34 24L26 32L18 24Z" fill="var(--copper)"/>
 </svg>;
}
