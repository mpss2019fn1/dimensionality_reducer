import argparse
import umap
import pandas
import logging
from gensim.models import Doc2Vec

from util.cluster_parser import ClusterParser
from util.filesystem_validators import AccessibleDirectory, AccessibleTextFile

import plotly
import plotly.graph_objs as go

cluster_mapping = {}


def main():
    logging.basicConfig(level=logging.DEBUG)
    parser = _initialize_parser()
    args = parser.parse_args()

    logging.info("Start processing cluster information")
    global cluster_mapping
    cluster_mapping = ClusterParser.cluster_mappings(args.clusters)
    logging.info("Finished processing cluster information")

    logging.info("Starting up -> loading model")
    model = Doc2Vec.load(args.input)
    logging.info("Model successfully loaded")
    doc_embeddings = model.docvecs.vectors_docs
    logging.info("Starting model transformation using UMAP")
    embedding = umap.UMAP(n_components=2).fit_transform(doc_embeddings)
    logging.info("Model successfully transformed")
    d = pandas.DataFrame(embedding, columns=['c1', 'c2'])
    d['word'] = [w for w in model.docvecs.doctags]
    d['tooltip'] = d.apply(build_tooltip, axis=1)

    trace = go.Scattergl(
        x=d['c1'],
        y=d['c2'],
        name='Embedding',
        mode='markers',

        marker=dict(
            color=list(map(get_color, d['word'])),
            size=6,
            line=dict(
                width=0.5,
            ),
            opacity=0.75
        ),
        text=d['tooltip']
    )

    layout = dict(title='Doc2Vec embeddings',
                  yaxis=dict(zeroline=False),
                  xaxis=dict(zeroline=False),
                  hovermode='closest')

    fig = go.Figure(data=[trace], layout=layout)
    chart = plotly.offline.plot(fig, filename=f'{args.output}/doc2vec-umap.html')


def _initialize_parser():
    general_parser = argparse.ArgumentParser(description='Clustering trained entity embeddings')
    general_parser.add_argument("--input", help='gensim model containing embedded entities',
                                action=AccessibleTextFile, required=True)
    general_parser.add_argument("--clusters", help='Textfiles containing cluster information',
                                action=AccessibleTextFile, required=True)
    general_parser.add_argument("--output", help='Desired location for storing dimensionality reduced resukts',
                                required=True, action=AccessibleDirectory)

    return general_parser


def build_tooltip(row):
    full_string = ['<b>Word:</b> ', row['word'],
                   '<br>']
    return ''.join(full_string)


def get_color(entity):
    if entity not in cluster_mapping:
        return "rgb(0,0,0)"
    cluster_id = cluster_mapping[entity]

    r = (35 + cluster_id * 7) % 255
    g = (133 + cluster_id * 13) % 255
    b = (289 + cluster_id * 23) % 255

    return f"rgb({r}, {g}, {b})"


if __name__ == "__main__":
    main()
