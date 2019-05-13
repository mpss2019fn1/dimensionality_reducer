CLUSTER_INDICATOR = "[[CLUSTER"


class ClusterParser:

    @staticmethod
    def cluster_mappings(cluster_file):
        mapping = {}
        current_cluster = ""
        for line in open(cluster_file, "r"):
            if line.startswith(CLUSTER_INDICATOR):
                current_cluster = int(line.split(" ")[1].replace("]", ""))
                continue
            mapping[line.replace("\n", "")] = current_cluster

        return mapping
