import UsersTable from '@/app/components/UserTable';
import { cookies } from 'next/headers';

async function getUsers(token) {
  try {
    const response = await fetch(`${process.env.API_URL}/api/users/`, {
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
    redirect('/login');
    return null;
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
