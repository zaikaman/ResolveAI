import React, { useState } from 'react';
import { sendContactEmail } from '../services/emailService';

// ContactSection component with form state and email submission
const ContactSection: React.FC = () => {
    const [formData, setFormData] = useState({ email: '', subject: '', message: '' });
    const [status, setStatus] = useState<'idle' | 'sending' | 'success' | 'error'>('idle');
    const [errorMessage, setErrorMessage] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setStatus('sending');
        setErrorMessage('');

        try {
            await sendContactEmail(formData);
            setStatus('success');
            setFormData({ email: '', subject: '', message: '' });
        } catch (err) {
            setStatus('error');
            setErrorMessage(err instanceof Error ? err.message : 'Failed to send message');
        }
    };

    return (
        <section className="flex flex-col py-16 w-full bg-gray-200 dark:bg-color-slate-700 gap-5 items-center" id="contact">
            <div className="flex flex-col gap-1 font-semibold items-center">
                <p className="text-base text-main dark:text-slate-500">Contact us</p>
                <h2 className="text-xl text-color-slate-700 dark:text-white items-center">We are here for you</h2>
            </div>

            {status === 'success' ? (
                <div className="container bg-green-100 border border-green-400 text-green-700 px-8 py-6 rounded-lg text-center">
                    <p className="text-lg font-semibold">Message sent successfully!</p>
                    <p className="mt-2">We'll get back to you soon.</p>
                    <button
                        onClick={() => setStatus('idle')}
                        className="mt-4 px-6 py-2 bg-main text-white rounded-md hover:bg-blue-700"
                    >
                        Send another message
                    </button>
                </div>
            ) : (
                <form onSubmit={handleSubmit} className="space-y-4 container">
                    {status === 'error' && (
                        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                            {errorMessage}
                        </div>
                    )}
                    <div>
                        <input
                            type="email"
                            value={formData.email}
                            onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                            className="shadow-sm bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-main focus:border-main block w-full p-4 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white"
                            placeholder="Your email"
                            required
                        />
                    </div>
                    <div>
                        <input
                            type="text"
                            value={formData.subject}
                            onChange={(e) => setFormData(prev => ({ ...prev, subject: e.target.value }))}
                            className="block p-4 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 shadow-sm focus:ring-main focus:border-main dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white"
                            placeholder="Subject"
                            required
                        />
                    </div>
                    <div className="sm:col-span-2">
                        <textarea
                            value={formData.message}
                            onChange={(e) => setFormData(prev => ({ ...prev, message: e.target.value }))}
                            rows={6}
                            className="block p-4 w-full text-sm text-gray-900 bg-gray-50 rounded-lg shadow-sm border border-gray-300 focus:ring-main focus:border-main dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white"
                            placeholder="Your message"
                            required
                        ></textarea>
                    </div>
                    <button
                        type="submit"
                        disabled={status === 'sending'}
                        className="w-full px-8 py-3 bg-main text-white border-2 border-white rounded-md shadow-md shadow-shadowcolor hover:bg-white hover:text-main disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {status === 'sending' ? 'Sending...' : 'Send message'}
                    </button>
                </form>
            )}
        </section>
    );
};

