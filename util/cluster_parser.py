import re


class ClusterParser:

    __cluster_regex = re.compile(r"\[\[CLUSTER (?P<id>\d+)]]", re.IGNORECASE)

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
