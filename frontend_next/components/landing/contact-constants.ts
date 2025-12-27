export interface FAQItem {
    id: string;
    number: string;
    question: string;
    answer: string;
}

export interface FormData {
    fullName: string;
    email: string;
    businessName: string;
    businessType: string;
    phoneNumber: string;
    monthlyCalls: string;
    message: string;
    newsletter: boolean;
    privacyPolicy: boolean;
}

export const FAQ_ITEMS: FAQItem[] = [
    {
        id: '1',
        number: '01',
        question: 'What kind of businesses is Calleem built for?',
        answer: 'Calleem is designed for service-based businesses like medical clinics, salons, consulting firms, law offices, repair services, and any business that receives appointment requests by phone. It’s perfect for automating customer communication 24/7.'
    },
    {
        id: '2',
        number: '02',
        question: 'Does Calleem integrate with my exsiting phone number ?',
        answer: 'Yes. Calleem seamlessly syncs with phone numbers. You will never lose your customers.'
    },
    {
        id: '3',
        number: '03',
        question: 'Can I customize the AI’s voice and greeting?',
        answer: 'Yes. You can choose from multiple natural-sounding voices, set custom greetings, and tailor conversation flows to match your brand’s tone and services.'
    },
    {
        id: '4',
        number: '04',
        question: 'Will I get conversation history in every call ?',
        answer: 'Yes. Every conversation is recorded and transcribed into text format, saved in your dashboard\'s History section. You can review full conversation transcripts, see call analytics, and export data for reporting.'
    },
    {
        id: '5',
        number: '05',
        question: 'Can I test the AI before going live?',
        answer: 'Absolutely. You can schedule a demo call with our team to walk through setup, and test conversations directly through your dashboard before connecting your business phone. Try the AI with sample calls to ensure it\'s ready.'
    },
    {
        id: '6',
        number: '06',
        question: 'How can I get support if I run into issues?',
        answer: 'We offer priority email support, live chat during business hours, and a comprehensive help center with setup guides and video tutorials.'
    }
];

export const CALL_VOLUME_OPTIONS = [
    '300-550 calls/month',
    '560-800 calls/month',
    '810-990 calls/month'
];

export const BUSINESS_TYPES = [
    'Salon',
    'Consulting',
    'Clinic',
    'Agency',
    'Law Firm',
    'Other'
];