const LandingPage: React.FC = () => {
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const [activeFaq, setActiveFaq] = useState<number | null>(1);
    const [isDarkMode, setIsDarkMode] = useState(false);



    const toggleDarkMode = () => {
        setIsDarkMode(!isDarkMode);
        const html = document.documentElement;
        if (isDarkMode) {
            html.classList.remove('dark');
            document.body.classList.remove('dark');
        } else {
            html.classList.add('dark');
            document.body.classList.add('dark');
        }
    };

    const toggleFaq = (index: number) => {
        setActiveFaq(activeFaq === index ? null : index);
    };

    return (
        <main className={`w-full bg-white dark:bg-color-slate-800 ${isDarkMode ? 'dark' : ''}`}>
            <section className=" bg-white dark:bg-color-slate-800 container  ">
                {/* nav */}
                <div className="flex flex-row gap-16  justify-between py-8 items-center">
                    <div className="flex items-center gap-2">
                        <img src="/logo.webp" alt="ResolveAI Logo" className="w-10 h-10" />
                        <h1 className="lg:text-xxl text-xl font-bold text-color-slate-800 dark:text-white">ResolveAI</h1>
                    </div>
                    {/* menu */}
                    <ul className="hidden lg:flex items-center space-x-5  text-color-slate-700 dark:text-white  ">
                        <li className="text-main "><a href="#home">Home</a></li>
                        <li className="hover:text-main"><a href="#features">Features</a></li>
                        <li className="hover:text-main"><a href="#how-it-works">How It Works</a></li>
                        <li className="hover:text-main"><a href="#tools">Tools</a></li>
                        <li className="hover:text-main"><a href="#faq">FAQ</a></li>
                        <li className="hover:text-main"><a href="#contact">Contact</a></li>
                    </ul>
                    <div className="flex gap-10 items-center ">
                        {/* btn */}
                        <a href="#contact" className="btn1 dark:shadow-white/10 hover:bg-emerald-500">Get Free Plan</a>

                        <div className="flex gap-2 5">
                            {/* moon and sun */}
                            <div className="day-night text-end  text-blue-500 dark:text-white" onClick={toggleDarkMode}>
                                {isDarkMode ? <i className="sun fa-solid fa-sun"></i> : <i className="moon fa-solid fa-moon"></i>}
                            </div>

                            {/* responsive nav */}
                            {/* hamburger icon */}
                            <div id="hamburger" className="lg:hidden cursor-pointer z-50 dark:text-white " onClick={() => setIsMenuOpen(!isMenuOpen)}>
                                <i className={`responsive fa-solid ${isMenuOpen ? 'fa-xmark' : 'fa-bars'}`}></i>
                            </div>
                        </div>
                    </div>

                    {/* mobile menu */}
                    <div id="menu" className={`${isMenuOpen ? '' : 'hidden'} bg-white h-[100vh] absolute inset-0 items-center z-20`}>
                        <ul className="h-full grid place-items-center py-20">
                            <li className="text-main " onClick={() => setIsMenuOpen(false)}><a href="#home">Home</a></li>
                            <li className="hover:text-main" onClick={() => setIsMenuOpen(false)}><a href="#features">Features</a></li>
                            <li className="hover:text-main" onClick={() => setIsMenuOpen(false)}><a href="#how-it-works">How It Works</a></li>
                            <li className="hover:text-main" onClick={() => setIsMenuOpen(false)}><a href="#tools">Tools</a></li>
                            <li className="hover:text-main" onClick={() => setIsMenuOpen(false)}><a href="#faq">FAQ</a></li>
                            <li className="hover:text-main" onClick={() => setIsMenuOpen(false)}><a href="#contact">Contact</a></li>
                            {/* btn */}
                            <a href="" className="btn1 dark:shadow-white/10 hover:bg-emerald-500" onClick={() => setIsMenuOpen(false)}>Get Free Plan</a>
                        </ul>
                    </div>
                </div>

                {/* Hero start */}
                <div id="home" className="flex flex-col  lg:flex-row text-center lg:text-left  w-2/2 gap-10  justify-between items-center pb-16  pt-10">
                    {/* left side */}
                    <div className="lg:w-1/2 w-2/2 flex flex-col gap-10  items-center lg:items-start">
                        <h1 className="text-xxl font-bold text-color-slate-800 dark:text-white">Break Free from Debt with <span className="text-main">AI-Powered Planning.</span> </h1>
                        <p className="text-base text-color-slate-500 dark:text-white">Your personalized AI financial coach. Create an optimized payoff plan in under 3 minutes and achieve lasting financial health.</p>
                        {/* hero btns */}
                        <div className="flex  gap-2 ">
                            <a href="#contact" className="btn1 dark:shadow-white/10 hover:bg-transparent dark:text-white hover:text-main border-2 border-main ">Start Assessment</a>
                            <a href="#how-it-works" className="btn2 dark:shadow-white/10 hover:bg-main hover:text-white dark:text-white">How It Works</a>
                        </div>
                    </div>
                    {/* Right side img */}
                    <div className="items-center">
                        <img src="images/finance.png" alt="" className=" w-[50rem]"></img>
                    </div>
                </div>
            </section>
            {/* Hero end */}


            {/* feature start */}

            <section id="features" className="flex flex-col  justify-between gap-5  py-16 container  items-center lg:items-start">
                {/* title */}
                <div className="flex flex-col gap-1  font-semibold">
                    <p className="text-base  text-main dark:text-slate-500">Our Features</p>
                    <h2 className="text-xl text-color-slate-700 dark:text-white ">Why Choose ResolveAI?</h2>
                </div>
                {/* Feature items */}
                <div className="w-full flex flex-col lg:flex-row  justify-between gap-10  ">
                    <div className="lg:w-1/2 w-full">
                        <img src="images/feature.webp" alt="" className="lg:w-[50rem] sm:w-[40rem] w-[30rem] rounded-lg bg-cover "></img>
                    </div>
                    {/* right side */}

                    <div className="lg:w-1/2 w-full  flex flex-col text-center lg:text-start gap-10 items-center lg:items-start ">
                        <div className=" flex flex-col  gap-3">
                            <p className="lg:text-base   text-color-slate-500 dark:text-white/70">From intelligent debt assessment to daily behavioral coaching, ResolveAI is your partner in financial freedom.</p>
                            <p className="lg:text-base text-color-slate-500 dark:text-white/70">Stop guessing. Let our AI analyze your situation and generate the fastest mathematical path to zero debt.</p>
                        </div>

                        <div className="grid grid-cols-1 lg:grid-cols-3 sm:grid-cols-3  items-center lg:items-start gap-5   ">
                            {/* feature 1 */}
                            <div className=" flex flex-col px-3   py-10  items-center  bg-white dark:bg-color-slate-800 shadow-md shadow-shadowcolor  dark:shadow-white/10  rounded-md gap-3  ">
                                <img src="images/icon1.png" alt="" className="w-16 "></img>
                                <h3 className="text-base text-center text-color-slate-600 font-bold dark:text-white">Smart Assessment</h3>
                                <a href="" className="text-main text-sm dark:text-white">Instant Analysis</a>
                            </div>
                            {/* feature 2 */}
                            <div className=" flex flex-col px-3   py-10 items-center  bg-white dark:bg-color-slate-800 shadow-md shadow-shadowcolor  dark:shadow-white/10  rounded-md gap-3  ">
                                <img src="images/icon2.png" alt="" className="w-16 "></img>
                                <h3 className="text-base  text-color-slate-600 font-bold dark:text-white">Daily Actions</h3>
                                <a href="" className="text-main text-sm dark:text-white">Stay on Track</a>
                            </div>
                            {/* feature 3 */}
                            <div className=" flex flex-col px-3   py-10 items-center  bg-white dark:bg-color-slate-800 shadow-md shadow-shadowcolor  dark:shadow-white/10  rounded-md gap-3  ">
                                <img src="images/icon3.png" alt="" className="w-16 "></img>
                                <h3 className="text-base  text-color-slate-600 font-bold dark:text-white">Negotiation AI</h3>
                                <a href="" className="text-main text-sm dark:text-white">Lower Rates</a>
                            </div>
                        </div>
                        <a href="" className="btn1 w-fit dark:shadow-white/10 hover:bg-emerald-600">See more</a>
                    </div>
                </div>
            </section>
            {/* feature end */}


            {/* About us start */}
            <section id="about" className="flex flex-col gap-5  py-16  container items-center lg:items-start ">
                {/* title */}
                <div className="flex flex-col gap-1 font-semibold lg:text-left text-center">
                    <p className="text-base  text-main dark:text-slate-500 ">How It Works</p>
                    <h2 className="text-xl text-color-slate-700 dark:text-white">Your Path to Freedom</h2>
                </div>
                {/* about items */}
                <div className="w-full flex flex-col  lg:flex-row gap-10 items-center">


                    {/* left side */}
                    <div id="how-it-works" className="lg:w-1/2 w-full  flex flex-col gap-8 items-center lg:items-start">
                        <h2 className="text-xl text-color-slate-500 dark:text-white lg:text-left text-center">Three steps to a debt-free life</h2>
                        <p className="text-base text-color-slate-500 dark:text-white lg:text-left text-center">We combine behavioral psychology with advanced mathematics to create a plan that works for YOU, not against you.</p>
                        {/* about lign1 */}
                        <div className="flex gap-3  items-center">
                            <img src="images/icon.png" alt="" className="w-4  "></img>
                            <p className="text-base text-color-slate-600 font-semibold dark:text-white/70 ">1. Connect your debts (OCR or Manual)</p>
                        </div>
                        {/* about lign2 */}
                        <div className="flex gap-3  items-center ">
                            <img src="images/icon.png" alt="" className="w-4 "></img>
                            <p className="text-base text-color-slate-600 font-semibold dark:text-white/70">2. Get your optimized AI Repayment Plan</p>
                        </div>
                        {/* about lign3 */}
                        <div className="flex gap-3  items-center ">
                            <img src="images/icon.png" alt="" className="w-4 "></img>
                            <p className="text-base text-color-slate-600 font-semibold dark:text-white/70">3. Follow daily actions & celebrate milestones</p>
                        </div>
                        <a href="#contact" className="btn1 w-fit pt-3 dark:shadow-white/30 hover:bg-emerald-500">Starts for Free</a>
                    </div>
                    {/* Right side img */}
                    <div className="lg:w-1/2 w-full">
                        <img src="images/about.png" alt="" className="lg:w-[50rem] sm:w-[40rem] w-[30rem] rounded-lg  bg-cover"></img>
                    </div>
                </div>
            </section>
            {/* about us end */}
            {/* services start */}
            <section id="tools" className="flex flex-col  gap-10  container  py-16">
                {/* title */}
                <div className="flex flex-col gap-1 font-semibold items-center text-center">
                    <p className="text-base  text-main dark:text-slate-500 ">Our Toolkit</p>
                    <h2 className="text-xl text-color-slate-700 dark:text-white">Tools for your freedom</h2>
                    <p className="text-base text-color-slate-500 font-normal dark:text-white/70 ">Everything you need to crush debt, in one app.</p>
                </div>
                {/* services items */}
                <div className="grid grid-cols-1 lg:grid-cols-3 sm:grid-cols-2 gap-10 lg:items-start items-center  ">

                    {/* item 1 */}
                    <div className="flex flex-col  shadow-md shadow-shadowcolor dark:shadow-white/10  items-center bg-white dark:bg-color-slate-800 px-6  py-10 gap-2   text-center rounded-md hover:bg-emerald-50">
                        <div className="w-12 h-12 flex items-center justify-center text-3xl text-main"><i className="fa-solid fa-calculator"></i></div>
                        <h3 className="text-lg text-color-slate-600 font-semibold dark:text-white  ">Plan Optimization </h3>
                        <p className="text-base text-color-slate-500 dark:text-white/70 font-normal">Avalanche or Snowball? We calculate the mathematically best route for you.</p>
                    </div>

                    {/* item 2 */}
                    <div className="flex flex-col  shadow-md shadow-shadowcolor dark:shadow-white/10  items-center bg-main px-6 py-10  gap-2 text-center rounded-md  hover:bg-emerald-500">
                        <div className="w-14 h-14 flex items-center justify-center text-3xl text-white"><i className="fa-solid fa-piggy-bank"></i></div>
                        <h3 className="text-lg text-white font-semibold">Spending Leaks</h3>
                        <p className="text-base text-white font-normal">Identify and plug spending leaks to free up cash for debt payments.</p>
                    </div>
                    {/* item 3 */}
                    <div className="flex flex-col  shadow-md shadow-shadowcolor dark:shadow-white/10  items-center bg-white dark:bg-color-slate-800 px-6  py-10 gap-2   text-center rounded-md hover:bg-emerald-50 ">
                        <div className="w-14 h-14 flex items-center justify-center text-3xl text-main"><i className="fa-solid fa-file-contract"></i></div>
                        <h3 className="text-lg text-color-slate-600 font-semibold dark:text-white">Negotiation Scripts</h3>
                        <p className="text-base text-color-slate-500 dark:text-white/70 font-normal">Use AI-crafted scripts to negotiate lower interest rates with creditors.</p>
                    </div>
                    {/* item 4 */}
                    <div className="flex flex-col  shadow-md shadow-shadowcolor  dark:shadow-white/10 items-center bg-white dark:bg-color-slate-800 px-6  py-10  gap-2   text-center rounded-md  hover:bg-emerald-50">
                        <div className="w-14 h-14 flex items-center justify-center text-3xl text-main"><i className="fa-solid fa-chart-pie"></i></div>
                        <h3 className="text-lg text-color-slate-600 font-semibold dark:text-white">Detailed Reporting</h3>
                        <p className="text-base text-color-slate-500 dark:text-white/70 font-normal">Visualize your journey to zero with beautiful charts and projections.</p>
                    </div>
                    {/* item 5  */}
                    <div className="flex flex-col  shadow-md shadow-shadowcolor  dark:shadow-white/10 items-center bg-white dark:bg-color-slate-800 px-6  py-10   gap-2   text-center rounded-md hover:bg-emerald-50 ">
                        <div className="w-12 h-12 flex items-center justify-center text-3xl text-main"><i className="fa-solid fa-heart-pulse"></i></div>
                        <h3 className="text-lg text-color-slate-600 font-semibold dark:text-white">Habit Coaching</h3>
                        <p className="text-base text-color-slate-500 dark:text-white/70 font-normal">Daily behavioral nudges to help you build lasting financial habits.</p>
                    </div>
                    {/* item 6 */}
                    <div className="flex flex-col  shadow-md shadow-shadowcolor  dark:shadow-white/10 items-center bg-white dark:bg-color-slate-800 px-6  py-10   gap-2   text-center rounded-md hover:bg-emerald-50 ">
                        <div className="w-16 h-16 flex items-center justify-center text-3xl text-main"><i className="fa-solid fa-shield-halved"></i></div>
                        <h3 className="text-lg text-color-slate-600 font-semibold dark:text-white">Secure Data</h3>
                        <p className="text-base text-color-slate-500 dark:text-white/70 font-normal">Bank-grade encryption (AES-256) keeps your financial data safe.</p>
                    </div>
                </div>
            </section>
            {/* services end */}



            {/* customers start */}
            <section className=" flex flex-col py-16   w-full bg-gray-200 dark:bg-color-slate-700 gap-5 items-center">

                {/* title */}
                <div className="flex flex-col gap-1 font-semibold items-center">
                    <p className="text-base  text-main  dark:text-slate-500 ">As Seen In</p>
                    <h2 className="text-xl text-color-slate-700 dark:text-white ">Trusted by thousands of users</h2>
                </div>
                <div className=" grid grid-cols-1 lg:grid-cols-5 sm:grid-cols-    :grid-cols-2  items-center gap-2  ">
                    <span className="text-2xl font-bold text-slate-400 p-3">TechCrunch</span>
                    <span className="text-2xl font-bold text-slate-400 p-3">Forbes</span>
                    <span className="text-2xl font-bold text-slate-400 p-3">Bloomberg</span>
                    <span className="text-2xl font-bold text-slate-400 p-3">Wired</span>
                    <span className="text-2xl font-bold text-slate-400 p-3">WSJ</span>
                </div>

            </section>
            {/* customers end */}

            {/* FAQ start */}
            <section id="faq" className="flex flex-col gap-5  py-16 container items-center lg:items-start">
                {/* title */}
                <div className="flex flex-col gap-1 font-semibold text-center lg:text-left">
                    <p className="text-base  text-main dark:text-slate-500 ">Our FAQ</p>
                    <h2 className="text-xl text-color-slate-700 dark:text-white">Frequently asked questions</h2>
                </div>

                <div className="w-full flex flex-col lg:flex-row gap-10 items-center ">
                    {/* left side img */}
                    <div className="xl:w-1/2 w-full  ">
                        <img src="images/faq.svg" alt="" className="w-[50rem]  "></img>
                    </div>
                    {/* right side  */}
                    <div id="faq" className="xl:w-1/2 w-full flex flex-col gap-0    py-16 container">

                        {/* faq items */}
                        <div className="">
                            <div className="">
                                <ul className="gap-3 bg-blue-50 ">
                                    {/* FAQ ITEM COMPONENT */}
                                    {[
                                        { id: 1, q: "Does ResolveAI work with any bank?", a: "Yes! We support thousands of financial institutions via Plaid to securely import your transaction data." },
                                        { id: 2, q: "Is my data secure?", a: "Absolutely. We use bank-grade AES-256 encryption. We never sell your data." },
                                        { id: 3, q: "Is there a free plan?", a: "Yes, our core assessment and planning tools are completely free. Upgrade for advanced automation." },
                                        { id: 4, q: "How fast can I get a plan?", a: "Less than 3 minutes. Upload your statements and our AI does the rest instantly." },
                                        { id: 5, q: "Can I negotiate my interest rates?", a: "Yes! Use our AI Negotiation Script generator to get a custom script for calling your banks." }
                                    ].map((item, index) => (
                                        <li key={item.id} className={`relative shadow-lg shadow-shadowcolor ${index === 4 ? 'dark:shadow-slate-500' : ''} z-${50 - (index * 10)}`}>
                                            <button className="w-full rounded-md  bg-blue-50 px-8 py-6 text-left" onClick={() => toggleFaq(item.id)}>
                                                <div className="flex items-center justify-between">
                                                    <h3 className="text-color-slate-600 text-base  ">{item.q}</h3>
                                                    <i className="fa-solid fa-circle-chevron-down text-main"></i>
                                                </div>
                                            </button>

                                            <div
                                                className={`relative overflow-hidden transition-all duration-500 bg-gray-50 flex dark:bg-color-slate-700 rounded-b-md ${activeFaq === item.id ? 'max-h-[500px]' : 'max-h-0'}`}
                                            >
                                                <div className={`px-6 pt-5 pb-[4rem] ${index === 4 ? 'dark:border-l-white' : ''}`}>
                                                    <p className="text-base  text-color-slate-500 dark:text-white/70 font-light">{item.a}</p>
                                                </div>
                                            </div>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </section>







            {/* Contact start */}
            <ContactSection />
            {/* Contact  end */}



            {/* FAQ end */}

            <footer className="w-full flex flex-col  gap-5   pt-16 container ">
                <div className="flex flex-col lg:flex-row  gap-10 lg:gap-56 lg:items-start items-center">
                    <div className=" lg:w-1/4  md:w-2/4 sm:w-full flex flex-col gap-5 lg:text-left text-center  ">
                        <div className="flex items-center gap-2 justify-center lg:justify-start">
                            <img src="/logo.webp" alt="ResolveAI Logo" className="w-10 h-10" />
                            <h1 className="text-xxl font-bold text-color-slate-800 dark:text-white">ResolveAI</h1>
                        </div>
                        <p className="text-base text-color-slate-500 font-normal dark:text-white/80">Helping you break free from debt through intelligent planning and behavioral coaching.</p>
                    </div>

                    <div className="grid grid-cols-3 gap-10 lg:gap-56   lg:w-2/4 sm:w-full">
                        {/* links */}
                        <div className="lg:w-1/4  md:w-2/4 sm:w-full flex flex-col gap-3  lg:items-start items-center ">
                            <h3 className="text-lg font-semibold text-color-slate-500 dark:text-white ">Links</h3>
                            <ul className="flex flex-col gap-2 text-color-slate-500 dark:text-white/80">
                                <li className="hover:text-main lg:text-left text-center"><a href="#features" id="features">Features</a></li>
                                <li className="hover:text-main lg:text-left text-center"><a href="#how-it-works" id="about">How It Works</a></li>
                                <li className="hover:text-main lg:text-left text-center"><a href="#tools" id="services">Tools</a></li>
                            </ul>
                        </div>

                        {/* category */}
                        <div className="lg:w-1/4  md:w-2/4 sm:w-full flex flex-col gap-3  items-center ">
                            <h3 className="text-lg font-semibold text-color-slate-500 dark:text-white">Category</h3>
                            <ul className="flex flex-col gap-2  text-color-slate-500 dark:text-white/80">
                                <li className="hover:text-main"><a href="" id="features">Features</a></li>
                                <li className="hover:text-main"><a href="" id="about">About Us</a></li>
                                <li className="hover:text-main"><a href="" id="services">Services</a></li>
                                <li className="hover:text-main"><a href="" id="portofolio">Portofolio</a></li>
                            </ul>
                        </div>
                        {/* category */}
                        <div className="lg:w-1/4  md:w-2/4 sm:w-full flex flex-col gap-3  items-center ">
                            <h3 className="text-lg font-semibold text-color-slate-500 dark:text-white">Category</h3>
                            <ul className="flex flex-col gap-2 text-color-slate-500 dark:text-white/80">
                                <li className="hover:text-main"><a href="" id="features">Features</a></li>
                                <li className="hover:text-main"><a href="" id="about">About Us</a></li>
                                <li className="hover:text-main"><a href="" id="services">Services</a></li>
                                <li className="hover:text-main"><a href="" id="portofolio">Portofolio</a></li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div className="w-full bg-color-slate-500 border"></div>

                <div className="flex flex-col lg:flex-row items-center lg:items-start gap-5 justify-between py-5 ">
                    <p className="text-base  text-color-slate-500 font-light dark:text-white/80">© 2026 ResolveAI. All rights reserved.</p>
                    <div className="flex gap-3 dark:text-white/80">
                        <a href="https://facebook.com" target="_blank"> <i className="fa-brands fa-facebook w-fit bg-color-slate-600 p-3 text-white rounded-full hover:bg-main"></i></a>
                        <a href="https://twitter.com" target="_blank"> <i className="fa-brands fa-twitter w-fit bg-color-slate-600 p-3 text-white rounded-full hover:bg-main "></i></a>
                        <a href="https://instagram.com" target="_blank"> <i className="fa-brands fa-instagram w-fit bg-color-slate-600 p-3 text-white rounded-full hover:bg-main"></i></a>
                    </div>
                </div>
            </footer>
        </main>
    );
};

export default LandingPage;
