'use client';

import React, { useState } from 'react';

export default function UserEditForm({ user, closeDialog }) {
  const [updatedUserData, setUpdatedUserData] = useState(user);

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch('/api/edit-user', {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: user.id,
          user_in: updatedUserData,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to update user');
      }

      const data = await response.json();
      console.log('User updated successfully:', data);
      closeDialog(); // Close the dialog after successful update
    } catch (error) {
      console.error('Error updating user:', error);
    }
  };

  return (
    <div className="dialog">
      <form onSubmit={handleSubmit}>
        <h2>Edit User</h2>
        <label>
          Name
          <input
            type="text"
            value={updatedUserData.name}
            onChange={(e) => setUpdatedUserData({ ...updatedUserData, name: e.target.value })}
          />
        </label>
        <label>
          Email
          <input
            type="email"
            value={updatedUserData.email}
            onChange={(e) => setUpdatedUserData({ ...updatedUserData, email: e.target.value })}
          />
        </label>
        <button type="submit">Save Changes</button>
        <button type="button" onClick={closeDialog}>
          Cancel
        </button>
      </form>
    </div>
  );
}
