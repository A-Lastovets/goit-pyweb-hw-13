import unittest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
import models
import schemas
from crud import (
    create_contact,
    get_contact,
    get_contacts,
    update_contact,
    delete_contact,
    create_user,
    authenticate_user,
    get_user_by_email,
    get_contacts_by_user,
    verify_user_email,
    is_user_verified,
    update_user_avatar,
)

class TestCRUD(unittest.TestCase):

    def setUp(self):
        self.db = MagicMock(spec=Session)
        self.contact_data = schemas.ContactCreate(name="John Doe", email="john@example.com")
        self.user_data = schemas.UserCreate(email="user@example.com", password="securepassword")

    def test_create_contact(self):
        contact = create_contact(self.db, self.contact_data)
        self.db.add.assert_called_once()
        self.db.commit.assert_called_once()
        self.assertIsInstance(contact, models.Contact)

    def test_get_contact(self):
        mock_contact = models.Contact(id=1, name="John Doe", email="john@example.com")
        self.db.query.return_value.filter.return_value.first.return_value = mock_contact
        contact = get_contact(self.db, 1)
        self.assertEqual(contact.name, "John Doe")

    def test_get_contacts(self):
        mock_contacts = [models.Contact(id=1, name="John Doe"), models.Contact(id=2, name="Jane Doe")]
        self.db.query.return_value.offset.return_value.limit.return_value.all.return_value = mock_contacts
        contacts = get_contacts(self.db)
        self.assertEqual(len(contacts), 2)

    def test_update_contact(self):
        mock_contact = models.Contact(id=1, name="John Doe", email="john@example.com")
        self.db.query.return_value.filter.return_value.first.return_value = mock_contact
        contact_update_data = schemas.ContactUpdate(name="Updated Name")
        updated_contact = update_contact(self.db, 1, contact_update_data)
        self.assertEqual(updated_contact.name, "Updated Name")

    def test_delete_contact(self):
        mock_contact = models.Contact(id=1, name="John Doe")
        self.db.query.return_value.filter.return_value.first.return_value = mock_contact
        deleted_contact = delete_contact(self.db, 1)
        self.db.delete.assert_called_once_with(mock_contact)
        self.db.commit.assert_called_once()
        self.assertEqual(deleted_contact.name, "John Doe")

    def test_create_user(self):
        new_user = create_user(self.db, self.user_data)
        self.assertIsInstance(new_user, models.User)
        self.db.add.assert_called_once()
        self.db.commit.assert_called_once()

    def test_authenticate_user(self):
        mock_user = models.User(email="user@example.com", hashed_password="hashedpassword")
        self.db.query.return_value.filter.return_value.first.return_value = mock_user
        with patch('crud.verify_password') as mock_verify:
            mock_verify.return_value = True
            user = authenticate_user(self.db, "user@example.com", "securepassword")
            self.assertEqual(user.email, "user@example.com")

    def test_get_user_by_email(self):
        mock_user = models.User(email="user@example.com")
        self.db.query.return_value.filter.return_value.first.return_value = mock_user
        user = get_user_by_email(self.db, "user@example.com")
        self.assertEqual(user.email, "user@example.com")

    def test_get_contacts_by_user(self):
        mock_contacts = [models.Contact(id=1, name="John Doe")]
        self.db.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = mock_contacts
        contacts = get_contacts_by_user(self.db, 1)
        self.assertEqual(len(contacts), 1)

    def test_verify_user_email(self):
        mock_user = models.User(email="user@example.com", is_verified=False)
        self.db.query.return_value.filter.return_value.first.return_value = mock_user
        verified_user = verify_user_email(self.db, "user@example.com")
        self.assertTrue(verified_user.is_verified)

    def test_is_user_verified(self):
        mock_user = models.User(email="user@example.com", is_verified=True)
        self.db.query.return_value.filter.return_value.first.return_value = mock_user
        is_verified = is_user_verified(self.db, "user@example.com")
        self.assertTrue(is_verified)

    def test_update_user_avatar(self):
        mock_user = models.User(id=1, avatar_url="old_avatar.png")
        self.db.query.return_value.filter.return_value.first.return_value = mock_user
        updated_user = update_user_avatar(self.db, 1, "new_avatar.png")
        self.assertEqual(updated_user.avatar_url, "new_avatar.png")

if __name__ == "__main__":
    unittest.main()
