# Java 开发者转 Python (Playwright) 极速上手指南

欢迎来到 Python 的世界！作为一名 Java 后端工程师，您会发现 Python 的很多概念其实只是换了个名字。本文档旨在帮助您利用现有的 Java 知识快速理解本项目的技术栈。

## 1. 核心概念映射 (Concept Mapping)

| 概念 | Java (Spring Boot / Selenium) | Python (本项目) | 备注 |
| :--- | :--- | :--- | :--- |
| **依赖管理** | `Maven (pom.xml)` / `Gradle` | `pip (requirements.txt)` | Python 没有像 Maven 那样复杂的生命周期管理，`pip install` 直接把包下载到环境里。 |
| **虚拟环境** | (无直接对应，类似 Project SDK) | `venv` / `conda` | Java 通常全局安装 JDK，Python 习惯为每个项目创建一个隔离的 `venv`，避免依赖冲突。 |
| **入口点** | `public static void main(String[] args)` | `if __name__ == "__main__":` | Python 脚本自上而下执行，这个判断是为了防止被 import 时执行代码。 |
| **包/模块** | `package com.example.demo;` | 文件夹内含 `__init__.py` | 任何包含 `__init__.py` 的文件夹都是一个 Package。 |
| **类型系统** | 强类型 (Static Typing) | 动态类型 (Dynamic) + Type Hints | Python 3.5+ 支持 `def func(a: int) -> str:`，但这只是提示，运行时不会报错（除非用 mypy 检查）。 |
| **异步编程** | `CompletableFuture` / `Reactive` | `async` / `await` | Playwright 强烈推荐使用异步模式。Python 的 `await` 必须在 `async def` 函数内使用。 |

## 2. Playwright vs Selenium (Java)

如果您用过 Selenium，Playwright 会让您感觉“鸟枪换炮”。

*   **Selenium (Java):**
    *   需要下载对应版本的 `chromedriver.exe`。
    *   `WebDriver driver = new ChromeDriver();`
    *   显式等待满天飞：`wait.until(ExpectedConditions.elementToBeClickable(...))`
*   **Playwright (Python):**
    *   自动管理浏览器二进制文件 (`playwright install`)。
    *   **自动等待 (Auto-wait):** 点击某个按钮时，Playwright 会自动等待元素出现在 DOM 中、可见、不被遮挡、停止动画。**这是最大的爽点，告别 `Thread.sleep`。**
    *   **上下文 (Context):** `Browser` (浏览器实例) -> `Context` (隐身窗口) -> `Page` (标签页)。Context 之间完全隔离，非常适合多账号模拟。

## 3. 项目结构说明

本项目的结构借鉴了 Java 项目的规范性，但保持了 Python 的简洁：

```text
AI自媒体运营/
├── src/                    # 类似 src/main/java
│   ├── __init__.py
│   ├── main.py             # 启动类
│   ├── browser/            # 浏览器控制逻辑 (Service Layer)
│   ├── content/            # 内容生成逻辑 (Service Layer)
│   └── utils/              # 工具类 (Util)
├── tests/                  # 类似 src/test/java
├── user_data/              # 存放 Cookie 等运行时数据 (类似本地 H2 DB 文件)
├── docs/                   # 文档
├── requirements.txt        # 类似 pom.xml
└── .env                    # 配置文件 (类似 application.properties)
```

## 4. 常用命令速查

*   **安装依赖:** `pip install -r requirements.txt` (等同于 `mvn install`)
*   **运行脚本:** `python src/main.py` (等同于 `java -jar ...`)
*   **运行测试:** `pytest` (等同于 `mvn test`)

## 5. 给 Java 开发者的建议

1.  **忘掉 Getter/Setter:** Python 直接访问属性 `obj.field` 是 Pythonic 的做法，需要封装时再用 `@property`。
2.  **拥抱推导式:** `List<String> names = list.stream().map(User::getName).collect(Collectors.toList());` 在 Python 里就是 `names = [u.name for u in users]`。
3.  **注意缩进:** Java 靠花括号 `{}`，Python 靠缩进。缩进错了逻辑就变了。
