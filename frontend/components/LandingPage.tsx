'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { useRouter } from 'next/navigation'
import { Brain, Zap, Target, ArrowRight, Play } from 'lucide-react'

export function LandingPage() {
  const router = useRouter()
  const [isHovered, setIsHovered] = useState(false)

  const features = [
    {
      icon: Brain,
      title: '一个回响',
      description: '体验选择的力量，见证微小意图如何引发不可预测的连锁反应',
      color: 'text-primary-400',
    },
    {
      icon: Target,
      title: '一个沙盒',
      description: '在零风险环境中，演练真实世界可能面临的金融决策',
      color: 'text-secondary-400',
    },
    {
      icon: Zap,
      title: '一座桥梁',
      description: '连接玩家情感、金融知识与银行服务的桥梁',
      color: 'text-accent-400',
    },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-neutral-900 via-neutral-800 to-neutral-900">
      {/* 背景动画 */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary-500/10 rounded-full blur-3xl animate-pulse-slow" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-secondary-500/10 rounded-full blur-3xl animate-pulse-slow" />
      </div>

      {/* 导航栏 */}
      <nav className="relative z-10 flex items-center justify-between p-6 lg:px-8">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-lg" />
          <span className="text-xl font-bold text-gradient">Echopolis</span>
        </div>
        
        <div className="flex items-center space-x-4">
          <button
            onClick={() => router.push('/login')}
            className="px-4 py-2 text-neutral-300 hover:text-white transition-colors"
          >
            登录
          </button>
          <button
            onClick={() => router.push('/register')}
            className="btn-primary"
          >
            注册
          </button>
        </div>
      </nav>

      {/* 主要内容 */}
      <main className="relative z-10 flex flex-col items-center justify-center min-h-[calc(100vh-80px)] px-6 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="max-w-4xl mx-auto"
        >
          {/* 标题 */}
          <h1 className="text-5xl lg:text-7xl font-bold mb-6">
            <span className="text-gradient">回声都市</span>
            <br />
            <span className="text-neutral-200">Echopolis</span>
          </h1>

          {/* 副标题 */}
          <p className="text-xl lg:text-2xl text-neutral-400 mb-8 max-w-2xl mx-auto">
            在一个由你复刻的AI城邦中，发出决策的回响，聆听命运的回声
          </p>

          {/* 特性介绍 */}
          <div className="grid md:grid-cols-3 gap-8 mb-12">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: index * 0.2 }}
                className="card text-left"
              >
                <feature.icon className={`w-8 h-8 ${feature.color} mb-4`} />
                <h3 className="text-lg font-semibold text-white mb-2">
                  {feature.title}
                </h3>
                <p className="text-neutral-400 text-sm">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>

          {/* CTA按钮 */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            <button
              onClick={() => router.push('/register')}
              onMouseEnter={() => setIsHovered(true)}
              onMouseLeave={() => setIsHovered(false)}
              className="group relative px-8 py-4 bg-gradient-to-r from-primary-600 to-secondary-600 text-white rounded-xl font-semibold text-lg transition-all duration-300 hover:scale-105 hover:shadow-2xl hover:shadow-primary-500/25"
            >
              <span className="flex items-center space-x-2">
                <Play className="w-5 h-5" />
                <span>开始你的回声之旅</span>
                <ArrowRight 
                  className={`w-5 h-5 transition-transform duration-300 ${
                    isHovered ? 'translate-x-1' : ''
                  }`} 
                />
              </span>
            </button>

            <button
              onClick={() => router.push('/demo')}
              className="px-8 py-4 border border-neutral-600 text-neutral-300 rounded-xl font-semibold text-lg hover:border-neutral-500 hover:text-white transition-all duration-300"
            >
              观看演示
            </button>
          </motion.div>

          {/* 统计数据 */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.8 }}
            className="mt-16 grid grid-cols-3 gap-8 max-w-md mx-auto"
          >
            <div className="text-center">
              <div className="text-2xl font-bold text-primary-400">1000+</div>
              <div className="text-sm text-neutral-500">AI化身</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-secondary-400">50M+</div>
              <div className="text-sm text-neutral-500">决策回响</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-accent-400">99%</div>
              <div className="text-sm text-neutral-500">用户满意度</div>
            </div>
          </motion.div>
        </motion.div>
      </main>

      {/* 页脚 */}
      <footer className="relative z-10 text-center py-8 text-neutral-500 text-sm">
        <p>&copy; 2024 Echopolis. 为工商银行创新大赛设计.</p>
      </footer>
    </div>
  )
}