import React, { useState, useEffect } from 'react';
import { ShieldAlert, ShieldCheck, Activity, AlertTriangle, AlertCircle, X, XOctagon } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

// Format currency
const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
};

// Format date
const formatDate = (dateString) => {
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }).format(new Date(dateString));
};

const getRiskLevel = (score) => {
  if (score >= 80) return 'critical';
  if (score >= 60) return 'high';
  if (score >= 30) return 'medium';
  return 'low';
};

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function App() {
  const [summary, setSummary] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTx, setSelectedTx] = useState(null);


  const [recentTransactions, setRecentTransactions] = useState([]);

  useEffect(() => {
    fetchData();
    // Poll every 10 seconds for real-time feel
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [summaryRes, txRes, recentRes] = await Promise.all([
        fetch(`${API_BASE_URL}/analytics/summary`),
        fetch(`${API_BASE_URL}/transactions?limit=50&sort_by_risk=true`),
        fetch(`${API_BASE_URL}/transactions?limit=20&sort_by_risk=false`)
      ]);
      const summaryData = await summaryRes.json();
      const txData = await txRes.json();
      const recentData = await recentRes.json();
      
      setSummary(summaryData);
      setTransactions(txData);
      setRecentTransactions(recentData);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching data:", error);
      setLoading(false);
    }
  };

  const handleTxClick = async (txId) => {
    try {
      const res = await fetch(`${API_BASE_URL}/transactions/${txId}/investigate`);
      const data = await res.json();
      setSelectedTx(data);
    } catch (error) {
      console.error("Error fetching tx details:", error);
    }
  };

  if (loading) {
    return <div className="loading">Initializing Fraud Detection Engine...</div>;
  }

  // Generate chart data from actual recent transactions
  const chartData = recentTransactions.reverse().map(tx => ({
    time: new Date(tx.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}),
    risk: tx.hybrid_risk_score || tx.sql_risk_score,
    amount: tx.amount
  }));

  return (
    <div className="dashboard-container">
      <header className="header">
        <h1><ShieldAlert size={28} /> <span>Fraud</span>Engine</h1>
        <div style={{display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)'}}>
          <Activity size={18} /> Live Monitoring Active
        </div>
      </header>

      {summary && (
        <div className="summary-grid" style={{gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))'}}>
          <div className="summary-card">
            <h3>Total Analyzed</h3>
            <div className="value">{summary.total_transactions.toLocaleString()}</div>
          </div>
          <div className="summary-card">
            <h3>High Risk Alerts</h3>
            <div className="value danger">{summary.high_risk_transactions.toLocaleString()}</div>
          </div>
          <div className="summary-card">
            <h3>Velocity Attacks</h3>
            <div className="value warning">{summary.velocity_flags.toLocaleString()}</div>
          </div>
          <div className="summary-card">
            <h3>Impossible Travel</h3>
            <div className="value warning">{summary.travel_flags.toLocaleString()}</div>
          </div>
          <div className="summary-card">
            <h3>Foreign TX</h3>
            <div className="value warning">{summary.foreign_flags?.toLocaleString() || 0}</div>
          </div>
          <div className="summary-card">
            <h3>Late Night</h3>
            <div className="value warning">{summary.late_night_flags?.toLocaleString() || 0}</div>
          </div>
          <div className="summary-card">
            <h3>Micro Testing</h3>
            <div className="value warning">{summary.micro_flags?.toLocaleString() || 0}</div>
          </div>
          <div className="summary-card">
            <h3>Category Hopping</h3>
            <div className="value warning">{summary.hopping_flags?.toLocaleString() || 0}</div>
          </div>
        </div>
      )}

      <div className="main-content">
        <div className="panel">
          <h2 className="panel-header">Recent High-Risk Activity</h2>
          <div className="transaction-list">
            {transactions.map(tx => {
              const risk = tx.hybrid_risk_score || tx.sql_risk_score;
              const level = getRiskLevel(risk);
              
              return (
                <div 
                  key={tx.transaction_id} 
                  className={`transaction-item risk-${level}`}
                  onClick={() => handleTxClick(tx.transaction_id)}
                >
                  <div className="tx-info">
                    <span className="tx-id">{tx.transaction_id.substring(0, 8)}...</span>
                    <span className="tx-amount">{formatCurrency(tx.amount)}</span>
                    <div className="tx-badges">
                      {tx.rule_high_velocity && <span className="badge danger">Velocity</span>}
                      {tx.rule_amount_anomaly && <span className="badge danger">Value Anomaly</span>}
                      {tx.rule_impossible_travel && <span className="badge danger">Travel</span>}
                      {tx.rule_new_device && <span className="badge danger">New Device</span>}
                      {tx.rule_foreign_transaction && <span className="badge warning">Foreign</span>}
                      {tx.rule_late_night && <span className="badge warning">Late Night</span>}
                      {tx.rule_micro_testing && <span className="badge danger">Micro Test</span>}
                      {tx.rule_rapid_category_hopping && <span className="badge warning">Cat Hop</span>}
                    </div>
                  </div>
                  <div className="tx-score">
                    <span className={`score-value ${level}`}>{risk}</span>
                    <span className="score-label">Risk Score</span>
                    <span style={{fontSize: '0.7rem', color: 'var(--text-secondary)'}}>{formatDate(tx.timestamp)}</span>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        <div>
          <div className="panel" style={{marginBottom: '2rem'}}>
            <h2 className="panel-header">Risk Timeline (Recent 20)</h2>
            <div style={{height: '250px'}}>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="colorRisk" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="var(--danger-color)" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="var(--danger-color)" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
                  <XAxis dataKey="time" stroke="var(--text-secondary)" fontSize={12} />
                  <YAxis stroke="var(--text-secondary)" fontSize={12} domain={[0, 100]} />
                  <Tooltip 
                    contentStyle={{backgroundColor: 'var(--bg-secondary)', borderColor: 'var(--border-color)', borderRadius: '8px'}}
                    itemStyle={{color: 'var(--text-primary)'}}
                  />
                  <Area type="monotone" dataKey="risk" stroke="var(--danger-color)" fillOpacity={1} fill="url(#colorRisk)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
          
          <div className="panel">
            <h2 className="panel-header">System Status</h2>
            <div className="rule-list">
              <div className="rule-item">
                <ShieldCheck size={18} className="rule-icon inactive" />
                <span>SQL Deterministic Engine Online</span>
              </div>
              <div className="rule-item">
                <ShieldCheck size={18} className="rule-icon inactive" />
                <span>ML Isolation Forest Active</span>
              </div>
              <div className="rule-item">
                <ShieldCheck size={18} className="rule-icon inactive" />
                <span>Hybrid Scoring Model Enabled</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Investigation Modal */}
      {selectedTx && (
        <div className="modal-overlay" onClick={(e) => {
          if(e.target.className === 'modal-overlay') setSelectedTx(null);
        }}>
          <div className="modal-content">
            <div className="modal-header">
              <h2 style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
                <AlertCircle color="var(--danger-color)" /> 
                Transaction Investigation
              </h2>
              <button className="btn-close" onClick={() => setSelectedTx(null)}><X size={24} /></button>
            </div>
            
            <div className="modal-body">
              <div className="detail-grid">
                
                <div className="detail-section">
                  <h4>Transaction Details</h4>
                  <div className="detail-row">
                    <span className="detail-label">ID</span>
                    <span className="detail-value" style={{fontFamily:'monospace'}}>{selectedTx.transaction_id}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Account</span>
                    <span className="detail-value" style={{fontFamily:'monospace'}}>{selectedTx.account_id}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Amount</span>
                    <span className="detail-value" style={{fontWeight: 700, fontSize: '1.2rem'}}>{formatCurrency(selectedTx.amount)}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Time</span>
                    <span className="detail-value">{formatDate(selectedTx.timestamp)}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Distance from Prev</span>
                    <span className="detail-value">{Number(selectedTx.distance_km).toFixed(2)} km</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Travel Speed</span>
                    <span className="detail-value">{Number(selectedTx.travel_speed_kmh).toFixed(2)} km/h</span>
                  </div>
                </div>

                <div className="detail-section">
                  <h4>Risk Evaluation</h4>
                  
                  <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '1rem'}}>
                    <div style={{textAlign: 'center'}}>
                      <div className="score-value" style={{color: 'var(--accent-color)'}}>{selectedTx.sql_risk_score}</div>
                      <div className="score-label">SQL Score</div>
                    </div>
                    <div style={{textAlign: 'center'}}>
                      <div className="score-value" style={{color: '#9f7aea'}}>{selectedTx.ml_risk_score}</div>
                      <div className="score-label">ML Score</div>
                    </div>
                    <div style={{textAlign: 'center', backgroundColor: 'rgba(255,255,255,0.05)', padding: '0 1rem', borderRadius: '8px'}}>
                      <div className="score-value critical">{selectedTx.hybrid_risk_score}</div>
                      <div className="score-label">Hybrid Risk</div>
                    </div>
                  </div>

                  <div className="rule-list">
                    <div className="rule-item">
                      {selectedTx.rule_high_velocity ? <XOctagon size={18} className="rule-icon active"/> : <ShieldCheck size={18} className="rule-icon inactive"/>}
                      <span>High Velocity Attack (&gt;{selectedTx.velocity_count} tx/2min)</span>
                    </div>
                    <div className="rule-item">
                      {selectedTx.rule_amount_anomaly ? <XOctagon size={18} className="rule-icon active"/> : <ShieldCheck size={18} className="rule-icon inactive"/>}
                      <span>Value Anomaly (Z-Score: {Number(selectedTx.z_score || 0).toFixed(2)})</span>
                    </div>
                    <div className="rule-item">
                      {selectedTx.rule_impossible_travel ? <XOctagon size={18} className="rule-icon active"/> : <ShieldCheck size={18} className="rule-icon inactive"/>}
                      <span>Impossible Travel (&gt;1000 km/h)</span>
                    </div>
                    <div className="rule-item">
                      {selectedTx.rule_new_device ? <AlertTriangle size={18} className="rule-icon active" style={{color: 'var(--warning-color)'}}/> : <ShieldCheck size={18} className="rule-icon inactive"/>}
                      <span>Unrecognized Device</span>
                    </div>
                    <div className="rule-item">
                      {selectedTx.rule_foreign_transaction ? <AlertTriangle size={18} className="rule-icon active" style={{color: 'var(--warning-color)'}}/> : <ShieldCheck size={18} className="rule-icon inactive"/>}
                      <span>Foreign Transaction (Cross-border)</span>
                    </div>
                    <div className="rule-item">
                      {selectedTx.rule_late_night ? <AlertTriangle size={18} className="rule-icon active" style={{color: 'var(--warning-color)'}}/> : <ShieldCheck size={18} className="rule-icon inactive"/>}
                      <span>Late Night Transaction (1AM - 5AM)</span>
                    </div>
                    <div className="rule-item">
                      {selectedTx.rule_micro_testing ? <XOctagon size={18} className="rule-icon active"/> : <ShieldCheck size={18} className="rule-icon inactive"/>}
                      <span>Micro-Charge Testing (Small frequent charges)</span>
                    </div>
                    <div className="rule-item">
                      {selectedTx.rule_rapid_category_hopping ? <AlertTriangle size={18} className="rule-icon active" style={{color: 'var(--warning-color)'}}/> : <ShieldCheck size={18} className="rule-icon inactive"/>}
                      <span>Rapid Category Hopping</span>
                    </div>
                  </div>
                </div>

              </div>
              
              <div className="detail-section" style={{marginTop: '2rem'}}>
                <h4>Account History (Last 5)</h4>
                <div style={{display: 'flex', flexDirection: 'column', gap: '0.5rem'}}>
                  {selectedTx.account_history?.slice(0, 5).map(h => (
                    <div key={h.transaction_id} style={{display: 'flex', justifyContent: 'space-between', padding: '0.75rem', backgroundColor: 'var(--bg-color)', borderRadius: '8px'}}>
                      <span style={{fontFamily: 'monospace', color: 'var(--text-secondary)'}}>{h.transaction_id.substring(0,8)}</span>
                      <span>{formatDate(h.timestamp)}</span>
                      <span style={{fontWeight: 600}}>{formatCurrency(h.amount)}</span>
                      <span style={{color: h.status === 'SUCCESS' ? 'var(--success-color)' : 'var(--danger-color)'}}>{h.status}</span>
                    </div>
                  ))}
                </div>
              </div>

            </div>
          </div>
        </div>
      )}
    </div>
  );
}
