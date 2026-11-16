import type { Metadata } from 'next';
import { Navigation } from '../components/navigation';
import { fragmentMono, newsreader, onest } from './fonts';
import { MotionRuntime } from '../components/motion-runtime';
import './globals.css';
import 'lenis/dist/lenis.css';

export const metadata:Metadata={
  metadataBase:new URL('https://github.com/varunaditya27/CERA'),
  title:{default:'CERA | Protein fitness research',template:'%s | CERA'},
  description:'CERA studies how to identify and repair unreliable learned rewards in protein fitness optimization.',
  openGraph:{title:'CERA',description:'Counterexample-guided reward auditing for protein fitness optimization.',type:'website'},
  robots:{index:true,follow:true}
};

export default function RootLayout({children}:{children:React.ReactNode}){
  return <html lang="en" className={`${newsreader.variable} ${onest.variable} ${fragmentMono.variable}`}><body>
    <a href="#main-content" className="skip-link">Skip to content</a>
    <Navigation/>
    <MotionRuntime/>
    <main id="main-content" className="main" tabIndex={-1}>{children}</main>
  </body></html>;
}
