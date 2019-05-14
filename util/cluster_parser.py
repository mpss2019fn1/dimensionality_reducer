import re
from pathlib import Path

from entity_relations.relation import Relation


class ClusterParser:
    __cluster_regex = re.compile(r"\[\[CLUSTER (?P<id>\d+)]]", re.IGNORECASE)
    __cluster_id_regex = re.compile(r"enriched_cluster_(?P<cluster_id>\d+)\.txt")
    __entity_relation_regex = re.compile(r"^Relation:\s(?P<name>[\w|\s]+)\s(?P<relative_occurrence>\d+\.\d+)%$")
    __entity_relation_value_regex = re.compile(r"^\s+↳\s(?P<relative_occurrence>\d+\.\d+)%\s(?P<name>[\w|\s]+)$")

    @staticmethod
    def cluster_mappings(cluster_file):
        mapping = {}
        current_cluster_id = None
        for line in open(cluster_file, "r"):
            # remove trailing \n
            line = line[:-1]
            match = ClusterParser.__cluster_regex.match(line)

            if not match:
                mapping[current_cluster_id].append(line)
                continue

            current_cluster_id = int(match.group("id"))
            mapping[current_cluster_id] = []

        return mapping

    @staticmethod
    def entity_relations(relations_dir):
        relations = {}
        for file in Path(relations_dir).iterdir():
            if file.is_dir():
                continue
            cluster_id = ClusterParser._extract_cluster_id_from_file(file)
            if cluster_id is None:
                continue
            relations[cluster_id] = ClusterParser._process_relation_file(file)
        return relations

    @staticmethod
    def _extract_cluster_id_from_file(file):
        match = ClusterParser.__cluster_id_regex.match(file.name)

        if not match:
            return None

        return int(match.group("cluster_id"))

    @staticmethod
    def _process_relation_file(file):
        with open(file, "r") as relation_input:
            cluster_relations = []
            current_relation = None
            for line in relation_input:
                line = line[:-1]
                relation_match = ClusterParser.__entity_relation_regex.match(line)
                if relation_match:
                    current_relation = Relation(relation_match.group("name"),
                                                float(relation_match.group("relative_occurrence")))
                    cluster_relations.append(current_relation)
                    continue
                value_match = ClusterParser.__entity_relation_value_regex.match(line)
                if value_match and current_relation:
                    current_relation.add_relation_value(value_match.group("name"),
                                                        float(value_match.group("relative_occurrence")))
            return cluster_relations
