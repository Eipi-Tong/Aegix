import openai
import json

# 假设这是你已经封装好的 Aegix 客户端
class AegixRuntime:
    def execute(self, command: str):
        # 这里模拟 Aegix 的返回
        # 实际代码中，你会调用 Aegix 的 API 并获取 stdout/exit_code
        print(f"--- [Aegix 执行中]: {command} ---")
        return {
            "stdout": f"Successfully executed: {command}",
            "stderr": "",
            "exit_code": 0
        }

# 1. 定义工具 Schema (告诉 OpenAI 你能做什么)
tools = [
    {
        "type": "function",
        "function": {
            "name": "aegix_bash",
            "description": "在安全的沙箱环境执行 bash 命令",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "要执行的命令, 例如 'ls -la'"}
                },
                "required": ["command"]
            }
        }
    }
]

client = openai.OpenAI(api_key="your_key_here")
aegix = AegixRuntime()

def run_agent(user_prompt):
    # 初始消息队列
    messages = [{"role": "user", "content": user_prompt}]

    # --- 步骤 2: 请求模型 ---
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    
    response_message = response.choices[0].message
    
    # --- 步骤 3: 判断是否需要调用工具 ---
    if response_message.tool_calls:
        messages.append(response_message) # 把模型的意图加入对话历史
        
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            if function_name == "aegix_bash":
                # --- 步骤 4: 真正的执行 (接入 Aegix) ---
                result = aegix.execute(args['command'])
                
                # --- 步骤 5: 回填结果 (Tool Output) ---
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps(result) # 包含 stdout, exit_code 等
                })
        
        # --- 步骤 6: 让模型总结结果 ---
        final_response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        return final_response.choices[0].message.content

    return response_message.content

# 测试
print(run_agent("帮我看看当前目录下有哪些文件？"))