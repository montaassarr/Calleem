import React, { useState } from 'react';
import { CALL_VOLUME_OPTIONS, BUSINESS_TYPES } from '../constants';
import { FormData } from '../types';
import { ArrowUpRight } from 'lucide-react';

const ContactForm: React.FC = () => {
  const [formData, setFormData] = useState<FormData>({
    fullName: '',
    email: '',
    businessName: '',
    businessType: '',
    phoneNumber: '',
    monthlyCalls: '300-550 calls/month',
    message: '',
    newsletter: true,
    privacyPolicy: false,
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = e.target;
    setFormData(prev => ({ ...prev, [name]: checked }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Form submitted:', formData);
    alert("Thanks for your interest! We'll be in touch soon.");
  };

  return (
    <div className="w-full max-w-[600px] bg-calleem-card rounded-[20px] p-6 md:p-10 shadow-xl">
      <h4 className="font-display font-bold text-2xl mb-8 text-white">Write us a message</h4>
      
      <form onSubmit={handleSubmit} className="flex flex-col gap-5">
        
        {/* Full Name & Email Row */}
        <div className="flex flex-col md:flex-row gap-5">
          <div className="flex-1 flex flex-col gap-2.5">
            <label className="text-[14px] font-medium text-white/90">Full name</label>
            <div className="bg-[#5c5146]/30 rounded-[10px] border border-white/10 focus-within:border-[#09f] focus-within:ring-1 focus-within:ring-[#09f] transition-all">
              <input
                type="text"
                name="fullName"
                placeholder="Jane"
                required
                className="w-full bg-transparent p-3 md:p-4 text-[14px] text-white placeholder-white/40 focus:outline-none"
                value={formData.fullName}
                onChange={handleChange}
              />
            </div>
          </div>
          <div className="flex-1 flex flex-col gap-2.5">
            <label className="text-[14px] font-medium text-white/90">Email</label>
            <div className="bg-[#5c5146]/30 rounded-[10px] border border-white/10 focus-within:border-[#09f] focus-within:ring-1 focus-within:ring-[#09f] transition-all">
              <input
                type="email"
                name="email"
                placeholder="jane@framer.com"
                required
                className="w-full bg-transparent p-3 md:p-4 text-[14px] text-white placeholder-white/40 focus:outline-none"
                value={formData.email}
                onChange={handleChange}
              />
            </div>
          </div>
        </div>

        {/* Business Name */}
        <div className="flex flex-col gap-2.5">
          <label className="text-[14px] font-medium text-white/90">Business Name</label>
          <div className="bg-[#5c5146]/30 rounded-[10px] border border-white/10 focus-within:border-[#09f] focus-within:ring-1 focus-within:ring-[#09f] transition-all">
            <input
              type="text"
              name="businessName"
              placeholder="Jane's Salon"
              required
              className="w-full bg-transparent p-3 md:p-4 text-[14px] text-white placeholder-white/40 focus:outline-none"
              value={formData.businessName}
              onChange={handleChange}
            />
          </div>
        </div>

        {/* Business Type */}
        <div className="flex flex-col gap-2.5">
          <label className="text-[14px] font-medium text-white/90">Business Type</label>
          <div className="relative bg-[#5c5146]/30 rounded-[10px] border border-white/10 focus-within:border-[#09f] focus-within:ring-1 focus-within:ring-[#09f] transition-all">
            <select
              name="businessType"
              required
              className="w-full bg-transparent p-3 md:p-4 text-[14px] text-white placeholder-white/40 focus:outline-none appearance-none cursor-pointer"
              value={formData.businessType}
              onChange={handleChange}
            >
              <option value="" disabled className="text-gray-500">Select...</option>
              {BUSINESS_TYPES.map(type => (
                <option key={type} value={type} className="text-black bg-white">{type}</option>
              ))}
            </select>
            <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-white/50">
              <svg width="12" height="8" viewBox="0 0 12 8" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M1 1.5L6 6.5L11 1.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
          </div>
        </div>

        {/* Phone Number */}
        <div className="flex flex-col gap-2.5">
          <label className="text-[14px] font-medium text-white/90">Phone Number</label>
          <div className="bg-[#5c5146]/30 rounded-[10px] border border-white/10 focus-within:border-[#09f] focus-within:ring-1 focus-within:ring-[#09f] transition-all">
            <input
              type="tel"
              name="phoneNumber"
              placeholder="+1234567890"
              required
              className="w-full bg-transparent p-3 md:p-4 text-[14px] text-white placeholder-white/40 focus:outline-none"
              value={formData.phoneNumber}
              onChange={handleChange}
            />
          </div>
        </div>

        {/* Number of Monthly Calls (Radio) */}
        <div className="flex flex-col gap-2.5">
          <label className="text-[14px] font-medium text-white/90">Number of Monthly Calls</label>
          <div className="flex flex-col gap-3">
            {CALL_VOLUME_OPTIONS.map((option) => (
              <label key={option} className="flex items-center gap-3 cursor-pointer group">
                <div className="relative w-4 h-4 rounded-full border border-white/30 bg-[#bbb3] flex items-center justify-center overflow-hidden">
                  <input
                    type="radio"
                    name="monthlyCalls"
                    value={option}
                    checked={formData.monthlyCalls === option}
                    onChange={handleChange}
                    className="appearance-none w-full h-full cursor-pointer checked:bg-white checked:border-[#09f] border-transparent border-[3px]"
                  />
                </div>
                <span className="text-[12px] font-medium text-white/60 group-hover:text-white transition-colors">{option}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Message */}
        <div className="flex flex-col gap-2.5">
          <label className="text-[14px] font-medium text-white/90">What would you like to see in the demo?</label>
          <div className="bg-[#5c5146]/30 rounded-[10px] border border-white/10 focus-within:border-[#09f] focus-within:ring-1 focus-within:ring-[#09f] transition-all h-[130px]">
            <textarea
              name="message"
              placeholder="Write your message here"
              className="w-full h-full bg-transparent p-3 md:p-4 text-[14px] text-white placeholder-white/40 focus:outline-none resize-none"
              value={formData.message}
              onChange={handleChange}
            />
          </div>
        </div>

        {/* Checkboxes */}
        <div className="flex flex-col gap-2.5 mt-2">
          {/* Privacy Policy */}
          <label className="flex items-center gap-3 cursor-pointer">
            <div className="relative w-6 h-6 rounded-md border border-[#2f2f2f] bg-[#807765]/30 flex items-center justify-center">
              <input
                type="checkbox"
                name="privacyPolicy"
                checked={formData.privacyPolicy}
                onChange={handleCheckboxChange}
                className="peer appearance-none w-full h-full cursor-pointer rounded-md checked:bg-[#2f2f2f] checked:border-[#2f2f2f] transition-all"
              />
              <div className="absolute inset-0 flex items-center justify-center text-[#8cff2e] opacity-0 peer-checked:opacity-100 pointer-events-none transition-opacity">
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M2.5 7L5.5 10L11.5 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
            </div>
            <span className="text-[12px] font-medium text-white/60">
              I agree to the <a href="#" className="underline hover:text-white">privacy policy.</a>
            </span>
          </label>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={!formData.privacyPolicy}
          className="mt-2 w-full bg-calleem-accent hover:bg-[#368f51] disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold text-[15px] py-4 rounded-[10px] shadow-[0_2px_18px_1px_rgba(5,5,5,0.31)] transition-all flex items-center justify-center gap-2"
        >
          Get in touch
        </button>

      </form>
    </div>
  );
};

export default ContactForm;
