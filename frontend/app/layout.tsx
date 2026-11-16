import type { Metadata } from 'next';
import { Navigation } from '../components/navigation';
import { fragmentMono, geologica, onest } from './fonts';
import { MotionRuntime } from '../components/motion-runtime';
import './globals.css';
import 'lenis/dist/lenis.css';

export const metadata:Metadata={
  title:{default:'CERA | Protein fitness research',template:'%s | CERA'},
  description:'CERA studies unreliable learned rewards in protein optimization and how to test possible corrections.',
  openGraph:{title:'CERA',description:'Counterexample-guided reward auditing for protein fitness optimization.',type:'website'},
  robots:{index:true,follow:true}
};

export default function RootLayout({children}:{children:React.ReactNode}){
  return <html lang="en" className={`${geologica.variable} ${onest.variable} ${fragmentMono.variable}`}><body>
    <a href="#main-content" className="skip-link">Skip to content</a>
    <Navigation/>
    <MotionRuntime/>
    <main id="main-content" className="main" tabIndex={-1}>{children}</main>
  </body></html>;
}
