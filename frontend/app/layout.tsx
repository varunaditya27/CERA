import type { Metadata } from 'next';
import { Navigation } from '../components/navigation';
import './globals.css';
export const metadata: Metadata = { title: { default: 'CERA | Research workspace', template: '%s | CERA' }, description: 'A workspace for auditing learned rewards in protein fitness optimization.' };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="en"><body><a className="skip-link" href="#main-content">Skip to content</a><div className="shell"><Navigation/><main id="main-content" className="main" tabIndex={-1}>{children}</main></div></body></html>; }
