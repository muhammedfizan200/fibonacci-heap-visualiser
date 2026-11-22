import streamlit as st
from dataclasses import dataclass, field
from typing import Optional

@dataclass(eq=False)
class Node:
    key: int
    uid: int
    parent: Optional["Node"] = None
    children: list = field(default_factory=list)
    degree: int = 0
    mark: bool = False

class FibonacciHeap:
    """Fibonacci heap using Python lists for root and child circular lists."""
    def __init__(self):
        self.roots = []
        self.minimum = None
        self._next_uid = 0

    def _new_node(self, key):
        node = Node(key, self._next_uid)
        self._next_uid += 1
        return node

    def insert(self, key):
        node = self._new_node(key)
        self.roots.append(node)
        if self.minimum is None or node.key < self.minimum.key:
            self.minimum = node
        return node

    def find_min(self):
        return self.minimum.key if self.minimum else None

    def _walk(self, start):
        """Yield every node in a forest without revisiting nodes."""
        stack = list(start)
        seen = set()
        while stack:
            node = stack.pop()
            if node.uid in seen:
                continue
            seen.add(node.uid)
            yield node
            stack.extend(node.children)

    def find_node(self, key):
        return next((n for n in self._walk(self.roots) if n.key == key), None)

    def _link(self, child, parent):
        child.parent = parent
        child.mark = False
        parent.children.append(child)
        parent.degree = len(parent.children)

    def _consolidate(self):
        degree_table = {}
        old_roots = list(self.roots)
        self.roots = []
        for node in old_roots:
            node.parent = None

        for x in old_roots:
            d = x.degree
            while d in degree_table:
                y = degree_table.pop(d)
                if y.key < x.key:
                    x, y = y, x
                self._link(y, x)
                d = x.degree
            degree_table[d] = x

        self.roots = list(degree_table.values())
        self.minimum = min(self.roots, key=lambda n: n.key) if self.roots else None

    def extract_min(self):
        z = self.minimum
        if z is None:
            return None
        for child in z.children:
            child.parent = None
            child.mark = False
            self.roots.append(child)
        z.children = []
        z.degree = 0
        self.roots.remove(z)
        if self.roots:
            self._consolidate()
        else:
            self.minimum = None
        return z.key

    def _cut(self, node, parent):
        parent.children.remove(node)
        parent.degree = len(parent.children)
        node.parent = None
        node.mark = False
        self.roots.append(node)

    def _cascading_cut(self, node):
        parent = node.parent
        if parent is not None:
            if not node.mark:
                node.mark = True
            else:
                self._cut(node, parent)
                self._cascading_cut(parent)

    def decrease_key(self, old_key, new_key):
        node = self.find_node(old_key)
        if node is None:
            return False, "Node not found."
        if new_key > node.key:
            return False, "The new key must be less than or equal to the old key."
        node.key = new_key
        parent = node.parent
        if parent is not None and node.key < parent.key:
            self._cut(node, parent)
            self._cascading_cut(parent)
        if self.minimum is None or node.key < self.minimum.key:
            self.minimum = node
        return True, f"Changed {old_key} to {new_key}."

    def delete(self, key):
        node = self.find_node(key)
        if node is None:
            return False, "Node not found."
        # Use a value strictly smaller than every current key so this node
        # becomes the unique minimum before extraction.
        all_keys = [n.key for n in self._walk(self.roots)]
        sentinel = min(all_keys) - 1
        ok, message = self.decrease_key(key, sentinel)
        if not ok:
            return False, message
        removed = self.extract_min()
        return True, f"Deleted node with key {key}."

    def all_nodes(self):
        return list(self._walk(self.roots))

    def validate(self):
        if self.minimum is None:
            return not self.roots
        nodes = self.all_nodes()
        if self.minimum not in self.roots:
            return False
        if self.minimum.key != min(n.key for n in nodes):
            return False
        for node in nodes:
            if node.degree != len(node.children):
                return False
            for child in node.children:
                if child.parent is not node or child.key < node.key:
                    return False
        return True

def graphviz_forest(heap):
    if not heap.roots:
        return 'digraph Heap { label="Empty Fibonacci Heap"; labelloc="t"; empty [label="Heap is empty", shape=box]; }'
    lines = [
        'digraph Heap {',
        'graph [rankdir=TB, bgcolor="transparent", nodesep=0.45, ranksep=0.7];',
        'node [shape=circle, style="filled", fillcolor="#e8f0fe", color="#4169a1", fontname="Arial", fontsize=12];',
        'edge [color="#718096", penwidth=1.4];'
    ]
    for node in heap.all_nodes():
        attrs = []
        if node is heap.minimum:
            attrs = ['fillcolor="#ffd166"', 'color="#d97706"', 'penwidth=2.5']
        elif node.mark:
            attrs = ['fillcolor="#fce7f3"', 'color="#be185d"']
        label = f'{node.key}\\n(d={node.degree})'
        lines.append(f'n{node.uid} [label="{label}"{", " + ", ".join(attrs) if attrs else ""}];')
        for child in node.children:
            lines.append(f'n{node.uid} -> n{child.uid};')
    lines.append('}')
    return "\n".join(lines)

