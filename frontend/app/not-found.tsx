import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';

export default function NotFound(){
 return <div className="missing-page">
   <span>404</span><h1>Page not found.</h1><p>There is no page at this address.</p>
   <Link href="/" className="inline-link"><ArrowLeft size={17}/> Back to overview</Link>
 </div>;
}
