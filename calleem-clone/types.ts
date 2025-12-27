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
