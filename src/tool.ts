import { tool } from '@langchain/core/tools';
import { z } from 'zod';

export const calculatorTool = tool(
  // 第一个参数：工具的执行函数
  async ({ a, b, operation }) => {
    let result: number;
    switch (operation) {
      case 'add':      result = a + b; break;
      case 'subtract': result = a - b; break;
      case 'multiply': result = a * b; break;
      case 'divide':
        if (b === 0) return '错误：除数不能为零';
        result = a / b;
        break;
      default:
        return `错误：不支持的操作 "${operation}"`;
    }
    return `${a} ${operation} ${b} = ${result}`;
  },
  // 第二个参数：工具的元信息
  {
    name: 'calculator',
    description: '对两个数字执行四则运算（加、减、乘、除）',
    schema: z.object({
      a: z.number().describe('第一个数字'),
      b: z.number().describe('第二个数字'),
      operation: z
        .enum(['add', 'subtract', 'multiply', 'divide'])
        .describe('要执行的操作：add（加）、subtract（减）、multiply（乘）、divide（除）'),
    }),
  }
);

export const getCurrentTimeTool = tool(
  async () => {
    const now = new Date();
    return `当前时间不好说：${now.toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' })}`;
  },
  {
    name: 'get_current_time',
    description: '获取当前的系统时间（北京时间）',
    schema: z.object({}),  // 空 schema → LLM 知道不用传参
  }
);

