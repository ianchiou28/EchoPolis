'use client'

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-neutral-900 p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Echopolis 仪表盘</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* AI化身状态 */}
          <div className="bg-neutral-800 p-6 rounded-xl">
            <h2 className="text-xl font-semibold mb-4">AI化身状态</h2>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>健康值:</span>
                <span className="text-green-400">85/100</span>
              </div>
              <div className="flex justify-between">
                <span>精力值:</span>
                <span className="text-blue-400">72/100</span>
              </div>
              <div className="flex justify-between">
                <span>幸福感:</span>
                <span className="text-yellow-400">68/100</span>
              </div>
            </div>
          </div>
          
          {/* 财务状况 */}
          <div className="bg-neutral-800 p-6 rounded-xl">
            <h2 className="text-xl font-semibold mb-4">财务状况</h2>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>信用点:</span>
                <span className="text-green-400">50,000 CP</span>
              </div>
              <div className="flex justify-between">
                <span>启示结晶:</span>
                <span className="text-purple-400">5 IC</span>
              </div>
              <div className="flex justify-between">
                <span>净资产:</span>
                <span className="text-blue-400">50,000 CP</span>
              </div>
            </div>
          </div>
          
          {/* 回响交互 */}
          <div className="bg-neutral-800 p-6 rounded-xl">
            <h2 className="text-xl font-semibold mb-4">回响交互</h2>
            <div className="space-y-4">
              <input
                type="text"
                placeholder="发送回响给AI化身..."
                className="w-full px-4 py-2 bg-neutral-700 rounded-lg"
              />
              <button className="w-full bg-primary-600 hover:bg-primary-700 px-4 py-2 rounded-lg">
                发送回响
              </button>
            </div>
          </div>
        </div>
        
        {/* 最近事件 */}
        <div className="mt-8 bg-neutral-800 p-6 rounded-xl">
          <h2 className="text-xl font-semibold mb-4">最近事件</h2>
          <div className="space-y-3">
            <div className="border-l-4 border-blue-500 pl-4">
              <p className="font-medium">市场波动</p>
              <p className="text-sm text-neutral-400">股市出现小幅波动，建议保持观望</p>
            </div>
            <div className="border-l-4 border-green-500 pl-4">
              <p className="font-medium">工作晋升</p>
              <p className="text-sm text-neutral-400">你的AI化身获得了工作晋升机会</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}