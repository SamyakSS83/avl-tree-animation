from flask import Flask, render_template, request, jsonify
import networkx as nx
import matplotlib
# Set non-interactive backend before importing pyplot
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

class AVLNode:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None
        self.height = 1

class AVLTree:
    def __init__(self):
        self.root = None

    def height(self, node):
        return node.height if node else 0

    def get_balance(self, node):
        return self.height(node.left) - self.height(node.right) if node else 0

    def right_rotate(self, z):
        y = z.left
        T3 = y.right
        y.right = z
        z.left = T3
        z.height = 1 + max(self.height(z.left), self.height(z.right))
        y.height = 1 + max(self.height(y.left), self.height(y.right))
        return y

    def left_rotate(self, z):
        y = z.right
        T2 = y.left
        y.left = z
        z.right = T2
        z.height = 1 + max(self.height(z.left), self.height(z.right))
        y.height = 1 + max(self.height(y.left), self.height(y.right))
        return y

    def insert(self, node, key):
        if not node:
            return AVLNode(key)
        if key < node.key:
            node.left = self.insert(node.left, key)
        else:
            node.right = self.insert(node.right, key)
        node.height = 1 + max(self.height(node.left), self.height(node.right))
        balance = self.get_balance(node)

        # LL Case
        if balance > 1 and key < node.left.key:
            return self.right_rotate(node)
        # RR Case
        if balance < -1 and key > node.right.key:
            return self.left_rotate(node)
        # LR Case
        if balance > 1 and key > node.left.key:
            node.left = self.left_rotate(node.left)
            return self.right_rotate(node)
        # RL Case
        if balance < -1 and key < node.right.key:
            node.right = self.right_rotate(node.right)
            return self.left_rotate(node)

        return node

    def get_min_value_node(self, node):
        current = node
        # Find the leftmost leaf
        while current.left is not None:
            current = current.left
        return current

    def delete(self, node, key):
        # Standard BST delete
        if not node:
            return node

        # Find the node to be deleted
        if key < node.key:
            node.left = self.delete(node.left, key)
        elif key > node.key:
            node.right = self.delete(node.right, key)
        else:
            # Node with only one child or no child
            if node.left is None:
                return node.right
            elif node.right is None:
                return node.left

            # Node with two children
            # Get inorder successor (smallest in right subtree)
            temp = self.get_min_value_node(node.right)
            
            # Copy the inorder successor's content to this node
            node.key = temp.key
            
            # Delete the inorder successor
            node.right = self.delete(node.right, temp.key)

        # If tree had only one node, return
        if node is None:
            return node

        # Update height
        node.height = 1 + max(self.height(node.left), self.height(node.right))
        
        # Get the balance factor
        balance = self.get_balance(node)
        
        # Balance the tree if needed
        
        # Left Left Case
        if balance > 1 and self.get_balance(node.left) >= 0:
            return self.right_rotate(node)
            
        # Left Right Case
        if balance > 1 and self.get_balance(node.left) < 0:
            node.left = self.left_rotate(node.left)
            return self.right_rotate(node)
            
        # Right Right Case
        if balance < -1 and self.get_balance(node.right) <= 0:
            return self.left_rotate(node)
            
        # Right Left Case
        if balance < -1 and self.get_balance(node.right) > 0:
            node.right = self.right_rotate(node.right)
            return self.left_rotate(node)
            
        return node

    def visualize_step(self, case, step):
        """Generates an image for the current tree state and saves it to static/demo_<case>_<step>.png"""
        G = nx.DiGraph()
        pos = {}

        def traverse(node, x=0, y=0, dx=1):
            if not node:
                return
            G.add_node(node.key)
            pos[node.key] = (x, y)
            if node.left:
                G.add_edge(node.key, node.left.key)
                traverse(node.left, x - dx, y - 1, dx / 2)
            if node.right:
                G.add_edge(node.key, node.right.key)
                traverse(node.right, x + dx, y - 1, dx / 2)
        
        traverse(self.root)
        
        plt.figure(figsize=(8, 5))
        if G.nodes():  # Only try to draw if there are nodes
            nx.draw(G, pos, with_labels=True, node_color='lightblue', 
                   node_size=2000, edge_color='gray', font_size=12, font_weight='bold')
        
        # Create a more specific file path and ensure directory exists
        file_name = f"demo_{case}_{step}.png"
        static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)
            
        img_path = os.path.join(static_dir, file_name)
        plt.savefig(img_path)
        plt.close()
        
        # Return just the filename, not the full path
        return f"/static/{file_name}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/demo/<case>')
