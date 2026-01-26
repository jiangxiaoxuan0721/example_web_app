/** 多实例 Schema Store - 支持存储和访问多个实例的 schema */

import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import type { UISchema } from '../types/schema';

interface MultiInstanceStore {
  // 所有实例的 schema
  instances: Map<string, UISchema>;

  // Actions
  setInstance: (instanceId: string, schema: UISchema) => void;
  getInstance: (instanceId: string) => UISchema | null;
  removeInstance: (instanceId: string) => void;
  clearAll: () => void;
}

export const useMultiInstanceStore = create<MultiInstanceStore>()(
  subscribeWithSelector((set, get) => ({
    instances: new Map(),

    setInstance: (instanceId, schema) => {
      set((state) => {
        const newInstances = new Map(state.instances);
        newInstances.set(instanceId, schema);
        return { instances: newInstances };
      });
    },

    getInstance: (instanceId) => {
      const state = get();
      return state.instances.get(instanceId) || null;
    },

    removeInstance: (instanceId) => {
      set((state) => {
        const newInstances = new Map(state.instances);
        newInstances.delete(instanceId);
        return { instances: newInstances };
      });
    },

    clearAll: () => set({ instances: new Map() })
  }))
);
