"""Interactive chat client for Media Search API."""

import json
from urllib.request import Request, urlopen
from urllib.error import URLError

BASE_URL = "http://localhost:8000"


def request(path: str, data: dict = None):
    """Make HTTP POST request."""
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}

    body = json.dumps(data).encode("utf-8")
    req = Request(url, data=body, headers=headers, method="POST")

    try:
        with urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except URLError as e:
        print(f"连接失败: {e}")
        return None


def print_result(query: str, data: dict):
    """Print search results in chat format."""
    results = data.get("results", [])
    total = data.get("total", 0)

    print(f"\n{'='*50}")
    print(f"🔍 查询: {query}")
    print(f"📊 找到 {total} 个结果")
    print(f"{'='*50}")

    if not results:
        print("没有找到相关结果")
        return

    for i, r in enumerate(results, 1):
        score_bar = "█" * int(r["score"] * 10) + "░" * (10 - int(r["score"] * 10))
        print(f"\n[{i}] {r['path']}")
        print(f"    相似度: {r['score']:.2%} |{score_bar}|")
        print(f"    类型: {r['media_type']}/{r['format']}")
        print(f"    描述: {r['description'][:50]}...")

    print(f"\n{'='*50}\n")


def print_help():
    """Print help message."""
    print("""
╔══════════════════════════════════════════════════════╗
║          Media Search 聊天式搜索客户端               ║
╠══════════════════════════════════════════════════════╣
║  命令:                                                ║
║    <搜索内容>    - 进行语义搜索                       ║
║    /help        - 显示帮助                           ║
║    /health      - 检查服务器状态                      ║
║    /quit        - 退出程序                           ║
║    /top <数字>  - 设置每次返回的结果数 (默认5)       ║
╚══════════════════════════════════════════════════════╝
""")


def main():
    """Main chat loop."""
    print_help()

    top_k = 5
    print(f"\n💡 当前设置: 每次返回 {top_k} 个结果")
    print("💡 输入搜索内容开始搜索，输入 /help 查看命令\n")

    while True:
        try:
            user_input = input("你> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n👋 再见!")
            break

        if not user_input:
            continue

        # Handle commands
        if user_input.startswith("/"):
            cmd = user_input.split()[0].lower()

            if cmd == "/quit" or cmd == "/exit":
                print("👋 再见!")
                break
            elif cmd == "/help":
                print_help()
            elif cmd == "/health":
                print("\n检查服务器状态...")
                url = f"{BASE_URL}/health"
                try:
                    with urlopen(Request(url, method="GET")) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                    print(f"✅ 服务器正常")
                    print(f"   模型: {data['model']}")
                    print(f"   索引条目: {data['index_items']}")
                except URLError as e:
                    print(f"❌ 连接失败: {e}")
            elif cmd == "/top":
                try:
                    top_k = int(user_input.split()[1])
                    print(f"✅ 已设置: 每次返回 {top_k} 个结果")
                except (ValueError, IndexError):
                    print(f"❌ 用法: /top <数字> (当前: {top_k})")
            else:
                print(f"❓ 未知命令: {cmd}")

        else:
            # Perform search
            print(f"\n🔄 搜索中: \"{user_input}\"...")
            data = request("/search", {"query": user_input, "top_k": top_k})
            if data:
                print_result(user_input, data)


if __name__ == "__main__":
    main()
