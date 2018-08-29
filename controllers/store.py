# /*******************************************************************************

# * IBM Confidential

# * OCO Source Materials

# * (C) Copyright IBM Corp  2018 All Rights Reserved.

# * The source code for this program is not published or otherwise divested of

# * its trade secrets, * irrespective of what has been deposited with

# * the U.S. Copyright Office.

# ******************************************************************************/
import abc


class Store(abc.ABC):
    @abc.abstractmethod
    def list_providers(self, author, account_id, filter_, page_size, page_token):
        pass

    @abc.abstractmethod
    def write_note(self, author, account_id, provider_id, note_id, body, mode):
        pass

    @abc.abstractmethod
    def get_note(self, author, account_id, provider_id, note_id):
        pass

    @abc.abstractmethod
    def list_notes(self, author, account_id, provider_id, filter_, page_size, page_token):
        pass

    @abc.abstractmethod
    def delete_note(self, author, account_id, provider_id, note_id):
        pass

    @abc.abstractmethod
    def write_occurrence(self, author, account_id, provider_id, occurrence_id, body, mode):
        pass

    @abc.abstractmethod
    def list_note_occurrences(self, author, account_id, provider_id, note_id, filter_, page_size, page_token):
        pass

    @abc.abstractmethod
    def get_occurrence(self, author, account_id, provider_id, occurrence_id):
        pass

    @abc.abstractmethod
    def list_occurrences(self, author, account_id, provider_id, filter_, page_size, page_token):
        pass

    @abc.abstractmethod
    def delete_occurrence(self, author, account_id, provider_id, occurrence_id):
        pass

    @abc.abstractmethod
    def delete_account_occurrences(self, author, account_id):
        pass
