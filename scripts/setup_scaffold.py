import os

dirs = [
    "data/pdf",
    "data/txt",
    "data/md",
    "src/agent/nodes",
    "src/rag",
    "src/personas",
    "src/escalation",
    "src/sentiment",
    "src/config",
    "src/utils",
    "src/orchestration/agents",
    "ui/components",
    "tests/unit",
    "tests/integration",
    "scripts"
]

files = [
    "src/__init__.py",
    "src/agent/__init__.py",
    "src/agent/nodes/__init__.py",
    "src/rag/__init__.py",
    "src/personas/__init__.py",
    "src/escalation/__init__.py",
    "src/sentiment/__init__.py",
    "src/config/__init__.py",
    "src/utils/__init__.py",
    "src/orchestration/__init__.py",
    "src/orchestration/agents/__init__.py",
    "tests/__init__.py",
    "tests/unit/__init__.py",
    "tests/integration/__init__.py",
    "__init__.py"
]

for d in dirs:
    path = os.path.join("c:\\Users\\pvenk\\Downloads\\Adsparkx AI", d)
    os.makedirs(path, exist_ok=True)
    print(f"Created directory: {path}")

for f in files:
    path = os.path.join("c:\\Users\\pvenk\\Downloads\\Adsparkx AI", f)
    if not os.path.exists(path):
        with open(path, "w") as file:
            pass
        print(f"Created file: {path}")
