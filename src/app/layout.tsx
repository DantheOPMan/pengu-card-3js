import type { Metadata } from 'next';
import './globals.css';
export const metadata:Metadata={title:'Winter Crown — The Frost King',description:'An interactive ivory and silver card. Turn it to explore the Frost King portrait and Frostbound Lattice reverse.'};
export default function RootLayout({children}:{children:React.ReactNode}) { return <html lang="en"><body>{children}</body></html>; }
