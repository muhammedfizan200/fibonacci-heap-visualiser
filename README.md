# Fibonacci Heap Visualizer

An interactive **Fibonacci Heap** visualizer built with Python and Streamlit for a Data Structures and Algorithms (DAA) college project.

## Features

- Insert a key
- View the heap as a tree/forest
- Find the minimum (shown in the information panel)
- Extract/delete the minimum
- Decrease a key
- Delete any node
- View root count, node count, degree and operation history
- Visual indication of the minimum node and marked nodes
- Displays amortized time complexities

## Requirements

- Python 3.9 or newer
- Streamlit

## Run locally

Open a terminal in this project folder and run:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Streamlit will print a local URL (usually `http://localhost:8501`). Open it in your browser.

## Upload to GitHub

1. Create a new **public** repository on GitHub (for example, `fibonacci-heap-visualizer`).
2. Extract this ZIP file.
3. Open a terminal in the extracted project folder.
4. Run:

```bash
git init
git add .
git commit -m "Initial Fibonacci Heap Visualizer project"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/fibonacci-heap-visualizer.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your GitHub username.

## How the implementation works

The heap stores a list of root nodes. Each node stores its key, parent, children, degree and mark flag. During `extract_min`, roots of equal degree are linked until the root list has at most one tree of each degree. During `decrease_key`, a node that violates heap order is cut from its parent; cascading cuts are used to preserve the Fibonacci-heap structure.

This is an educational implementation. Root and child lists are represented by Python lists rather than circular doubly linked lists, so the visualizer focuses on the Fibonacci heap operations and their tree structure rather than pointer-level implementation details.

## Complexity (amortized)

| Operation | Complexity |
|---|---:|
| Insert | O(1) |
| Find minimum | O(1) |
| Decrease key | O(1) |
| Extract minimum | O(log n) |
| Delete | O(log n) |
