'use client';

import LandingNavbar  from '@/components/Landing/Navbar';
import Hero           from '@/components/Landing/Hero';
import Features       from '@/components/Landing/Features';
import HowItWorks     from '@/components/Landing/HowItWorks';
import DemoPreview    from '@/components/Landing/DemoPreview';
import CTA            from '@/components/Landing/CTA';
import Footer         from '@/components/Landing/Footer';

export default function LandingPage() {
  return (
    <div className="font-sans antialiased text-gray-900 overflow-x-hidden">
      <LandingNavbar />
      <Hero />
      <Features />
      <HowItWorks />
      <DemoPreview />
      <CTA />
      <Footer />
    </div>
  );
}
