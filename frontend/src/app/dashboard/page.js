import UsersTable from '@/app/components/UserTable';
import { cookies } from 'next/headers';
import { NextResponse } from 'next/server';

async function getUsers(token) {
  try {
    const response = await fetch(`https://auto-nabavka.onrender.com/api/users/`, {
        method: 'GET',
        cache: 'no-store',
        headers: {
          'Authorization': `Bearer ${token.value}`
        },    
      }      
    );

    if (!response.ok) {
      throw new Error('Failed to fetch users');
    }

    const users = await response.json();
    return users.data;

  } catch (error) {
    console.error('Error fetching users:', error);
    return null;
  }
}

export default async function Page() {
  const token = (await cookies()).get("token")

  // Redirect to login if no token is found
  if (!token) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  const users = await getUsers(token);

  return (
    <>
      <UsersTable 
        users={users}
        token={token}
      />
    </>
  )
}
