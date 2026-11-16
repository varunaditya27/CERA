import type { Metadata } from 'next';
import { Navigation } from '../components/navigation';
import './globals.css';

export const metadata: Metadata = {
  title: { default: 'CERA | The Evidence Atlas', template: '%s | CERA' },
  description: 'A research atlas for auditing learned rewards, investigating counterexamples, and studying constrained repairs in protein fitness optimization.',
  openGraph: {title:'CERA — A search that questions itself',description:'The evidence atlas for counterexample-guided reward auditing.',type:'website'}
};

export default function RootLayout({children}:{children:React.ReactNode}) {
  return <html lang="en"><body>
    <a href="#main-content" className="skip-link">Skip to research content</a>
    <div className="shell"><Navigation/><main className="main" id="main-content" tabIndex={-1}>{children}</main></div>
  </body></html>;
}
