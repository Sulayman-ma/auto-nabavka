'use client'

import React, { useState } from 'react';
import { MagnifyingGlassIcon, TrashIcon } from "@heroicons/react/24/outline";
import { UserPlusIcon } from "@heroicons/react/24/solid";
import SkeletonTable from '@/app/components/UserTableSkeleton';
import {
  Card,
  CardHeader,
  Input,
  Typography,
  Button,
  CardBody,
  Switch,
  Dialog, 
  DialogHeader, 
  DialogBody, 
  DialogFooter,
  CardFooter,
  Spinner
} from "@material-tailwind/react";

const TABLE_HEAD = ["User", "ID", "Chat ID", "Status", ""];

export default function UsersTable({ users: initialUsers, token }) {
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [createOpen, setCreateOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [selectedId, setSelectedId] = useState(null);
  const [users, setUsers] = useState(initialUsers);

  const handleToggleUser = async (id) => {
    setLoading(true);
    try {
      const toggleUrl = `https://auto-nabavka.onrender.com/api/users/toggle/${id}`;
      const response = await fetch(toggleUrl, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token.value}`,
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json()
  
      if (!response.ok) {
        alert(data.message || "Failed to toggle user status.");
        return;
      }
  
      setUsers((prevUsers) =>
        prevUsers.map((user) =>
          // Update the toggled user's data in place to reflect change without the need to refresh page
          user.id === id ? { ...user, is_active: !user.is_active } : user
        )
      );
      alert(data.message);
    } catch (error) {
        console.error(error);
        alert("An error occurred while toggling user status.");
    } finally {
        setLoading(false);
        setConfirmOpen(false);
    }
  };  

  const handleDeleteUser = async (id) => {
    setLoading(true);
    try {
      const toggleUrl = `https://auto-nabavka.onrender.com/api/users/${id}`;
      const response = await fetch(toggleUrl, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token.value}`,
        },
      });

      const data = await response.json()
  
      if (!response.ok) {
        alert(data.message || "Failed to delete user.");
        return;
      }

      setUsers((prevUsers) => prevUsers.filter((user) => user.id !== id));
      alert(data.message);
    } catch (error) {
        console.error(error);
        alert("An error occurred while deleting the user.");
    } finally {
        setLoading(false);
        setConfirmOpen(false);
    }
  };  

  const handleCreateUser = async () => {
    setLoading(true);
    try {
      const url = `https://auto-nabavka.onrender.com/api/users/`;
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token.value}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      // Response is the user
      const data = await response.json();
      if (response.ok) {
        // Add new user to list of users for automatic rerender
        setUsers((prevUsers) => [...prevUsers, data]); 
      } else {
        alert("Failed to create user");
      }
    } catch (error) {
      console.error(error);
        alert("An error occurred while creating the user.");
    } finally {
        setLoading(false);
        setCreateOpen(false);
    }
  };

  return (
    <div className='container mx-auto flex items-center justify-center h-screen my-20'>
      <Card className="flex justify-center w-full">
        <CardHeader floated={false} shadow={false} className="rounded-none">
          <div className="mb-8 flex items-center justify-between gap-8">
            <Typography variant='h3'>Auto Nabavka Admin</Typography>
            <div className="flex shrink-0 flex-col gap-2 sm:flex-row">
              <Button
                className="flex items-center gap-3"
                size="sm"
                onClick={() => setCreateOpen((cur) => !cur)}
              >
                <UserPlusIcon strokeWidth={2} className="h-4 w-4" /> Create User
              </Button>
            </div>
          </div>
          <div className="flex flex-col items-center justify-between gap-4 md:flex-row">
            <div className="w-full md:w-72">
              <Input
                label="Search"
                icon={<MagnifyingGlassIcon className="h-5 w-5" />}
              />
            </div>
          </div>
        </CardHeader>
        <CardBody className="overflow-none px-0">
          <div className='text-center'>
            <Typography variant="h5" color="blue-gray">Users List</Typography>
            <Typography color="gray" className="mt-1 font-normal">See information about all platform users</Typography>
          </div>
          <table className="mt-4 w-full min-w-max table-auto text-left">
            <thead>
              <tr>
                {TABLE_HEAD.map((head, index) => (
                  <th key={index} className="cursor-pointer border-y border-blue-gray-100 bg-blue-gray-50/50 p-4 transition-colors hover:bg-blue-gray-50">
                    <Typography variant="small" color="blue-gray" className="flex items-center justify-between gap-2 font-normal leading-none opacity-70">
                      {head}
                    </Typography>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {users.map(({ id, name, email, is_active, chat_id, is_superuser }, index) => {
                const isLast = index === users.length - 1;
                const classes = isLast ? "p-4" : "p-4 border-b border-blue-gray-50";
                return (
                  <tr key={id}>
                    <td className={classes}>
                      <div className="flex items-center gap-3">
                        <div className="flex flex-col">
                          <Typography variant="small" color="blue-gray" className="font-normal">{email}</Typography>
                          <Typography variant="small" color="blue-gray" className="font-normal opacity-70">
                            {
                              is_superuser ?
                              'Admin' : 'User'
                            }
                          </Typography>
                        </div>
                      </div>
                    </td>
                    <td className={classes}>
                      <div className="flex items-center gap-3">
                        <div className="flex flex-col">
                          <Typography variant="small" color="blue-gray" className="font-normal">{id}</Typography>
                        </div>
                      </div>
                    </td>
                    <td className={classes}>
                      <div className="items-center gap-3">
                        <Typography variant="small" color="blue-gray" className="font-normal">
                          {chat_id ? chat_id : "-"}
                        </Typography>
                      </div>
                    </td>
                    <td className={classes}>
                      <div className="w-max">
                        <Switch 
                          checked={is_active} 
                          onChange={() => {
                            setConfirmOpen((cur) => !cur)
                            setSelectedId(id)
                          }}
                          disabled={loading} 
                        />
                      </div>
                    </td>
                    <td className={classes}>
                      <div className="w-max">
                        <TrashIcon 
                          className='w-8 h-8'
                          onClick={() => {
                            setDeleteOpen((cur) => !cur)
                            setSelectedId(id)
                          }}
                        />
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </CardBody>
      </Card>

      {/* Toggle user confirm Dialog */}
      <Dialog open={confirmOpen} handler={() => setConfirmOpen((cur) => !cur)}>
        <DialogHeader>Toggle user status</DialogHeader>
        <DialogBody>Are you sure you want to toggle the status of this user?</DialogBody>
        <DialogFooter>
          <button onClick={() => setConfirmOpen(false)} className="mr-2 bg-gray-500 text-white px-4 py-2 rounded">Cancel</button>
          <button onClick={() => handleToggleUser(selectedId)} className="flex items-center bg-blue-500 text-white px-4 py-2 rounded" disabled={loading}>
            {loading ? <Spinner /> : "Confirm"}
          </button>
        </DialogFooter>
      </Dialog>
      
      {/* Create User Dialog */}
      <Dialog size="xs" open={createOpen} handler={() => setCreateOpen((cur) => !cur)} className="bg-transparent shadow-none">
        <Card className="mx-auto w-full max-w-[24rem]">
          <CardBody className="flex flex-col gap-4">
            <Typography variant="h4" color="blue-gray">Create User</Typography>
            <Typography className="mb-3 font-normal" variant="paragraph" color="gray">Enter user email and password.</Typography>
            <Input label="Email" onChange={(e) => setEmail(e.target.value)} value={email} size="lg" />
            <Input label="Password" onChange={(e) => setPassword(e.target.value)} value={password} size="lg" />
          </CardBody>
          <CardFooter className="pt-0">
            <Button variant="gradient" className='mb-4' onClick={handleCreateUser} fullWidth disabled={loading}>
              {loading ? <Spinner /> : "Submit"}
            </Button>
          </CardFooter>
        </Card>
      </Dialog>

      {/* Delete User Dialog */}
      <Dialog open={deleteOpen} handler={() => setDeleteOpen((cur) => !cur)}>
        <DialogHeader>Delete user</DialogHeader>
        <DialogBody>Are you sure you want to delete this user? This action cannot be undone</DialogBody>
        <DialogFooter>
          <button onClick={() => setDeleteOpen(false)} className="mr-2 bg-gray-500 text-white px-4 py-2 rounded">Cancel</button>
          <button onClick={() => handleDeleteUser(selectedId)} className="flex items-center bg-red-500 text-white px-4 py-2 rounded" disabled={loading}>
            {loading ? <Spinner /> : "Delete"}
          </button>
        </DialogFooter>
      </Dialog>
    </div>
  );
}
