import type { OpenCodePlugin } from @opencode-ai/plugin;

const plugin: OpenCodePlugin = {
  name: opencode-skillful,
  hooks: {
    config: async () => {
      // Skill management hooks
      return {};
    },
  },
};

export default plugin;
export const setup = () => {};
