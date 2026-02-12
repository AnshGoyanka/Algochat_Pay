import { useState, useEffect } from 'react'

function App() {
  const [metrics, setMetrics] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchMetrics()
  }, [])

  const fetchMetrics = async () => {
    try {
      const response = await fetch('/api/demo/pitch-summary')
      const data = await response.json()
      setMetrics(data)
    } catch (error) {
      console.error('Failed to fetch metrics:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Hero Section */}
      <header className="bg-slate-900/50 backdrop-blur-sm border-b border-algorand/20">
        <div className="container mx-auto px-6 py-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-algorand rounded-lg flex items-center justify-center">
                <span className="text-2xl">💬</span>
              </div>
              <div>
                <h1 className="text-3xl font-bold text-white">AlgoChat Pay</h1>
                <p className="text-gray-400">Your Campus Wallet on WhatsApp</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <span className="px-4 py-2 bg-algorand/20 text-algorand rounded-lg text-sm font-medium">
                Powered by Algorand
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-12">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <StatCard
            title="Active Students"
            value={metrics?.top_metrics?.[0]?.details?.total_users || "500"}
            subtitle={metrics?.top_metrics?.[0]?.value || "77% activation"}
            icon="👥"
          />
          <StatCard
            title="Daily Active"
            value={metrics?.top_metrics?.[1]?.value || "387"}
            subtitle="Consistent engagement"
            icon="⚡"
          />
          <StatCard
            title="Total Transactions"
            value="2,500+"
            subtitle="98% success rate"
            icon="💳"
          />
          <StatCard
            title="Settlement Time"
            value="4.5s"
            subtitle="Algorand blockchain"
            icon="⏱️"
          />
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
          <FeatureCard
            title="💸 Instant Payments"
            description="Send ALGO via WhatsApp text. No app download required."
            demo="pay 10 ALGO to +1234567890"
          />
          <FeatureCard
            title="🍽️ Bill Splitting"
            description="Smart contracts ensure fair splits and automatic settlement."
            demo="split 40 ALGO dinner with @sarah @mike @emma"
          />
          <FeatureCard
            title="🎫 NFT Tickets"
            description="Event tickets as blockchain NFTs. No more fake screenshots."
            demo="buy ticket TechFest 2026"
          />
          <FeatureCard
            title="🎯 Fundraising"
            description="Transparent campaigns with on-chain tracking."
            demo="create fund Library Renovation goal 500 ALGO"
          />
        </div>

        {/* Elevator Pitch */}
        {metrics?.elevator_pitch && (
          <div className="bg-gradient-to-r from-algorand/10 to-blue-500/10 border border-algorand/30 rounded-2xl p-8 mb-12">
            <h2 className="text-2xl font-bold text-white mb-4">🚀 Elevator Pitch</h2>
            <p className="text-lg text-gray-300">{metrics.elevator_pitch}</p>
          </div>
        )}

        {/* Key Insights */}
        {metrics?.top_insights && (
          <div className="bg-slate-800/50 border border-slate-700 rounded-2xl p-8">
            <h2 className="text-2xl font-bold text-white mb-6">💡 Key Insights</h2>
            <div className="space-y-4">
              {metrics.top_insights.map((insight: string, index: number) => (
                <div key={index} className="flex items-start space-x-3">
                  <span className="text-algorand text-xl">✓</span>
                  <p className="text-gray-300">{insight}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-slate-900/50 border-t border-slate-800 mt-12">
        <div className="container mx-auto px-6 py-8 text-center text-gray-400">
          <p>Built with ❤️ for Algorand Hackathon | Powered by FastAPI + React + PyTeal</p>
        </div>
      </footer>

      {loading && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center">
          <div className="bg-slate-800 rounded-lg p-8 text-center">
            <div className="animate-spin w-12 h-12 border-4 border-algorand border-t-transparent rounded-full mx-auto mb-4"></div>
            <p className="text-white">Loading metrics...</p>
          </div>
        </div>
      )}
    </div>
  )
}

function StatCard({ title, value, subtitle, icon }: any) {
  return (
    <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6 hover:border-algorand/50 transition-all">
      <div className="text-3xl mb-3">{icon}</div>
      <div className="text-3xl font-bold text-white mb-1">{value}</div>
      <div className="text-sm text-gray-400 mb-2">{title}</div>
      <div className="text-xs text-algorand">{subtitle}</div>
    </div>
  )
}

function FeatureCard({ title, description, demo }: any) {
  return (
    <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6 hover:border-algorand/50 transition-all">
      <h3 className="text-xl font-bold text-white mb-3">{title}</h3>
      <p className="text-gray-300 mb-4">{description}</p>
      <div className="bg-slate-900 border border-slate-600 rounded-lg p-3 font-mono text-sm text-algorand">
        {demo}
      </div>
    </div>
  )
}

export default App
