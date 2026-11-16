import { ImageResponse } from 'next/og';

export const size={width:1200,height:630};
export const contentType='image/png';

export default function OpenGraphImage(){
 return new ImageResponse(
  <div style={{width:'100%',height:'100%',display:'flex',flexDirection:'column',justifyContent:'space-between',background:'#102425',color:'#F3F1EB',padding:'68px 75px'}}>
   <div style={{display:'flex',alignItems:'center',gap:20}}>
    <svg width="82" height="82" viewBox="0 0 80 80" fill="none">
     <path d="M62 17H32C20 17 15 24 15 35V45C15 56 20 63 32 63H62" stroke="#F3F1EB" strokeWidth="10"/>
     <path d="M60 40H43" stroke="#E9875C" strokeWidth="8"/>
    </svg>
    <span style={{fontSize:40,fontWeight:700,letterSpacing:-2}}>CERA</span>
   </div>
   <div style={{display:'flex',flexDirection:'column',gap:22,maxWidth:1060}}>
    <div style={{fontSize:96,lineHeight:1,letterSpacing:-5,fontWeight:600}}>A prediction isn't proof.</div>
    <div style={{fontSize:22,color:'#ACC6BD'}}>Protein fitness research</div>
   </div>
   <div style={{width:'100%',height:1,background:'#405D55',display:'flex'}}/>
  </div>,
  size
 );
}
