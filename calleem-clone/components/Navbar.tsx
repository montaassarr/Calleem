import React, { useState } from 'react';
import { Menu, X, ArrowUpRight } from 'lucide-react';

const Navbar: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 transition-all duration-300">
      <div className="absolute inset-0 bg-[#648768]/50 backdrop-blur-[15px] border-b border-white/5"></div>
      
      <div className="relative mx-auto max-w-[1200px] px-6 h-20 flex items-center justify-between">
        {/* Logo */}
        <a href="/" className="flex items-center gap-2 group">
          <div className="w-10 h-6 relative">
             <svg viewBox="0 0 41 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full h-full text-white">
                <path d="M21.821 0.929C22.354 0.38 23.092 0.068 23.865 0.065L33.762 0.065C40.198 0.065 43.42 8.011 38.869 12.659L28.958 22.783C28.503 23.247 27.725 22.918 27.725 22.26L27.725 13.345L28.87 12.174C29.78 11.245 29.136 9.656 27.848 9.656L13.276 9.656L21.821 0.929Z" fill="currentColor"/>
                <path d="M19.179 22.071C18.646 22.62 17.908 22.932 17.135 22.935L7.238 22.935C0.802 22.935 -2.42 14.988 2.131 10.341L12.042 0.217C12.497 -0.247 13.276 0.082 13.276 0.739L13.276 9.655L12.13 10.825C11.22 11.755 11.864 13.344 13.152 13.344L27.724 13.344L19.178 22.071Z" fill="currentColor"/>
             </svg>
          </div>
          <span className="font-display font-semibold text-xl tracking-tight text-white">Calleem</span>
        </a>

        {/* Desktop Links */}
        <div className="hidden md:flex items-center gap-8">
          {['How it works', 'Features', 'Pricing', 'FAQ'].map((link) => (
            <a 
              key={link} 
              href={`#${link.toLowerCase().replace(/\s/g, '-')}`}
              className="text-white/90 hover:text-white font-medium text-[15px] transition-colors"
            >
              {link}
            </a>
          ))}
        </div>

        {/* CTA Button */}
        <div className="hidden md:flex">
          <a 
            href="#contact" 
            className="group flex items-center gap-2 bg-calleem-accent hover:bg-[#368f51] text-white px-5 py-3 rounded-full font-semibold text-[15px] transition-all duration-300 shadow-[0_1px_16px_2px_rgba(5,5,5,0.18)]"
          >
            Request Access
            <ArrowUpRight className="w-4 h-4 transition-transform group-hover:-translate-y-0.5 group-hover:translate-x-0.5" />
          </a>
        </div>

        {/* Mobile Toggle */}
        <button 
          className="md:hidden relative z-10 p-2 text-white bg-calleem-card rounded-full"
          onClick={() => setIsOpen(!isOpen)}
        >
          {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Mobile Menu */}
      {isOpen && (
        <div className="md:hidden absolute top-20 left-0 w-full bg-calleem-dark/95 backdrop-blur-xl border-t border-white/10 p-6 flex flex-col gap-6 shadow-2xl h-screen">
          {['How it works', 'Features', 'Pricing', 'FAQ'].map((link) => (
            <a 
              key={link} 
              href={`#${link.toLowerCase().replace(/\s/g, '-')}`}
              className="text-white text-lg font-medium"
              onClick={() => setIsOpen(false)}
            >
              {link}
            </a>
          ))}
          <a 
            href="#contact" 
            className="flex items-center justify-center gap-2 bg-calleem-accent text-white px-5 py-4 rounded-full font-bold text-lg mt-4"
            onClick={() => setIsOpen(false)}
          >
            Request Access
            <ArrowUpRight className="w-5 h-5" />
          </a>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
