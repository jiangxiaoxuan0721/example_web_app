/**
 * Sidebar 组件 - 用于长页面的目录导航
 *
 * 功能：
 * - 显示 schema 中所有 blocks 的导航
 * - 点击可平滑滚动到对应 block
 * - 自动高亮当前可见的 block
 * - 支持折叠/展开
 */

import { useState, useEffect, useRef } from 'react';
import { useSchemaStore } from '../store/schemaStore';

interface SidebarProps {
  // 无需 props，直接从 store 获取 schema
}

interface NavigationItem {
  id: string;
  title: string;
}

export default function Sidebar({ }: SidebarProps) {
  const schema = useSchemaStore((state) => state.schema);

  if (!schema) {
    return null;
  }
  const [activeId, setActiveId] = useState<string>('');

  // 从 localStorage 读取初始折叠状态
  const [isCollapsed, setIsCollapsed] = useState(() => {
    const savedState = localStorage.getItem('pta-sidebar-collapsed');
    return savedState === 'true';
  });

  const observerRef = useRef<IntersectionObserver | null>(null);

  // 当折叠状态改变时，保存到 localStorage
  useEffect(() => {
    localStorage.setItem('pta-sidebar-collapsed', String(isCollapsed));
  }, [isCollapsed]);

  // 生成导航项列表
  const navItems: NavigationItem[] = schema.blocks
    ?.map(block => {
      // 尝试从 block 中获取标题，优先级：meta.title > block.id
      const title = (block as any).meta?.title || (block as any).props?.title || block.id;
      return {
        id: block.id,
        title: title
      };
    }) || [];

  // 使用 IntersectionObserver 自动高亮当前可见的 block
  useEffect(() => {
    if (navItems.length === 0) return;

    // 创建 IntersectionObserver
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setActiveId(entry.target.id);
          }
        });
      },
      {
        rootMargin: '-20% 0px -60% 0px', // 当元素在屏幕中间时触发
        threshold: 0
      }
    );

    // 观察所有 block 元素
    navItems.forEach((item) => {
      const element = document.getElementById(`block-${item.id}`);
      if (element) {
        observer.observe(element);
      }
    });

    observerRef.current = observer;

    // 清理
    return () => {
      observer.disconnect();
    };
  }, [navItems]);

  // 点击导航项，平滑滚动到对应 block 并高亮
  const scrollToBlock = (blockId: string) => {
    const element = document.getElementById(`block-${blockId}`);
    if (element) {
      element.scrollIntoView({
        behavior: 'smooth',
        block: 'center'
      });

      // 添加高亮动画
      element.style.transition = 'background-color 0.3s ease';
      element.style.backgroundColor = '#fff3cd';
      element.style.borderRadius = '4px';
      element.style.padding = '8px';

      // 2秒后移除高亮
      setTimeout(() => {
        element.style.backgroundColor = '';
        element.style.borderRadius = '';
        element.style.padding = '';
      }, 2000);
    }
  };

  // 如果没有导航项，不显示 sidebar
  if (navItems.length === 0) {
    return null;
  }

  return (
    <div className={`pta-sidebar ${isCollapsed ? 'pta-sidebar--collapsed' : ''}`}>
      {/* 折叠按钮 */}
      <button
        className="pta-sidebar__toggle"
        onClick={() => setIsCollapsed(!isCollapsed)}
        title={isCollapsed ? '展开导航' : '折叠导航'}
      >
        <span className={`pta-sidebar__toggle-icon ${isCollapsed ? 'pta-sidebar__toggle-icon--collapsed' : ''}`}>
          ◀
        </span>
      </button>

      {/* 导航内容 */}
      <div className="pta-sidebar__content">
        <div className="pta-sidebar__header">
          <h3 className="pta-sidebar__title">目录</h3>
        </div>

        <nav className="pta-sidebar__nav">
          <ul className="pta-sidebar__list">
            {navItems.map((item) => (
              <li key={item.id} className="pta-sidebar__item">
                <button
                  className={`pta-sidebar__link ${activeId === item.id ? 'pta-sidebar__link--active' : ''}`}
                  onClick={() => scrollToBlock(item.id)}
                >
                  <span className="pta-sidebar__link-text">{item.title}</span>
                  {activeId === item.id && <span className="pta-sidebar__link-indicator">●</span>}
                </button>
              </li>
            ))}
          </ul>
        </nav>

        {/* 底部信息 */}
        <div className="pta-sidebar__footer">
          <span className="pta-sidebar__footer-text">
            共 {navItems.length} 个区块
          </span>
        </div>
      </div>
    </div>
  );
}
