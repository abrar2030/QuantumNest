import Layout from '../components/Layout';
import Link from 'next/link';

export default function Home({ darkMode, toggleDarkMode }) {
  return (
    <Layout darkMode={darkMode} toggleDarkMode={toggleDarkMode}>
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold mb-6 text-gray-900 dark:text-white">
            QuantumNest Capital
          </h1>
          <p className="text-xl mb-8 text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
            A futuristic fintech platform integrating AI, Blockchain, Data Science, and Automation for next-generation hedge fund management.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link href="/portfolio" className="px-6 py-3 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 transition-colors duration-300">
              Explore Portfolio
            </Link>
            <Link href="/login" className="px-6 py-3 bg-white dark:bg-gray-800 text-indigo-600 dark:text-indigo-400 font-medium rounded-lg border border-indigo-600 dark:border-indigo-400 hover:bg-indigo-50 dark:hover:bg-gray-700 transition-colors duration-300">
              Get Started
            </Link>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
          <div className="p-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300">
            <div className="text-indigo-600 dark:text-indigo-400 mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h2 className="text-2xl font-semibold mb-4 text-gray-800 dark:text-white">AI-Powered Analytics</h2>
            <p className="text-gray-600 dark:text-gray-300 mb-4">Advanced machine learning models for financial prediction and portfolio optimization with LSTM, GARCH, and PCA implementations.</p>
            <Link href="/ai-recommendations" className="text-indigo-600 dark:text-indigo-400 font-medium hover:underline">
              Learn more →
            </Link>
          </div>
          
          <div className="p-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300">
            <div className="text-indigo-600 dark:text-indigo-400 mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
              </svg>
            </div>
            <h2 className="text-2xl font-semibold mb-4 text-gray-800 dark:text-white">Blockchain Integration</h2>
            <p className="text-gray-600 dark:text-gray-300 mb-4">Secure transactions with Ethereum smart contracts and transparent ledger technology for trustless trading and settlement.</p>
            <Link href="/blockchain-explorer" className="text-indigo-600 dark:text-indigo-400 font-medium hover:underline">
              Learn more →
            </Link>
          </div>
          
          <div className="p-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300">
            <div className="text-indigo-600 dark:text-indigo-400 mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h2 className="text-2xl font-semibold mb-4 text-gray-800 dark:text-white">Real-time Data</h2>
            <p className="text-gray-600 dark:text-gray-300 mb-4">Live financial data streaming with advanced visualization and insights powered by WebSockets and real-time analytics.</p>
            <Link href="/market-analysis" className="text-indigo-600 dark:text-indigo-400 font-medium hover:underline">
              Learn more →
            </Link>
          </div>
        </div>
        
        <div className="bg-indigo-50 dark:bg-gray-800 rounded-2xl p-8 mb-16">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">Why Choose QuantumNest Capital?</h2>
            <p className="text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">Our platform combines cutting-edge technologies to provide unparalleled insights and performance for your investments.</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="flex items-start">
              <div className="flex-shrink-0 bg-indigo-100 dark:bg-gray-700 rounded-lg p-3 mr-4">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-indigo-600 dark:text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-800 dark:text-white mb-2">Advanced Security</h3>
                <p className="text-gray-600 dark:text-gray-300">Enterprise-grade security with blockchain verification and multi-factor authentication.</p>
              </div>
            </div>
            
            <div className="flex items-start">
              <div className="flex-shrink-0 bg-indigo-100 dark:bg-gray-700 rounded-lg p-3 mr-4">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-indigo-600 dark:text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-800 dark:text-white mb-2">Performance Optimization</h3>
                <p className="text-gray-600 dark:text-gray-300">AI-driven portfolio optimization with risk profiling and automated rebalancing.</p>
              </div>
            </div>
            
            <div className="flex items-start">
              <div className="flex-shrink-0 bg-indigo-100 dark:bg-gray-700 rounded-lg p-3 mr-4">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-indigo-600 dark:text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-800 dark:text-white mb-2">Intelligent Insights</h3>
                <p className="text-gray-600 dark:text-gray-300">Predictive analytics and market sentiment analysis to stay ahead of market trends.</p>
              </div>
            </div>
            
            <div className="flex items-start">
              <div className="flex-shrink-0 bg-indigo-100 dark:bg-gray-700 rounded-lg p-3 mr-4">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-indigo-600 dark:text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-800 dark:text-white mb-2">Real-time Monitoring</h3>
                <p className="text-gray-600 dark:text-gray-300">24/7 portfolio monitoring with customizable alerts and notifications.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
