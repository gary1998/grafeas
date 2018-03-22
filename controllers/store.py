import abc


class Store(abc.ABC):
    @abc.abstractmethod
    def create_project(self, account_id, project_id, body):
        pass

    @abc.abstractmethod
    def get_project(self, account_id, project_id):
        pass

    @abc.abstractmethod
    def list_projects(self, account_id, filter_, page_size, page_token):
        pass

    @abc.abstractmethod
    def delete_project(self, account_id, project_id):
        pass

    @abc.abstractmethod
    def write_note(self, account_id, project_id, note_id, body, mode):
        pass

    @abc.abstractmethod
    def get_note(self, account_id, project_id, note_id):
        pass

    @abc.abstractmethod
    def list_notes(self, account_id, project_id, filter_, page_size, page_token):
        pass

    @abc.abstractmethod
    def delete_note(self, account_id, project_id, note_id):
        pass

    @abc.abstractmethod
    def write_occurrence(self, account_id, project_id, occurrence_id, body, mode):
        pass

    @abc.abstractmethod
    def list_note_occurrences(self, account_id, project_id, note_id, filter_, page_size, page_token):
        pass

    @abc.abstractmethod
    def get_occurrence(self, account_id, project_id, occurrence_id):
        pass

    @abc.abstractmethod
    def list_occurrences(self, account_id, project_id, filter_, page_size, page_token):
        pass

    @abc.abstractmethod
    def delete_occurrence(self, account_id, project_id, occurrence_id):
        pass

    @abc.abstractmethod
    def delete_all_account_data(self, account_id):
        pass
