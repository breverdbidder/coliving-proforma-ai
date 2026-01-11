import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Send, Download, FileSpreadsheet, FileText, BarChart3, Building, DollarSign, TrendingUp, AlertCircle, CheckCircle, Upload } from 'lucide-react';

/**
 * Co-Living Proforma AI Chatbot
 * NLP-powered interface for co-living real estate analysis
 * 
 * Features:
 * - Natural language query processing
 * - Excel template integration
 * - Custom scenario inputs
 * - Multi-format outputs (Excel, PDF, Dashboard)
 * - Real-time financial calculations
 */

const CoLivingProformaChatbot = () => {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: `🏠 **BidDeed.AI Co-Living Proforma Analyzer**

I'm your AI-powered co-living investment analyst specializing in Brevard County, FL markets.

**What I Can Do:**
✅ Analyze the uploaded Excel proforma template
✅ Run custom scenarios with your inputs
✅ Generate professional Excel reports
✅ Create PDF executive summaries
✅ Build interactive dashboards

**Quick Start Examples:**
• "Analyze a 20-unit property with $900/bedroom rent"
• "What's the NOI for 15 studios and 10 1-bedrooms?"
• "Show me sensitivity analysis for occupancy rates"
• "Compare scenario A: 93% occupancy vs scenario B: 88%"

**Financial Metrics I Calculate:**
📊 NOI, Cap Rate, Cash-on-Cash Return
📊 DSCR, IRR, Equity Multiple
📊 Sensitivity Analysis & Risk Assessment

How can I help with your co-living investment analysis today?`
    }
  ]);
  
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentAnalysis, setCurrentAnalysis] = useState(null);
  const [uploadedFile, setUploadedFile] = useState(null);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Handle message submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage = inputValue.trim();
    setInputValue('');
    
    // Add user message
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      // Call the backend API (this would connect to your Python LangGraph orchestrator)
      const response = await analyzeCoLivingProperty(userMessage, uploadedFile);
      
      // Add AI response
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: response.chatbot_response,
        analysis: response.full_analysis,
        dashboard: response.dashboard_data
      }]);
      
      setCurrentAnalysis(response.full_analysis);
      
    } catch (error) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: `⚠️ **Analysis Error**\n\n${error.message}\n\nPlease try rephrasing your question or check your inputs.`
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  // Simulate backend API call (replace with actual API endpoint)
  const analyzeCoLivingProperty = async (query, file) => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // This would call your Python backend endpoint
    // const response = await fetch('/api/coliving/analyze', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify({ query, file })
    // });
    // return response.json();
    
    // Mock response for demonstration
    return {
      chatbot_response: generateMockResponse(query),
      full_analysis: generateMockAnalysis(),
      dashboard_data: generateMockDashboard()
    };
  };

  // Mock response generator (replace with actual API)
  const generateMockResponse = (query) => {
    // Extract numbers from query for realistic calculations
    const unitMatch = query.match(/(\d+)[\s-]?unit/i);
    const rentMatch = query.match(/\$?(\d+)/);
    
    const units = unitMatch ? parseInt(unitMatch[1]) : 20;
    const rent = rentMatch ? parseInt(rentMatch[1]) : 900;
    
    const totalBedrooms = units * 1.5; // Average 1.5 bedrooms per unit
    const monthlyGPI = totalBedrooms * rent;
    const annualGPI = monthlyGPI * 12;
    const occupancy = 0.93;
    const egi = annualGPI * occupancy;
    const opex = egi * 0.50;
    const noi = egi - opex;
    const purchasePrice = noi / 0.07; // 7% cap rate
    const capRate = (noi / purchasePrice) * 100;
    
    return `🏠 **Co-Living Analysis Complete**

**Property Overview:**
• Total Units: ${units}
• Total Bedrooms: ${Math.round(totalBedrooms)}
• Average Rent: $${rent}/bedroom/month
• Location: Brevard County, FL

**Financial Performance:**
• Gross Potential Income: $${annualGPI.toLocaleString()}/year
• Effective Gross Income: $${Math.round(egi).toLocaleString()}/year (${(occupancy * 100).toFixed(0)}% occupancy)
• Operating Expenses: $${Math.round(opex).toLocaleString()}/year (50% OpEx ratio)
• **Net Operating Income: $${Math.round(noi).toLocaleString()}/year**

**Investment Metrics:**
• **Cap Rate: ${capRate.toFixed(2)}%**
• Estimated Value: $${Math.round(purchasePrice).toLocaleString()}
• DSCR: 1.35x (assuming 75% LTV at 5.5%)

**Market Analysis (Brevard County):**
✅ Above average cap rate for market
✅ Strong occupancy supports revenue
⚠️ Monitor OpEx ratio (target: 45-50%)

**Available Outputs:**
📊 Click "Download Excel" for full proforma
📄 Click "Generate PDF" for executive summary  
📈 Click "View Dashboard" for interactive charts

What would you like to explore next?`;
  };

  const generateMockAnalysis = () => {
    return {
      cash_flow: {
        noi: 156000,
        annual_debt_service: 115000,
        dscr: 1.35,
        cash_flow_after_debt: 41000
      },
      returns_metrics: {
        cap_rate: 7.2,
        cash_on_cash_return: 8.5,
        purchase_price: 2167000,
        down_payment: 542000
      }
    };
  };

  const generateMockDashboard = () => {
    return {
      key_metrics: {
        NOI: 156000,
        'Cap Rate': 7.2,
        'Cash-on-Cash': 8.5,
        DSCR: 1.35
      },
      revenue_breakdown: {
        bedroom_rent: 324000,
        parking: 12000,
        amenities: 8000
      },
      expense_breakdown: {
        property_management: 34400,
        utilities: 41280,
        maintenance: 27520,
        insurance: 13760,
        property_taxes: 34400,
        marketing: 10320,
        cleaning: 17200,
        wifi_tech: 6880,
        amenities: 10320
      }
    };
  };

  // Handle file upload
  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file && file.name.endsWith('.xlsx')) {
      setUploadedFile(file);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `✅ **Excel File Uploaded: ${file.name}**\n\nI've loaded your Excel template. I can now:\n• Analyze existing assumptions\n• Override with custom scenarios\n• Update calculations in real-time\n• Generate revised Excel output\n\nWhat would you like me to analyze?`
      }]);
    } else {
      alert('Please upload an Excel file (.xlsx)');
    }
  };

  // Quick action handlers
  const handleQuickAction = (action) => {
    setInputValue(action);
  };

  // Export handlers
  const handleDownloadExcel = () => {
    if (!currentAnalysis) {
      alert('Please run an analysis first');
      return;
    }
    // This would trigger the backend to generate Excel
    alert('Generating Excel proforma... (Backend integration required)');
  };

  const handleGeneratePDF = () => {
    if (!currentAnalysis) {
      alert('Please run an analysis first');
      return;
    }
    // This would trigger the backend to generate PDF
    alert('Generating PDF report... (Backend integration required)');
  };

  const handleViewDashboard = () => {
    if (!currentAnalysis) {
      alert('Please run an analysis first');
      return;
    }
    // This would open the interactive dashboard
    alert('Opening interactive dashboard... (Component to be rendered)');
  };

  const quickActions = [
    "Analyze 20-unit property at $900/bedroom",
    "Show me sensitivity for 85-95% occupancy",
    "Compare Class A vs Class B co-living",
    "What's the break-even occupancy rate?",
    "Generate full investment memo",
    "Run scenario: $800 rent, 50 units"
  ];

  return (
    <div style={{
      fontFamily: 'system-ui, -apple-system, sans-serif',
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      backgroundColor: '#f8fafc'
    }}>
      {/* Header */}
      <div style={{
        background: 'linear-gradient(135deg, #2563eb 0%, #10b981 100%)',
        padding: '20px',
        color: 'white',
        boxShadow: '0 4px 20px rgba(0,0,0,0.1)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <Building size={32} />
            <div>
              <h1 style={{ margin: 0, fontSize: '24px', fontWeight: '700' }}>
                BidDeed.AI Co-Living Analyzer
              </h1>
              <p style={{ margin: 0, fontSize: '14px', opacity: 0.9 }}>
                AI-Powered Proforma Analysis • Brevard County, FL
              </p>
            </div>
          </div>
          
          <div style={{ display: 'flex', gap: '12px' }}>
            <button
              onClick={() => fileInputRef.current?.click()}
              style={{
                background: 'rgba(255,255,255,0.2)',
                border: 'none',
                padding: '10px 16px',
                borderRadius: '8px',
                color: 'white',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                fontSize: '14px',
                fontWeight: '500'
              }}
            >
              <Upload size={18} />
              Upload Excel
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept=".xlsx"
              onChange={handleFileUpload}
              style={{ display: 'none' }}
            />
          </div>
        </div>
      </div>

      {/* Action Bar */}
      {currentAnalysis && (
        <div style={{
          padding: '16px',
          backgroundColor: 'white',
          borderBottom: '1px solid #e5e7eb',
          display: 'flex',
          gap: '12px',
          justifyContent: 'center'
        }}>
          <button
            onClick={handleDownloadExcel}
            style={{
              background: '#10b981',
              color: 'white',
              border: 'none',
              padding: '10px 20px',
              borderRadius: '8px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              fontWeight: '500'
            }}
          >
            <FileSpreadsheet size={18} />
            Download Excel
          </button>
          
          <button
            onClick={handleGeneratePDF}
            style={{
              background: '#ef4444',
              color: 'white',
              border: 'none',
              padding: '10px 20px',
              borderRadius: '8px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              fontWeight: '500'
            }}
          >
            <FileText size={18} />
            Generate PDF
          </button>
          
          <button
            onClick={handleViewDashboard}
            style={{
              background: '#f59e0b',
              color: 'white',
              border: 'none',
              padding: '10px 20px',
              borderRadius: '8px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              fontWeight: '500'
            }}
          >
            <BarChart3 size={18} />
            View Dashboard
          </button>
        </div>
      )}

      {/* Messages */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '20px',
        display: 'flex',
        flexDirection: 'column',
        gap: '16px'
      }}>
        {messages.map((message, index) => (
          <div
            key={index}
            style={{
              display: 'flex',
              justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start'
            }}
          >
            <div
              style={{
                maxWidth: '80%',
                padding: '16px 20px',
                borderRadius: '16px',
                backgroundColor: message.role === 'user' ? '#2563eb' : 'white',
                color: message.role === 'user' ? 'white' : '#111827',
                boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                whiteSpace: 'pre-wrap',
                lineHeight: '1.6',
                border: message.role === 'assistant' ? '1px solid #e5e7eb' : 'none'
              }}
            >
              {message.content}
            </div>
          </div>
        ))}

        {isLoading && (
          <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
            <div style={{
              padding: '16px 20px',
              borderRadius: '16px',
              backgroundColor: 'white',
              border: '1px solid #e5e7eb',
              display: 'flex',
              alignItems: 'center',
              gap: '12px'
            }}>
              <div style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                backgroundColor: '#10b981',
                animation: 'pulse 1.5s ease-in-out infinite'
              }} />
              <div style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                backgroundColor: '#10b981',
                animation: 'pulse 1.5s ease-in-out infinite 0.2s'
              }} />
              <div style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                backgroundColor: '#10b981',
                animation: 'pulse 1.5s ease-in-out infinite 0.4s'
              }} />
              <span style={{ marginLeft: '8px', color: '#6b7280', fontSize: '14px' }}>
                Running 12-stage analysis pipeline...
              </span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Quick Actions */}
      <div style={{
        padding: '16px',
        backgroundColor: 'white',
        borderTop: '1px solid #e5e7eb'
      }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '8px',
          marginBottom: '16px'
        }}>
          {quickActions.map((action, index) => (
            <button
              key={index}
              onClick={() => handleQuickAction(action)}
              disabled={isLoading}
              style={{
                background: '#f8fafc',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                padding: '10px 12px',
                cursor: isLoading ? 'not-allowed' : 'pointer',
                textAlign: 'left',
                fontSize: '13px',
                color: '#374151',
                opacity: isLoading ? 0.5 : 1,
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => !isLoading && (e.target.style.backgroundColor = '#e5e7eb')}
              onMouseLeave={(e) => !isLoading && (e.target.style.backgroundColor = '#f8fafc')}
            >
              {action}
            </button>
          ))}
        </div>

        {/* Input Form */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '12px' }}>
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Ask about co-living analysis, NOI, cap rates, scenarios..."
            disabled={isLoading}
            style={{
              flex: 1,
              padding: '14px 16px',
              border: '2px solid #e5e7eb',
              borderRadius: '12px',
              fontSize: '15px',
              outline: 'none',
              transition: 'border-color 0.2s'
            }}
            onFocus={(e) => e.target.style.borderColor = '#2563eb'}
            onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
          />
          
          <button
            type="submit"
            disabled={!inputValue.trim() || isLoading}
            style={{
              background: inputValue.trim() && !isLoading ? '#2563eb' : '#e5e7eb',
              color: inputValue.trim() && !isLoading ? 'white' : '#9ca3af',
              border: 'none',
              borderRadius: '12px',
              padding: '14px 24px',
              cursor: inputValue.trim() && !isLoading ? 'pointer' : 'not-allowed',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              fontWeight: '500',
              transition: 'all 0.2s'
            }}
          >
            <Send size={18} />
            Analyze
          </button>
        </form>
      </div>

      {/* CSS Animation */}
      <style>{`
        @keyframes pulse {
          0%, 100% {
            opacity: 0.4;
            transform: scale(1);
          }
          50% {
            opacity: 1;
            transform: scale(1.2);
          }
        }
      `}</style>
    </div>
  );
};

export default CoLivingProformaChatbot;
