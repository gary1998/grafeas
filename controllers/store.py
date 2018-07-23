import abc


class Store(abc.ABC):
    @abc.abstractmethod
    def list_providers(self, author_id, account_id, filter_, page_size, page_token):
        pass

    @abc.abstractmethod
    def write_note(self, author_id, account_id, provider_id, note_id, body, mode):
        pass

    @abc.abstractmethod
    def get_note(self, author_id, account_id, provider_id, note_id):
        pass

    @abc.abstractmethod
    def list_notes(self, author_id, account_id, provider_id, filter_, page_size, page_token):
        pass

    @abc.abstractmethod
    def delete_note(self, author_id, account_id, provider_id, note_id):
        pass

    @abc.abstractmethod
    def write_occurrence(self, author_id, account_id, provider_id, occurrence_id, body, mode):
        pass

    @abc.abstractmethod
    def list_note_occurrences(self, author_id, account_id, provider_id, note_id, filter_, page_size, page_token):
        pass

    @abc.abstractmethod
    def get_occurrence(self, author_id, account_id, provider_id, occurrence_id):
        pass

    @abc.abstractmethod
    def list_occurrences(self, author_id, account_id, provider_id, filter_, page_size, page_token):
        pass

    @abc.abstractmethod
    def delete_occurrence(self, author_id, account_id, provider_id, occurrence_id):
        pass

    @abc.abstractmethod
    def delete_account_occurrences(self, author_id, account_id):
        pass
