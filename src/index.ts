import { agent } from "./agents";

// const stream = await agent.stream(
//   { messages: [{ role: 'user', content: '帮我计算 128 乘以 47 等于多少' }] },
//   { ...config, streamMode: 'messages' },
// );

// for await (const [message] of stream) {
//   console.log(message);  // 会看到各种类型的消息
// }

// 开启thing后，stream会新增thinking的block
// message.content === [
//   { type: 'thinking', thinking: '用户让我算 128 × 47，我需要用计算器工具...' },
//   { type: 'tool_use', ... },
//   { type: 'text', text: '128 × 47 = 6016' },
// ]


async function printStream(stream: AsyncIterable<[any, any]>) {
  for await (const [message] of stream) {
    // 只处理 AI 消息，跳过 tool / human
    if (message?._getType?.() === 'ai') {
      // 情况 1：content 是字符串
      if (typeof message.content === 'string' && message.content) {
        process.stdout.write(message.content);
      }
      // 情况 2：content 是数组，遍历找 text block
      else if (Array.isArray(message.content)) {
        for (const block of message.content) {
            // 增加对thinking的处理
            if (block.type === 'thinking' && block.thinking) {
                process.stdout.write(`\x1b[90m[思考] ${block.thinking}\x1b[0m`);
            }
          if (block.type === 'text' && block.text) {
            process.stdout.write(block.text);
          }
        }
      }
    }
  }
}

// agent 通过checkpointer(记忆存储器)存储会话，memeorysaver按照thread_id存储对话历史，同一个thread_id的所有消息被累积存储
// agent每次都能看到之前的完整对话
const config = { configurable: { thread_id: 'session-1' } };
// 第一轮：计算器
await agent.stream(
  { messages: [{ role: 'user', content: '帮我计算 128 乘以 47 等于多少' }] },
  { ...config, streamMode: 'messages' },
);
// Agent 回复："128 × 47 = 6016"

// 第二轮：故意质疑
await agent.stream(
  { messages: [{ role: 'user', content: '算的不对吧' }] },
  { ...config, streamMode: 'messages' },
);
// Agent 会回顾之前的计算，重新审视结果
// 因为它"记得"上一轮自己算了什么