def demo(case):
    # Create a new AVL tree for each demo
    tree = AVLTree()
    steps = []
    
    if case == "ll-insert":
        # Clear LL case: Insert in descending order 50, 40, 30
        keys = [50, 40, 30]
        operation = "insert"
        explanation = ("LL Rotation (Right Rotation): Inserting keys in descending order (50, 40, 30) "
                       "creates a left-heavy imbalance. The balance factor at node 50 becomes +2 "
                       "after inserting 30. Since 30 is inserted into the left subtree of the left "
                       "child (40), this is a Left-Left case. The tree rebalances with a single right rotation.")
    elif case == "rr-insert":
        # Clear RR case: Insert in ascending order 10, 20, 30
        keys = [10, 20, 30]
        operation = "insert"
        explanation = ("RR Rotation (Left Rotation): Inserting keys in ascending order (10, 20, 30) "
                       "creates a right-heavy imbalance. The balance factor at node 10 becomes -2 "
                       "after inserting 30. Since 30 is inserted into the right subtree of the right "
                       "child (20), this is a Right-Right case. The tree rebalances with a single left rotation.")
    elif case == "lr-insert":
        # Clear LR case: First left child, then right grandchild
        keys = [50, 30, 40]
        operation = "insert"
        explanation = ("LR Rotation (Left-Right Rotation): Inserting 50, then 30, then 40 creates "
                       "a left-heavy tree, but the imbalance is caused by a right child (40) of the left subtree (30). "
                       "This requires two rotations: first a left rotation on the left child (30), which transforms "
                       "it to an LL case, and then a right rotation on the root (50).")
    elif case == "rl-insert":
        # Clear RL case: First right child, then left grandchild
        keys = [10, 30, 20]
        operation = "insert"
        explanation = ("RL Rotation (Right-Left Rotation): Inserting 10, then 30, then 20 creates "
                       "a right-heavy tree, but the imbalance is caused by a left child (20) of the right subtree (30). "
                       "This requires two rotations: first a right rotation on the right child (30), which transforms "
                       "it to an RR case, and then a left rotation on the root (10).")
    elif case == "ll-delete":
        # More pronounced LL case after deletion
        keys = [50, 30, 70, 20, 40, 60, 80, 10, 25]
        delete_key = 60
        operation = "delete"
        explanation = ("LL Rotation after Deletion: After building a balanced tree and deleting node 60, "
                       "the right subtree becomes shorter, causing the overall tree to be left-heavy. "
                       "The balance factor at node 50 becomes +2. Since the left subtree is left-heavy (LL case), "
                       "the tree rebalances using a single right rotation.")
    elif case == "rr-delete":
        # More pronounced RR case after deletion
        keys = [50, 30, 70, 20, 40, 60, 80, 35, 45]
        delete_key = 20
        operation = "delete"
        explanation = ("RR Rotation after Deletion: After building a balanced tree and deleting node 20, "
                       "the left subtree becomes shorter, causing the overall tree to be right-heavy. "
                       "The balance factor at node 50 becomes -2. Since the right subtree is right-heavy (RR case), "
                       "the tree rebalances using a single left rotation.")
    elif case == "lr-delete":
        # Clearer LR case after deletion
        keys = [50, 20, 70, 10, 30, 60, 80, 25, 35]
        delete_key = 10
        operation = "delete"
        explanation = ("LR Rotation after Deletion: After building a balanced tree and deleting node 10, "
                       "the left subtree of the left child becomes shorter. This creates an imbalance at node 50, "
                       "but the left subtree is right-heavy (node 30). This is an LR case requiring two rotations: "
                       "first a left rotation on node 20, followed by a right rotation on node 50.")
    elif case == "rl-delete":
        # Clearer RL case after deletion
        keys = [50, 30, 80, 20, 40, 70, 90, 60, 75]
        delete_key = 90
        operation = "delete"
        explanation = ("RL Rotation after Deletion: After building a balanced tree and deleting node 90, "
                       "the right subtree of the right child becomes shorter. This creates an imbalance at node 50, "
                       "but the right subtree is left-heavy (node 70). This is an RL case requiring two rotations: "
                       "first a right rotation on node 80, followed by a left rotation on node 50.")
    else:
        return 'Invalid demo case', 404

    # Insert all keys one by one
    for i, key in enumerate(keys):
        tree.root = tree.insert(tree.root, key)
        if operation == "insert" and i < len(keys) - 1:  # Don't save last step for insert to show it separately
            img_path = tree.visualize_step(case, i)
            steps.append({
                "img": img_path,
                "description": f"Inserted {key}",
                "state": "normal"
            })
        elif operation == "delete":  # For delete, show all insertions
            img_path = tree.visualize_step(case, i)
            steps.append({
                "img": img_path,
                "description": f"Inserted {key}",
                "state": "normal"
            })
    
    # For delete operations, show the tree before deletion
    if operation == "delete":
        img_path = tree.visualize_step(case, "before_delete")
        steps.append({
            "img": img_path,
            "description": f"Tree before deleting {delete_key}",
            "state": "before"
        })
        
        # Perform the deletion
        tree.root = tree.delete(tree.root, delete_key)
        
        # Show the tree after deletion but before balancing
        img_path = tree.visualize_step(case, "after_delete")
        steps.append({
            "img": img_path,
            "description": f"Tree after deleting {delete_key} (imbalanced)",
            "state": "imbalanced"
        })
        
        # Show the tree after balancing
        img_path = tree.visualize_step(case, "after_balance")
        steps.append({
            "img": img_path,
            "description": f"Tree after rebalancing with {case.split('-')[0].upper()} rotation",
            "state": "balanced"
        })
    else:
        # For insert operations, show the tree before the final insertion
        img_path = tree.visualize_step(case, "before_final")
        steps.append({
            "img": img_path, 
            "description": f"Tree before inserting {keys[-1]}", 
            "state": "before"
        })
        
        # Create a special step to show the insertion that causes imbalance
        temp_tree = AVLTree()
        for key in keys[:-1]:  # All keys except the last
            temp_tree.root = temp_tree.insert(temp_tree.root, key)
        # Only insert the last key without balancing to show imbalance
        if temp_tree.root:
            if keys[-1] < temp_tree.root.key:
                temp_tree.root.left = temp_tree.insert(temp_tree.root.left, keys[-1])
            else:
                temp_tree.root.right = temp_tree.insert(temp_tree.root.right, keys[-1])
            # Update height but don't balance
            temp_tree.root.height = 1 + max(temp_tree.height(temp_tree.root.left), 
                                          temp_tree.height(temp_tree.root.right))
        
        img_path = temp_tree.visualize_step(case, "imbalanced")
        steps.append({
            "img": img_path, 
            "description": f"Tree after inserting {keys[-1]} (imbalanced)", 
            "state": "imbalanced"
        })
        
        # Show the final balanced tree
        img_path = tree.visualize_step(case, "balanced")
        steps.append({
            "img": img_path, 
            "description": f"Tree after rebalancing with {case.split('-')[0].upper()} rotation", 
            "state": "balanced"
        })

    return render_template('demo.html', explanation=explanation, steps=steps, demo_case=case, operation=operation)

if __name__ == '__main__':
    app_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(app_dir, "static")
    templates_dir = os.path.join(app_dir, "templates")
    
    # Ensure directories exist
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    # Set static folder explicitly
    app.static_folder = static_dir
    app.template_folder = templates_dir
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)
