"""
初始化新闻事件数据库
从 finai.org.cn 爬取新闻并生成事件池
"""
import sys
import os
import time

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.database.news_event_db import news_event_db
from core.systems.news_event_generator import news_event_generator


def init_news_events():
    """初始化新闻事件数据库"""
    print("=" * 60)
    print("🚀 EchoPolis 新闻事件数据库初始化")
    print("=" * 60)
    
    # 1. 检查数据库状态
    print("\n📊 当前数据库状态:")
    stats = news_event_db.get_event_stats()
    print(f"   - 活跃新闻: {stats.get('active_news', 0)} 条")
    print(f"   - 活跃事件: {stats.get('active_events', 0)} 条")
    print(f"   - 历史新闻: {stats.get('total_news', 0)} 条")
    print(f"   - 历史事件: {stats.get('total_events', 0)} 条")
    
    # 2. 爬取新闻
    print("\n📰 正在从 finai.org.cn 爬取最新金融新闻...")
    print("   (使用 Selenium 加载 SPA 页面，请稍候...)")
    
    news_items = news_event_generator.fetch_news()
    print(f"\n   ✅ 获取到 {len(news_items)} 条新闻")
    
    if news_items:
        # 显示新闻
        print("\n   📋 新闻列表:")
        for i, news in enumerate(news_items, 1):
            sentiment_icon = {'positive': '📈', 'negative': '📉', 'neutral': '➖'}.get(news.sentiment, '➖')
            print(f"   {i:2d}. [{news.category:6s}] {sentiment_icon} {news.title_cn[:40]}...")
        
        # 保存新闻
        print("\n💾 保存新闻到数据库...")
        saved = news_event_db.save_news_batch([n.to_dict() for n in news_items])
        print(f"   ✅ 保存了 {saved} 条新闻")
    
    # 3. 显示市场状态
    print(f"\n📊 市场情绪: {news_event_generator.market_sentiment}")
    if news_event_generator.hot_topics:
        print(f"🔥 热门话题: {', '.join(news_event_generator.hot_topics[:5])}")
    
    # 保存市场状态
    news_event_db.save_market_status({
        'sentiment': news_event_generator.market_sentiment,
        'hot_topics': news_event_generator.hot_topics
    })
    
    # 4. 生成事件
    print("\n🎲 正在基于新闻生成游戏事件...")
    events = news_event_generator.generate_events_from_news()
    print(f"   ✅ 生成了 {len(events)} 条事件")
    
    if events:
        # 显示事件
        print("\n   📋 事件列表:")
        for i, event in enumerate(events, 1):
            print(f"   {i:2d}. {event.title}")
            print(f"       📰 来源: {event.source_news[:35]}...")
            print(f"       🏷️ 标签: {', '.join(event.tags[:3])}")
        
        # 保存事件
        print("\n💾 保存事件到数据库...")
        saved = news_event_db.save_events_batch([e.to_dict() for e in events])
        print(f"   ✅ 保存了 {saved} 条事件")
    
    # 5. 最终状态
    print("\n" + "=" * 60)
    print("✅ 初始化完成!")
    print("=" * 60)
    
    final_stats = news_event_db.get_event_stats()
    print(f"\n📊 最终数据库状态:")
    print(f"   - 活跃新闻: {final_stats.get('active_news', 0)} 条")
    print(f"   - 活跃事件: {final_stats.get('active_events', 0)} 条")
    print(f"   - 历史新闻: {final_stats.get('total_news', 0)} 条")
    print(f"   - 历史事件: {final_stats.get('total_events', 0)} 条")
    
    market = news_event_db.get_latest_market_status()
    if market:
        print(f"\n📈 市场状态:")
        print(f"   - 情绪: {market.get('sentiment', 'N/A')}")
        topics = market.get('hot_topics', [])
        if topics:
            print(f"   - 热门: {', '.join(topics[:5])}")
    
    return True


if __name__ == "__main__":
    try:
        init_news_events()
    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
