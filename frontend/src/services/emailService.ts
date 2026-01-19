import emailjs from '@emailjs/browser';

// ============================================
// EMAILJS CONFIGURATION - UPDATE THESE VALUES
// ============================================
// 1. Go to https://www.emailjs.com/ and create a free account
// 2. Add your Gmail service and note the Service ID
// 3. Create a template with variables: {{from_email}}, {{subject}}, {{message}}
// 4. Get your Public Key from Account > API Keys
// ============================================

const EMAILJS_SERVICE_ID = import.meta.env.VITE_EMAILJS_SERVICE_ID;
const EMAILJS_TEMPLATE_ID = import.meta.env.VITE_EMAILJS_TEMPLATE_ID;
const EMAILJS_PUBLIC_KEY = import.meta.env.VITE_EMAILJS_PUBLIC_KEY;

export interface ContactFormData {
    email: string;
    subject: string;
    message: string;
}

export const sendContactEmail = async (data: ContactFormData): Promise<void> => {
    // Validate that credentials are configured
    if (!EMAILJS_SERVICE_ID || !EMAILJS_TEMPLATE_ID || !EMAILJS_PUBLIC_KEY) {
        throw new Error('EmailJS credentials not configured. Please set defaults in frontend/.env');
    }

    const templateParams = {
        from_email: data.email,
        subject: data.subject,
        message: data.message,
    };

    await emailjs.send(
        EMAILJS_SERVICE_ID,
        EMAILJS_TEMPLATE_ID,
        templateParams,
        EMAILJS_PUBLIC_KEY
    );
};
