import abc


class Store(abc.ABC):
    @abc.abstractmethod
    def create_project(self, subject_account_id, project_id, body):
        pass

    @abc.abstractmethod
    def get_project(self, subject_account_id, project_id):
        pass

    @abc.abstractmethod
    def list_projects(self, subject_account_id, filter_, page_size, page_token):
        pass

    @abc.abstractmethod
    def delete_project(self, subject_account_id, project_id):
        pass

    @abc.abstractmethod
    def write_note(self, subject_account_id, project_id, note_id, body, mode):
        pass

    @abc.abstractmethod
    def get_note(self, subject_account_id, project_id, note_id):
        pass

    @abc.abstractmethod
    def list_notes(self, subject_account_id, project_id, filter_, page_size, page_token):
        pass

    @abc.abstractmethod
    def delete_note(self, subject_account_id, project_id, note_id):
        pass

    @abc.abstractmethod
    def write_occurrence(self, subject_account_id, project_id, occurrence_id, body, mode):
        pass

    @abc.abstractmethod
    def list_note_occurrences(self, subject_account_id, project_id, note_id, filter_, page_size, page_token):
        pass

    @abc.abstractmethod
    def get_occurrence(self, subject_account_id, project_id, occurrence_id):
        pass

    @abc.abstractmethod
    def list_occurrences(self, subject_account_id, project_id, filter_, page_size, page_token):
        pass

    @abc.abstractmethod
    def delete_occurrence(self, subject_account_id, project_id, occurrence_id):
        pass

    @abc.abstractmethod
    def delete_account_occurrences(self, resource_account_id):
        pass
