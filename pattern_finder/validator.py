# validator.py

class LinkValidator:
    """
    Performs sanity checks on inferred links
    """

    def validate(self, link_map):
        issues = []

        for link, cells in link_map.items():
            if len(cells) == 1:
                issues.append(f"{link} has only one cell (low confidence group)")

        return issues
