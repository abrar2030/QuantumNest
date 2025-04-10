import Layout from '../components/Layout';
import { useState } from 'react';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis } from 'recharts';

export default function AIRecommendations({ darkMode, toggleDarkMode }) {
  // Mock data for AI prediction accuracy
  const predictionAccuracyData = [
    { month: 'Jan', accuracy: 82 },
    { month: 'Feb', accuracy: 85 },
    { month: 'Mar', accuracy: 83 },
    { month: 'Apr', accuracy: 87 },
    { month: 'May', accuracy: 89 },
    { month: 'Jun', accuracy: 88 },
    { month: 'Jul', accuracy: 91 },
  ];

  // Mock data for model performance comparison
  const modelComparisonData = [
    { name: 'Accuracy', lstm: 91, garch: 87, pca: 84, ensemble: 93 },
    { name: 'Precision', lstm: 89, garch: 85, pca: 82, ensemble: 90 },
    { name: 'Recall', lstm: 87, garch: 83, pca: 80, ensemble: 89 },
    { name: 'F1 Score', lstm: 88, garch: 84, pca: 81, ensemble: 91 },
    { name: 'Stability', lstm: 85, garch: 89, pca: 86, ensemble: 92 },
  ];

  // Mock data for portfolio optimization scenarios
  const optimizationScenariosData = [
    { name: 'Conservative', return: 6.2, risk: 4.5, sharpe: 1.38 },
    { name: 'Balanced', return: 8.5, risk: 7.2, sharpe: 1.18 },
    { name: 'Growth', return: 11.8, risk: 12.5, sharpe: 0.94 },
    { name: 'Aggressive', return: 15.2, risk: 18.7, sharpe: 0.81 },
    { name: 'AI Optimized', return: 12.5, risk: 9.8, sharpe: 1.28 },
  ];

  // Mock data for stock recommendations
  const stockRecommendations = [
    {
      ticker: "AAPL",
      name: "Apple Inc.",
      action: "Buy",
      targetPrice: "$215.50",
      currentPrice: "$198.25",
      potential: "+8.7%",
      confidence: "High",
      reasoning: "Strong product cycle, services growth, and AI integration potential"
    },
    {
      ticker: "MSFT",
      name: "Microsoft Corporation",
      action: "Hold",
      targetPrice: "$425.00",
      currentPrice: "$410.75",
      potential: "+3.5%",
      confidence: "Medium",
      reasoning: "Cloud growth remains strong but valuation is approaching full potential"
    },
    {
      ticker: "NVDA",
      name: "NVIDIA Corporation",
      action: "Buy",
      targetPrice: "$950.00",
      currentPrice: "$845.30",
      potential: "+12.4%",
      confidence: "High",
      reasoning: "Continued AI chip demand and data center expansion"
    },
    {
      ticker: "AMZN",
      name: "Amazon.com Inc.",
      action: "Buy",
      targetPrice: "$195.00",
      currentPrice: "$175.80",
      potential: "+10.9%",
      confidence: "Medium",
      reasoning: "AWS growth acceleration and retail margin improvements"
    },
    {
      ticker: "META",
      name: "Meta Platforms Inc.",
      action: "Hold",
      targetPrice: "$520.00",
      currentPrice: "$505.25",
      potential: "+2.9%",
      confidence: "Medium",
      reasoning: "Ad revenue recovery balanced against metaverse investment costs"
    }
  ];

  // Mock data for market trend predictions
  const marketTrendPredictions = [
    {
      title: "Technology Sector Outlook",
      prediction: "Bullish",
      timeframe: "3-6 months",
      confidence: "High",
      description: "Our AI models predict continued strength in the technology sector, particularly in companies focused on AI, cloud computing, and cybersecurity."
    },
    {
      title: "Interest Rate Impact",
      prediction: "Neutral to Positive",
      timeframe: "6-12 months",
      confidence: "Medium",
      description: "Expected interest rate stabilization should provide a supportive environment for equities, with potential for multiple expansion in growth stocks."
    },
    {
      title: "Consumer Discretionary",
      prediction: "Cautious",
      timeframe: "3 months",
      confidence: "Medium",
      description: "Consumer spending may face headwinds in the near term as inflation impacts continue to be felt, suggesting selective positioning in this sector."
    },
    {
      title: "Healthcare Innovation",
      prediction: "Bullish",
      timeframe: "12+ months",
      confidence: "High",
      description: "Breakthrough technologies in genomics, precision medicine, and AI-driven diagnostics position the healthcare innovation segment for strong long-term growth."
    }
  ];

  return (
    <Layout darkMode={darkMode} toggleDarkMode={toggleDarkMode}>
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">AI Recommendations</h1>
          <p className="text-gray-600 dark:text-gray-300">
            Advanced machine learning models providing investment insights and portfolio optimization.
          </p>
        </div>

        {/* AI Model Performance */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">AI Prediction Accuracy</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={predictionAccuracyData}
                margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis domain={[75, 95]} />
                <Tooltip formatter={(value) => `${value}%`} />
                <Legend />
                <Line type="monotone" dataKey="accuracy" stroke="#8884d8" activeDot={{ r: 8 }} name="Prediction Accuracy" />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
            Our AI models have consistently improved in accuracy over time, with the latest ensemble approach achieving over 90% accuracy in market trend predictions.
          </p>
        </div>

        {/* Model Comparison */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">Model Performance Comparison</h2>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart outerRadius={90} data={modelComparisonData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="name" />
                <PolarRadiusAxis angle={30} domain={[0, 100]} />
                <Radar name="LSTM" dataKey="lstm" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
                <Radar name="GARCH" dataKey="garch" stroke="#82ca9d" fill="#82ca9d" fillOpacity={0.6} />
                <Radar name="PCA" dataKey="pca" stroke="#ffc658" fill="#ffc658" fillOpacity={0.6} />
                <Radar name="Ensemble" dataKey="ensemble" stroke="#ff8042" fill="#ff8042" fillOpacity={0.6} />
                <Legend />
                <Tooltip />
              </RadarChart>
            </ResponsiveContainer>
          </div>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
            Comparison of our different AI models across key performance metrics. The ensemble approach combines the strengths of individual models for superior results.
          </p>
        </div>

        {/* Portfolio Optimization */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">Portfolio Optimization Scenarios</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={optimizationScenariosData}
                margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis yAxisId="left" orientation="left" stroke="#8884d8" />
                <YAxis yAxisId="right" orientation="right" stroke="#82ca9d" />
                <Tooltip />
                <Legend />
                <Bar yAxisId="left" dataKey="return" name="Expected Return (%)" fill="#8884d8" />
                <Bar yAxisId="left" dataKey="risk" name="Risk (%)" fill="#82ca9d" />
                <Bar yAxisId="right" dataKey="sharpe" name="Sharpe Ratio" fill="#ffc658" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
            Our AI-optimized portfolio aims to maximize the Sharpe ratio, providing better risk-adjusted returns compared to traditional allocation strategies.
          </p>
        </div>

        {/* Stock Recommendations */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">AI-Generated Stock Recommendations</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Ticker</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Company</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Action</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Current</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Target</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Potential</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Confidence</th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {stockRecommendations.map((stock, index) => (
                  <tr key={index}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">{stock.ticker}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">{stock.name}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        stock.action === 'Buy' 
                          ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' 
                          : stock.action === 'Sell'
                            ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                            : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                      }`}>
                        {stock.action}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">{stock.currentPrice}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">{stock.targetPrice}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-green-500">{stock.potential}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">{stock.confidence}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-4">
            <button className="text-indigo-600 dark:text-indigo-400 font-medium hover:underline">
              View All Recommendations
            </button>
          </div>
        </div>

        {/* Market Trend Predictions */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">Market Trend Predictions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {marketTrendPredictions.map((trend, index) => (
              <div key={index} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white">{trend.title}</h3>
                  <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                    trend.prediction.includes('Bullish') 
                      ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' 
                      : trend.prediction.includes('Cautious') || trend.prediction.includes('Neutral')
                        ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                        : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                  }`}>
                    {trend.prediction}
                  </span>
                </div>
                <div className="flex space-x-4 text-sm text-gray-500 dark:text-gray-400 mb-2">
                  <span>Timeframe: {trend.timeframe}</span>
                  <span>Confidence: {trend.confidence}</span>
                </div>
                <p className="text-gray-600 dark:text-gray-300">{trend.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* AI Methodology */}
        <div className="bg-indigo-50 dark:bg-indigo-900/20 rounded-xl shadow-lg p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">Our AI Methodology</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white dark:bg-gray-800 rounded-lg p-4">
              <div className="flex items-center mb-3">
                <div className="flex-shrink-0 bg-indigo-100 dark:bg-indigo-800 rounded-full p-2 mr-3">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-indigo-600 dark:text-indigo-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-800 dark:text-white">LSTM Networks</h3>
              </div>
              <p className="text-gray-600 dark:text-gray-300">
                Long Short-Term Memory networks excel at capturing temporal dependencies in financial time series data, enabling accurate prediction of market trends and price movements.
              </p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg p-4">
              <div className="flex items-center mb-3">
                <div className="flex-shrink-0 bg-indigo-100 dark:bg-indigo-800 rounded-full p-2 mr-3">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-indigo-600 dark:text-indigo-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-800 dark:text-white">GARCH Models</h3>
              </div>
              <p className="text-gray-600 dark:text-gray-300">
                Generalized Autoregressive Conditional Heteroskedasticity models are specifically designed to capture volatility clustering in financial markets, providing robust risk assessments.
              </p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg p-4">
              <div className="flex items-center mb-3">
                <div className="flex-shrink-0 bg-indigo-100 dark:bg-indigo-800 rounded-full p-2 mr-3">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-indigo-600 dark:text-indigo-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-800 dark:text-white">Ensemble Learning</h3>
              </div>
              <p className="text-gray-600 dark:text-gray-300">
                Our ensemble approach combines multiple models to leverage their individual strengths, resulting in more robust and accurate predictions across various market conditions.
              </p>
            </div>
          </div>
        </div>

        {/* Personalized Recommendations */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-8">
          <div className="flex items-start mb-6">
            <div className="flex-shrink-0 bg-indigo-100 dark:bg-indigo-800 rounded-full p-3 mr-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-indigo-600 dark:text-indigo-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5.121 17.804A13.937 13.937 0 0112 16c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 11-6 0 3 3 0 016 0zm6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-800 dark:text-white">Get Personalized AI Recommendations</h2>
              <p className="text-gray-600 dark:text-gray-300">Complete your risk profile and investment goals to receive tailored AI-powered investment recommendations.</p>
            </div>
          </div>
          <div className="bg-indigo-50 dark:bg-indigo-900/20 rounded-lg p-6 text-center">
            <h3 className="text-lg font-medium text-gray-800 dark:text-white mb-4">Ready to optimize your portfolio with AI?</h3>
            <button className="px-6 py-3 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 transition-colors duration-300">
              Start Personalized Assessment
            </button>
            <p className="mt-3 text-sm text-gray-500 dark:text-gray-400">
              Takes approximately 5 minutes to complete
            </p>
          </div>
        </div>
      </div>
    </Layout>
  );
}
