import UsersTable from '@/app/components/UserTable';
import { cookies } from 'next/headers';

async function getUsers(token) {
  // const token = (await cookies()).get("token")
  const response = await fetch(
    "https://auto-nabavka.onrender.com/api/users/",
    {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token.value}`
      }
    }      
  );

  const users = await response.json();

  return users.data;
}

async function createUser(formData) {
  // Fetch token for request
  const token = (await cookies()).get("token")

  // Send POST request
  const response = await fetch('https://auto-nabavka.onrender.com/api/users/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token.value}`
    },
    body: JSON.stringify(formData),
  });

  // Check and log response accordingly
  if (response.ok) {
    console.log('User created successfully');
  } else {
    console.error('Failed to create user');
  }      

  const data = await response.json()
  
  return data;
}

export default async function Page() {
  const token = (await cookies()).get("token")
  const users = await getUsers(token);
  // console.log(users)

  return (
    <>
      <UsersTable 
        users={users}
        token={token}
      />
    </>
  )
}
