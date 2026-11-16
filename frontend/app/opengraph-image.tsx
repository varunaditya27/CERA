import { ImageResponse } from 'next/og';

export const size={width:1200,height:630};
export const contentType='image/png';

export default function OpenGraphImage(){
 return new ImageResponse(
  <div style={{width:'100%',height:'100%',display:'flex',flexDirection:'column',justifyContent:'space-between',background:'#102425',color:'#F2F3EE',padding:'64px 72px',position:'relative'}}>
   <div style={{display:'flex',alignItems:'center',gap:22}}>
    <div style={{width:58,height:58,display:'flex',alignItems:'center',justifyContent:'center',border:'1px solid #415649',position:'relative'}}>
      <div style={{display:'flex',width:35,height:35,flexDirection:'column',justifyContent:'space-around'}}>
        <div style={{height:3,background:'#F2F3EE'}}/><div style={{height:3,background:'#F2F3EE'}}/><div style={{height:3,background:'#F2F3EE'}}/>
      </div>
      <div style={{position:'absolute',width:13,height:13,background:'#E9875C',transform:'rotate(45deg)'}}/>
    </div>
    <span style={{fontSize:34,fontWeight:700,letterSpacing:-2}}>CERA</span>
   </div>
   <div style={{display:'flex',flexDirection:'column',gap:24,maxWidth:940}}>
    <div style={{fontSize:82,lineHeight:1.05,letterSpacing:-4,fontWeight:400}}>A prediction isn't proof.</div>
    <div style={{fontSize:22,color:'#B4C3B9'}}>Research in protein fitness optimization</div>
   </div>
   <div style={{height:2,width:90,background:'#E9875C'}}/>
  </div>,
  size
 );
}
