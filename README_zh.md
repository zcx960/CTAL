# 基于LLM的加密货币趋势分析器 📈

## 描述
本项目是一个命令行界面（CLI）和Streamlit Web UI应用程序，允许用户：
1. 从交易所（目前为币安）获取加密货币的K线数据。
2. 提供一个大型语言模型（LLM）的API密钥和可选的API端点。
3. 基于K线数据，通过LLM生成趋势分析和建议。

## 特性
- **命令行界面（CLI）**：用于直接交互。
- **Streamlit Web UI**：提供图形化用户界面，方便操作。
- **币安数据源**：从币安获取加密货币K线数据。
- **可配置LLM**：支持用户提供自己的LLM API密钥和端点。
- **Docker支持**：提供Dockerfile，方便容器化部署。
- **单元测试**：包含核心逻辑的单元测试。

## 项目结构
- `app.py`: 包含核心应用程序逻辑（CLI、数据获取、LLM集成、分析）。
- `streamlit_app.py`: Streamlit Web UI的实现代码。
- `test_app.py`: 核心功能的单元测试。
- `Dockerfile`: 用于构建应用程序的Docker镜像。
- `requirements.txt`: Python项目依赖项列表。
- `README.md`: 项目的英文版说明文档。
- `README_zh.md`: 项目的中文版说明文档（本文档）。

## 先决条件
- Python 3.9+
- Docker (可选, 如果使用Docker进行部署)

## 安装与设置
1.  **克隆仓库** (如果适用):
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```
2.  **创建虚拟环境** (推荐):
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/macOS
    # venv\Scripts\activate  # Windows
    ```
3.  **安装依赖**:
    ```bash
    pip install -r requirements.txt
    ```

## 运行应用程序

### CLI模式
1.  运行以下命令启动CLI应用程序:
    ```bash
    python app.py
    ```
2.  根据提示输入:
    *   **加密货币符号** (例如: `BTCUSDT`)
    *   **K线周期** (例如: `1h`, `1d`, `1w`)
    *   **您的LLM API密钥** (此密钥敏感，请注意保密)
    *   **LLM API URL (可选)** (如果留空，将使用 `app.py` 中定义的 `DEFAULT_LLM_API_URL`)

### Streamlit Web UI模式
1.  运行以下命令启动Streamlit Web UI:
    ```bash
    streamlit run streamlit_app.py
    ```
2.  应用程序将在您的默认浏览器中打开。
3.  通过侧边栏输入以下信息:
    *   **加密货币符号**
    *   **K线周期**
    *   **您的LLM API密钥** (输入时会自动隐藏)
    *   **LLM API URL (可选)**
4.  点击 "Analyze Trends 🚀" 按钮。
5.  K线数据和LLM分析结果将显示在主区域。

## 使用Docker构建和运行

1.  **构建Docker镜像**:
    ```bash
    docker build -t crypto-analyzer .
    ```
2.  **运行Streamlit Web UI容器**:
    ```bash
    docker run -it -p 8501:8501 crypto-analyzer
    ```
    在浏览器中访问 `http://localhost:8501`。
3.  **在Docker中运行CLI模式** (可选):
    ```bash
    docker run -it crypto-analyzer python app.py
    ```
    (注意: CLI模式在 `docker run` 时直接交互可能不便，通常Web UI是Docker部署的首选。)

## 运行测试
运行单元测试:
```bash
python -m unittest test_app.py
```

## LLM配置
- 您需要提供自己兼容OpenAI API格式的大型语言模型（LLM）的API密钥。
- 默认的LLM API URL (`DEFAULT_LLM_API_URL`) 在 `app.py` 中定义，但可以在CLI或Web UI中被覆盖。
- 分析的质量和具体建议将取决于所使用的LLM模型和提示工程。

## 已知限制
- **币安API**: 从沙箱环境或受限地理位置访问币安API可能会遇到问题（例如，IP地理封锁）。
- **LLM分析**: 分析的质量和建议的有效性高度依赖于所用LLM的能力以及`app.py`中`get_trend_analysis`函数内提示的构建方式。
- **错误处理**: 已实现基本的错误处理，但可以进一步扩展以覆盖更多场景。
- **数据量**: 为了管理LLM提示的大小和成本，K线数据在传递给LLM之前可能会被截断（默认为最新的30条记录）。

## 手动Web UI测试

### 1. 启动应用程序
*   **测试用例**: 运行 `streamlit run streamlit_app.py`。
*   **预期结果**: 应用程序应在Web浏览器中打开，没有即时错误。

### 2. 初始UI元素
*   **测试用例**: 观察加载的页面。
*   **预期结果**:
    *   显示正确的标题。
    *   侧边栏包含符号、周期、API密钥和API URL的输入字段。
    *   "Analyze Trends 🚀"按钮可见。
    *   K线数据和LLM分析的占位符区域应正确显示或为空。

### 3. 有效输入和成功路径（模拟）
*   **测试用例**:
    *   输入一个已知的有效加密货币符号 (例如: "BTCUSDT")。
    *   选择一个K线周期。
    *   输入一个（占位符/虚拟）LLM API密钥。
    *   点击 "Analyze Trends 🚀"。
*   **预期结果**:
    *   应出现数据获取和分析的加载指示器。
    *   由于币安API可能被阻止：K线数据部分应显示获取到的数据（如果连接成功）或关于API失败的明确错误消息（例如，“从币安获取数据时出错...”）。
    *   如果K线数据获取失败：LLM分析部分应指示无法继续分析或显示适当的消息。
    *   如果K线数据获取成功（假设情况）：LLM分析部分随后应尝试分析。使用虚拟API密钥，它应显示与LLM API密钥相关的错误（例如，“LLM API密钥无效或分析失败。”）。

### 4. 缺少API密钥
*   **测试用例**: 将LLM API密钥字段留空，然后点击 "Analyze Trends 🚀"。
*   **预期结果**: 应显示错误消息，如 "LLM API Key is required..."。不应继续获取数据。

### 5. 缺少符号
*   **测试用例**: 将符号字段留空，然后点击 "Analyze Trends 🚀"。
*   **预期结果**: 应显示警告/错误消息，如 "Please enter a cryptocurrency symbol"。不应继续获取数据。

### 6. 交互和错误消息清晰度
*   **测试用例**: 触发各种错误条件（如上所述）。
*   **预期结果**: 错误消息应清晰地显示在UI的适当部分。占位符应正确更新。
```
