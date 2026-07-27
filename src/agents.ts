import { ChatAnthropic } from '@langchain/anthropic';
import { createDeepAgent } from 'deepagents';
import { MemorySaver } from '@langchain/langgraph';
import { calculatorTool, getCurrentTimeTool } from './tool'

const model = new ChatAnthropic({
  model: process.env.MODEL_NAME || 'qwen3.7-plus',
  anthropicApiKey: process.env.ANTHROPIC_API_KEY,
  anthropicApiUrl: process.env.ANTHROPIC_BASE_URL,
  streaming: true, // invoke:同步调用，等完整回复；stream: 流式调用，逐token返回
  maxTokens: 10000,
  thinking: { // 让模型在回复前先进行内部推理
    type: 'enabled',
    budget_tokens: 5000,
  },
});


export const agent = createDeepAgent({
  model,
  tools: [calculatorTool, getCurrentTimeTool],
  systemPrompt: '你是一个乐于助人的 AI 助手。当用户需要进行数学计算或查询时间时，请使用相应的工具来完成。',
  checkpointer: new MemorySaver(),
});


