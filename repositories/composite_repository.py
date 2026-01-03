class CompositeRepository:
    def __init__(self, primary_repo, secondary_repos):
        self._primary_repo = primary_repo
        self._secondary_repos = secondary_repos
        self._all_repos = [primary_repo] + secondary_repos

    def add_item(self, item):
        for repo in self._all_repos:
            try:
                repo.add_item(item)
            except Exception as e:
                print(f"WARNING: Failed to sync one repo {e}")
    
    def remove_item(self, item_id):
        for repo in self._all_repos:
            try:
                repo.remove_item(item_id)
            except Exception as e:
                print(f"WARNING: Failed to remove from one repo {e}")

    def search_by_id(self, item_id):
        return self._primary_repo.search_by_id(item_id)
    
    def get_data(self):
        return self._primary_repo.get_data()
    
    def update(self, new_item):
        for repo in self._all_repos:
            try:
                repo.update(new_item)
            except Exception as e:
                print(f"WARNING: Failed to update in one repo {e}")

    def __len__(self):
        return len(self._primary_repo)
    