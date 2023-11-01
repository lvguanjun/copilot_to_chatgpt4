# COPILOT TO CHATGPT4

## 说明

本项目简单的将 `copilot-chat` 的请求代理，并提供类似于 `chatgpt` 的接口。基于本服务，可以使用具备 `copilot` 权限的 `github token` 获得使用 `chatgpt` 感受。并且当前 `copilot-chat` 开放 `gpt4 model`，意味着可以无限制使用 `chatgpt4` 聊天。

**重要：此操作目前观测极易被禁用 `copilot` 权限，除非你的 `github token` 非常多，否则慎重使用**

## 使用

### 演示demo

1. 点击[链接](https://chat.3211000.xyz)直达 BetterChatGPT 演示站点

2. 配置 API 端点为：`https://chatserver.3211000.xyz/v1/chat/completions`, API 密钥为你的 `github token`

![api](readme/api.png)

3. 根据个人喜好配置其他选项，选择 `gpt-4` 模型，即可开始聊天

[**关于 `GitHub token` 获取**](#其他)

**本后端服务未存取任何聊天记录及 `github token`，仅作为请求代理，若有疑虑建议自行部署**

### 个人部署

#### 1. 虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 2. 启动服务

```bash
uvicorn main:app --host 127.0.0.1 --port 8000
```

#### 3. 使用

1. 获取 `github token`，可以使用 zhile 大佬提供的接口：[get_token](https://cocopilot.org/copilot/token)
2. 将部署的后端服务接入可以使用代理网站的 `chatgpt` 客户端，如 [BetterChatGpt](https://github.com/ztjhz/BetterChatGPT)

当然，也可以直接使用 `curl` 请求：

```bash
curl --location 'http://127.0.0.1:8080/v1/chat/completions' \
--header 'Authorization: Bearer ghu_xxx' \
--data '{"messages": [
        {   "role": "system",
            "content": "You are an AI programming assistant."
        },
        {
            "role": "user",
            "content": "hello"
        }
    ],
    "model": "gpt-4",
}'
```

## 其他

感谢 zhile 大佬提供的 `github token` 获取接口：[get_token](https://cocopilot.org/copilot/token)