st.set_page_config(page_title="Fibonacci Heap Visualizer", page_icon="🌳", layout="wide")
st.title("🌳 Fibonacci Heap Visualizer")
st.caption("An interactive Data Structures & Algorithms project — explore heap operations and the tree structure.")

if "heap" not in st.session_state:
    st.session_state.heap = FibonacciHeap()
if "history" not in st.session_state:
    st.session_state.history = ["Create a heap, then insert a few values to get started."]
if "last_message" not in st.session_state:
    st.session_state.last_message = ""

heap = st.session_state.heap

with st.sidebar:
    st.header("Heap operations")
    with st.form("insert_form", clear_on_submit=True):
        insert_value = st.number_input("Value to insert", step=1, value=10, key="insert_value")
        insert_submit = st.form_submit_button("＋ Insert")
    if insert_submit:
        heap.insert(int(insert_value))
        st.session_state.last_message = f"Inserted {int(insert_value)}."
        st.session_state.history.insert(0, st.session_state.last_message)

    with st.form("extract_form"):
        st.write("**Delete minimum**")
        extract_submit = st.form_submit_button("− Extract minimum")
    if extract_submit:
        removed = heap.extract_min()
        st.session_state.last_message = "Heap is empty." if removed is None else f"Extracted minimum: {removed}."
        st.session_state.history.insert(0, st.session_state.last_message)

    with st.form("decrease_form", clear_on_submit=True):
        st.write("**Decrease key**")
        old_value = st.number_input("Existing key", step=1, value=10, key="old_value")
        new_value = st.number_input("New smaller key", step=1, value=5, key="new_value")
        decrease_submit = st.form_submit_button("↓ Decrease key")
    if decrease_submit:
        ok, msg = heap.decrease_key(int(old_value), int(new_value))
        st.session_state.last_message = msg
        st.session_state.history.insert(0, msg)

    with st.form("delete_form", clear_on_submit=True):
        st.write("**Delete any node**")
        delete_value = st.number_input("Key to delete", step=1, value=10, key="delete_value")
        delete_submit = st.form_submit_button("✕ Delete node")
    if delete_submit:
        ok, msg = heap.delete(int(delete_value))
        st.session_state.last_message = msg
        st.session_state.history.insert(0, msg)

    st.divider()
    if st.button("↻ Reset heap", use_container_width=True):
        st.session_state.heap = FibonacciHeap()
        st.session_state.history = ["Heap reset."]
        st.session_state.last_message = "Heap reset."
        st.rerun()

left, right = st.columns([2, 1])
with left:
    st.subheader("Heap structure")
    st.graphviz_chart(graphviz_forest(heap), use_container_width=True)
    st.caption("Yellow = minimum node · Pink = marked node · d = number of children")
with right:
    st.subheader("Heap information")
    st.metric("Minimum", "—" if heap.find_min() is None else heap.find_min())
    st.metric("Total nodes", len(heap.all_nodes()))
    st.metric("Root nodes", len(heap.roots))
    st.metric("Heap valid", "Yes ✓" if heap.validate() else "Check structure")

st.subheader("Root list")
if heap.roots:
    st.write("  ·  ".join(f"**{n.key}** (degree {n.degree})" for n in heap.roots))
else:
    st.info("The root list is empty.")

st.subheader("Operation log")
for entry in st.session_state.history[:8]:
    st.write("• " + entry)

with st.expander("Algorithm complexity (amortized)"):
    st.markdown("""
| Operation | Time complexity |
|---|---:|
| Insert | O(1) |
| Find minimum | O(1) |
| Decrease key | O(1) amortized |
| Merge / meld | O(1) |
| Extract minimum | O(log n) amortized |
| Delete | O(log n) amortized |

A Fibonacci heap achieves these bounds using lazy consolidation, linking trees of equal degree during extract-min, and cuts/cascading cuts during decrease-key.
""")

with st.expander("How to use this visualizer"):
    st.markdown("""
1. Insert several integers to create a collection of separate root trees.
2. Extract the minimum to trigger **consolidation** — trees with equal degrees are linked.
3. Decrease a key to see a node move to the root list when the heap-order property is broken.
4. A node can become **marked** after losing its first child; losing another child triggers a cascading cut.
5. Delete any node using the delete operation.

Duplicate keys are allowed; when a key occurs more than once, the first matching node found is changed or deleted.
""")
