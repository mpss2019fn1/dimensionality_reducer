import argparse
import logging
import time
from operator import itemgetter

import pandas
import plotly
import plotly.graph_objs as go
import umap
from gensim.models import Doc2Vec

from util.cluster_parser import ClusterParser
from util.filesystem_validators import AccessibleDirectory, AccessibleTextFile

cluster_mapping = {}
entity_relations = {}


def main():
    logging.basicConfig(format='%(asctime)s : [%(threadName)s] %(levelname)s : %(message)s', level=logging.INFO)
    parser = _initialize_parser()
    args = parser.parse_args()
    _initialize_cluster_mapping(args.clusters)
    global entity_relations
    entity_relations = ClusterParser.entity_relations(args.entity_relations)
    relation_clusters = _inverse_cluster_mapping(cluster_mapping)
    model = _load_model(args.input)
    doc_embeddings = model.docvecs.vectors_docs
    embedding = _apply_umap(doc_embeddings)

    d = pandas.DataFrame(embedding, columns=["c1", "c2", "c3"])
    d["word"] = [w for w in model.docvecs.doctags]
    d["cluster_id"] = [relation_clusters[w] if w in relation_clusters else -1 for w in model.docvecs.doctags]
    d["tooltip"] = d.apply(build_tooltip, axis=1)
    layout = dict(title="Doc2Vec embeddings",
                  yaxis=dict(zeroline=False),
                  xaxis=dict(zeroline=False),
                  hovermode="closest")

    data = []
    for cluster_id in cluster_mapping:
        indices = [index for index, value in enumerate(d["word"]) if value in cluster_mapping[cluster_id]]
        cluster_color = get_color(cluster_id)

        cluster = go.Scatter3d(
            x=itemgetter(*indices)(d["c1"]),
            y=itemgetter(*indices)(d["c2"]),
            z=itemgetter(*indices)(d["c3"]),
            name=f"CLUSTER #{cluster_id} ({len(cluster_mapping[cluster_id])} entities)",
            mode="markers",
            marker=dict(
                color=cluster_color,
                size=6,
                line=dict(
                    width=0.5,
                ),
                opacity=0.75
            ),
            text=itemgetter(*indices)(d["tooltip"])
        )

        data.append(cluster)

    fig = go.Figure(data=data, layout=layout)
    chart = plotly.offline.plot(fig, filename=f"{args.output}/doc2vec-umap.html")


def _initialize_parser():
    general_parser = argparse.ArgumentParser(description="Clustering trained entity embeddings")
    general_parser.add_argument("--input", help="gensim model containing embedded entities",
                                action=AccessibleTextFile, required=True)
    general_parser.add_argument("--clusters", help="Textfiles containing cluster information",
                                action=AccessibleTextFile, required=True)
    general_parser.add_argument("--output", help="Desired location for storing dimensionality reduced resukts",
                                required=True, action=AccessibleDirectory)
    general_parser.add_argument("--entity-relations", help="Path to directory containing relation info about entities",
                                required=True, action=AccessibleDirectory)

    return general_parser


def _initialize_cluster_mapping(cluster_file):
    global cluster_mapping
    logging.info(f"building cluster mapping...")
    start_time = time.perf_counter()

    cluster_mapping = ClusterParser.cluster_mappings(cluster_file)

    end_time = time.perf_counter()
    logging.info(f"cluster mapping built after {end_time - start_time} seconds")


def _load_model(model_file):
    logging.info(f"loading embeddings model...")
    start_time = time.perf_counter()

    model = Doc2Vec.load(model_file)

    end_time = time.perf_counter()
    logging.info(f"embeddings model loaded after {end_time - start_time} seconds")
    return model


def _apply_umap(embedding):
    logging.info(f"applying umap...")
    start_time = time.perf_counter()

    transformed = umap.UMAP(n_components=3).fit_transform(embedding)

    end_time = time.perf_counter()
    logging.info(f"umap applied after {end_time - start_time} seconds")
    return transformed


def build_tooltip(row):
    full_string = ["Word: ", row["word"]]
    if row["cluster_id"] >= 0:
        full_string.extend(
            ["<br><br>", f"<b>Cluster relations ({len(cluster_mapping[row['cluster_id']])} entities):</b><br>"])
        full_string.append("<br>".join(f"{relation.as_html()}" if row["cluster_id"] != 1 else "" for relation in
                                       entity_relations[row["cluster_id"]]))
    return "".join(full_string)


def get_color(cluster_id):
    r = (35 + cluster_id * 7) % 255
    g = (133 + cluster_id * 13) % 255
    b = (289 + cluster_id * 23) % 255

    return f"rgb({r}, {g}, {b})"


def _inverse_cluster_mapping(id_entity_mapping):
    inverse = {}
    for id in id_entity_mapping:
        for entity in id_entity_mapping[id]:
            inverse[entity] = id

    return inverse


if __name__ == "__main__":
    main()
