# -*- coding: utf-8 -*-
import json
import networkx as nx
from pyvis.network import Network
import os
import uuid
import threading
import time


def create_graph_html_from_json(json_data, static_folder, delete_after_seconds=300):
    """
    Erzeugt aus einem JSON-Objekt eine Graph-HTML-Datei im static-Ordner mit individuellem Namen.
    Löscht die Datei nach delete_after_seconds automatisch wieder.
    Gibt den relativen Pfad zur HTML-Datei zurück.
    """
    NODE_SIZE = 30

    # === Graph erstellen ===
    G = nx.DiGraph()

    # === Nodes hinzufügen ===
    for node in json_data["nodes"]:
        node_id = node["id"]
        G.add_node(node_id, size=NODE_SIZE)

    # === Edges hinzufügen ===
    for edge in json_data["edges"]:
        src = edge["from"]
        dst = edge["to"]
        label = edge.get("label", "")
        G.add_edge(src, dst, label=label)

    # === Visualisierung ===
    net = Network(height="500px", width="500px", directed=True)
    net.from_nx(G)
    net.toggle_physics(False)

    # Individueller Dateiname
    unique_id = uuid.uuid4().hex
    filename = f"graph_{unique_id}.html"
    save_path = os.path.join(static_folder, filename)
    net.show(save_path, notebook=False)

    # Timer zum Löschen der Datei
    def delete_file_later(path, delay):
        def delete():
            time.sleep(delay)
            try:
                os.remove(path)
                print(f"{path} wurde gelöscht.")
            except Exception as e:
                print(f"Fehler beim Löschen von {path}: {e}")
        threading.Thread(target=delete, daemon=True).start()

    delete_file_later(save_path, delete_after_seconds)

    return filename  # z.B. "graph_abc123.html"


# Beispielaufruf:
# with open(JSON_PATH, "r") as f:
#     data = json.load(f)
# static_folder = os.path.join(application.root_path, "static")
# html_filename = create_graph_html_from_json(data, static_folder)
# # Im Template: url_for('static', filename=html_filename)